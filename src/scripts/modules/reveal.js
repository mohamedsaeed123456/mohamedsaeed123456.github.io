/* Count the key numbers up and fill the language meters, once, when they scroll into view. */
(function (App) {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var COUNT_DURATION = 1300;

  function countUp(el, formatter) {
    var end = Number(el.dataset.count);
    var suffix = el.dataset.suffix || '';
    if (reduceMotion) {
      el.textContent = formatter.format(end) + suffix;
      return;
    }
    var start = performance.now();
    (function tick(now) {
      var t = Math.min((now - start) / COUNT_DURATION, 1);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = formatter.format(Math.round(end * eased)) + (t === 1 ? suffix : '');
      if (t < 1) requestAnimationFrame(tick);
    })(start);
  }

  function observeOnce(targets, threshold, callback) {
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        callback(entry.target);
        obs.unobserve(entry.target);
      });
    }, { threshold: threshold });
    targets.forEach(function (target) { observer.observe(target); });
  }

  function init() {
    // Stop the SVG packets for people who prefer less motion.
    if (reduceMotion) {
      document.querySelectorAll('.pkt').forEach(function (el) { el.remove(); });
    }
    if (!('IntersectionObserver' in window)) return;

    var formatter = new Intl.NumberFormat('en-US');
    var numbers = document.querySelector('.numbers');
    if (numbers) {
      observeOnce([numbers], 0.4, function (section) {
        section.querySelectorAll('[data-count]').forEach(function (el) { countUp(el, formatter); });
      });
    }

    var meters = Array.prototype.slice.call(document.querySelectorAll('.meter'));
    meters.forEach(function (meter) { meter.classList.add('ready'); });
    observeOnce(meters, 0.6, function (meter) { meter.classList.add('in'); });
  }

  App.reveal = { init: init };
})(window.App = window.App || {});
