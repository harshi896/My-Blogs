from multiprocessing import context
import random
import string
from unicodedata import name
from django.http import JsonResponse
from django.shortcuts import render , HttpResponse
from datetime import datetime, timezone
from home.models import Contact
from django.contrib import messages
from home.models import Blog, Story  # Import your Blog and Story models
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from home.forms import SignUpForm, LoginForm
from django.contrib import messages
from .forms import OTPForm, PostForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Comment  # Import the Comment model
from .forms import CommentForm  # Import the CommentForm
from django.contrib.contenttypes.models import ContentType


# Create your views here.
def index(request):
    recent_posts = Blog.objects.order_by('-published_date')[:5]  # Change the number as needed
    return render(request, 'index.html', {'recent_posts': recent_posts})

def home(request):
    return render (request, 'home.html')

def about(request):
    return render (request , 'about.html' )

def search(request):
    query = request.GET.get('q')
    if query:
        results = Blog.objects.filter(title__icontains=query)  # Adjust filter as needed
    else:
        results = Blog.objects.none()  # Return an empty QuerySet if no query
    return render(request, 'search_results.html', {'results': results, 'query': query})

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = Blog.objects.filter(title__icontains=query).values('id', 'title')[:5]
    return JsonResponse({'suggestions': list(suggestions)})
   

def blogs(request):
    blogs = Blog.objects.filter(category='Blogs')  # Fetch all blogs from the Blog model
    return render(request, 'blogs.html', {'blogs': blogs})

def stories(request):
    stories = Blog.objects.filter(category='Stories')  # Fetch all stories from the Story model
    return render(request, 'stories.html', {'stories': stories})

def technology(request):
    technology_posts = Blog.objects.filter(category='Technology')  # Fetch tech-related posts
    return render(request, 'technology.html', {'technology_posts': technology_posts})



def send_otp(email):
    otp = random.randint(100000, 999999)
    send_mail('Your OTP', f'Your OTP is {otp}', 'from@example.com', [email])

# def verify_otp(request):
#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid():
#             otp = request.session.get('otp')
#             if otp == form.cleaned_data['otp']:
#                 form_data = request.session.get('form_data')
#                 user = User.objects.create_user(
#                     username=form_data['username'],
#                     email=form_data['email'],
#                     password=form_data['password']
#                 )
#                 del request.session['otp']
#                 del request.session['form_data']
#                 return redirect('login')
#             else:
#                 form.add_error('otp', 'Invalid OTP')
#         else:
#             form = OTPForm()

#             return render(request, 'verify_otp.html', {'form': form})        

# def signup(request):
#     if request.method == 'POST':  # Initial signup form submission
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             # Check if the username or email already exists
#             if User.objects.filter(username=form.cleaned_data['username']).exists() or User.objects.filter(email=form.cleaned_data['email']).exists():
#                 messages.error(request, 'Username or email already exists. Please choose a different one.')
#                 return redirect('signup')  # Redirect to signup form

#             # Create the user
#             user = User.objects.create_user(
#                 username=form.cleaned_data['username'],
#                 email=form.cleaned_data['email'],
#                 password=form.cleaned_data['password']
#             )
#             user.save()

#             messages.success(request, "Signup successful! You can now log in.")
#             return redirect('home')  # Redirect to homepage
#         else:
#             messages.error(request, "Invalid form submission. Please correct the errors and try again.")
#     else:
#         form = SignUpForm()

#     return render(request, 'signup.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        if 'otp' in request.POST:  # Check if the OTP is being submitted
            form = OTPForm(request.POST)
            if form.is_valid():
                otp = request.session.get('otp')
                if otp == form.cleaned_data['otp']:
                    form_data = request.session.get('form_data')

                    if User.objects.filter(username=form_data['username'], email=form_data['email']).exists():
                        messages.error(request, 'Username or email already exists. Please choose a different one.')
                        return redirect('signup')  # Redirect to signup form

                    user = User.objects.create_user(
                        username=form_data['username'],
                        email=form_data['email'],
                        password=form_data['password']
                    )
                    user.save()

                    # Clear the session data after successful signup
                    del request.session['otp']
                    del request.session['form_data']

                    messages.success(request, "Signup successful! You can now log in.")
                    return redirect('login')
                else:
                    messages.error(request, "Invalid OTP.")
            else:
                messages.error(request, "Invalid OTP. Please try again.")

            return redirect('verify_otp')  # Redirect back to OTP verification page if there's an error

        else:  # Initial signup form submission
            form = SignUpForm(request.POST)
            if form.is_valid():
                otp = ''.join(random.choices(string.digits, k=6))
                request.session['otp'] = otp  # Save OTP in session
                request.session['form_data'] = form.cleaned_data  # Save form data in session
                
                # Send OTP to user's email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}. It will expire in 10 minutes.',
                    'from@example.com',
                    [form.cleaned_data['email']],
                    fail_silently=False,
                )
                
                messages.info(request, "An OTP has been sent to your email. Please enter it below.")
                return redirect('verify_otp')  # Redirect to OTP verification page
            else:
                messages.error(request, "Invalid form submission. Please correct the errors and try again.")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})



