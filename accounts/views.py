from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import logging
from .forms import MemberRegistrationForm
from .utils import send_registration_email, send_admin_notification
from members.models import Member
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def register(request):
    """Регистрация нового члена ассоциации"""
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)
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
            member.status = 'pending'
            member.save()
            
            # Отправляем email уведомления
            email_errors = []
            
            try:
                email_sent = send_registration_email(user, member, request)
                if not email_sent:
                    email_errors.append('регистрационное')
            except Exception as e:
                logger.error(f"Registration email error: {e}")
                email_errors.append('регистрационное')
            
            try:
                admin_sent = send_admin_notification(member, request)
                if not admin_sent:
                    email_errors.append('администратору')
            except Exception as e:
                logger.error(f"Admin notification error: {e}")
                email_errors.append('администратору')
            
            # Автоматически входим в систему
            login(request, user)
            
            # Очищаем все предыдущие сообщения, чтобы избежать дублей
            storage = messages.get_messages(request)
            storage.used = True
            
            # Сообщение пользователю (только одно!)
            if email_errors:
                messages.warning(
                    request, 
                    f'Регистрация успешно завершена! Ваша заявка отправлена на модерацию. '
                    f'Не удалось отправить {" и ".join(email_errors)} письмо(а). '
                    f'Мы свяжемся с вами в ближайшее время.'
                )
            else:
                messages.success(
                    request, 
                    'Регистрация успешно завершена! Ваша заявка отправлена на модерацию. '
                    'Уведомление отправлено на ваш email.'
                )
            
            return redirect('accounts:profile')
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
        
        # Очищаем старые сообщения перед добавлением нового
        storage = messages.get_messages(request)
        storage.used = True
        
        messages.success(request, 'Данные успешно обновлены!')
        return redirect('accounts:profile')
    
    context = {
        'member': member,
    }
    return render(request, 'accounts/profile.html', context)