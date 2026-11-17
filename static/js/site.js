document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#main-nav');
  if (toggle && nav) {
    const label = toggle.querySelector('.sr-only');
    const setMenuState = (open) => {
      nav.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      if (label) label.textContent = open ? 'Fermer le menu' : 'Ouvrir le menu';
      if (open) nav.querySelector('a')?.focus();
      else toggle.focus();
    };

    toggle.addEventListener('click', () => setMenuState(toggle.getAttribute('aria-expanded') !== 'true'));
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) setMenuState(false);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) setMenuState(false);
      if (event.key === 'Tab' && nav.classList.contains('is-open')) {
        const links = [...nav.querySelectorAll('a[href]')];
        const first = links[0];
        const last = links[links.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
  }

  const consentBanner = document.querySelector('#consent-banner');
  const consentCookie = 'lg_analytics_consent';
  const readCookie = (name) => document.cookie.split('; ').find((item) => item.startsWith(`${name}=`))?.split('=').slice(1).join('=') || '';
  const writeConsent = (value) => {
    const secure = window.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = `${consentCookie}=${value}; Path=/; Max-Age=31536000; SameSite=Lax${secure}`;
  };
  const track = (eventName) => {
    if (readCookie(consentCookie) !== 'yes') return;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    fetch(document.body.dataset.eventEndpoint, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken || '' },
      body: JSON.stringify({ event: eventName, path: window.location.pathname }),
      keepalive: true,
    }).catch(() => {});
  };

  if (consentBanner && !readCookie(consentCookie)) window.setTimeout(() => { consentBanner.hidden = false; }, 700);
  document.querySelectorAll('[data-consent-accept]').forEach((button) => button.addEventListener('click', () => {
    writeConsent('yes');
    if (consentBanner) consentBanner.hidden = true;
  }));
  document.querySelectorAll('[data-consent-refuse]').forEach((button) => button.addEventListener('click', () => {
    writeConsent('no');
    if (consentBanner) consentBanner.hidden = true;
  }));
  document.querySelectorAll('[data-manage-consent]').forEach((button) => button.addEventListener('click', () => {
    if (consentBanner) {
      consentBanner.hidden = false;
      consentBanner.querySelector('[data-consent-refuse]')?.focus();
    }
  }));

  document.querySelectorAll('[data-track-event]').forEach((element) => {
    element.addEventListener('click', () => track(element.dataset.trackEvent));
  });
  document.querySelectorAll('.track-cta:not([data-track-event])').forEach((element) => {
    element.addEventListener('click', () => track('primary_cta'));
  });

  const needChoices = [...document.querySelectorAll('[data-need-choice]')];
  const needPanel = document.querySelector('[data-need-panel]');
  if (needChoices.length && needPanel) {
    const panelTitle = needPanel.querySelector('[data-need-title]');
    const panelDescription = needPanel.querySelector('[data-need-description]');
    const panelPoints = [
      needPanel.querySelector('[data-need-point-one]'),
      needPanel.querySelector('[data-need-point-two]'),
      needPanel.querySelector('[data-need-point-three]'),
    ];
    const panelCta = needPanel.querySelector('[data-need-cta]');
    const panelCtaLabel = needPanel.querySelector('[data-need-cta-label]');

    needChoices.forEach((choice) => choice.addEventListener('click', () => {
      needChoices.forEach((item) => {
        const selected = item === choice;
        item.classList.toggle('is-selected', selected);
        item.setAttribute('aria-pressed', String(selected));
      });

      if (panelTitle) panelTitle.textContent = choice.dataset.title || '';
      if (panelDescription) panelDescription.textContent = choice.dataset.description || '';
      panelPoints.forEach((point, index) => {
        if (point) point.textContent = choice.dataset[`point${['One', 'Two', 'Three'][index]}`] || '';
      });
      if (panelCta && choice.dataset.href) panelCta.href = choice.dataset.href;
      if (panelCtaLabel) panelCtaLabel.textContent = choice.dataset.cta || 'Parlons de votre projet';
    }));
  }

  if (document.querySelector('[data-expertise-detail]')) track('expertise_view');
  if (document.querySelector('[data-track-success]')) track('form_success');

  document.querySelectorAll('.project-form').forEach((form) => {
    const email = form.querySelector('#id_email');
    const phone = form.querySelector('#id_phone');
    const whatsapp = form.querySelector('#id_whatsapp');
    const checkContact = () => {
      const hasContact = Boolean(email?.value.trim() || phone?.value.trim() || whatsapp?.value.trim());
      const message = hasContact ? '' : 'Indiquez un e-mail ou un numéro de téléphone/WhatsApp.';
      if (email) email.setCustomValidity(message);
      if (phone) phone.setCustomValidity(message);
      if (whatsapp) whatsapp.setCustomValidity(message);
      return hasContact;
    };
    [email, phone, whatsapp].filter(Boolean).forEach((field) => field.addEventListener('input', checkContact));
    form.addEventListener('submit', (event) => {
      if (!checkContact()) {
        event.preventDefault();
        (email || phone || whatsapp)?.reportValidity();
        return;
      }
      const submit = form.querySelector('button[type="submit"]');
      if (submit) {
        submit.disabled = true;
        submit.setAttribute('aria-busy', 'true');
        submit.textContent = 'Envoi en cours…';
      }
    });
  });

  const faqSearch = document.querySelector('#faq-search');
  if (faqSearch) {
    const faqItems = [...document.querySelectorAll('[data-faq-item]')];
    const faqCategories = [...document.querySelectorAll('[data-faq-category]')];
    const emptyState = document.querySelector('#faq-no-results');
    const normalize = (value) => value.toLocaleLowerCase('fr-FR').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    faqSearch.addEventListener('input', () => {
      const term = normalize(faqSearch.value.trim());
      let visibleCount = 0;
      faqItems.forEach((item) => {
        const matches = !term || normalize(item.dataset.search || '').includes(term);
        item.hidden = !matches;
        if (!matches) item.open = false;
        if (matches) visibleCount += 1;
      });
      faqCategories.forEach((category) => {
        category.hidden = !category.querySelector('[data-faq-item]:not([hidden])');
      });
      if (emptyState) emptyState.hidden = visibleCount !== 0;
    });
  }
});
