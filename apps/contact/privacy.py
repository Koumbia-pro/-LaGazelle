import re

from apps.core.models import SiteSetting
from apps.pages.models import Page


PRIVACY_POLICY_SETTING_KEYS = (
    "site_privacy_legal_basis",
    "site_privacy_processors",
    "site_privacy_data_location",
    "site_privacy_technical_data",
    "site_privacy_cookies",
    "site_privacy_notification_recipient",
    "site_privacy_rights",
    "site_privacy_contact",
    "site_lead_retention_months",
    "site_privacy_updated_at",
)
INCOMPLETE_MARKERS = (
    "provisoire",
    "à confirmer",
    "a confirmer",
    "à valider",
    "a valider",
    "à définir",
    "a definir",
    "à compléter",
    "a completer",
    "[",
)


def contact_collection_is_ready():
    """Keep personal-data collection closed until its published policy is complete."""
    page = Page.objects.filter(
        slug="politique-de-confidentialite",
        status="published",
    ).first()
    if not page or not page.meta_title.strip() or not page.meta_description.strip():
        return False

    policy_text = re.sub(r"\s+", " ", f"{page.intro} {page.content}").casefold()
    if not policy_text.strip() or any(marker in policy_text for marker in INCOMPLETE_MARKERS):
        return False

    settings_by_key = {
        row["key"]: row["value"].strip()
        for row in SiteSetting.objects.filter(key__in=PRIVACY_POLICY_SETTING_KEYS).values("key", "value")
    }
    return all(
        settings_by_key.get(key)
        and re.sub(r"\s+", " ", settings_by_key[key]).casefold() in policy_text
        for key in PRIVACY_POLICY_SETTING_KEYS
    )
