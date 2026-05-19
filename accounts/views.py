from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import MemberRegistrationForm
from members.models import Member
from django.contrib.auth.models import User

def register(request):
    """Регистрация нового члена ассоциации"""
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            
            # Создаем члена ассоциации
            member = form.save(commit=False)
            member.user = user
            member.status = 'pending'  # На модерации
            member.save()
            
            # Автоматически входим в систему
            login(request, user)
            
            messages.success(request, 'Регистрация успешно завершена! Ваша заявка отправлена на модерацию.')
            return redirect('accounts:profile')  # Добавили accounts:
    else:
        form = MemberRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """Личный кабинет пользователя"""
    try:
        member = request.user.member
    except Member.DoesNotExist:
        messages.error(request, 'Профиль не найден. Обратитесь к администратору.')
        return redirect('home')
    
    if request.method == 'POST':
        # Обновляем данные (нельзя менять категорию и статус)
        member.company_name = request.POST.get('company_name', member.company_name)
        member.legal_address = request.POST.get('legal_address', member.legal_address)
        member.actual_address = request.POST.get('actual_address', member.actual_address)
        member.director_fullname = request.POST.get('director_fullname', member.director_fullname)
        member.phone = request.POST.get('phone', member.phone)
        member.save()
        messages.success(request, 'Данные успешно обновлены!')
        return redirect('accounts:profile')  # Добавили accounts:
    
    return render(request, 'accounts/profile.html', {'member': member})
