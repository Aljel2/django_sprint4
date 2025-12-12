from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView, UpdateView, ListView, DetailView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.utils import timezone
from .forms import PostForm, CommentForm
from .models import Post, Category, Comment


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


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    login_url = 'login'
    
    def form_valid(self, form):
        """Установка автора и сохранение публикации"""
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Перенаправление на отредактированный пост"""
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})

class PostEditView(LoginRequiredMixin, UpdateView):
    """Редактирование публикации"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    login_url = 'login'
    
    def dispatch(self, request, *args, **kwargs):
        """Проверка прав автора перед редактированием"""
        post = self.get_object()
        if post.author != request.user:
            # Перенаправить на страницу просмотра поста
            return redirect('post_detail', post_id=post.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """Перенаправление на отредактированный пост"""
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.id})


class PostListView(ListView):
    """Список всех опубликованных публикаций"""
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Показать только опубликованные посты в прошлом"""
        now = timezone.now()
        posts = Post.objects.filter(
            is_published=True,
            pub_date__lte=now
        ).order_by('-pub_date')
        return posts

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    login_url = 'login'
    
    def get_object(self, queryset=None):
        """Получить пост и проверить, что это автор"""
        post = super().get_object(queryset)
        
        # Проверяем, что это автор поста
        if post.author != self.request.user:
            raise Http404("Вы не можете удалить чужой пост")
        
        return post
    
    def get_success_url(self):
        """Перенаправление на профиль пользователя после удаления"""
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})
    
class PostDetailView(DetailView):
    """Просмотр конкретной публикации"""
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    
    def get_object(self, queryset=None):
        """Получить пост или вернуть 404"""
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        
        # Если пост не опубликован
        if not post.is_published:
            # Может просмотреть только автор
            if post.author != self.request.user:
                raise Http404("Публикация не найдена")
        
        # Если пост отложенный (дата в будущем)
        if post.pub_date > timezone.now():
            # Может просмотреть только автор
            if post.author != self.request.user:
                raise Http404("Публикация еще недоступна")
        
        return post


class UserProfileView(DetailView):
    """Профиль пользователя со всеми его публикациями"""
    template_name = 'blog/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        """Получить пользователя по username"""
        from django.contrib.auth.models import User
        return get_object_or_404(User, username=self.kwargs['username'])
    
    def get_context_data(self, **kwargs):
        """Получить все публикации пользователя"""
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Получить все посты пользователя
        posts = user.posts.all().order_by('-pub_date')
        
        # Если это не текущий пользователь, показать только опубликованные в прошлом
        if user != self.request.user:
            now = timezone.now()
            posts = posts.filter(is_published=True, pub_date__lte=now)
        
        context['posts'] = posts
        return context