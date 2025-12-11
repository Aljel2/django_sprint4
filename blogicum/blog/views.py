from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category


def index(request):
    # Получаем все посты, отфильтрованные по критериям публикации
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,).order_by('-pub_date')[:5]

    # Подготавливаем контекст для шаблона
    context = {
        'post_list': posts,
    }

    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    # Получаем пост по ID
    post = get_object_or_404(Post, pk=id)

    # Проверяем условие 1: дата публикации не позже текущего времени
    if post.pub_date > timezone.now():
        raise get_object_or_404(Post, pk=None)

    # Проверяем условие 2: пост опубликован
    if not post.is_published:
        raise get_object_or_404(Post, pk=None)

    # Проверяем условие 3: категория опубликована
    if post.category and not post.category.is_published:
        raise get_object_or_404(Post, pk=None)

    # Подготавливаем контекст для шаблона
    context = {
        'post': post,
    }

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    # Получаем категорию по slug
    category = get_object_or_404(Category, slug=category_slug)

    # Проверяем, что категория опубликована
    if not category.is_published:
        raise get_object_or_404(Category, slug=None)

    # Получаем все опубликованные посты из этой категории
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now(),).order_by('-pub_date')

    # Подготавливаем контекст для шаблона
    context = {
        'category': category,
        'post_list': posts,
    }

    return render(request, 'blog/category.html', context)

def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # мы ее не используем в шаблоне, но она обязательна для обработчика 404
    return render(request, 'pages/404.html', status=404)

def csrf_failure(request, reason=''):
    # Обработчик ошибки 403 CSRF
    return render(request, 'pages/403csrf.html', status=403)

def server_error(request):
    # Обработчик ошибки 500
    return render(request, 'pages/500.html', status=500)