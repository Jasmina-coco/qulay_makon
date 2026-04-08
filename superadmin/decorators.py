from functools import wraps

from django.shortcuts import redirect


def superadmin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("superadmin_login")
        if not request.user.is_superuser:
            return redirect("superadmin_login")
        return view_func(request, *args, **kwargs)

    return _wrapped
