from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category, MasterProfile
from orders.models import Order
from .utils import haversine_distance
from core.telegram import send_telegram_message

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    all_masters = MasterProfile.objects.filter(
        categories=category,
        status='approved'
    ).order_by('-avg_rating', '-ratings_count')

    masters_list = list(all_masters)

    if (
        request.user.is_authenticated
        and request.user.latitude
        and request.user.longitude
    ):
        for master in masters_list:
            mu = master.user

            if mu.latitude and mu.longitude:
                distance = haversine_distance(
                    request.user.latitude,
                    request.user.longitude,
                    mu.latitude,
                    mu.longitude
                )

                master.distance = (
                    round(distance, 1)
                    if distance is not None
                    else None
                )
            else:
                master.distance = None

        masters_list.sort(
            key=lambda m: (
                m.distance is None,
                m.distance
            )
        )

    return render(
        request,
        'masters/category_detail.html',
        {
            'category': category,
            'masters': masters_list,
        }
    )


@login_required
@never_cache
def create_order(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.user.user_type != 'client':
        messages.error(
            request,
            "Faqat mijozlar buyurtma bera oladi."
        )
        return redirect('home')

    if request.method == 'POST':
        description = request.POST.get(
            'description',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        latitude = request.POST.get(
            'latitude'
        ) or None

        longitude = request.POST.get(
            'longitude'
        ) or None

        time_from = request.POST.get(
            'time_from'
        ) or None

        time_to = request.POST.get(
            'time_to'
        ) or None

        if not description:
            messages.error(
                request,
                "Muammo tavsifini kiriting."
            )

            return render(
                request,
                'masters/create_order.html',
                {
                    'category': category
                }
            )

        if not address:
            messages.error(
                request,
                "Manzilni aniqlang."
            )

            return render(
                request,
                'masters/create_order.html',
                {
                    'category': category
                }
            )

        if phone:
            request.user.phone = phone
            request.user.save(
                update_fields=['phone']
            )

        order = Order.objects.create(
            client=request.user,
            category=category,
            description=description,
            address=address,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            time_from=time_from,
            time_to=time_to,
            status='pending',
        )

        notify_masters = MasterProfile.objects.filter(
            categories=category,
            status='approved',
            telegram_id__isnull=False,
        )

        for nm in notify_masters:
            text = (
                f"🆕 <b>Yangi buyurtma</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔧 <b>Kategoriya:</b> {category.name}\n"
                f"📝 <b>Tavsif:</b> {description}\n"
                f"📍 <b>Manzil:</b> {address}\n"
                f"📞 <b>Telefon:</b> {phone}"
            )

            if time_from and time_to:
                text += f"\n🕐 <b>Bo'sh vaqt:</b> {time_from} — {time_to}"

            reply_markup = {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅ Qabul qilish",
                            "callback_data": f"accept_order_{order.id}"
                        }
                    ]
                ]
            }

            if latitude and longitude:
                reply_markup["inline_keyboard"].append([
                    {
                        "text": "📍 Xaritada ko'rish",
                        "url": f"https://maps.google.com/?q={latitude},{longitude}"
                    }
                ])

            send_telegram_message(nm.telegram_id, text, reply_markup)

        messages.success(
            request,
            f"Buyurtma #{order.id} muvaffaqiyatli yuborildi! "
            f"Tez orada usta bog'lanadi."
        )

        return redirect('client_dashboard')

    return render(
        request,
        'masters/create_order.html',
        {
            'category': category
        }
    )

@login_required
@never_cache
def create_order_for_master(
    request,
    slug,
    master_id
):
    category = get_object_or_404(
        Category,
        slug=slug
    )

    master = get_object_or_404(
        MasterProfile,
        id=master_id
    )

    if request.user.user_type != 'client':
        messages.error(
            request,
            "Faqat mijozlar buyurtma bera oladi."
        )

        return redirect('home')

    if request.method == 'POST':
        description = request.POST.get(
            'description',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        latitude = request.POST.get(
            'latitude'
        ) or None

        longitude = request.POST.get(
            'longitude'
        ) or None

        time_from = request.POST.get(
            'time_from'
        ) or None

        time_to = request.POST.get(
            'time_to'
        ) or None

        if not description:
            messages.error(
                request,
                "Muammo tavsifini kiriting."
            )

            return render(
                request,
                'masters/create_order.html',
                {
                    'category': category,
                    'master': master
                }
            )

        if not address:
            messages.error(
                request,
                "Manzilni aniqlang."
            )

            return render(
                request,
                'masters/create_order.html',
                {
                    'category': category,
                    'master': master
                }
            )

        if phone:
            request.user.phone = phone
            request.user.save(
                update_fields=['phone']
            )

        order = Order.objects.create(
            client=request.user,
            category=category,
            master=master,
            description=description,
            address=address,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            time_from=time_from,
            time_to=time_to,
            status='pending',
        )

        if master.telegram_id:
            text = (
                f"🆕 <b>Sizga yangi buyurtma yuborildi</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔧 <b>Kategoriya:</b> {category.name}\n"
                f"📝 <b>Tavsif:</b> {description}\n"
                f"📍 <b>Manzil:</b> {address}\n"
                f"📞 <b>Telefon:</b> {phone}"
            )

            if time_from and time_to:
                text += f"\n🕐 <b>Bo'sh vaqt:</b> {time_from} — {time_to}"

            reply_markup = None
            if latitude and longitude:
                reply_markup = {
                    "inline_keyboard": [[
                        {
                            "text": "📍 Xaritada ko'rish",
                            "url": f"https://maps.google.com/?q={latitude},{longitude}"
                        }
                    ]]
                }

            send_telegram_message(master.telegram_id, text, reply_markup)

        messages.success(
            request,
            f"Buyurtma {master.user.username}ga yuborildi!"
        )

        return redirect('client_dashboard')

    return render(
        request,
        'masters/create_order.html',
        {
            'category': category,
            'master': master
        }
    )


@login_required
def connect_telegram(request):
    """
    Usta o'z Telegram akkauntini Xizmat Uz botiga ulaydi.
    """

    master = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    bot_username = "XizmatUzAppBot"

    telegram_link = (
        f"https://t.me/{bot_username}"
        f"?start=master_{master.id}"
    )

    return redirect(telegram_link)