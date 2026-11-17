from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import validate_public_image


class TeamPole(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="team/poles/", blank=True, null=True, validators=[validate_public_image])
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "pôle"
        verbose_name_plural = "pôles"

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    pole = models.ForeignKey(TeamPole, related_name="members", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=180)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="team/", blank=True, null=True, validators=[validate_public_image])
    photo_alt = models.CharField(max_length=180, blank=True)
    is_verified = models.BooleanField(default=False, help_text="Autoriser l’affichage public après validation du nom, du rôle et des droits photo.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "membre de l’équipe"
        verbose_name_plural = "membres de l’équipe"

    def __str__(self):
        return f"{self.name} — {self.role}"

    def clean(self):
        super().clean()
        if self.is_verified and self.photo and not self.photo_alt.strip():
            raise ValidationError({"photo_alt": "Une photo publiée doit avoir un texte alternatif descriptif."})
