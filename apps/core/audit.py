import ipaddress

from django.conf import settings

from .models import AuditLog


def client_ip(request):
    """Return the peer address, trusting X-Real-IP only behind configured Nginx."""
    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.META.get("HTTP_X_REAL_IP", "").strip()
        try:
            return str(ipaddress.ip_address(forwarded))
        except ValueError:
            pass
    return request.META.get("REMOTE_ADDR") or None


def record_audit(*, action, obj, request=None, user=None):
    actor = user or getattr(request, "user", None)
    if not actor or not actor.is_authenticated:
        actor = None
    AuditLog.objects.create(
        user=actor,
        action=action,
        object_repr=str(obj)[:255],
        ip_address=client_ip(request) if request else None,
    )
