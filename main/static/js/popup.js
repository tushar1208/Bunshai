document.addEventListener('DOMContentLoaded', function () {

    /* ===============================
       COMMON FUNCTIONS
    ================================ */

    function openModal(id) {
        const modal = document.getElementById(id);
        if (!modal) {
            console.error('Modal not found:', id);
            return;
        }
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        resetModal(modal);
    }

    function resetModal(modal) {
        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }

        // Scroll modal to top (extra polish)
        const body = modal.querySelector('.modal-body');
        if (body) {
            body.scrollTop = 0;
        }
    }

    /* ===============================
       PROPOSAL POPUP
    ================================ */

    document.getElementById('openProposalBtn')?.addEventListener('click', () => {
        openModal('proposalModal');
    });

    document.getElementById('openProposalBtnHero')?.addEventListener('click', () => {
        openModal('proposalModal');
    });

    /* ===============================
       LOGO POPUP
    ================================ */

    const logoTrigger = document.getElementById('logoTrigger');
    const logoModal = document.getElementById('logoModal');

    if (logoTrigger && logoModal) {
        logoTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            openModal('logoModal');
        });
    }

    /* ===============================
       CLOSE BUTTONS
    ================================ */

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            closeModal(modal);
        });
    });

    /* ===============================
       OUTSIDE CLICK CLOSE
    ================================ */

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', e => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
});

// document.addEventListener('click', function (e) {

//     // Proposal popup
//     const proposalBtn = e.target.closest('#openProposalBtn, #openProposalBtnHero');
//     if (proposalBtn) {
//         e.preventDefault();
//         const modal = document.getElementById('proposalModal');
//         if (modal) {
//             modal.style.display = 'flex';
//             document.body.style.overflow = 'hidden';
//         }
//         return;
//     }
// });
