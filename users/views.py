from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from masters.models import MasterProfile


@never_cache
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.user_type == 'master':
                user.is_active = False
            user.save()

            if user.user_type == 'master':
                master_profile = MasterProfile.objects.create(
                    user=user,
                    bio=form.cleaned_data.get('extra_info') or '',
                    experience_years=form.cleaned_data.get('experience_years') or 0,
                    
                )
                selected_categories = form.cleaned_data.get('categories')
                if selected_categories:
                    master_profile.categories.set(selected_categories)

                messages.success(request, "Arizangiz qabul qilindi! Admin tasdiqlagandan so'ng tizimga kira olasiz.")
                return redirect('login')
            else:
                login(request, user)
                messages.success(request, "Xush kelibsiz! Ro'yxatdan muvaffaqiyatli o'tdingiz.")
                return redirect_by_role(user)
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect_by_role(user)
        else:
            from .models import User
            try:
                existing_user = User.objects.get(username=username)
                if not existing_user.is_active:
                    messages.error(request, "Hisobingiz hali admin tomonidan tasdiqlanmagan.")
                else:
                    messages.error(request, "Login yoki parol noto'g'ri.")
            except User.DoesNotExist:
                messages.error(request, "Login yoki parol noto'g'ri.")
    return render(request, 'users/login.html')


def redirect_by_role(user):
    if user.is_superuser:
        return redirect('/admin/')
    elif user.user_type == 'master':
        return redirect('master_dashboard')
    else:
        return redirect('client_dashboard')


def logout_view(request):
    logout(request)
    return redirect('home')


@csrf_exempt
def save_location(request):
    if request.method == 'POST' and request.user.is_authenticated:
        city = request.POST.get('city')
        if city:
            request.user.city = city
            request.user.save()
            return JsonResponse({'status': 'ok', 'city': city})
    return JsonResponse({'status': 'error'})