import json
import logging
import mimetypes
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from apps.core.audit import client_ip, record_audit
from apps.core.rate_limits import increment_rate_limit
from apps.services.models import Expertise

from .forms import ProjectRequestForm
from .models import ProjectRequest, ProjectRequestStatusHistory
from .notifications import send_project_notifications
from .privacy import contact_collection_is_ready

logger = logging.getLogger(__name__)


@never_cache
def project_request(request):
    if not contact_collection_is_ready():
        return render(request, "contact/project.html", {
            "form_available": False,
            "submitted": False,
        }, status=503)

    submitted = (
        request.GET.get("sent") == "1"
        and bool(request.session.get("project_confirmation_reference"))
    )
    if request.method == "POST":
        request.session.pop("project_confirmation_reference", None)
        ip = client_ip(request) or "unknown"
        rate_key = f"project-request-attempt:{ip}"
        attempts = increment_rate_limit(rate_key, 15 * 60)
        if attempts > 5:
            form = ProjectRequestForm(request.POST)
            form.is_valid()
            form.add_error(None, "Trop de tentatives rapprochées. Merci de réessayer dans quelques minutes.")
            return render(request, "contact/project.html", {
                "form": form,
                "form_available": True,
                "submitted": False,
                "rate_limited": True,
            })

        form = ProjectRequestForm(request.POST)
        if form.is_valid():
            if settings.HCAPTCHA_SECRET_KEY and not _verify_hcaptcha(request):
                form.add_error(None, "La vérification anti-robot a échoué. Merci de réessayer.")
            else:
                with transaction.atomic():
                    project = form.save()
                    ProjectRequestStatusHistory.objects.create(request=project, to_status=project.status)
                    record_audit(action="création", obj=f"Demande {project.reference}", request=request)
                send_project_notifications(project)
                request.session["project_confirmation_reference"] = project.reference
                confirmation_url = f"{reverse('contact:project')}?sent=1"
                return redirect(confirmation_url)
    else:
        initial = {}
        expertise_slug = request.GET.get("expertise", "")
        expertise = Expertise.objects.filter(slug=expertise_slug, is_active=True).first() if expertise_slug else None
        if expertise:
            initial["service"] = expertise.name
        elif request.GET.get("service") == "advice":
            initial["service"] = "Je souhaite être conseillé"
        form = ProjectRequestForm(initial=initial)
    return render(request, "contact/project.html", {
        "form": form,
        "form_available": True,
        "submitted": submitted,
        "confirmation_reference": request.session.get("project_confirmation_reference", "") if submitted else "",
        "rate_limited": False,
    })


@permission_required("contact.view_projectrequest", raise_exception=True)
@never_cache
def project_attachment(request, pk):
    """Serve a historical project attachment only to staff users with lead access."""
    if not request.user.is_staff:
        raise PermissionDenied
    project = get_object_or_404(ProjectRequest, pk=pk)
    if not project.attachment:
        raise Http404("Cette demande ne contient pas de pièce jointe.")
    file_path = Path(project.attachment.path)
    if not file_path.is_file():
        raise Http404("La pièce jointe est introuvable.")
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    return FileResponse(
        project.attachment.open("rb"),
        as_attachment=True,
        filename=file_path.name,
        content_type=content_type,
    )


def _verify_hcaptcha(request):
    token = request.POST.get("h-captcha-response", "")
    if not token:
        return False
    payload = urlencode({
        "secret": settings.HCAPTCHA_SECRET_KEY,
        "sitekey": settings.HCAPTCHA_SITE_KEY,
        "response": token,
        "remoteip": client_ip(request) or "",
    }).encode()
    try:
        with urlopen(Request("https://api.hcaptcha.com/siteverify", data=payload), timeout=5) as response:
            return json.loads(response.read().decode()).get("success", False)
    except Exception:
        logger.exception("hCaptcha verification failed")
        return False
