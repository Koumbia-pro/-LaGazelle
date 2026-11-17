import tempfile
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import AuditLog
from apps.core.models import SiteSetting
from apps.contact.models import ProjectRequest, validate_project_attachment
from apps.pages.models import Page


class ProjectRequestTests(TestCase):
    def setUp(self):
        cache.clear()
        privacy_values = {
            "site_privacy_legal_basis": "Consentement et mesures précontractuelles",
            "site_privacy_processors": "Django et hCaptcha",
            "site_privacy_data_location": "Burkina Faso",
            "site_privacy_technical_data": "Adresse IP du navigateur",
            "site_privacy_cookies": "Cookie facultatif de mesure",
            "site_privacy_notification_recipient": "equipe@example.com",
            "site_privacy_rights": "Accès et rectification",
            "site_privacy_contact": "privacy@example.com",
            "site_lead_retention_months": "12",
            "site_privacy_updated_at": "2026-11-16",
        }
        SiteSetting.objects.bulk_create([
            SiteSetting(key=key, value=value, is_public=False)
            for key, value in privacy_values.items()
        ])
        Page.objects.create(
            title="Confidentialité",
            slug="politique-de-confidentialite",
            intro="Politique validée.",
            content=" ".join(privacy_values.values()),
            status="published",
            meta_title="Politique de confidentialité",
            meta_description="Informations sur le traitement des demandes.",
        )
        self.assertTrue(Page.objects.filter(
            slug="politique-de-confidentialite",
            status="published",
        ).exists())

    def valid_data(self):
        return {
            "first_name": "Awa",
            "last_name": "Traoré",
            "company": "Entreprise test",
            "email": "awa@example.com",
            "phone": "+22600000000",
            "whatsapp": "",
            "client_type": "company",
            "service": "Marketing et médias sociaux",
            "description": "Nous souhaitons structurer notre présence digitale.",
            "budget": "À définir",
            "deadline": "À définir",
            "consent": "on",
            "captcha_confirmed": "on",
            "website": "",
        }

    def test_incomplete_published_privacy_policy_keeps_collection_closed(self):
        Page.objects.filter(slug="politique-de-confidentialite").update(content="Texte incomplet")
        response = self.client.get(reverse("contact:project"))
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.context["form_available"])

    def test_contact_form_response_is_not_cached(self):
        response = self.client.get(reverse("contact:project"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])

    @override_settings(PROJECT_NOTIFICATION_EMAIL="equipe@example.com")
    def test_valid_request_is_saved_and_sends_emails(self):
        response = self.client.post(reverse("contact:project"), self.valid_data())
        self.assertRedirects(response, f"{reverse('contact:project')}?sent=1")
        self.assertNotIn("reference=", response.url)
        follow_up = self.client.get(response.url)
        self.assertTrue(follow_up.context["submitted"])
        self.assertEqual(ProjectRequest.objects.count(), 1)
        self.assertContains(follow_up, ProjectRequest.objects.get().reference)
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    def test_consent_is_required(self):
        data = self.valid_data()
        data.pop("consent")
        response = self.client.post(reverse("contact:project"), data)
        self.assertFalse(response.context["submitted"])
        self.assertEqual(ProjectRequest.objects.count(), 0)

    def test_honeypot_rejects_bot(self):
        data = self.valid_data()
        data["website"] = "https://spam.example"
        response = self.client.post(reverse("contact:project"), data)
        self.assertFalse(response.context["submitted"])
        self.assertEqual(ProjectRequest.objects.count(), 0)

    @override_settings(HCAPTCHA_SITE_KEY="test-site", HCAPTCHA_SECRET_KEY="test-secret")
    @patch("apps.contact.views._verify_hcaptcha", return_value=False)
    def test_hcaptcha_failure_does_not_save_request(self, verify_hcaptcha):
        response = self.client.post(reverse("contact:project"), self.valid_data())
        verify_hcaptcha.assert_called_once()
        self.assertFalse(response.context["submitted"])
        self.assertContains(response, "vérification anti-robot")
        self.assertEqual(ProjectRequest.objects.count(), 0)

    @override_settings(HCAPTCHA_SITE_KEY="test-site", HCAPTCHA_SECRET_KEY="test-secret")
    @patch("apps.contact.views._verify_hcaptcha", return_value=True)
    def test_hcaptcha_success_allows_request(self, verify_hcaptcha):
        response = self.client.post(reverse("contact:project"), self.valid_data())
        verify_hcaptcha.assert_called_once()
        self.assertRedirects(response, f"{reverse('contact:project')}?sent=1")
        self.assertEqual(ProjectRequest.objects.count(), 1)

    def test_project_form_is_rate_limited(self):
        cache.clear()
        for _ in range(5):
            response = self.client.post(reverse("contact:project"), self.valid_data())
            self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("contact:project"), self.valid_data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trop de tentatives rapprochées")

    def test_invalid_file_signature_is_rejected(self):
        upload = SimpleUploadedFile(
            "brief.pdf",
            b"not a PDF",
            content_type="application/pdf",
        )
        with self.assertRaises(ValidationError):
            validate_project_attachment(upload)

    def test_project_attachment_requires_lead_permission(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            project = ProjectRequest.objects.create(
                first_name="Awa",
                last_name="Traoré",
                email="awa@example.com",
                client_type="company",
                service="Test",
                description="Demande avec pièce jointe.",
                consent=True,
                attachment=SimpleUploadedFile("brief.pdf", b"%PDF-1.4\nbrief"),
            )
            url = reverse("contact:attachment", args=[project.pk])
            self.assertEqual(self.client.get(url).status_code, 403)

            user = get_user_model().objects.create_user(username="staff", password="Strong-password-123!", is_staff=True)
            self.client.force_login(user)
            self.assertEqual(self.client.get(url).status_code, 403)

            permission = user.user_permissions.model.objects.get(codename="view_projectrequest")
            user.user_permissions.add(permission)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("attachment", response["Content-Disposition"])
