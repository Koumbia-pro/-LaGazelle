from django.db import models


class FAQCategory(models.Model):
    expertise = models.ForeignKey("services.Expertise", related_name="faq_categories", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "catégorie FAQ"
        verbose_name_plural = "catégories FAQ"

    def __str__(self):
        return self.name


class FAQItem(models.Model):
    category = models.ForeignKey(FAQCategory, related_name="items", on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "question"]
        verbose_name = "question FAQ"
        verbose_name_plural = "questions FAQ"

    def __str__(self):
        return self.question
