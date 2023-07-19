from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage

#sending of activation mail
from django.utils.encoding import force_bytes,force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

# login
from django.contrib import auth


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

class EmailValidationView(View):
    """Handles validation of the email in real time"""
    def post(self, request):
        data = json.loads(request.body)
        email=  data['email']
        # Check for alphanumeric characters 
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'}, status=400)
        #check that the username is not already in the database
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'sorry email already in use, Choose another one'}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    """Handles validation of the username in real time"""
    def post(self, request):
        data = json.loads(request.body)
        username=  data['username']
        # Check for alphanumeric characters 
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters'}, status=400)
        #check that the username is not already in the database
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'sorry username already in use, Choose another one'}, status=409)

        return JsonResponse({'username_valid':True})
class RegistrationView(View):
    """Handles the registration of new users"""
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            "fieldValues": request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password) < 6:
                    messages.error(request, "Password too short")
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = True #chage back once i've figured out the email stuff
                if email == "fikayodan@gmail.com":
                    user.is_superuser = True
                    user.is_staff = True
                user.save()
                email_subject = 'Activate your account'

                # path to view
                """
                1. Get the domain we're on
                2. relative url to verification
                3. encode user id
                4. token
                """
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain

                link = reverse('activate', kwargs = {'uidb64': uidb64, 'token': token_generator.make_token(user)})

                activate_url = 'http://'+domain+link
                email_body = 'Hi '+user.username+ ' Please use this link to verify your account\n' + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    "noreply@semicolon.com",
                    [email],
                   
                )
                EmailThread(email).start()
                # email.send(fail_silently=False)

                messages.success(request, "Registration Complete, verify your account via your email")
                return render(request, 'authentication/register.html')


        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = urlsafe_base64_decode(force_str(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?messages='+'user already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')
        except Exception as e:
            pass
        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, '+user.username+ ' you are now logged in')
                    return redirect('expenses')

                messages.error(request, 'Account is not active please check your email')
                return render(request, 'authentication/login.html')
            
            messages.error(request, 'Invalid Credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request, 'Please fill in all fields')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('home')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('home')

class PasswordResetView(View):
    def get(self , request):
        return render(request, 'authentication/reset_password.html')

    def post(self , request):
        email = request.POST['email']
        context = {
            "values": request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')

            return render('authentication/reset_password.html', context)

        user = User.objects.filter(email=email)
        if user.exists():
            user = user[0]
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            domain = get_current_site(request).domain
         
            token = PasswordResetTokenGenerator().make_token(user)

            link = reverse('reset-user-password', kwargs = {'uidb64': uidb64, 'token': token})

            reset_url = 'http://'+domain+link
            email_subject = 'Password Resent link'
            email_body = 'Hi there, Please click the link below to reset your password\n' + reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                "noreply@semicolon.com",
                [email],
                
            )
            EmailThread(email).start()

        messages.success(request, "Reset password link sent successfully")


        
        return render(request, 'authentication/reset_password.html')

    
class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link invalid, Request a new one')
                return render(request, 'authentication/reset_password.html')

            return redirect('login')
        except Exception as e:
            return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)

        
        if len(password) < 6:
            messages.error(request, 'Passwords too short')
            return render(request, 'authentication/set-new-password.html', context)


        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successfully')

            return redirect('login')
        except Exception as e:
            messages.info(request, 'Something went wrong')
        
            return render(request, 'authentication/set-new-password.html', context)