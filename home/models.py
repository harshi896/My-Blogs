from django.db import models
from ckeditor.fields import RichTextField  # type: ignore # Import RichTextField from CKEditor
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



# Contact model (already defined)
class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    phone = models.CharField(max_length=12)
    desc = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name


# Blog model with CKEditor for the content field
class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  # Use RichTextField for rich text editing
    category = models.CharField(max_length=100, choices=[('Blogs', 'Blogs'), ('Technology', 'Technology'), ('Stories', 'Stories')])
    published_date = models.DateField()
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title


# Story model with CKEditor for the content field
class Story(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  # Use RichTextField for rich text editing
    published_date = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True)  # Optional field for an image URL

    def __str__(self):
        return self.title


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')  # Refers to either Blog or Story

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username}'
