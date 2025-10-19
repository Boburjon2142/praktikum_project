from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin


# 🔐 Foydalanuvchi tizimga kirish
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('user_profile')
                else:
                    return HttpResponse("Sizning hisobingiz faol emas.")
            else:
                return HttpResponse("Noto'g'ri foydalanuvchi nomi yoki parol.")
    else:
        form = LoginForm()
    context = {'form': form}
    return render(request, 'registration/login.html', context)


# 🔐 Dashboard yoki profil
@login_required
def dashboard_view(request):
    user = request.user
    profile = Profile.objects.filter(user=user).first()
    context = {'user': user, 'profile': profile}
    return render(request, 'pages/user_profile.html', context)


# ?? User profilini ko`rish

@login_required
def user_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'pages/user_profile.html', {'profile': profile})

def user_register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'account/register.html'


class SignUpView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'account/register.html', {'user_form': user_form})
    
    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user})


# 🔐 Profilni tahrirlash (funksiya ko‘rinishida)
@login_required
def edit_user(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        
    return render(request, 'account/profile_edit.html', {"user_form": user_form, "profile_form": profile_form})


# 🔐 Profilni tahrirlash (class-based view)
@method_decorator(login_required, name='dispatch')
class EditUserView(LoginRequiredMixin, View):
    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, 'account/profile_edit.html', {"user_form": user_form, "profile_form": profile_form})
    
    def post(self, request):
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        return redirect('user_profile')




