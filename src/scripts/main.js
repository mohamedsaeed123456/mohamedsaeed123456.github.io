/* Entry point: start each module once the DOM is ready. */
(function (App) {
  'use strict';

  function start() {
    ['theme', 'reveal', 'roles', 'filter', 'analytics'].forEach(function (name) {
      try { App[name].init(); } catch (err) { console.error('Module "' + name + '" failed to start', err); }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})(window.App = window.App || {});
