/* BunShai TECHNOHUB - global site behaviour (loader, nav, popups, toasts, AJAX forms) */
(function () {
    'use strict';

    // ---------- helpers ----------
    function getCookie(name) {
        const m = document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith(name + '='));
        return m ? decodeURIComponent(m.split('=')[1]) : '';
    }
    function csrfToken() {
        const input = document.querySelector('input[name=csrfmiddlewaretoken]');
        return getCookie('csrftoken') || (input ? input.value : '');
    }
    window.getCSRFToken = csrfToken;

    // ---------- toast notifications ----------
    const style = document.createElement('style');
    style.textContent = `
      #site-toasts{position:fixed;top:90px;right:20px;z-index:100000;display:flex;flex-direction:column;gap:10px;max-width:360px}
      .site-toast{padding:14px 18px;border-radius:10px;color:#fff;font:500 14px/1.4 Poppins,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.2);
        animation:toastIn .3s ease;cursor:pointer}
      .site-toast.success{background:#10b981}.site-toast.error{background:#ef4444}.site-toast.info{background:#3b82f6}
      @keyframes toastIn{from{opacity:0;transform:translateX(30px)}to{opacity:1;transform:none}}
      .loader.hidden{opacity:0;visibility:hidden;pointer-events:none;transition:opacity .5s,visibility .5s}`;
    document.head.appendChild(style);

    window.showAlert = function (type, message, duration) {
        let box = document.getElementById('site-toasts');
        if (!box) {
            box = document.createElement('div');
            box.id = 'site-toasts';
            document.body.appendChild(box);
        }
        const t = document.createElement('div');
        t.className = 'site-toast ' + (type || 'info');
        t.setAttribute('role', 'alert');
        t.textContent = message;
        t.onclick = () => t.remove();
        box.appendChild(t);
        setTimeout(() => t.remove(), duration || 6000);
    };

    // ---------- modals / popups ----------
    function openModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        const first = modal.querySelector('input:not([type=hidden]), textarea, select');
        if (first) setTimeout(() => first.focus(), 200);
    }
    function closeModal(modal) {
        if (!modal) return;
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    window.openModal = openModal;
    window.closeModal = closeModal;
    window.showProposalPopup = function () { closeMobileMenu(); openModal('proposalModal'); };
    window.closeProposalPopup = function () { closeModal(document.getElementById('proposalModal')); };
    window.showServiceInquiryPopup = function (service) {
        const sel = document.querySelector('#serviceInquiryForm [name=service]');
        if (sel && service) sel.value = service;
        openModal('serviceInquiryModal');
    };
    window.hideServiceInquiryPopup = function () { closeModal(document.getElementById('serviceInquiryModal')); };
    window.showCourseEnrollPopup = function (slug, title) {
        const slugEl = document.querySelector('#courseEnrollModalForm [name=course_slug]');
        const titleEl = document.querySelector('#courseEnrollModalForm [name=course_title]');
        const badgeEl = document.getElementById('modalCourseTitle');
        if (slugEl && slug) slugEl.value = slug;
        if (titleEl && title) titleEl.value = title;
        if (badgeEl && title) badgeEl.textContent = title;
        openModal('courseEnrollModal');
    };
    window.hideCourseEnrollPopup = function () { closeModal(document.getElementById('courseEnrollModal')); };
    window.showSyllabusPopup = function (slug, title) {
        const slugEl = document.querySelector('#syllabusDownloadForm [name=course_slug]');
        const titleEl = document.querySelector('#syllabusDownloadForm [name=course_title]');
        const badgeEl = document.getElementById('syllabusModalCourseTitle');
        const dlLink = document.getElementById('syllabusDirectLink');
        if (slugEl && slug) slugEl.value = slug;
        if (titleEl && title) titleEl.value = title;
        if (badgeEl && title) badgeEl.textContent = title;
        if (dlLink) dlLink.style.display = 'none';
        openModal('syllabusModal');
    };
    window.hideSyllabusPopup = function () { closeModal(document.getElementById('syllabusModal')); };
    window.scrollToTop = function () { window.scrollTo({ top: 0, behavior: 'smooth' }); };

    // ---------- mobile menu ----------
    function closeMobileMenu() {
        const nav = document.getElementById('main-nav');
        if (nav) {
            nav.classList.remove('show');
            nav.querySelectorAll('.nav-dropdown.open').forEach(dd => {
                dd.classList.remove('open');
                const trigger = dd.querySelector(':scope > .nav-link');
                if (trigger) trigger.setAttribute('aria-expanded', 'false');
            });
        }
        document.body.classList.remove('menu-open');
        document.body.style.overflow = 'auto';
    }
    function toggleMobileMenu() {
        const nav = document.getElementById('main-nav');
        if (!nav) return;
        if (nav.classList.contains('show')) return closeMobileMenu();
        nav.classList.add('show');
        document.body.classList.add('menu-open');
        document.body.style.overflow = 'hidden';
    }

    // ---------- AJAX form handling ----------
    const FORMS = {
        proposalForm: { url: '/proposal-request/', ok: () => window.closeProposalPopup() },
        'footer-subscribe-form': { url: '/subscribe/submit/', email: true },
        'newsletter-form': { url: '/subscribe/submit/', email: true },
        heroSubscribeForm: { url: '/subscribe/submit/', email: true },
        statsSubscribeForm: { url: '/subscribe/submit/', email: true },
        finalSubscribeForm: { url: '/subscribe/submit/', email: true },
        supportTicketForm: { url: '/support/ticket/' },
        careerApplicationForm: { url: '/career/' },
        serviceInquiryForm: { url: '/service-inquiry/', ok: () => window.hideServiceInquiryPopup() },
        courseEnrollForm: { url: '/courses/enroll/' },
        courseEnrollModalForm: { url: '/courses/enroll/', ok: () => window.hideCourseEnrollPopup() },
        syllabusDownloadForm: {
            url: '/courses/syllabus-request/',
            ok: (data) => {
                if (data.download_url) {
                    const dlLink = document.getElementById('syllabusDirectLink');
                    if (dlLink) {
                        dlLink.href = data.download_url;
                        dlLink.style.display = 'inline-flex';
                    }
                    const a = document.createElement('a');
                    a.href = data.download_url;
                    a.download = '';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                }
                setTimeout(() => window.hideSyllabusPopup(), 1400);
            },
        },
    };

    async function submitForm(form, cfg) {
        if (!form.checkValidity()) { form.reportValidity(); return; }
        const fd = new FormData(form);
        if (cfg.email) {
            const email = form.querySelector('input[type=email]');
            fd.set('email', email ? email.value.trim() : '');
        }
        const btn = form.querySelector('button[type=submit]');
        const original = btn ? btn.innerHTML : '';
        if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; }
        try {
            const res = await fetch(cfg.url, {
                method: 'POST',
                body: fd,
                credentials: 'same-origin',
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrfToken(), 'Accept': 'application/json' },
            });
            let data = {};
            try { data = await res.json(); } catch (e) { /* non-JSON error page */ }
            if (res.ok && data.success) {
                window.showAlert('success', data.message || 'Submitted successfully!');
                form.reset();
                if (cfg.ok) cfg.ok(data);
            } else {
                let msg = data.message || 'Something went wrong. Please try again.';
                if (data.errors) {
                    const first = Object.entries(data.errors)[0];
                    if (first) msg = (first[0] === '__all__' ? '' : first[0].replace(/_/g, ' ') + ': ') + first[1][0];
                }
                window.showAlert('error', msg);
            }
        } catch (err) {
            window.showAlert('error', 'Network error. Please check your connection and try again.');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = original; }
        }
    }

    // Capture phase: runs before page-specific (simulated) handlers, which we then suppress.
    document.addEventListener('submit', function (e) {
        const cfg = FORMS[e.target.id];
        if (!cfg) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        submitForm(e.target, cfg);
    }, true);

    // ---------- init ----------
    function hideLoader() {
        const l = document.querySelector('.loader');
        if (l) l.classList.add('hidden');
        document.body.classList.remove('loading');
    }
    window.addEventListener('load', () => setTimeout(hideLoader, 300));
    setTimeout(hideLoader, 3000); // never leave the page covered

    document.addEventListener('DOMContentLoaded', function () {
        const header = document.getElementById('main-header');
        const toTop = document.querySelector('.back-to-top');
        function onScroll() {
            if (header) header.classList.toggle('scrolled', window.scrollY > 50);
            if (toTop) toTop.classList.toggle('visible', window.scrollY > 300);
        }
        window.addEventListener('scroll', onScroll);
        onScroll();

        const toggle = document.getElementById('mobile-menu-toggle');
        if (toggle) toggle.addEventListener('click', toggleMobileMenu);
        const navClose = document.getElementById('nav-close');
        if (navClose) navClose.addEventListener('click', closeMobileMenu);
        document.querySelectorAll('.nav-dropdown > .nav-link').forEach(l =>
            l.addEventListener('click', function (e) {
                const parent = l.parentElement;
                if (window.innerWidth <= 992) {
                    e.preventDefault();
                    const willOpen = !parent.classList.contains('open');
                    document.querySelectorAll('#main-nav .nav-dropdown.open').forEach(other => {
                        if (other !== parent) {
                            other.classList.remove('open');
                            const otherLink = other.querySelector(':scope > .nav-link');
                            if (otherLink) otherLink.setAttribute('aria-expanded', 'false');
                        }
                    });
                    parent.classList.toggle('open', willOpen);
                    l.setAttribute('aria-expanded', String(willOpen));
                } else {
                    parent.classList.toggle('open');
                }
            }));

        document.querySelectorAll('#main-nav a[href]').forEach(link =>
            link.addEventListener('click', function () {
                if (window.innerWidth <= 992 && !link.matches('.nav-dropdown > .nav-link')) {
                    closeMobileMenu();
                }
            }));

        // Two-pane Courses mega-menu switcher
        const megaBtns = document.querySelectorAll('.mega-cat-btn');
        const megaPanels = document.querySelectorAll('.mega-panel');
        function activateMegaCat(slug) {
            megaBtns.forEach(b => b.classList.toggle('active', b.dataset.megaCat === slug));
            megaPanels.forEach(p => p.classList.toggle('active', p.dataset.megaPanel === slug));
        }
        megaBtns.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                if (window.innerWidth > 992) activateMegaCat(btn.dataset.megaCat);
            });
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                activateMegaCat(btn.dataset.megaCat);
                if (window.innerWidth <= 992) {
                    btn.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                }
            });
        });

        ['openProposalBtn', 'openProposalBtnHero'].forEach(id => {
            const b = document.getElementById(id);
            if (b) b.addEventListener('click', window.showProposalPopup);
        });

        const logoTrigger = document.getElementById('logoTrigger');
        if (logoTrigger) logoTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            openModal('logoModal');
        });

        document.querySelectorAll('.modal-close, .popup-close').forEach(btn =>
            btn.addEventListener('click', () => closeModal(btn.closest('.modal'))));
        document.querySelectorAll('.modal').forEach(modal =>
            modal.addEventListener('click', e => {
                if (e.target === modal || e.target.classList.contains('popup-overlay')) closeModal(modal);
            }));
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal').forEach(closeModal);
                closeMobileMenu();
            }
        });

        // Flash messages from non-AJAX redirects (Django messages framework)
        document.querySelectorAll('[data-flash]').forEach(el =>
            window.showAlert(el.dataset.flash, el.textContent.trim()));

        const year = document.getElementById('currentYear');
        if (year) year.textContent = new Date().getFullYear();
    });
})();

