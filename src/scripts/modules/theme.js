/* Theme toggle (dark and light), remembered between visits. */
(function (App) {
  'use strict';

  var DARK_COLOR = '#0B1A24';
  var LIGHT_COLOR = '#F3F6F8';

  function init() {
    var root = document.documentElement;
    var button = document.getElementById('theme');
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!button) return;

    function apply(theme) {
      root.setAttribute('data-theme', theme);
      if (meta) meta.setAttribute('content', theme === 'light' ? LIGHT_COLOR : DARK_COLOR);
      button.setAttribute('aria-label', theme === 'light' ? button.dataset.labelDark : button.dataset.labelLight);
    }

    apply(root.getAttribute('data-theme') === 'light' ? 'light' : 'dark');

    button.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      apply(next);
      try { localStorage.setItem('theme', next); } catch (err) { /* storage can be blocked */ }
    });
  }

  App.theme = { init: init };
})(window.App = window.App || {});
