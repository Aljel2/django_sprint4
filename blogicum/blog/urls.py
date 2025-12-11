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
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:id>/edit/', views.PostEditView.as_view(), name='post_edit'),  

    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
]
