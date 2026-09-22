from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@login_required
def profile_view(request):
    user = request.user
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'profile':
            user.phone = request.POST.get('phone', '').strip()
            user.full_address = request.POST.get('full_address', '').strip()
            user.city = request.POST.get('city', '').strip()
            user.district = request.POST.get('district', '').strip()
            user.street = request.POST.get('street', '').strip()

            lat = _to_float(request.POST.get('latitude'))
            lon = _to_float(request.POST.get('longitude'))
            if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
                user.latitude = lat
                user.longitude = lon

            user.save()
            messages.success(request, "Ma'lumotlaringiz saqlandi.")
            return redirect('profile')

        if action == 'password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # tizimdan chiqib ketmaslik uchun
                messages.success(request, "Parol o'zgartirildi.")
                return redirect('profile')
            messages.error(request, "Parolni o'zgartirib bo'lmadi. Xatolarni tuzating.")

    return render(request, 'users/profile.html', {'password_form': password_form})