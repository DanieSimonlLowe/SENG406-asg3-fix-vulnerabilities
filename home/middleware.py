from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # List of URLs or view names that don't require authentication
        exempt_urls = [reverse('register_user'), reverse('login_user')]

        if not request.user.is_authenticated and request.path not in exempt_urls:
            return redirect('%s?next=%s' % (reverse('login_user'), request.path))
