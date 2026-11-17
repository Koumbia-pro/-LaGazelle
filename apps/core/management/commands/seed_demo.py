from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.contact.models import ProjectRequest, ProjectRequestStatusHistory
from apps.core.models import AnalyticsEvent, AboutMilestone, Media, QualityPoint, SiteMetric, SiteSetting, SocialLink, Value
from apps.faq.models import FAQCategory, FAQItem
from apps.pages.models import Page
from apps.services.models import Expertise, Prestation
from apps.stories.models import Article, ArticleSection, CaseStudy
from apps.team.models import TeamMember, TeamPole


EXPERTISES = [
    {
        "name": "Audit digital et stratégie marketing",
        "slug": "audit-digital-strategie-marketing",
        "headline": "Prenez les bonnes décisions avant d’investir dans votre communication.",
        "cta_label": "Parlons de votre audit digital",
        "summary": "Identifiez vos priorités et construisez une stratégie alignée sur vos objectifs commerciaux.",
        "description": "Vous publiez, vous sponsorisez, vous multipliez les outils… mais savez-vous ce qui contribue réellement à votre activité ? La Gazelle analyse votre présence digitale, votre positionnement et le parcours de vos clients pour vous aider à décider où concentrer vos efforts.",
        "audience_need": "Vous manquez de visibilité sur vos performances, préparez une nouvelle étape ou souhaitez mieux utiliser votre budget marketing.",
        "activities": "Audit du site, des réseaux sociaux et des points de contact en ligne.\nAnalyse du positionnement, des publics et de la concurrence.\nDéfinition des objectifs, des messages et des canaux prioritaires.\nPlan marketing et feuille de route adaptés à vos ressources.",
        "deliverables": "Un diagnostic argumenté.\nUne liste de priorités.\nUn plan d’action.\nDes indicateurs de suivi définis avec vous.",
        "outcomes": "Vous disposez d’une direction claire et d’un cadre pour arbitrer vos investissements.",
        "scope_note": "Le périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Audit digital et stratégie marketing | La Gazelle",
        "meta_description": "Audit digital et stratégie marketing pour PME au Burkina Faso. La Gazelle analyse votre présence en ligne et structure vos priorités.",
        "icon": "⌕",
    },
    {
        "name": "Réseaux sociaux et création de contenus",
        "slug": "reseaux-sociaux-contenus",
        "headline": "Des réseaux sociaux qui donnent envie de vous connaître et de vous contacter.",
        "cta_label": "Confions un rôle clair à vos réseaux sociaux",
        "summary": "Confiez-nous vos contenus, vos publications et l’animation de vos communautés.",
        "description": "Votre présence en ligne demande de la cohérence, du temps et des contenus utiles. La Gazelle construit votre ligne éditoriale, produit vos contenus et gère vos réseaux sociaux pour faire vivre votre marque au quotidien.",
        "audience_need": "Vous publiez de façon irrégulière, manquez de contenus ou souhaitez déléguer votre communication à une équipe qui comprend votre activité.",
        "activities": "Stratégie social media et calendrier éditorial.\nRédaction, design graphique, photographie, vidéos courtes et carrousels.\nProgrammation, publication, animation et modération des échanges.\nCampagnes publicitaires et suivi des demandes générées selon la mission.",
        "deliverables": "Une ligne éditoriale.\nUn calendrier validé.\nLes contenus convenus.\nUn cadre de modération.\nUn bilan de performance.",
        "outcomes": "Votre marque gagne en cohérence et votre équipe dispose d’un suivi clair de ce qui est publié et des réactions obtenues.",
        "scope_note": "Le nombre de contenus, les réseaux gérés, les horaires de modération et les dépenses publicitaires sont précisés dans la proposition. Les budgets de diffusion sont distingués des honoraires.\n\nLe périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Réseaux sociaux et création de contenus | La Gazelle",
        "meta_description": "Gestion des réseaux sociaux et création de contenus à Ouagadougou. La Gazelle anime votre présence digitale et suit vos performances.",
        "icon": "◉",
    },
    {
        "name": "Digitalisation des PME et solutions web",
        "slug": "digitalisation-pme-solutions-web",
        "headline": "Faites du digital un outil de travail utile à votre entreprise.",
        "cta_label": "Identifions vos priorités de digitalisation",
        "summary": "Simplifiez vos processus et facilitez la relation client avec des outils adaptés.",
        "description": "La digitalisation commence par une question simple : qu’est-ce qui vous fait perdre du temps ou des opportunités ? La Gazelle vous accompagne pour choisir, déployer et faire adopter des solutions qui répondent à vos usages réels.",
        "audience_need": "Vos informations sont dispersées, vos demandes clients difficiles à suivre ou vos équipes utilisent des outils qui ne communiquent pas entre eux.",
        "activities": "Diagnostic des besoins et des parcours de travail.\nCréation ou refonte de sites vitrines et de pages de campagne.\nOrganisation des demandes clients, formulaires, CRM et automatisations simples.\nAccompagnement à la prise en main et documentation des usages.",
        "deliverables": "Un périmètre fonctionnel.\nLes outils et interfaces convenus.\nUne documentation.\nUne passation à vos équipes.",
        "outcomes": "Vous clarifiez votre organisation et facilitez le passage de la prise de contact au suivi commercial.",
        "scope_note": "Le périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Digitalisation des PME et solutions web | La Gazelle",
        "meta_description": "Digitalisation des PME et solutions web au Burkina Faso. La Gazelle accompagne vos outils, votre site et votre organisation commerciale.",
        "icon": "↗",
    },
    {
        "name": "E-réputation et communication de crise",
        "slug": "e-reputation-communication-crise",
        "headline": "Votre réputation se construit chaque jour. Préparez-vous à la protéger.",
        "cta_label": "Parlons de votre réputation en toute discrétion",
        "summary": "Comprenez ce qui se dit de vous et préparez une réponse adaptée aux situations sensibles.",
        "description": "Une critique, une information inexacte ou une prise de parole mal comprise peut fragiliser la confiance. La Gazelle vous aide à suivre votre image publique, à qualifier les signaux et à organiser vos réponses avec discernement.",
        "audience_need": "Vous souhaitez surveiller votre image, mieux gérer les avis ou disposer d’un cadre de réaction en cas de situation sensible.",
        "activities": "État des lieux de votre visibilité et de votre réputation en ligne.\nVeille des mentions publiques et qualification des alertes selon le périmètre convenu.\nConseil sur les réponses, les messages et les prises de parole.\nPréparation de scénarios de crise et accompagnement de la communication.",
        "deliverables": "Un diagnostic.\nUn dispositif de veille.\nDes recommandations.\nSelon la mission, une procédure de réponse et un bilan de situation.",
        "outcomes": "Vous gagnez en recul pour agir au bon moment et maintenir une communication cohérente.",
        "scope_note": "Nous analysons les possibilités de signalement ou de demande de retrait lorsque la situation le justifie. Les décisions de suppression relèvent des plateformes, des éditeurs ou des autorités compétentes ; aucun retrait n’est garanti.\n\nLe périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "E-réputation et communication de crise | La Gazelle",
        "meta_description": "E-réputation et communication de crise au Burkina Faso. La Gazelle accompagne votre veille, vos réponses et vos prises de parole sensibles.",
        "icon": "◎",
    },
    {
        "name": "Personal branding des dirigeants",
        "slug": "personal-branding-dirigeants",
        "headline": "Votre expertise mérite une présence à sa hauteur.",
        "cta_label": "Travaillons votre positionnement personnel",
        "summary": "Rendez votre expertise visible avec une image et des prises de parole qui vous ressemblent.",
        "description": "Diriger, entreprendre ou exercer un métier d’expertise ne laisse pas toujours le temps de travailler son image. La Gazelle vous aide à clarifier votre positionnement personnel et à prendre la parole avec justesse, sans vous fabriquer un personnage.",
        "audience_need": "Vous souhaitez affirmer votre expertise, rendre votre parcours lisible ou développer votre présence professionnelle, notamment sur LinkedIn.",
        "activities": "Clarification du positionnement, des publics et des sujets de légitimité.\nRédaction de biographie et optimisation des profils professionnels.\nPortraits, interviews et contenus de prise de parole.\nCalendrier éditorial et accompagnement à l’expression publique.",
        "deliverables": "Une plateforme de positionnement personnel.\nDes profils harmonisés.\nLes contenus prévus dans votre programme.",
        "outcomes": "Vos interlocuteurs comprennent mieux qui vous êtes, ce que vous apportez et sur quels sujets vous solliciter.",
        "scope_note": "Le périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Personal branding des dirigeants | La Gazelle",
        "meta_description": "Personal branding des dirigeants et entrepreneurs à Ouagadougou. La Gazelle structure votre positionnement et vos contenus professionnels.",
        "icon": "✦",
    },
    {
        "name": "Lancement de produits et activation",
        "slug": "lancement-produits-activation",
        "headline": "Donnez à votre lancement une stratégie et une suite.",
        "cta_label": "Préparons votre prochain lancement",
        "summary": "Préparez votre lancement et faites passer votre public de la découverte à l’action.",
        "description": "Un produit, une plateforme ou un nouveau service a besoin d’un message clair et d’un parcours pour rencontrer son public. La Gazelle conçoit et coordonne votre lancement, du cadrage de l’offre aux actions de communication et au suivi des contacts.",
        "audience_need": "Vous préparez une mise sur le marché, une inauguration, un lancement de plateforme ou une campagne pour réactiver une offre.",
        "activities": "Cadrage des cibles, de la proposition de valeur et du plan de lancement.\nCréation des supports, des contenus et des pages de campagne.\nActivation digitale et terrain, publicité, influence et relations presse selon le projet.\nCoordination des intervenants et suivi des demandes après le lancement.",
        "deliverables": "Un plan de lancement.\nUn calendrier.\nLes supports convenus.\nUn dispositif de collecte des contacts.\nUn bilan de campagne.",
        "outcomes": "Vous reliez la visibilité du lancement aux prochaines étapes de votre développement commercial.",
        "scope_note": "Le périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Lancement de produits et activation | La Gazelle",
        "meta_description": "Lancement de produits et activation au Burkina Faso. La Gazelle coordonne votre stratégie, vos contenus et vos campagnes de lancement.",
        "icon": "➜",
    },
    {
        "name": "Intelligence artificielle et automatisation",
        "slug": "intelligence-artificielle-automatisation",
        "headline": "Une IA utile à vos équipes et à vos objectifs.",
        "cta_label": "Identifions un premier usage utile de l’IA",
        "summary": "Intégrez l’IA à vos usages pour mieux produire, organiser et suivre votre activité.",
        "description": "L’intelligence artificielle devient intéressante lorsqu’elle répond à un besoin concret. La Gazelle vous aide à repérer les usages pertinents, à tester les outils et à intégrer l’IA dans vos pratiques avec une supervision humaine.",
        "audience_need": "Vous souhaitez gagner du temps sur certaines tâches, structurer la production de contenus ou faciliter le traitement d’informations répétitives.",
        "activities": "Identification et priorisation des cas d’usage.\nAteliers pratiques et méthodes de travail adaptées à vos métiers.\nAssistants, modèles de requêtes et automatisations selon les outils retenus.\nTests, vérification des productions et règles d’utilisation des données.",
        "deliverables": "Une sélection de cas d’usage.\nUn prototype ou un processus testé.\nUn guide d’utilisation.\nUne formation selon la mission.",
        "outcomes": "Vous avancez par étapes, avec des usages compréhensibles et une évaluation de leur intérêt réel.",
        "scope_note": "Les contenus et recommandations produits avec l’IA font l’objet d’une vérification humaine. Les données confidentielles sont traitées selon les règles définies avec votre organisation.\n\nLe périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Intelligence artificielle et automatisation | La Gazelle",
        "meta_description": "IA et automatisation pour les PME au Burkina Faso. La Gazelle accompagne vos cas d’usage, vos tests et la prise en main par vos équipes.",
        "icon": "✧",
    },
    {
        "name": "Cybersécurité et protection des accès",
        "slug": "cybersecurite-protection-acces",
        "headline": "Protégez les accès qui font vivre votre activité.",
        "cta_label": "Faisons le point sur vos accès numériques",
        "summary": "Renforcez les accès, les pratiques et la protection de votre présence numérique.",
        "description": "Comptes sociaux, messageries, site web et outils partagés sont devenus essentiels à votre entreprise. La Gazelle vous accompagne dans la prévention des risques numériques et l’amélioration des pratiques de vos équipes.",
        "audience_need": "Vous partagez des accès, avez connu une tentative de piratage ou souhaitez mieux organiser la protection de vos comptes et de vos informations.",
        "activities": "Revue des accès, des rôles et des procédures de récupération.\nAccompagnement à la double authentification et à la gestion des habilitations.\nSensibilisation au phishing, aux usurpations et aux erreurs de manipulation.\nPlan d’amélioration et orientation vers des spécialistes pour les besoins techniques avancés.",
        "deliverables": "Un état des lieux du périmètre convenu.\nUne liste d’actions prioritaires.\nDes procédures.\nUn atelier de sensibilisation selon la mission.",
        "outcomes": "Vos équipes disposent de repères concrets pour réduire les risques et réagir plus rapidement à un incident.",
        "scope_note": "Le périmètre des vérifications est convenu à l’avance. Les tests techniques avancés nécessitent une mission dédiée et des intervenants qualifiés. Aucune protection ne peut éliminer tous les risques.\n\nLe périmètre, le calendrier et les modalités de suivi sont définis dans votre proposition d’accompagnement.",
        "meta_title": "Cybersécurité et protection des accès | La Gazelle",
        "meta_description": "Protection des comptes et sensibilisation à la cybersécurité pour PME. La Gazelle aide vos équipes à renforcer leurs pratiques numériques.",
        "icon": "◇",
    },
]

