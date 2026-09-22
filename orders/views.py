from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from .models import Order
from masters.models import MasterProfile
from masters.utils import haversine_distance


@login_required
def client_dashboard(request):
    if request.user.user_type != 'client':
        return redirect('home')

    my_orders = Order.objects.filter(
        client=request.user
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

        incoming_orders = Order.objects.filter(
            category__in=my_categories,
            status='pending'
        ).select_related(
            'client',
            'category'
        )

        accepted_orders = Order.objects.filter(
            master=master_profile,
            status__in=['accepted', 'in_progress']
        ).select_related(
            'client',
            'category'
        )

    except MasterProfile.DoesNotExist:
        incoming_orders = []
        messages.warning(
            request,
            "Avval profilingizni to'ldiring (kategoriya tanlang)."
        )

    return render(request, 'dashboard/master_dashboard.html', {
        'orders': incoming_orders,
        'accepted_orders': accepted_orders,
    })


@login_required
def accept_order(request, order_id):
    if request.user.user_type != 'master':
        return redirect('home')

    master_profile = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id
        )

        if order.status != 'pending':
            messages.error(
                request,
                "Bu buyurtma allaqachon boshqa usta tomonidan qabul qilingan."
            )
            return redirect('master_dashboard')

        if not master_profile.categories.filter(
            id=order.category.id
        ).exists():
            messages.error(
                request,
                "Bu buyurtma sizning xizmat kategoriyangizga mos emas."
            )
            return redirect('master_dashboard')

        order.master = master_profile
        order.status = 'accepted'
        order.save(update_fields=['master', 'status'])

    messages.success(
        request,
        "Buyurtma qabul qilindi! Endi ishni boshlashingiz mumkin."
    )

    return redirect('master_dashboard')


@login_required
def start_order(request, order_id):
    if request.user.user_type != 'master':
        return redirect('home')

    master_profile = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    order = get_object_or_404(
        Order,
        id=order_id,
        master=master_profile
    )

    if order.status != 'accepted':
        messages.error(
            request,
            "Bu buyurtmani hozir boshlash mumkin emas."
        )
        return redirect('master_dashboard')

    order.status = 'in_progress'
    order.save(update_fields=['status'])

    messages.success(
        request,
        "Ish boshlandi! Mijozga buyurtma bajarilayotgani ko'rsatiladi."
    )

    return redirect('master_dashboard')


@login_required
def complete_order(request, order_id):
    if request.user.user_type != 'master':
        return JsonResponse({
            'success': False,
            'message': "Ruxsat berilmagan."
        })

    order = get_object_or_404(
        Order,
        id=order_id
    )

    master_profile = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    if order.master != master_profile:
        return JsonResponse({
            'success': False,
            'message': "Bu buyurtma sizga tegishli emas."
        })

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': "Noto'g'ri so'rov."
        })

    if order.status != 'in_progress':
        return JsonResponse({
            'success': False,
            'message': "Avval ishni boshlashingiz kerak."
        })

    master_lat = request.POST.get('latitude')
    master_lon = request.POST.get('longitude')

    if not master_lat or not master_lon:
        return JsonResponse({
            'success': False,
            'message': "Joylashuvingiz aniqlanmadi."
        })

    if order.latitude is None or order.longitude is None:
        return JsonResponse({
            'success': False,
            'message': "Mijoz manzili koordinatasi yo'q, yakunlab bo'lmaydi."
        })

    try:
        master_lat = float(master_lat)
        master_lon = float(master_lon)

        distance = haversine_distance(
            master_lat,
            master_lon,
            order.latitude,
            order.longitude
        )

    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': "Joylashuv koordinatalari noto'g'ri."
        })

    if distance is not None and distance <= 0.3:
        order.status = 'completed'
        order.save(update_fields=['status'])

        return JsonResponse({
            'success': True,
            'message': "Buyurtma muvaffaqiyatli yakunlandi!"
        })

    if distance is None:
        return JsonResponse({
            'success': False,
            'message': "Masofani aniqlab bo'lmadi."
        })

    return JsonResponse({
        'success': False,
        'message': (
            f"Siz mijoz manzilidan {round(distance, 2)} km uzoqdasiz. "
            "Yaqinroq borib, qaytadan urinib ko'ring."
        )
    })


@login_required
def order_status(request, order_id):
    if request.user.user_type != 'client':
        return JsonResponse({
            'success': False,
            'message': "Ruxsat berilmagan."
        }, status=403)

    order = get_object_or_404(
        Order.objects.select_related(
            'category',
            'master',
            'master__user'
        ),
        id=order_id,
        client=request.user
    )

    master_name = None

    if order.master:
        master_name = order.master.user.get_full_name()

        if not master_name:
            master_name = order.master.user.username

    return JsonResponse({
        'success': True,
        'order_id': order.id,
        'status': order.status,
        'status_display': order.get_status_display(),
        'master_name': master_name,
    })