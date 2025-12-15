from django.contrib.auth import get_user_model
from django import forms
from .models import Post, Comment

User = get_user_model()

class PostForm(forms.ModelForm):    
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок публикации'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Содержание публикации',
                'rows': 10
            }),
            'pub_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        return pub_date

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Содержание комментария',
                'rows': 10
            }),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")