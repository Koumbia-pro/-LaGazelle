import csv
from io import BytesIO, StringIO
from types import SimpleNamespace

from PIL import Image
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.contact.models import ProjectRequest
from apps.core.models import Media
from apps.core.views import record_conversion
from apps.faq.models import FAQCategory
from apps.pages.models import Page
from apps.services.models import Expertise
from apps.stories.models import Article, CaseStudy


class UploadSecurityTests(TestCase):
    def test_public_media_accepts_verified_raster_and_rejects_svg(self):
        image_bytes = BytesIO()
        Image.new("RGB", (2, 2), "white").save(image_bytes, format="PNG")
        valid_image = SimpleUploadedFile("logo.png", image_bytes.getvalue(), content_type="image/png")
        Media(file=valid_image).full_clean()

        active_content = SimpleUploadedFile(
            "logo.svg",
            b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>",
            content_type="image/svg+xml",
        )
        with self.assertRaises(ValidationError):
            Media(file=active_content).full_clean()

        mislabeled_content = SimpleUploadedFile(
            "logo.png",
            b"<html><script>alert(1)</script></html>",
            content_type="image/png",
        )
        with self.assertRaises(ValidationError):
            Media(file=mislabeled_content).full_clean()


class PrivatePreviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="content-editor",
            password="Strong-password-123!",
            is_staff=True,
        )
        self.client.force_login(self.user)

        self.page = Page.objects.create(title="Page test", slug="page-test")
        self.expertise = Expertise.objects.create(name="Conseil", slug="conseil", summary="Résumé")
        self.article = Article.objects.create(title="Article test", slug="article-test", excerpt="Résumé", content="Texte")
        self.case = CaseStudy.objects.create(
            title="Cas test", slug="cas-test", context="Contexte", objective="Objectif",
            intervention="Intervention", deliverables="Livrables", lesson="Enseignement",
        )
        self.faq = FAQCategory.objects.create(name="FAQ test", slug="faq-test")

    def test_previews_require_model_permissions_and_are_never_cached(self):
        previews = (
            ("pages:page-preview", self.page, "pages", "page"),
            ("expertises:preview", self.expertise, "services", "expertise"),
            ("stories:article-preview", self.article, "stories", "article"),
            ("stories:case-preview", self.case, "stories", "casestudy"),
            ("faq:preview", self.faq, "faq", "faqcategory"),
        )
        for route, obj, app_label, model_name in previews:
            with self.subTest(route=route):
                url = reverse(route, args=[obj.pk])
                self.assertEqual(self.client.get(url).status_code, 403)
                permission = self.user.user_permissions.model.objects.get(
                    codename=f"view_{model_name}",
                    content_type__app_label=app_label,
                )
                self.user.user_permissions.add(permission)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn("no-store", response["Cache-Control"])


class SpreadsheetExportTests(TestCase):
    def test_user_text_is_escaped_before_csv_export(self):
        project = ProjectRequest.objects.create(
            first_name="Awa",
            last_name="Traoré",
            company="=HYPERLINK(\"https://bad.example\")",
            email="awa@example.com",
            phone="+22600000000",
            client_type="company",
            service="Conseil",
            description="\t=1+1",
            consent=True,
        )
        request = SimpleNamespace(user=SimpleNamespace(has_perm=lambda _permission: True))
        model_admin = admin.site._registry[ProjectRequest]
        response = model_admin.export_selected_requests(request, ProjectRequest.objects.filter(pk=project.pk))
        rows = list(csv.reader(StringIO(response.content.decode("utf-8-sig"))))

        self.assertEqual(rows[1][3], "'=HYPERLINK(\"https://bad.example\")")
        self.assertEqual(rows[1][8], "'\t=1+1")


class AnalyticsPayloadTests(TestCase):
    def test_payload_size_limit_applies_even_without_content_length(self):
        request = RequestFactory().generic(
            "POST",
            "/mesure/conversion/",
            data=b" " * 2049,
            content_type="application/json",
        )
        request.META.pop("CONTENT_LENGTH", None)
        request.COOKIES["lg_analytics_consent"] = "yes"

        response = record_conversion(request)
        self.assertEqual(response.status_code, 413)
