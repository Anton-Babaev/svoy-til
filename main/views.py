from django.shortcuts import render


def home(request):
    """Главная страница с блоками-заглушками"""
    context = {
        'title': 'Главная страница',
    }
    return render(request, 'main/home.html', context)


def about(request):
    """Временная страница 'О нас'"""
    return render(request, 'main/about.html', {'title': 'О нас'})
