from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class AdminAccessMiddleware:
    """
    Restricts Django admin access to staff/superuser only.
    Regular users are redirected to home page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is trying to access admin
        if request.path.startswith('/admin/'):
            # Allow anonymous users to reach admin login (handled by Django admin itself),
            # but redirect logged-in users who are not staff/superuser.
            if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
                messages.warning(request, 'You do not have permission to access the admin panel.')
                return redirect('home')
        
        response = self.get_response(request)
        return response
