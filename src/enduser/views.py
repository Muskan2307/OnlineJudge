from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_protect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from .tokens import account_activation_token
from enduser.models import User, Submission
from .forms import CreateUserForm,ProfileUpdateForm
from django.urls import reverse_lazy
from django.http import HttpResponse
import re
from django.urls import reverse
# Create your views here.
from .decorators import unauthenticated_user

email_regex_setter = re.compile(r'^\S+@oj\.com$')

class PasswordsChangeView(PasswordChangeView):
    from_class = PasswordChangeForm
    success_url = reverse_lazy( 'dashboard')

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            userEmail = form.cleaned_data.get('email')
            if User.objects.filter(emailid=userEmail).exists():
                messages.error(request, 'This Email is already registered')
                context = {'form' : form}
                return render(request,'enduser/register.html', context)
            
            user = form.save(commit=False)
            user.is_active = False
            user.emailid = userEmail
            if email_regex_setter.match(userEmail):
                user.role='setter'
            else:
                user.role='participant'
            user.save()
            messages.success(request,'Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.')
            username = form.cleaned_data.get('username')
            current_site = get_current_site(request)
            email_sub = 'Welcome to OJ- Django Login!!'
            email_msg = render_to_string('enduser/emailConfirmation.html',
            {
                'name':username,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                email_sub,
                email_msg,
                settings.EMAIL_HOST_USER,
                to=[to_email],
            )
            email.fail_silently = True
            email.send()

            return redirect('login')
        
        else:
            form = CreateUserForm()
    context = {'form' : form}
    return render(request, 'enduser/register.html',context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role=='setter':
                return redirect('dashboardPage')
            elif user.role=='participant':
                return redirect('dashboard')
            else:
                return redirect(reverse('admin:index'))
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'enduser/login.html', context)

@login_required(login_url='login')
def updateProfile(request):
    form = ProfileUpdateForm(instance=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'enduser/updateProfile.html', context)

def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None
  
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active=True
        user.save()
        login(request,user)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        messages.error(request,'Activation failed, Please try again!')
        # print("activation failed")
        return render(request,'enduser/register.html')

@login_required(login_url='login')
def allSubmissionPage(request):
    submissions = Submission.objects.filter(user=request.user.id)
    return render(request, 'enduser/submission.html', {'submissions': submissions})

def logoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.user == request.user:
        context={'submission':submission}
        return render(request,'enduser/submissionspecial.html',context)
    else:
        return HttpResponse("No your solution, so not allowed to see")
    