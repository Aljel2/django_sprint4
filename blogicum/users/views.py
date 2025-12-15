from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (
    CreateView, UpdateView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .forms import UserEditForm
from .models import User

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index') 
    template_name = 'registration/registration_form.html'

class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # все посты пользователя (для владельца) / только опубликованные для остальных
        posts = user.posts.select_related(
            'author', 'category', 'location'
        ).order_by('-pub_date')

        if self.request.user != user:
            now = timezone.now()
            posts = posts.filter(is_published=True, pub_date__lte=now)

        context['page_obj'] = posts
        # флаг: просматривает ли профиль его владелец
        context['is_owner'] = self.request.user.is_authenticated and self.request.user == user
        return context
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "registration/registration_form.html"
    model = User
    form_class = UserEditForm
    def get_object(self, queryset=None):
        return self.request.user
    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})