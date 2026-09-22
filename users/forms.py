from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from masters.models import Category


class RegisterForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('client', 'Mijoz sifatida'),
        ('master', 'Usta sifatida'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, label="Kim sifatida ro'yxatdan o'tasiz?")
    phone = forms.CharField(max_length=20, label="Telefon raqam")
    city = forms.CharField(max_length=100, required=True, widget=forms.HiddenInput())
    district = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    street = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())
    full_address = forms.CharField(max_length=500, required=True, label="Manzilingiz", widget=forms.TextInput(attrs={'readonly': 'readonly', 'id': 'id_full_address'}))
    latitude = forms.FloatField(required=True, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=True, widget=forms.HiddenInput())
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.filter(parent__isnull=False), required=False, label="Qaysi soha(lar)da ishlaysiz? (faqat usta uchun)", widget=forms.CheckboxSelectMultiple())
    extra_info = forms.CharField(required=False, label="Qo'shimcha ma'lumot", widget=forms.Textarea(attrs={'rows': 2}))
    experience_years = forms.IntegerField(required=False, min_value=0, label="Tajriba (necha yil)")
    
    class Meta:
        model = User
        fields = ['username', 'phone', 'full_address', 'city', 'district', 'street', 'latitude', 'longitude', 'user_type', 'password1', 'password2']