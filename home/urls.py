from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from Hello import settings
from home import views
from .views import search, search_suggestions

urlpatterns = [
    path("", views.index, name='home'),
    path("home", views.index, name= 'home'),
    path("about", views.about, name='about'),
    path("login", views.login, name='login'),
    path('search/', search, name='search'),
    path('search_suggestions/', search_suggestions, name='search_suggestions'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path("signup", views.signup, name='signup'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path("logout", views.logout, name='logout'),
    path("blogs" , views.blogs , name="blogs"),
    path("stories" , views.stories , name="stories"),
    path("technology" , views.technology , name="technology"),
    path('add_post', views.add_post, name='add_post'),
    path('posts/', views.view_posts, name='view_posts'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),  # Detail view for individual posts















 ] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
