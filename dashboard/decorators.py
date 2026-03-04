from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_staff:
            return HttpResponseForbidden('You do not have permission to access this page.')
        return view_func(request, *args, **kwargs)
    return wrapper
