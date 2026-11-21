/* Project filter chips. */
(function (App) {
  'use strict';

  function init() {
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
    var items = Array.prototype.slice.call(document.querySelectorAll('#rows li'));

    function select(chip) {
      var filter = chip.dataset.filter;
      chips.forEach(function (other) {
        var on = other === chip;
        other.classList.toggle('on', on);
        other.setAttribute('aria-pressed', String(on));
      });
      items.forEach(function (item) {
        item.hidden = !(filter === 'all' || item.dataset.tags.split(' ').indexOf(filter) > -1);
      });
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () { select(chip); });
    });
  }

  App.filter = { init: init };
})(window.App = window.App || {});
