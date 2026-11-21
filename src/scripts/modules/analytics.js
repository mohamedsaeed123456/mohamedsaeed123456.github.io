/* Optional visit counts with GoatCounter: no cookies, no personal data.
   Turn it on by writing the site code in assets/config.js. */
(function (App) {
  'use strict';

  function init() {
    var config = window.PORTFOLIO_CONFIG || {};
    if (!config.goatcounterCode) return;

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://gc.zgo.at/count.js';
    script.setAttribute('data-goatcounter', 'https://' + config.goatcounterCode + '.goatcounter.com/count');
    document.head.appendChild(script);

    var note = document.getElementById('privacy-note');
    if (note) note.hidden = false;

    // Count CV downloads as an event: only which file, nothing about the visitor.
    document.addEventListener('click', function (event) {
      var link = event.target.closest ? event.target.closest('a[download]') : null;
      var href = link && link.getAttribute('href');
      if (!href || !/\.pdf$/i.test(href)) return;
      var name = href.split('/').pop().replace(/\.pdf$/i, '');
      try {
        if (window.goatcounter && window.goatcounter.count) {
          window.goatcounter.count({ path: 'cv-download/' + name, title: 'CV download: ' + name, event: true });
        }
      } catch (err) { /* counting must never break the page */ }
    });
  }

  App.analytics = { init: init };
})(window.App = window.App || {});
