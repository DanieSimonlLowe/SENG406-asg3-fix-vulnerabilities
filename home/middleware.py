from django.core import cache
from django.http import HttpResponseForbidden

from djangoProject import settings


# from https://unfoldai.com/preventing-brute-force-with-django-middleware/
class BruteForceProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        print(response)  # For debugging, print the response object

        # Check if the request is for the login page and the method is POST
        if request.path == settings.LOGIN_URL and request.method == "POST":
            # Get the IP address of the client
            ip_address = request.META.get("REMOTE_ADDR")

            # Increment the failed login attempt count for this IP address
            cache_key = f"login_attempts:{ip_address}"
            login_attempts = cache.get(cache_key, 0)
            if response.status_code != 200:
                cache.set(cache_key, login_attempts + 1, timeout=settings.BRUTE_FORCE_TIMEOUT)

            # If the login attempts exceed the threshold, block further attempts
            if login_attempts >= settings.BRUTE_FORCE_THRESHOLD:
                return HttpResponseForbidden(
                    f"Too many login attempts. Please try again later after {settings.BRUTE_FORCE_TIMEOUT // 60} minutes."
                )

        return response