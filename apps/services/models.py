from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.core.models import validate_public_image


class Expertise(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    headline = models.CharField(max_length=255, blank=True)
    cta_label = models.CharField(max_length=180, blank=True)
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audience_need = models.TextField(blank=True, help_text="Situation ou besoin auquel cette expertise répond.")
    activities = models.TextField(blank=True, help_text="Une action réalisée par ligne.")
    deliverables = models.TextField(blank=True, help_text="Un livrable par ligne.")
    outcomes = models.TextField(blank=True, help_text="Un bénéfice concret par ligne.")
    scope_note = models.TextField(blank=True, help_text="Limites et précisions à afficher sur la fiche.")
    benefits = models.TextField(blank=True, help_text="Un bénéfice par ligne.")
    process = models.TextField(blank=True, help_text="Une étape par ligne.")
    related_expertises = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="related_from")
    icon = models.CharField(max_length=10, default="✦")
    image = models.ImageField(upload_to="expertises/", blank=True, null=True, validators=[validate_public_image])
    image_alt = models.CharField(max_length=180, blank=True)
    accent_color = models.CharField(max_length=20, default="#F26522")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "expertise"
        verbose_name_plural = "expertises"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("expertises:detail", kwargs={"slug": self.slug})

    def benefit_list(self):
        return [line.strip() for line in self.benefits.splitlines() if line.strip()]

    def process_list(self):
        return [line.strip() for line in self.process.splitlines() if line.strip()]

    def activity_list(self):
        return [line.strip() for line in self.activities.splitlines() if line.strip()]

    def deliverable_list(self):
        return [line.strip() for line in self.deliverables.splitlines() if line.strip()]

    def outcome_list(self):
        return [line.strip() for line in self.outcomes.splitlines() if line.strip()]

    def clean(self):
        super().clean()
        if self.is_active and self.image and not self.image_alt.strip():
            raise ValidationError({"image_alt": "Une image d’expertise publiée doit avoir un texte alternatif descriptif."})


class Prestation(models.Model):
    expertise = models.ForeignKey(Expertise, related_name="prestations", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        constraints = [models.UniqueConstraint(fields=["expertise", "slug"], name="unique_prestation_per_expertise")]
        verbose_name = "prestation"
        verbose_name_plural = "prestations"

    def __str__(self):
        return f"{self.expertise.name} — {self.name}"
