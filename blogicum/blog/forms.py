from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикации"""
    
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location')
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
        """Валидация даты публикации"""
        pub_date = self.cleaned_data.get('pub_date')
        # Дата может быть в прошлом или будущем
        return pub_date
