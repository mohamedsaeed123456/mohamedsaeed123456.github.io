/* Role picker. Content comes from the JSON block the build script writes into the page. */
(function (App) {
  'use strict';

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function list(tag, className, items, itemTag) {
    var parent = el(tag, className);
    items.forEach(function (text) { parent.appendChild(el(itemTag, '', text)); });
    return parent;
  }

  function renderPanel(role, labels) {
    var fragment = document.createDocumentFragment();
    fragment.appendChild(el('h3', '', role.title));
    fragment.appendChild(el('p', 'sum', role.sum));
    fragment.appendChild(el('h4', '', labels.tools));
    fragment.appendChild(list('div', 'tags', role.tags, 'span'));
    fragment.appendChild(el('h4', '', labels.proof_title));
    fragment.appendChild(list('ul', 'proof', role.proof, 'li'));
    if (role.note) fragment.appendChild(el('p', 'note', role.note));

    var download = el('p', 'dl');
    var link = el('a', 'btn primary', labels.download);
    link.href = role.href;
    link.setAttribute('download', '');
    download.appendChild(link);
    fragment.appendChild(download);
    return fragment;
  }

  function init() {
    var dataNode = document.getElementById('roles-data');
    var panel = document.getElementById('panel');
    if (!dataNode || !panel) return;

    var data = JSON.parse(dataNode.textContent);
    var tabs = Array.prototype.slice.call(document.querySelectorAll('[role="tab"]'));

    function show(id) {
      var role = data.roles[id];
      if (!role) return;
      panel.replaceChildren(renderPanel(role, data.labels));
      panel.setAttribute('aria-labelledby', 't-' + id);
      panel.classList.remove('swap');
      void panel.offsetWidth; // restart the CSS animation
      panel.classList.add('swap');
      tabs.forEach(function (tab) {
        tab.setAttribute('aria-selected', String(tab.dataset.role === id));
      });
    }

    // Arrow keys follow reading direction, so they are swapped in right-to-left pages.
    var rtl = document.documentElement.dir === 'rtl';
    var KEY_STEP = { ArrowDown: 1, ArrowUp: -1, ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1 };

    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () { show(tab.dataset.role); });
      tab.addEventListener('keydown', function (event) {
        var step = KEY_STEP[event.key];
        if (!step) return;
        event.preventDefault();
        var next = tabs[(index + step + tabs.length) % tabs.length];
        next.focus();
        show(next.dataset.role);
      });
    });

    show(tabs.length ? tabs[0].dataset.role : Object.keys(data.roles)[0]);
  }

  App.roles = { init: init };
})(window.App = window.App || {});
