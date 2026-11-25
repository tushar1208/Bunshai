// Clean, non-destructive protection against Inspect / DevTools / View Source shortcuts
(function () {
    'use strict';

    let lastAlertAt = 0;

    function notifyInspectDisabled() {
        const now = Date.now();
        if (now - lastAlertAt < 3000) return;
        lastAlertAt = now;
        if (typeof window.showAlert === 'function') {
            window.showAlert('info', 'Inspect is disabled on this website.');
        }
    }

    // Disable right-click context menu (prevents "Inspect" from context menu)
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
        notifyInspectDisabled();
        return false;
    });

    // Block DevTools and View Source shortcuts while keeping normal form typing/printing intact
    document.addEventListener('keydown', function (e) {
        const key = (e.key || '').toUpperCase();
        const isF12 = e.key === 'F12' || e.keyCode === 123;
        const isCtrlShiftDevTools =
            e.ctrlKey && e.shiftKey && (key === 'I' || key === 'J' || key === 'C');
        const isMacDevTools =
            e.metaKey && e.altKey && (key === 'I' || key === 'J' || key === 'C' || key === 'U');
        const isViewSource = e.ctrlKey && !e.shiftKey && !e.altKey && key === 'U';

        if (isF12 || isCtrlShiftDevTools || isMacDevTools || isViewSource) {
            e.preventDefault();
            e.stopPropagation();
            notifyInspectDisabled();
            return false;
        }
    });
})();
