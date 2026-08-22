/* Progressive enhancement only. Every word of content is in the HTML;
   this file adds a theme toggle and marks the active nav link. Nothing here
   is required for the page to be read by a person, a crawler or an agent. */
(function () {
  'use strict';

  var KEY = 'platizhka-theme';

  function current() {
    var set = document.documentElement.getAttribute('data-theme');
    if (set) return set;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem(KEY, theme); } catch (e) {}
    var btn = document.querySelector('.themebtn');
    if (btn) btn.setAttribute('aria-label', btn.getAttribute('data-label-' + theme) || 'Theme');
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.themebtn');
    if (!btn) return;
    apply(current() === 'dark' ? 'light' : 'dark');
  });

  // Mark the nav entry for the section we are in, so the header reflects position.
  var path = location.pathname.replace(/\/+$/, '/') || '/';
  Array.prototype.forEach.call(document.querySelectorAll('.navlink'), function (a) {
    var href = a.getAttribute('href');
    if (!href || href === '#') return;
    var isBlog = href.indexOf('blog') !== -1;
    if (isBlog && path.indexOf('blog') !== -1) a.setAttribute('aria-current', 'page');
  });

  // Reveal-on-scroll. The `js` class is set by the inline head script (before
  // first paint, so there is no flash); without JavaScript the CSS never
  // engages and every block renders visible — nothing is hidden from a
  // crawler, a reader mode, or a browser with scripting off.
  var targets = document.querySelectorAll('.reveal');
  if (!targets.length) return;
  if (!('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  Array.prototype.forEach.call(targets, function (el) { io.observe(el); });
})();
