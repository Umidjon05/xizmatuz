from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order
from masters.models import MasterProfile
from masters.utils import haversine_distance
from core.telegram import send_telegram_message


@login_required
def client_dashboard(request):
    if request.user.user_type != 'client':
        return redirect('home')

    my_orders = Order.objects.filter(
        client=request.user,
        hidden_by_client=False,
    ).select_related(
        'category',
        'master',
        'master__user'
    )

    return render(request, 'dashboard/client_dashboard.html', {
        'orders': my_orders
    })


@login_required
def master_dashboard(request):
    if request.user.user_type != 'master':
        return redirect('home')

    accepted_orders = []
    try:
        master_profile = MasterProfile.objects.get(user=request.user)
        my_categories = master_profile.categories.all()
        incoming_orders = Order.objects.filter(category__in=my_categories, status='pending')
        accepted_orders = Order.objects.filter(master=master_profile, status__in=['accepted', 'in_progress'])
    except MasterProfile.DoesNotExist:
        incoming_orders = []
        messages.warning(request, "Avval profilingizni to'ldiring (kategoriya tanlang).")

    return render(request, 'dashboard/master_dashboard.html', {
        'orders': incoming_orders,
        'accepted_orders': accepted_orders,
    })


@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    master_profile = get_object_or_404(MasterProfile, user=request.user)

    if order.status != 'pending':
        messages.error(request, "Bu buyurtma allaqachon qabul qilingan yoki yopilgan.")
        return redirect('master_dashboard')

    if not master_profile.categories.filter(id=order.category.id).exists():
        messages.error(request, "Bu buyurtma sizning xizmat kategoriyangizga mos emas.")
        return redirect('master_dashboard')

    has_active_order = Order.objects.filter(
        master=master_profile,
        status__in=['accepted', 'in_progress']
    ).exists()

    if has_active_order:
        messages.error(
            request,
            "Avval joriy buyurtmangizni yakunlang, "
            "keyin yangi buyurtma qabul qilishingiz mumkin."
        )
        return redirect('master_dashboard')

    order.master = master_profile
    order.status = 'accepted'
    order.save(update_fields=['master', 'status'])

    messages.success(request, "Buyurtma qabul qilindi! Mijozga xabar yuborildi.")
    return redirect('master_dashboard')
@login_required
def start_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    master_profile = get_object_or_404(MasterProfile, user=request.user)

    if order.master != master_profile:
        messages.error(request, "Bu buyurtma sizga tegishli emas.")
        return redirect('master_dashboard')

    order.status = 'in_progress'
    order.save(update_fields=['status'])
    messages.success(request, "Ish boshlandi! Tugagach, 'Ishni yakunlash' tugmasini bosing.")
    return redirect('master_dashboard')


@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        master_lat = request.POST.get('latitude')
        master_lon = request.POST.get('longitude')

        if not master_lat or not master_lon:
            return JsonResponse({'success': False, 'message': "Joylashuvingiz aniqlanmadi."})

        if not order.latitude or not order.longitude:
            return JsonResponse({'success': False, 'message': "Mijoz manzili koordinatasi yo'q, yakunlab bo'lmaydi."})

        distance = haversine_distance(
            float(master_lat), float(master_lon),
            order.latitude, order.longitude
        )

        if distance is not None and distance <= 0.3:
            order.status = 'completed'
            order.save()
            return JsonResponse({'success': True, 'message': "Buyurtma muvaffaqiyatli yakunlandi!"})
        else:
            return JsonResponse({'success': False, 'message': f"Siz mijoz manzilidan {round(distance, 2)} km uzoqdasiz. Yaqinroq borib, qaytadan urinib ko'ring."})

    return JsonResponse({'success': False, 'message': "Noto'g'ri so'rov."})


@login_required
def master_orders_history(request):
    if request.user.user_type != 'master':
        return redirect('home')

    try:
        master_profile = MasterProfile.objects.get(user=request.user)
        completed = Order.objects.filter(master=master_profile, status='completed')
        cancelled = Order.objects.filter(master=master_profile, status='cancelled')
    except MasterProfile.DoesNotExist:
        completed = []
        cancelled = []

    return render(request, 'dashboard/master_orders_history.html', {
        'completed_orders': completed,
        'cancelled_orders': cancelled,
    })


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user)

    if order.status not in ['pending', 'accepted']:
        messages.error(
            request,
            "Bu buyurtmani endi bekor qilib bo'lmaydi."
        )
        return redirect('client_dashboard')

    was_accepted = order.status == 'accepted'
    master = order.master

    order.status = 'cancelled'
    order.hidden_by_client = True
    order.save(update_fields=['status', 'hidden_by_client'])
    if was_accepted and master and master.telegram_id:
        send_telegram_message(
            master.telegram_id,
            f"❌ <b>Buyurtma bekor qilindi</b>\n"
            f"Buyurtma #{order.id} mijoz tomonidan bekor qilindi."
        )

    messages.success(
        request,
        f"Buyurtma #{order.id} bekor qilindi."
    )
    return redirect('client_dashboard')
@login_required
def hide_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user)

    if order.status not in ['completed', 'cancelled']:
        return JsonResponse({'success': False, 'message': "Faqat yakunlangan yoki bekor qilingan buyurtmani yopish mumkin."})

    order.hidden_by_client = True
    order.save(update_fields=['hidden_by_client'])

    return JsonResponse({'success': True})