FAQ_DATA = {
    "strategie": ("Stratégie marketing", [
        ("À qui s’adresse La Gazelle ?", "Nous accompagnons en priorité les PME et les entrepreneurs. Nous pouvons également intervenir auprès d’organisations ou de dirigeants sur des besoins de communication, de positionnement et de digitalisation."),
        ("Comment commence un accompagnement ?", "Nous échangeons sur votre activité et votre besoin. Nous précisons ensuite le périmètre, les livrables, le calendrier et le budget avant le démarrage."),
        ("Proposez-vous des missions ponctuelles ?", "Oui. Un audit, une campagne de contenus, un lancement ou un atelier peuvent faire l’objet d’une mission précise. Un accompagnement récurrent peut aussi être proposé selon votre besoin."),
        ("Quel budget faut-il prévoir ?", "Le budget dépend des objectifs, du périmètre, des contenus et des moyens à mobiliser. Les achats publicitaires, abonnements ou prestations externes sont identifiés dans la proposition lorsqu’ils sont nécessaires."),
        ("Pouvez-vous garantir des ventes ou un nombre d’abonnés ?", "Nous définissons des objectifs et suivons les performances. Les résultats dépendent aussi de votre offre, du marché, du budget et de la qualité du suivi commercial. Nous vous présentons des indicateurs et des ajustements, sans garantie artificielle."),
    ]),
    "social": ("Réseaux sociaux et contenus", [
        ("Pouvez-vous gérer nos réseaux sociaux au quotidien ?", "Oui. La mission peut couvrir la ligne éditoriale, la création de contenus, la publication, l’animation, la modération et le suivi des performances. Les réseaux concernés et les volumes sont définis dans la proposition."),
    ]),
    "digitalisation": ("Digitalisation et IA", [
        ("Faut-il avoir un site web pour travailler avec vous ?", "Non. Nous partons de votre situation actuelle. Un site peut être utile, mais il doit répondre à un objectif et s’intégrer à votre parcours commercial."),
        ("L’IA peut-elle être utile à une petite entreprise ?", "Oui, si elle répond à un usage concret et si ses productions sont vérifiées. Nous vous aidons à choisir un premier cas d’usage et à tester son intérêt avant d’étendre le dispositif."),
    ]),
    "image-securite": ("Image et sécurité numérique", [
        ("Pouvez-vous supprimer un contenu négatif sur Internet ?", "Nous évaluons la situation et les options possibles : réponse, signalement ou demande de retrait selon le cas. La décision revient aux plateformes, aux éditeurs ou aux autorités compétentes ; la suppression n’est pas garantie."),
        ("Que couvre votre accompagnement en cybersécurité ?", "La prévention, la protection des accès, les bonnes pratiques et la sensibilisation des équipes. Les audits techniques approfondis et les interventions spécialisées font l’objet d’un cadrage distinct."),
    ]),
}


