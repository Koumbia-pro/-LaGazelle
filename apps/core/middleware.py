from django.http import HttpResponse

from .audit import client_ip
from .rate_limits import increment_rate_limit


class AdminLoginRateLimitMiddleware:
    """Limit repeated POST attempts against the Django admin login form."""

    window_seconds = 15 * 60
    max_attempts = 10

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_admin_login = request.method == "POST" and request.path.rstrip("/") == "/admin/login"
        if not is_admin_login:
            return self.get_response(request)

        ip_address = client_ip(request) or "unknown"
        cache_key = f"admin-login-attempt:{ip_address}"
        attempts = increment_rate_limit(cache_key, self.window_seconds)
        if attempts > self.max_attempts:
            return HttpResponse(
                "Trop de tentatives de connexion. Réessayez dans quelques minutes.",
                status=429,
            )

        response = self.get_response(request)

        # A successful login clears the counter for this IP. The reverse proxy
        # must preserve the client address consistently for this to be useful.
        if request.session.get("_auth_user_id"):
            cache.delete(cache_key)
        return response
