from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.core.models import validate_public_image


class PublishableContent(models.Model):
    STATUS_CHOICES = [("draft", "Brouillon"), ("published", "Publié")]
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Article(PublishableContent):
    CATEGORY_CHOICES = [
        ("strategie", "Stratégie marketing"),
        ("social", "Réseaux sociaux et contenus"),
        ("digitalisation", "Digitalisation et IA"),
        ("image-securite", "Image et sécurité numérique"),
    ]
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="strategie")
    excerpt = models.TextField()
    content = models.TextField()
    author = models.CharField(max_length=150, blank=True)
    published_at = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="articles/", blank=True, null=True, validators=[validate_public_image])
    image_alt = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ["-published_at", "title"]
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("stories:article", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        if self.status == "published" and (not self.author.strip() or not self.published_at):
            raise ValidationError("Un article publié doit avoir un auteur réel et une date de publication.")
        if self.status == "published" and self.image and not self.image_alt.strip():
            raise ValidationError({"image_alt": "Une image d’article publiée doit avoir un texte alternatif descriptif."})


class ArticleSection(models.Model):
    article = models.ForeignKey(Article, related_name="sections", on_delete=models.CASCADE)
    heading = models.CharField(max_length=180)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "section d’article"
        verbose_name_plural = "sections d’article"

    def __str__(self):
        return self.heading


class CaseStudy(PublishableContent):
    client_name = models.CharField(max_length=180, blank=True)
    client_authorized = models.BooleanField(default=False, help_text="Accord du client pour publier le cas lui-même.")
    client_name_authorized = models.BooleanField(default=False, help_text="Accord distinct pour publier le nom du client.")
    client_logo = models.ImageField(upload_to="case-logos/", blank=True, null=True, validators=[validate_public_image])
    client_logo_alt = models.CharField(max_length=180, blank=True)
    client_logo_authorized = models.BooleanField(default=False, help_text="Accord distinct pour publier le logo du client.")
    quote = models.TextField(blank=True)
    quote_authorized = models.BooleanField(default=False, help_text="Accord distinct pour publier cette citation.")
    context = models.TextField()
    objective = models.TextField()
    intervention = models.TextField()
    period = models.CharField(max_length=120, blank=True)
    deliverables = models.TextField()
    results = models.TextField(blank=True)
    result_method = models.TextField(blank=True, help_text="Méthode et période utilisées pour mesurer les résultats.")
    lesson = models.TextField()
    image = models.ImageField(upload_to="cases/", blank=True, null=True, validators=[validate_public_image])
    image_alt = models.CharField(max_length=180, blank=True)
    image_authorized = models.BooleanField(default=False, help_text="Accord pour publier cette image dans la réalisation.")

    class Meta:
        ordering = ["-updated_at", "title"]
        verbose_name = "réalisation documentée"
        verbose_name_plural = "réalisations documentées"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("stories:case", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        if self.status != "published":
            return
        if not self.client_authorized:
            raise ValidationError("L’accord du client pour publier cette réalisation est obligatoire.")
        if self.client_name.strip() and not self.client_name_authorized:
            raise ValidationError("L’accord pour publier le nom du client est obligatoire.")
        if self.client_logo and not self.client_logo_authorized:
            raise ValidationError("L’accord pour publier le logo du client est obligatoire.")
        if self.client_logo and not self.client_logo_alt.strip():
            raise ValidationError({"client_logo_alt": "Le logo publié doit avoir un texte alternatif descriptif."})
        if self.quote.strip() and not self.quote_authorized:
            raise ValidationError("L’accord pour publier cette citation est obligatoire.")
        if self.image and not self.image_authorized:
            raise ValidationError("L’accord pour publier cette image est obligatoire.")
        if self.image and not self.image_alt.strip():
            raise ValidationError({"image_alt": "Une image de réalisation publiée doit avoir un texte alternatif descriptif."})
        required = ("context", "objective", "intervention", "period", "deliverables", "lesson")
        if any(not getattr(self, field).strip() for field in required):
            raise ValidationError("Une réalisation publiée doit documenter le contexte, l’objectif, la période, les actions, les livrables et l’enseignement.")
        if self.results.strip() and not self.result_method.strip():
            raise ValidationError("Tout résultat publié doit préciser sa méthode et sa période de mesure.")
