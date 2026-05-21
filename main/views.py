from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from main.models import News, Project, SupportMeasure, Event, EventRegistration
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from datetime import timedelta
from django.utils import timezone

def home(request):
    context = {
        'news': News.objects.filter(is_published=True)[:3],
        'projects': Project.objects.filter(is_active=True)[:3],
        'support_measures': SupportMeasure.objects.all()[:3],
    }
    return render(request, 'main/home.html', context)

def about(request):
    return render(request, 'main/about.html')

def news_list(request):
    """Список всех новостей"""
    news_list = News.objects.filter(is_published=True).order_by('-published_at')
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)
    return render(request, 'main/news_list.html', {'news': news})

def news_detail(request, news_id):
    """Детальная страница новости"""
    news = get_object_or_404(News, id=news_id, is_published=True)
    other_news = News.objects.filter(is_published=True).exclude(id=news_id)[:3]
    return render(request, 'main/news_detail.html', {'news': news, 'other_news': other_news})

def projects_list(request):
    """Список проектов"""
    projects = Project.objects.filter(is_active=True).order_by('-start_date')
    return render(request, 'main/projects_list.html', {'projects': projects})

def support_measures_list(request):
    """Список мер поддержки"""
    measures = SupportMeasure.objects.all().order_by('-created_at')
    return render(request, 'main/support_measures.html', {'measures': measures})

def search(request):
    """Поиск по сайту"""
    query = request.GET.get('q', '')
    results = {
        'news': [],
        'projects': [],
        'support_measures': []
    }
    
    if query:
        results['news'] = News.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_published=True
        )[:10]
        
        results['projects'] = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:10]
        
        results['support_measures'] = SupportMeasure.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:10]
    
    context = {
        'query': query,
        'results': results,
        'total_count': sum([len(results['news']), len(results['projects']), len(results['support_measures'])])
    }
    return render(request, 'main/search.html', context)

def events_list(request):
    """Список мероприятий"""
    from django.utils import timezone
    
    events = Event.objects.filter(
        status='published',
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    # Разделяем на предстоящие и прошедшие
    upcoming_events = events.filter(start_date__gte=timezone.now())
    past_events = Event.objects.filter(
        status='published',
        start_date__lt=timezone.now()
    ).order_by('-start_date')[:5]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'main/events_list.html', context)

def event_detail(request, event_id):
    """Детальная страница мероприятия"""
    from django.utils import timezone
    
    event = get_object_or_404(Event, id=event_id, status='published')
    
    # Проверяем, зарегистрирован ли текущий пользователь (только активные регистрации)
    is_registered = False
    if request.user.is_authenticated and hasattr(request.user, 'member'):
        is_registered = EventRegistration.objects.filter(
            event=event,
            member=request.user.member,
            status='registered'  # Только активные
        ).exists()
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'places_left': event.places_left(),
    }
    return render(request, 'main/event_detail.html', context)

def project_detail(request, project_id):
    """Детальная страница проекта"""
    project = get_object_or_404(Project, id=project_id)
    # Другие проекты для блока "Похожие проекты"
    other_projects = Project.objects.filter(is_active=True).exclude(id=project_id)[:3]
    return render(request, 'main/project_detail.html', {'project': project, 'other_projects': other_projects})

@login_required
def event_register(request, event_id):
    """Регистрация на мероприятие"""
    event = get_object_or_404(Event, id=event_id)
    
    # Проверяем, есть ли у пользователя профиль
    if not hasattr(request.user, 'member'):
        messages.error(request, 'Для регистрации на мероприятия необходимо заполнить профиль')
        return redirect('accounts:profile')
    
    # Проверяем, открыта ли регистрация
    if not event.is_registration_open():
        messages.error(request, 'Регистрация на это мероприятие закрыта')
        return redirect('event_detail', event_id=event.id)
    
    # Проверяем, не зарегистрирован ли уже (включая отмененные)
    existing_registration = EventRegistration.objects.filter(
        event=event,
        member=request.user.member
    ).first()
    
    if existing_registration:
        if existing_registration.status == 'registered':
            messages.warning(request, 'Вы уже зарегистрированы на это мероприятие')
        elif existing_registration.status == 'cancelled':
            # Если была отмена, можно зарегистрироваться снова
            existing_registration.status = 'registered'
            existing_registration.save()
            event.current_participants += 1
            event.save()
            messages.success(request, f'Вы успешно зарегистрированы на мероприятие "{event.title}"')
        return redirect('event_detail', event_id=event.id)
    
    # Новая регистрация
    EventRegistration.objects.create(
        event=event,
        member=request.user.member,
        status='registered'
    )
    
    # Обновляем счетчик участников
    event.current_participants += 1
    event.save()
    
    messages.success(request, f'Вы успешно зарегистрированы на мероприятие "{event.title}"')
    return redirect('event_detail', event_id=event.id)


@login_required
def event_cancel(request, event_id):
    """Отмена регистрации на мероприятие"""
    event = get_object_or_404(Event, id=event_id)
    
    # Проверка: мероприятие уже началось?
    if event.start_date < timezone.now():
        messages.error(request, 'Невозможно отменить регистрацию: мероприятие уже началось')
        return redirect('event_detail', event_id=event.id)
    
    # Проверка: можно отменить за 24 часа до начала?
    cancel_deadline = event.start_date - timedelta(hours=24)
    if cancel_deadline < timezone.now():
        hours_left = int((event.start_date - timezone.now()).total_seconds() / 3600)
        messages.error(request, f'Невозможно отменить регистрацию: до начала мероприятия осталось менее {hours_left} часов. Отмена возможна за 24 часа.')
        return redirect('event_detail', event_id=event.id)
    
    if not hasattr(request.user, 'member'):
        messages.error(request, 'Профиль не найден')
        return redirect('home')
    
    registration = EventRegistration.objects.filter(
        event=event,
        member=request.user.member,
        status='registered'
    ).first()
    
    if registration:
        registration.status = 'cancelled'
        registration.save()
        
        if event.current_participants > 0:
            event.current_participants -= 1
            event.save()
        
        messages.success(request, f'Регистрация на мероприятие "{event.title}" отменена')
    else:
        messages.error(request, 'Активная регистрация на это мероприятие не найдена')
    
    return redirect('event_detail', event_id=event.id)