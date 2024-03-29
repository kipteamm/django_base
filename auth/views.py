from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, logout, login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib import messages

from django_project import config

from .tokens import *


# Signup
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password_0 = request.POST.get('password_0')
        password_1 = request.POST.get('password_1')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "This username is already in use.")
            return redirect('signup')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "This email-address is already in use.")
            return redirect('signup')

        if not config.allowed_characters_regex.match(username):
            messages.error(request, "Your username contains invalid characters. You can only use a-z, A-Z, 0-9, -, _")
            return redirect('signup')

        if len(username) > 25:
            messages.error(request, "Your username can only be 25 characters long.")
            return redirect('signup')

        if not "@" in email or " " in email:
            messages.error(request, "Invalid email-address provided.")
            return redirect('signup')

        if len(password_0) < 8:
            messages.error(request, "Your password needs to be at least 8 characters long.")
            return redirect('signup')

        if password_0 != password_1:
            messages.error(request, "Your passwords need to match!")

        try:
            user = User.objects.create_user(username, email, password_0)
            user.is_active = False
            user.save()

            mail_subject = 'Activate your INSERT_NAME account.'
            message = render_to_string(
                'auth/activation_email.html', {
                    'user': user,
                    'domain': get_current_site(request),
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
            email = EmailMessage(mail_subject, message, to=[email])
            email.send()

            return render(request, 'auth/awaiting_verification.html')
        except Exception as e:
            messages.error(request, 'Unexpected error occured, let the developers know. ERROR: ' + str(e))
            return render(request, 'auth/signup.html')

    return render(request, 'auth/signup.html')


# The activation link
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Successfully activated your account!")
        return redirect('login_user')
    else:
        return HttpResponse('Invalid activation link.')


# Logging in
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password_0 = request.POST.get('password_0')

        if not User.objects.filter(username__iexact=username).exists():
            messages.error(request, "This username is not in use.")
            return redirect('login_user')

        if len(password_0) < 8:
            messages.error(request, "Your password needs to be at least 8 characters long.")
            return redirect('login_user')

        user = authenticate(request, username=username, password=password_0)

        if user is not None and user.is_active:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid password.")
        return redirect('login_user')

    return render(request, 'auth/login.html')


# Logging out
@login_required
def logout_user(request):
    logout(request)

    return redirect('login')


# Reset password form
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        associated_users = User.objects.filter(email=email)

        if not associated_users.exists():
            messages.error(request, "Invalid email-address.")
            return redirect('reset_password')

        for user in associated_users:
            mail_subject = 'Password reset request.'
            message = render_to_string(
                    'auth/reset_password_email.html', {
                    'user': user,
                    'domain': get_current_site(request),
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            return render(request, 'auth/awaiting_password_rest.html')

    return render(request, 'auth/reset_password.html')


# Password reset confirmation
def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check(user, token):
        return HttpResponse('Invalid activation link.')

    if request.method == "POST":
        password_0 = request.POST.get('password_0')
        password_1 = request.POST.get('password_1')

        if len(password_0) < 8:
            messages.error(request, "Your password needs to be at least 8 characters long.")
            return render(request, 'auth/reset_password_confirm.html')

        if password_0 != password_1:
            messages.error(request, "Your passwords need to match!")
            return render(request, 'auth/reset_password_confirm.html')

        user.set_password(password_0)
        user.save()

        messages.success(request, "Your password has been changed.")
        return redirect('login_user')
    
    return render(request, 'auth/reset_password_confirm.html')