class Command(BaseCommand):
    help = "Charge les contenus de référence de La Gazelle sans supprimer les demandes reçues."

    def handle(self, *args, **options):
        self.seed_settings()
        self.seed_social_links()
        self.seed_pages()
        self.seed_expertises()
        self.seed_faq()
        self.seed_article()
        self.hide_unverified_content()
        self.seed_roles()
        self.stdout.write(self.style.SUCCESS("Contenus de référence La Gazelle chargés. Les éléments à confirmer restent en brouillon ou masqués."))

    def seed_settings(self):
        values = {
            "site_name": ("Nom du site", "La Gazelle", True),
            "site_tagline": ("Descripteur", "Cabinet d’expertise digitale et de stratégie marketing", True),
            "site_slogan": ("Signature", "La Gazelle, l’Élan des Marques.", True),
            "site_intro": ("Présentation courte", "La Gazelle accompagne les PME dans leur communication, leur présence en ligne et leur digitalisation. Nous associons le conseil à la mise en œuvre pour transformer vos priorités en actions concrètes.", True),
            "about_mission": ("Mission", "Aider les PME à structurer leur marketing, développer leur présence en ligne et digitaliser leur activité avec des solutions adaptées à leurs moyens et à leurs objectifs.", True),
            "about_vision": ("Ambition", "Faire du digital un outil de développement accessible aux PME et contribuer à des marques africaines visibles, crédibles et capables de durer.", True),
            "about_positioning": ("Positionnement", "Nous associons le conseil à la mise en œuvre pour transformer vos priorités en actions concrètes.", True),
            "site_location": ("Ville et pays", "Ouagadougou, Burkina Faso", True),
            "site_email": ("E-mail proposé — à confirmer", "hello@lagazelle.media", False),
            "site_phone_standard": ("Téléphone proposé — à confirmer", "+226 25 65 53 95", False),
            "site_phone": ("Téléphone proposé — à confirmer", "+226 25 65 53 95", False),
            "site_phone_additional": ("Autres téléphones — à confirmer", "", False),
            "site_whatsapp": ("WhatsApp proposé — à confirmer", "+226 64 09 31 96", False),
            "site_address": ("Adresse complète — à confirmer", "", False),
            "site_contact_note": ("Note de validation des coordonnées", "Confirmer les coordonnées et les tester avant publication.", False),
            "site_legal_name": ("Dénomination légale proposée — à confirmer", "La Gazelle Agence Web Marketing SARL", False),
            "site_company_capital": ("Capital social proposé — à confirmer", "1 500 000 FCFA", False),
            "site_rccm": ("RCCM proposé — à confirmer", "BF OUA 2021 B 12449", False),
            "site_ifu": ("IFU proposé — à confirmer", "00168924D", False),
            "site_website": ("Site officiel — à confirmer", "", False),
            "site_lead_retention_months": ("Durée de conservation des demandes (mois) — à définir", "", False),
            "site_privacy_legal_basis": ("Fondement du traitement — à valider", "", False),
            "site_privacy_processors": ("Destinataires et prestataires — à valider", "", False),
            "site_privacy_data_location": ("Localisation et transferts de données — à valider", "", False),
            "site_privacy_technical_data": ("Données techniques et journaux — à documenter", "", False),
            "site_privacy_cookies": ("Cookies et mesure d’audience — à documenter", "", False),
            "site_privacy_notification_recipient": ("Destinataire des demandes et notifications — à valider", "", False),
            "site_privacy_rights": ("Droits et modalités d’exercice — à valider", "", False),
            "site_privacy_contact": ("Contact pour les données personnelles — à valider", "", False),
            "site_privacy_updated_at": ("Date de mise à jour de la politique — à définir", "", False),
            "site_hosting_provider": ("Hébergeur et coordonnées — à confirmer", "", False),
            "site_publication_manager": ("Responsable de publication — à confirmer", "", False),
        }
        for key, (label, value, is_public) in values.items():
            defaults = {"label": label, "value": value, "is_public": is_public}
            if is_public:
                SiteSetting.objects.update_or_create(key=key, defaults=defaults)
            else:
                SiteSetting.objects.get_or_create(key=key, defaults=defaults)

    def seed_social_links(self):
        proposed_accounts = {
            "Facebook": "La Gazelle Agence Web Marketing",
            "LinkedIn": "La Gazelle Agence Web Marketing",
            "Instagram": "Lagazellemedia",
            "X": "Lagazellemedia",
            "TikTok": "Lagazellemedia",
        }
        for platform, account_name in proposed_accounts.items():
            SocialLink.objects.get_or_create(
                platform=platform,
                defaults={"account_name": account_name, "url": "", "is_active": False},
            )

    def seed_pages(self):
        Page.objects.filter(slug="a-propos").update(status="draft")
        Page.objects.update_or_create(
            slug="le-cabinet",
            defaults={
                "title": "Le cabinet",
                "intro": "Un cabinet qui relie stratégie marketing et mise en œuvre digitale.",
                "content": "La Gazelle accompagne les PME, les entrepreneurs et les organisations qui veulent rendre leur présence digitale plus claire, plus cohérente et plus utile à leur activité. Nous intervenons sur le diagnostic, le marketing, les contenus et les outils, avec une même exigence : partir de vos besoins réels.\n\nNotre rôle à vos côtés\nVous aider à faire des choix, puis à les traduire en actions. Nous cadrons les priorités, organisons les interventions et assurons le suivi convenu. Selon votre besoin, nous prenons en charge une mission précise ou un accompagnement dans la durée.\n\nPourquoi La Gazelle\nL’agilité nous invite à comprendre vite et à ajuster nos actions quand votre marché ou vos priorités évoluent. L’élégance nous pousse à rendre vos messages plus lisibles et votre image plus cohérente. La résistance nous rappelle qu’une présence digitale se construit dans la durée, avec méthode et continuité.\n\nCes qualités prennent une forme concrète : des recommandations adaptées, des contenus soignés et des outils que vos équipes peuvent s’approprier.\n\nNos engagements de travail\nComprendre votre activité avant de recommander des actions.\nDéfinir un périmètre, des livrables et des responsabilités compréhensibles.\nProtéger la confidentialité des informations confiées.\nVous donner de la visibilité sur le travail réalisé et les points à améliorer.\n\nDes compétences mobilisées selon votre projet\nStratégie, création de contenus, gestion des réseaux sociaux, développement web et accompagnement des usages numériques : votre projet détermine les compétences à réunir. Un interlocuteur coordonne la mission et les échanges avec votre équipe.\n\nNotre ambition\nFaire du digital un outil de développement accessible aux PME et contribuer à des marques africaines visibles, crédibles et capables de durer.",
                "status": "published",
                "meta_title": "Cabinet d’expertise digitale à Ouagadougou | La Gazelle",
                "meta_description": "Découvrez La Gazelle, cabinet d’expertise digitale et de stratégie marketing au service des PME, de leurs contenus et de leur digitalisation.",
            },
        )
        for slug, title in (("mentions-legales", "Mentions légales"), ("politique-de-confidentialite", "Confidentialité")):
            Page.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "intro": "Cette page doit être complétée et validée avant sa publication.",
                    "content": "",
                    "status": "draft",
                    "meta_title": f"{title} | La Gazelle",
                    "meta_description": "",
                },
            )

    def seed_expertises(self):
        active_slugs = []
        expertises = {}
        for index, data in enumerate(EXPERTISES):
            active_slugs.append(data["slug"])
            defaults = {
                **data,
                "order": index,
                "is_active": True,
                "benefits": data["outcomes"],
                "process": "Comprendre votre activité et vos contraintes.\nPrioriser les actions utiles.\nMettre en œuvre les actions convenues.\nMesurer et ajuster selon les retours.",
                "accent_color": "#FFAA00",
            }
            expertise, _ = Expertise.objects.update_or_create(slug=data["slug"], defaults=defaults)
            expertises[data["slug"]] = expertise
        Expertise.objects.exclude(slug__in=active_slugs).update(is_active=False)
        related = {
            "audit-digital-strategie-marketing": ("digitalisation-pme-solutions-web", "reseaux-sociaux-contenus"),
            "reseaux-sociaux-contenus": ("audit-digital-strategie-marketing", "lancement-produits-activation"),
            "digitalisation-pme-solutions-web": ("intelligence-artificielle-automatisation", "cybersecurite-protection-acces"),
            "e-reputation-communication-crise": ("personal-branding-dirigeants", "cybersecurite-protection-acces"),
            "personal-branding-dirigeants": ("reseaux-sociaux-contenus", "e-reputation-communication-crise"),
            "lancement-produits-activation": ("reseaux-sociaux-contenus", "digitalisation-pme-solutions-web"),
            "intelligence-artificielle-automatisation": ("digitalisation-pme-solutions-web", "cybersecurite-protection-acces"),
            "cybersecurite-protection-acces": ("e-reputation-communication-crise", "digitalisation-pme-solutions-web"),
        }
        for slug, related_slugs in related.items():
            expertises[slug].related_expertises.set(expertises[related_slug] for related_slug in related_slugs)

    def seed_faq(self):
        active_category_slugs = []
        for order, (slug, (name, items)) in enumerate(FAQ_DATA.items()):
            active_category_slugs.append(slug)
            category, _ = FAQCategory.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "order": order, "is_active": True, "expertise": None},
            )
            existing_questions = []
            for question_order, (question, answer) in enumerate(items):
                item, _ = FAQItem.objects.update_or_create(
                    category=category,
                    question=question,
                    defaults={"answer": answer, "order": question_order, "is_active": True},
                )
                existing_questions.append(item.pk)
            category.items.exclude(pk__in=existing_questions).update(is_active=False)
        FAQCategory.objects.exclude(slug__in=active_category_slugs).update(is_active=False)

    def seed_article(self):
        article, _ = Article.objects.get_or_create(
            slug="pme-priorites-digitales",
            defaults={
                "title": "PME : comment choisir vos premières priorités digitales",
                "category": "strategie",
                "excerpt": "Votre entreprise n’a pas besoin d’être partout pour commencer à mieux utiliser le digital. Elle a besoin de savoir ce qu’elle veut améliorer.",
                "content": "Votre entreprise n’a pas besoin d’être partout pour commencer à mieux utiliser le digital. Elle a besoin de savoir ce qu’elle veut améliorer : être trouvée, recevoir davantage de demandes pertinentes, mieux répondre aux clients ou gagner du temps au quotidien.\n\nVous souhaitez identifier votre première priorité ? La Gazelle peut vous accompagner dans un audit digital et la construction de votre plan d’action.",
                "author": "",
                "published_at": None,
                "status": "draft",
                "meta_title": "PME : choisir vos priorités digitales | La Gazelle",
                "meta_description": "Objectifs, présence en ligne, organisation et indicateurs : les repères de La Gazelle pour choisir vos premières priorités digitales.",
            },
        )
        sections = [
            ("Partez de votre objectif commercial", "Avant de choisir un réseau social ou un nouvel outil, décrivez le changement attendu. Un restaurant qui cherche des réservations, un cabinet qui veut présenter son expertise et une PME qui perd ses demandes clients n’ont pas la même priorité. Formulez un objectif compréhensible par votre équipe."),
            ("Vérifiez vos points de contact", "Un prospect trouve-t-il facilement votre activité, votre offre et un moyen de vous joindre ? Vos informations sont-elles cohérentes entre votre site, vos réseaux et vos profils professionnels ? Corriger ces bases peut être plus utile que multiplier les publications."),
            ("Choisissez un dispositif que vous pouvez tenir", "Un canal bien animé et un parcours de contact simple valent un plan que personne ne peut exécuter. Définissez qui prépare les contenus, qui les valide, qui répond aux messages et comment les demandes sont suivies."),
            ("Mesurez ce qui aide à décider", "Les vues et les abonnés donnent une indication de visibilité. Ajoutez des repères liés à votre activité : demandes reçues, qualité des contacts, rendez-vous obtenus ou temps gagné. Comparez des périodes cohérentes et ajustez progressivement."),
        ]
        headings = []
        for order, (heading, content) in enumerate(sections):
            headings.append(heading)
            ArticleSection.objects.update_or_create(
                article=article,
                heading=heading,
                defaults={"content": content, "order": order},
            )
        ArticleSection.objects.filter(article=article).exclude(heading__in=headings).delete()

    def hide_unverified_content(self):
        SiteMetric.objects.filter(value__in=("14+", "100+", "50+", "7")).update(is_active=False)
        AboutMilestone.objects.filter(year__in=("2010", "2015", "2020", "Aujourd’hui")).update(is_active=False)
        Value.objects.filter(name__in=("Professionnalisme", "Créativité", "Engagement", "Éthique")).update(is_active=False)
        QualityPoint.objects.filter(name__in=("Satisfaction client", "Professionnalisme de l’équipe", "Méthodologie éprouvée", "Veille technologique")).update(is_active=False)

    def seed_roles(self):
        content_models = [
            Page, Expertise, Prestation, TeamPole, TeamMember, FAQCategory,
            FAQItem, SocialLink, SiteSetting, Media, SiteMetric, Value,
            QualityPoint, AboutMilestone, Article, ArticleSection, CaseStudy,
        ]

        def permissions_for(models, actions):
            content_types = [ContentType.objects.get_for_model(model) for model in models]
            codenames = [f"{action}_{model._meta.model_name}" for model in models for action in actions]
            return Permission.objects.filter(content_type__in=content_types, codename__in=codenames)

        export_permission = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(ProjectRequest),
            codename="export_projectrequest",
        )
        role_permissions = {
            "Administrateur contenu": permissions_for(
                content_models + [ProjectRequest, ProjectRequestStatusHistory, AnalyticsEvent],
                ("add", "change", "delete", "view"),
            ),
            "Commercial / projet": permissions_for(
                [ProjectRequest, ProjectRequestStatusHistory], ("change", "view"),
            ) | export_permission,
            "Éditeur": permissions_for(content_models, ("add", "change", "view")),
            "Lecteur": permissions_for(content_models + [AnalyticsEvent], ("view",)),
        }
        for group_name, permissions in role_permissions.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.set(permissions)
