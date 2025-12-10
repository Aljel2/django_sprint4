from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path('auth/registration/', views.UserRegistrationView.as_view(), 
         name='registration'),
    
    # Профиль пользователя
    path('profile/<str:username>/', views.UserProfileView.as_view(), 
         name='profile'),
    
    # Редактирование профиля
    path('profile/<str:username>/edit/', views.UserEditView.as_view(), 
         name='profile_edit'),
]

