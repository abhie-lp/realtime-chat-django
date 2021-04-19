"""Custom decorators to use in application"""

from functools import wraps
from django.http.response import HttpResponseBadRequest


def require_ajax(view):
    """Decorator to check if requests are ajax"""

    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax():
            return view(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("Only AJAX requests are allowed.")
    return _wrapped_view

