from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Blog
from .models import Comment


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PostForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'category', 'published_date']

        
class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Only include the content field in the form
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }