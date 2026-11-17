from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.services.models import Expertise

from .models import ProjectRequest


class ProjectRequestForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    captcha_confirmed = forms.BooleanField(
        label="Vérification anti-robot",
        required=False,
        widget=forms.CheckboxInput(),
        help_text="Cette vérification de démonstration est remplacée par hCaptcha en production.",
    )
    budget = forms.ChoiceField(
        label="Budget indicatif — facultatif",
        required=False,
        choices=(
            ("", "À définir"),
            ("À définir", "À définir"),
            ("J’ai une enveloppe à préciser dans mon message", "J’ai une enveloppe à préciser dans mon message"),
        ),
    )

    class Meta:
        model = ProjectRequest
        fields = ["first_name", "company", "email", "phone", "whatsapp", "service", "description", "budget", "deadline", "consent"]
        labels = {
            "first_name": "Votre nom",
            "company": "Votre entreprise ou votre activité",
            "email": "Votre e-mail",
            "phone": "Votre téléphone",
            "whatsapp": "Votre numéro WhatsApp",
            "service": "Votre besoin principal",
            "description": "Votre message",
            "deadline": "Votre échéance — facultative",
            "consent": "J’accepte l’utilisation de ces informations pour traiter ma demande.",
        }
        help_texts = {
            "email": "Renseignez au moins un e-mail ou un numéro de téléphone/WhatsApp.",
            "description": "Ne communiquez ni mot de passe, ni donnée sensible, ni document confidentiel.",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "consent": forms.CheckboxInput(),
            "deadline": forms.TextInput(attrs={"placeholder": "Ex. : dans les prochains mois"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "Choisissez une expertise")]
        choices.extend((expertise.name, expertise.name) for expertise in Expertise.objects.filter(is_active=True))
        choices.append(("Je souhaite être conseillé", "Je souhaite être conseillé"))
        self.fields["service"].widget = forms.Select(choices=choices)
        self.fields["company"].required = True
        self.fields["first_name"].required = True
        self.fields["email"].required = False
        self.fields["phone"].required = False
        self.fields["whatsapp"].required = False
        self.fields["deadline"].required = False
        self.fields["budget"].required = False

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise ValidationError("La soumission n’a pas pu être vérifiée.")
        return value

    def clean_consent(self):
        consent = self.cleaned_data.get("consent")
        if not consent:
            raise ValidationError("Votre consentement est nécessaire pour envoyer la demande.")
        return consent

    def clean_captcha_confirmed(self):
        confirmed = self.cleaned_data.get("captcha_confirmed")
        if not settings.HCAPTCHA_SECRET_KEY and not confirmed:
            raise ValidationError("La vérification anti-robot est obligatoire.")
        return confirmed

    def clean(self):
        cleaned_data = super().clean()
        if not any((cleaned_data.get("email"), cleaned_data.get("phone"), cleaned_data.get("whatsapp"))):
            message = "Indiquez un e-mail ou un numéro de téléphone/WhatsApp pour que nous puissions vous répondre."
            self.add_error("email", message)
            self.add_error("phone", message)
        return cleaned_data
