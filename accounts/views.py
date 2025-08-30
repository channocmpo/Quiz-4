from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Profile, CustomUser
from jobs.models import Job, JobApplicant

# Create your views here.

def signup_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already signed in.')
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validate required fields
        if not all([email, username, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})

        # Username validation
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})
        
        if not username.isalnum():
            messages.error(request, 'Username can only contain letters and numbers.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})

        # Password validation
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})

        # Check existing users
        try:
            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'auth/signup.html', {'username': username})

            if CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, 'This username is already taken.')
                return render(request, 'auth/signup.html', {'email': email})

            # Create user
            user = CustomUser.objects.create_user(
                email=email.lower(),
                username=username,
                password=password
            )
            
            messages.success(request, 'Account created successfully! Please sign in.')
            return redirect('auth:signin')

        except IntegrityError:
            messages.error(request, 'An error occurred while creating your account. Please try again.')
            return render(request, 'auth/signup.html', {'email': email, 'username': username})
    return render(request, 'auth/signup.html')
def signin_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if not Profile.objects.filter(user=user).exists():
                print('User does not have a profile.')
            print('User has a profile.')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'auth/signin.html')

def profile_create_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You are not logged in.')
        return redirect('auth:signin')

    if not Profile.objects.filter(user=request.user).exists():
        if request.method == 'POST':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            bio = request.POST.get('bio', '').strip()
            profile_picture = request.FILES.get('profile_picture')

            if not all([first_name, last_name, profile_picture]):
                messages.error(request, 'All fields are required.')
                return render(request, 'auth/profile_create.html', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'profile_picture': profile_picture,
                })

            profile = Profile.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                bio=bio,
                profile_picture=profile_picture,
            )
            messages.success(request, 'Profile created successfully!')
            return redirect('auth:profile_view')

    return render(request, 'auth/profile_create.html')
def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please sign in first.')
        return redirect('auth:signin')

    profile = Profile.objects.filter(user=request.user).first()
    if profile:
        user = request.user
        if user.is_admin and user.is_staff:
            job_posted = Job.objects.filter(user=user)
            context = {
                'profile': profile,
                'job_posted': job_posted,
                'user': user,
            }
        else:
            applied_jobs = JobApplicant.objects.filter(user=user)
            context = {
                'profile': profile,
                'applied_jobs': applied_jobs,
                'user': user,
            }
        return render(request, 'auth/profile_view.html', context)
    else:
        messages.info(request, 'Profile does not exist.')
        return redirect('auth:profile_create')

def logout_view(request):
    logout(request)
    return redirect('auth:signin')