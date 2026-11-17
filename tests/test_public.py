from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.contrib.auth.models import Group, Permission

from apps.faq.models import FAQCategory, FAQItem
from apps.contact.models import ProjectRequest
from apps.pages.models import Page
from apps.services.models import Expertise
from apps.team.models import TeamMember, TeamPole


class PublicPagesTests(TestCase):
    def test_homepage_is_available(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "la Gazelle")

    def test_service_detail_is_available(self):
        expertise = Expertise.objects.create(name="Test", slug="test", summary="Résumé")
        response = self.client.get(expertise.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")

    def test_incomplete_legal_pages_stay_hidden_and_seo_endpoints_are_available(self):
        for name in ("pages:legal-notice", "pages:privacy"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 404)
        for name in ("sitemap", "robots"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)

    def test_sitemap_contains_active_expertise(self):
        expertise = Expertise.objects.create(name="Test sitemap", slug="test-sitemap", summary="Résumé")
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expertise.get_absolute_url())

    def test_legal_page_can_be_managed_as_published_page(self):
        Page.objects.create(
            title="Mentions validées",
            slug="mentions-legales",
            intro="Introduction validée",
            content="Contenu légal validé",
            status="published",
        )
        response = self.client.get(reverse("pages:legal-notice"))
        self.assertContains(response, "Contenu légal validé")

    def test_maquette_catalog_routes_are_available(self):
        self.assertEqual(self.client.get(reverse("expertises:list")).status_code, 200)
        self.assertRedirects(
            self.client.get(reverse("prestations:list")),
            reverse("expertises:list"),
            status_code=301,
        )

    def test_faq_page_contains_structured_data(self):
        response = self.client.get(reverse("faq:list"))
        self.assertContains(response, "FAQPage")

    def test_realisation_directory_keeps_navigation_without_fabricating_cases(self):
        response = self.client.get(reverse("stories:cases"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Les premiers projets seront bientôt présentés ici.")
        self.assertContains(response, 'content="noindex,follow"')
        self.assertContains(self.client.get(reverse("pages:home")), "Réalisations")

    def test_inactive_team_members_and_faq_items_are_not_public(self):
        pole = TeamPole.objects.create(name="Pôle test", is_active=True)
        TeamMember.objects.create(
            pole=pole,
            name="Visible",
            role="Profil visible",
            is_active=True,
            is_verified=True,
        )
        TeamMember.objects.create(
            pole=pole,
            name="Masqué",
            role="Profil masqué",
            is_active=False,
        )
        category = FAQCategory.objects.create(
            name="Catégorie test",
            slug="categorie-test",
            is_active=True,
        )
        FAQItem.objects.create(
            category=category,
            question="Question visible",
            answer="Réponse visible",
            is_active=True,
        )
        FAQItem.objects.create(
            category=category,
            question="Question masquée",
            answer="Réponse masquée",
            is_active=False,
        )

        team_response = self.client.get(reverse("team:list"))
        faq_response = self.client.get(reverse("faq:list"))
        self.assertContains(team_response, "Visible")
        self.assertNotContains(team_response, "Masqué")
        self.assertContains(faq_response, "Question visible")
        self.assertNotContains(faq_response, "Question masquée")


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin-test",
            email="admin@example.com",
            password="Strong-password-123!",
        )

    def test_dashboard_requires_staff_access(self):
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_dashboard_is_available_to_staff_users(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertContains(response, "Tableau de bord")
        self.assertContains(response, "Bibliothèque de contenus")

    def test_dashboard_uses_the_current_project_statuses(self):
        shared = {
            "first_name": "Awa",
            "email": "awa@example.com",
            "service": "Conseil",
            "description": "Besoin de conseil.",
            "consent": True,
        }
        for status in ("new", "in_progress", "treated"):
            ProjectRequest.objects.create(**shared, status=status)

        self.client.force_login(self.user)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertContains(response, "Demandes en cours de traitement")
        self.assertContains(response, "Demandes clôturées par l’équipe")
        self.assertContains(response, "status__exact=treated")
        self.assertNotContains(response, "converted")
        self.assertNotContains(response, "qualifying")

    def test_admin_login_is_rate_limited(self):
        cache.clear()
        login_url = reverse("admin:login")
        for _ in range(10):
            response = self.client.post(login_url, {"username": "unknown", "password": "invalid"})
            self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.post(login_url, {"username": "unknown", "password": "invalid"}).status_code,
            429,
        )

    def test_staff_permissions_limit_dashboard_and_admin_models(self):
        group = Group.objects.create(name="Expertise uniquement")
        group.permissions.add(
            Permission.objects.get(content_type__app_label="services", codename="view_expertise")
        )
        editor = get_user_model().objects.create_user(username="expert-editor", is_staff=True)
        editor.groups.add(group)
        self.client.force_login(editor)

        dashboard_response = self.client.get(reverse("admin-dashboard"))
        self.assertContains(dashboard_response, "Expertises")
        self.assertNotContains(dashboard_response, "Pages éditoriales")
        self.assertEqual(
            self.client.get(reverse("admin:pages_page_changelist")).status_code,
            403,
        )
