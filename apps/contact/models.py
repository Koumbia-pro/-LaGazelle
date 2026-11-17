import zipfile
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import validate_public_image


ALLOWED_ATTACHMENT_EXTENSIONS = {"pdf", "doc", "docx", "jpg", "jpeg", "png"}
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024


def validate_project_attachment(upload):
    extension = upload.name.rsplit(".", 1)[-1].lower() if "." in upload.name else ""
    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError("Ce type de fichier n’est pas accepté.")
    if upload.size > MAX_ATTACHMENT_SIZE:
        raise ValidationError("La pièce jointe ne doit pas dépasser 5 Mo.")

    file_obj = upload.file
    original_position = file_obj.tell()
    try:
        file_obj.seek(0)
        signature = file_obj.read(16)
        file_obj.seek(0)
        if extension == "pdf" and not signature.startswith(b"%PDF-"):
            raise ValidationError("Le fichier PDF est invalide.")
        if extension == "doc" and not signature.startswith(b"\xd0\xcf\x11\xe0"):
            raise ValidationError("Le document Word est invalide.")
        if extension == "docx":
            if not zipfile.is_zipfile(file_obj):
                raise ValidationError("Le document Word est invalide.")
            file_obj.seek(0)
            with zipfile.ZipFile(file_obj) as archive:
                try:
                    archive.getinfo("word/document.xml")
                except KeyError:
                    raise ValidationError("Le document Word est invalide.")
        if extension in {"jpg", "jpeg", "png"}:
            validate_public_image(upload)
    finally:
        file_obj.seek(original_position)


class ProjectRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "Nouvelle"),
        ("in_progress", "En cours"),
        ("treated", "Traitée"),
    ]
    CLIENT_TYPES = [("company", "Entreprise"), ("organization", "Organisation"), ("individual", "Particulier"), ("other", "Autre")]
    reference = models.CharField(max_length=14, unique=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="nom")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="complément du nom")
    company = models.CharField(max_length=180, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    whatsapp = models.CharField(max_length=40, blank=True)
    client_type = models.CharField(max_length=30, choices=CLIENT_TYPES, blank=True)
    service = models.CharField(max_length=180)
    description = models.TextField()
    budget = models.CharField(max_length=120, blank=True)
    deadline = models.CharField(max_length=120, blank=True)
    attachment = models.FileField(
        upload_to="project-requests/%Y/%m/",
        blank=True,
        null=True,
        validators=[validate_project_attachment],
    )
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    team_notification_status = models.CharField(
        max_length=20,
        choices=[("pending", "En attente"), ("sent", "Envoyée"), ("failed", "Échec"), ("unknown", "Historique non renseigné")],
        default="pending",
    )
    visitor_notification_status = models.CharField(
        max_length=20,
        choices=[("pending", "En attente"), ("sent", "Envoyée"), ("failed", "Échec"), ("skipped", "Non applicable"), ("unknown", "Historique non renseigné")],
        default="pending",
    )
    notification_error = models.TextField(blank=True)
    last_notification_attempt = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "created_at"]), models.Index(fields=["email"])]
        permissions = [("export_projectrequest", "Peut exporter les demandes de projet")]
        verbose_name = "demande de projet"
        verbose_name_plural = "demandes de projet"

    def __str__(self):
        return f"{self.reference or 'Nouvelle demande'} — {self.full_name} — {self.service}"

    @property
    def full_name(self):
        return " ".join(part for part in (self.first_name, self.last_name) if part).strip()

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"LG-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if not any((self.email, self.phone, self.whatsapp)):
            raise ValidationError("Une adresse e-mail ou un numéro de téléphone/WhatsApp est obligatoire.")


class ProjectRequestStatusHistory(models.Model):
    request = models.ForeignKey(ProjectRequest, related_name="status_history", on_delete=models.CASCADE)
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