def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = request.session.get('otp')
            input_otp = form.cleaned_data['otp']
            
            # Debugging output
            print(f"Session OTP: {otp}")
            print(f"Input OTP: {input_otp}")
            
            if otp == input_otp:
                if request.session.get('reset_password'):
                    email = request.session.get('email')
                    user = User.objects.filter(email=email).first()
                    if user:
                        request.session['user_id'] = user.id
                        # Clear the OTP session data after successful verification
                        del request.session['otp']
                        del request.session['reset_password']
                        return redirect('reset_password')  # Redirect to reset password page
                    else:
                        messages.error(request, "No user found with this email.")
                        return redirect('forgot_password')
                else:
                    form_data = request.session.get('form_data')
                    if User.objects.filter(username=form_data['username'], email=form_data['email']).exists():
                        messages.error(request, 'Username or email already exists. Please choose a different one.')
                        return redirect('signup')

                    user = User.objects.create_user(
                        username=form_data['username'],
                        email=form_data['email'],
                        password=form_data['password']
                    )
                    user.save()

                    # Clear session data after successful signup
                    del request.session['otp']
                    del request.session['form_data']

                    messages.success(request, "Signup successful! You can now log in.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid OTP.")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPForm()

    return render(request, 'verify_otp.html', {'form': form})




    

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('home')  # Redirect to the home page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')  # Redirect to the home page

# def add_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')  # Redirect to home or any page after saving
#     else:
#         form = PostForm()
    
#     return render(request, 'add_post.html', {'form': form})

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post has been added successfully!')
            return redirect('home')  # Redirect to home or any page after saving
    else:
        form = PostForm()

    return render(request, 'add_post.html', {'form': form})

def view_posts(request):
    posts = Blog.objects.all().order_by('-published_date')  # Fetch all posts ordered by the published date
    return render(request, 'view_posts.html', {'posts': posts})

def post_detail(request, id):
    post = Blog.objects.get(id=id)
    comments = Comment.objects.filter(
        content_type=ContentType.objects.get_for_model(post),
        object_id=post.id
    ).order_by('-created_at')  # Get the comments for this post

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.content_type = ContentType.objects.get_for_model(post)
                comment.object_id = post.id
                comment.author = request.user
                comment.save()
                messages.success(request, 'Your comment has been posted.')
                return redirect('post_detail', id=post.id)  # Redirect to the same post after saving comment
        else:
            messages.error(request, 'You must be logged in to post a comment.')
            return redirect('login')
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email).first()
        
        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['reset_password'] = True  # Indicate that OTP is for password reset
            
            # Send OTP to the user's email
            send_mail(
                'Your Password Reset OTP',
                f'Your OTP code is {otp}. It will expire in 10 minutes.',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            
            messages.info(request, "An OTP has been sent to your email. Please check your inbox.")
            return redirect('verify_otp')  # Redirect to OTP verification page
        else:
            messages.error(request, "No account found with that email.")
    
    return render(request, 'forgot_password.html')


def reset_password(request):
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.session.get('user_id'):
            messages.error(request, "Session expired or invalid request.")
            return redirect('forgot_password')

        if new_password1 and new_password1 == new_password2:
            user_id = request.session.get('user_id')
            user = User.objects.filter(id=user_id).first()
            
            if user:
                user.set_password(new_password1)
                user.save()
                
                # Clear session data after successful password reset
                request.session.flush()  # Clears all session data
                
                messages.success(request, "Your password has been reset successfully. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid user.")
        else:
            messages.error(request, "Passwords do not match or are invalid.")
    
    return render(request, 'reset_password.html')


