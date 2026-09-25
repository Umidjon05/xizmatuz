from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from orders.models import Order
from .models import Review


@login_required
@require_POST
def submit_review(request, order_id):
    """
    Mijoz o'zi buyurtma bergan va 'completed' bo'lgan ishga 1-5 yulduz baho qo'yadi.
    Frontenddan fetch(POST) orqali chaqiriladi: rating (majburiy), comment (ixtiyoriy).
    """
    order = get_object_or_404(Order, id=order_id, client=request.user)

    if order.status != 'completed':
        return JsonResponse(
            {'ok': False, 'error': "Faqat yakunlangan ishga baho qo'yish mumkin"},
            status=400,
        )

    if order.master_id is None:
        return JsonResponse(
            {'ok': False, 'error': "Bu buyurtmaga usta biriktirilmagan"},
            status=400,
        )

    if hasattr(order, 'review'):
        return JsonResponse(
            {'ok': False, 'error': "Bu buyurtmaga baho allaqachon qo'yilgan"},
            status=400,
        )

    rating = request.POST.get('rating')
    if rating not in ('1', '2', '3', '4', '5'):
        return JsonResponse({'ok': False, 'error': "Noto'g'ri baho"}, status=400)

    Review.objects.create(
        order=order,
        master=order.master,
        client=request.user,
        rating=int(rating),
        comment=request.POST.get('comment', '').strip(),
    )

    return JsonResponse({
        'ok': True,
        'new_avg_rating': float(order.master.avg_rating),
        'ratings_count': order.master.ratings_count,
    })