from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from main.models import News, Project, SupportMeasure

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
    paginator = Paginator(news_list, 10)  # 10 новостей на страницу
    
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)
    
    return render(request, 'main/news_list.html', {'news': news})

def news_detail(request, news_id):
    """Детальная страница новости"""
    news = get_object_or_404(News, id=news_id, is_published=True)
    # Другие новости для блока "Читайте также"
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
