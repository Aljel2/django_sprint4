from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    
    # Просмотр поста по ID
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    
    # Категория по slug
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    
    # Создание нового поста
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    
    # Редактирование поста по ID
    path('posts/<int:post_id>/edit/', views.PostEditView.as_view(), name='edit_post'),
    
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),

    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),

    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    
    # Редактирование комментария
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.CommentEditView.as_view(), name='edit_comment'),
    
    # Удаление комментария
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
]
