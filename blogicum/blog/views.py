from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404
from django import forms

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

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'password1', 'password2')

# Форма для редактирования профиля
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        
    def clean_username(self):
        username = self.cleaned_data['username']
        # Проверяем, что новое имя не занято другим пользователем
        if User.objects.filter(username=username).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

# Регистрация
class UserRegistrationView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'auth/registration.html'
    success_url = reverse_lazy('blog:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # После создания, перенаправляем на главную
        return redirect(self.success_url)

# Профиль пользователя
class UserProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        # Получаем все публикации пользователя
        # (предполагается, что есть модель Post с foreign key на User)
        context['posts'] = profile_user.post_set.all()
        # Проверяем, является ли текущий пользователь хозяином аккаунта
        context['is_owner'] = self.request.user == profile_user
        return context

# Редактирование профиля
class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/profile_edit.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def test_func(self):
        # Только владелец может редактировать свой профиль
        user = self.get_object()
        return self.request.user == user
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', 
                           kwargs={'username': self.object.username})
    
    def handle_no_permission(self):
        raise Http404("Вы не имеете доступа к этой странице")