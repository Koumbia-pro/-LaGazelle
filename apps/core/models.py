from pathlib import Path

from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models


MAX_MEDIA_IMAGE_SIZE = 7 * 1024 * 1024
MAX_MEDIA_IMAGE_PIXELS = 30_000_000
MEDIA_IMAGE_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
}


def validate_public_image(upload):
    """Accept only small, verified raster images uploaded through the CMS."""
    extension = Path(upload.name).suffix.lower().lstrip(".")
    expected_format = MEDIA_IMAGE_FORMATS.get(extension)
    if not expected_format:
        raise ValidationError("Seules les images JPG, PNG ou WebP sont acceptées.")
    if upload.size > MAX_MEDIA_IMAGE_SIZE:
        raise ValidationError("L’image ne peut pas dépasser 7 Mo.")

    file_obj = getattr(upload, "file", upload)
    try:
        original_position = file_obj.tell()
    except (AttributeError, OSError):
        original_position = None
    try:
        file_obj.seek(0)
        image = Image.open(file_obj)
        if image.format != expected_format:
            raise ValidationError("Le format réel de l’image ne correspond pas à son extension.")
        if image.width * image.height > MAX_MEDIA_IMAGE_PIXELS:
            raise ValidationError("L’image dépasse la résolution maximale autorisée.")
        image.verify()
    except ValidationError:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValidationError("Le fichier image est invalide ou endommagé.") from exc
    finally:
        if original_position is not None:
            try:
                file_obj.seek(original_position)
            except (AttributeError, OSError):
                pass


# Keep the historical migration import path valid.
validate_media_image = validate_public_image


class SiteSetting(models.Model):
    key = models.SlugField(max_length=100, unique=True)
    value = models.TextField(blank=True)
    label = models.CharField(max_length=180, blank=True)
    is_public = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "paramètre du site"
        verbose_name_plural = "paramètres du site"

    def __str__(self):
        return self.label or self.key


class SocialLink(models.Model):
    PLATFORM_CHOICES = [(name, name) for name in ("Facebook", "LinkedIn", "Instagram", "X", "TikTok", "WhatsApp")]
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=180, blank=True, default="")
    url = models.URLField(validators=[URLValidator()], blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "platform"]
        unique_together = ["platform", "url"]

    def __str__(self):
        return f"{self.platform} — {self.account_name}" if self.account_name else self.platform


class Media(models.Model):
    file = models.ImageField(upload_to="media/%Y/%m/", validators=[validate_media_image])
    alt_text = models.CharField(max_length=180, blank=True)
    description = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "médias"

    def __str__(self):
        return self.description or self.file.name


class AuditLog(models.Model):
    user = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    object_repr = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "journal d’audit"
        verbose_name_plural = "journaux d’audit"


class AnalyticsEvent(models.Model):
    EVENT_CHOICES = [
        ("primary_cta", "Clic sur un appel à l’action"),
        ("phone_click", "Clic téléphone"),
        ("whatsapp_click", "Clic WhatsApp"),
        ("form_success", "Demande envoyée"),
        ("expertise_view", "Consultation d’une expertise"),
    ]
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    page_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["event_type", "created_at"])]
        verbose_name = "mesure de conversion"
        verbose_name_plural = "mesures de conversion"

    def __str__(self):
        return f"{self.get_event_type_display()} — {self.page_path}"


class SiteMetric(models.Model):
    value = models.CharField(max_length=40)
    label = models.CharField(max_length=120)
    description = models.CharField(max_length=180, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "chiffre clé"
        verbose_name_plural = "chiffres clés"

    def __str__(self):
        return f"{self.value} — {self.label}"


class Value(models.Model):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=10, default="✦")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "valeur"
        verbose_name_plural = "valeurs"

    def __str__(self):
        return self.name


class QualityPoint(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "point qualité"
        verbose_name_plural = "points qualité"

    def __str__(self):
        return self.name


class AboutMilestone(models.Model):
    year = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "jalon historique"
        verbose_name_plural = "jalons historiques"

    def __str__(self):
        return f"{self.year} — {self.title}"
