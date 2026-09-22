
from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category, MasterProfile
from orders.models import Order
from .utils import haversine_distance


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    all_masters = MasterProfile.objects.filter(
        categories=category,
        status='approved'
    )

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
            status='pending',
        )

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
            status='accepted',
        )

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

