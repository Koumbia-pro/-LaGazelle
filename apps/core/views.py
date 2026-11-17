import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .audit import client_ip
from .models import AnalyticsEvent
from .rate_limits import increment_rate_limit


@require_POST
def record_conversion(request):
    if request.COOKIES.get("lg_analytics_consent") != "yes":
        return JsonResponse({"recorded": False}, status=200)
    if request.META.get("CONTENT_LENGTH", "0").isdigit() and int(request.META.get("CONTENT_LENGTH", "0")) > 2048:
        return JsonResponse({"error": "Payload too large"}, status=413)
    raw_body = request.body
    if len(raw_body) > 2048:
        return JsonResponse({"error": "Payload too large"}, status=413)
    ip = client_ip(request) or "unknown"
    rate_key = f"conversion-event:{ip}"
    attempts = increment_rate_limit(rate_key, 15 * 60)
    if attempts > 120:
        return JsonResponse({"error": "Rate limited"}, status=429)
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "Invalid event"}, status=400)
    event_type = payload.get("event")
    page_path = payload.get("path", "")
    allowed_events = {choice[0] for choice in AnalyticsEvent.EVENT_CHOICES}
    if event_type not in allowed_events:
        return JsonResponse({"error": "Invalid event"}, status=400)
    if not isinstance(page_path, str) or not page_path.startswith("/") or page_path.startswith("//"):
        return JsonResponse({"error": "Invalid path"}, status=400)
    # Query strings may contain contact details or other user-entered values.
    page_path = page_path.split("?", 1)[0].split("#", 1)[0][:255]
    AnalyticsEvent.objects.create(event_type=event_type, page_path=page_path)
    return JsonResponse({"recorded": True}, status=201)
