from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.core.models import validate_public_image


class Page(models.Model):
    STATUS_CHOICES = [("draft", "Brouillon"), ("published", "Publiée")]
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    intro = models.TextField(blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="pages/", blank=True, null=True, validators=[validate_public_image])
    image_alt = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        special_urls = {
            "le-cabinet": "pages:about",
            "a-propos": "pages:about",
            "mentions-legales": "pages:legal-notice",
            "politique-de-confidentialite": "pages:privacy",
        }
        if self.slug in special_urls:
            return reverse(special_urls[self.slug])
        return reverse("pages:page", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        if self.status == "published" and self.image and not self.image_alt.strip():
            raise ValidationError({"image_alt": "Une image publiée doit avoir un texte alternatif descriptif."})
