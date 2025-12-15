from django.contrib import admin
from .models import Category
from .models import Post
from .models import Location
from .models import Comment

admin.site.register(Post)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Comment)
# Register your models here.
