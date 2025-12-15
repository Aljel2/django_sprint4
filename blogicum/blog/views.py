from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView, UpdateView, ListView, DetailView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import PostForm, CommentForm
from .models import Post, Category, Comment, User


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

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

class PostEditView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'include/post_card.html'
    success_url = reverse_lazy('blog:posts')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['user'] = User
        # Возвращаем словарь контекста.
        return context 

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        context = {"pk": self.kwargs["pk"]}
        return reverse_lazy(
            "blog:post_detail",
            kwargs=context
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.object
        return context

    def get_success_url(self):
        context = {"pk": self.object.post.pk}
        return reverse_lazy(
            "blog:post_detail",
            kwargs=context,
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment.html"

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.object
        context.pop("form", None)
        return context

    def get_success_url(self):
        context = {"pk": self.object.post.pk}
        return reverse_lazy(
            "blog:post_detail",
            kwargs=context,
        )