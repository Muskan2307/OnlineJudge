from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func): 
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated: 
            return redirect( 'dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_staff(view_func): 
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff: 
            return view_func(request, *args, **kwargs)
        else:
            return redirect( 'dashboard')
    return wrapper_func