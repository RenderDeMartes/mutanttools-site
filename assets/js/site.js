/* Mutant Tools - static. Spam-safe mail button, plus a menu fallback. */
(function () {
  'use strict';
  document.addEventListener('click', function (e) {
    var m = e.target.closest ? e.target.closest('[data-mail]') : null;
    if (!m) return;
    var addr = m.getAttribute('data-u') + String.fromCharCode(64) + m.getAttribute('data-d');
    var s = m.getAttribute('data-s');
    window.location.href = 'mailto:' + addr + (s ? '?subject=' + encodeURIComponent(s) : '');
  });
})();
