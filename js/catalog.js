// catalog.js — renders the full product catalog on products.html
// Reads window.HUITONG_CATALOG (from assets/products.js) and builds:
//   1. A sticky 2-level sidebar (categories > sub-categories)
//   2. The product grid (all SKUs, grouped by sub-category)
// Relies on reveal-safety from main.js (content visible by default).
document.addEventListener('DOMContentLoaded', function () {
  var CATALOG = window.HUITONG_CATALOG;
  var catnav = document.getElementById('catnav');
  var root = document.getElementById('catalogRoot');
  if (!CATALOG || !catnav || !root) return;

  // Map category id -> folder name for product images
  var FOLDER = {
    'public': 'public-cleaning',
    'house': 'house-cleaning',
    'pest': 'pest-control'
  };

  // ---- Build sidebar (2-level menu) ----
  var navHtml = '<div class="catnav__title">Catalog</div>';
  CATALOG.forEach(function (cat) {
    navHtml += '<div class="catnav__cat">';
    navHtml += '<div class="catnav__catname"><span class="catnav__num">' + cat.num + '</span>' + esc(cat.name) + '</div>';
    cat.subs.forEach(function (sub) {
      navHtml += '<a class="catnav__sub" href="#' + sub.id + '">' + esc(sub.name) + '</a>';
    });
    navHtml += '</div>';
  });
  catnav.innerHTML = navHtml;

  // ---- Build product grid (grouped by category > sub-category) ----
  var gridHtml = '';
  CATALOG.forEach(function (cat) {
    cat.subs.forEach(function (sub) {
      gridHtml += '<section class="subsection reveal" id="' + sub.id + '">';
      gridHtml += '<div class="subhead">';
      gridHtml += '<div class="subhead__cat">' + esc(cat.num) + ' · ' + esc(cat.name) + '</div>';
      gridHtml += '<h2 class="subhead__name">' + esc(sub.name) + '</h2>';
      gridHtml += '<div class="subhead__count">' + sub.skus.length + (sub.skus.length === 1 ? ' item' : ' items') + '</div>';
      gridHtml += '</div>';
      gridHtml += '<div class="grid grid--4">';
      sub.skus.forEach(function (sku) {
        var img = sku.img ? ('assets/products/' + FOLDER[cat.id] + '/' + sku.img + '.webp') : '';
        gridHtml += '<div class="productcard' + (img ? '' : ' productcard--textonly') + '">';
        if (img) {
          gridHtml += '<img class="productcard__img" src="' + img + '" alt="' + esc(sub.name) + ' ' + esc(sku.model) + '" loading="lazy">';
        }
        gridHtml += '<div class="productcard__model">' + esc(sku.model) + '</div>';
        if (sku.spec) {
          gridHtml += '<div class="productcard__spec">' + esc(sku.spec) + '</div>';
        }
        gridHtml += '</div>';
      });
      gridHtml += '</div></section>';
    });
  });
  root.innerHTML = gridHtml;

  // ---- Highlight active sub-category in sidebar on scroll ----
  var subLinks = catnav.querySelectorAll('.catnav__sub');
  var subSections = root.querySelectorAll('.subsection');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var id = entry.target.id;
          subLinks.forEach(function (l) {
            l.classList.toggle('active', l.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { rootMargin: '-96px 0px -60% 0px', threshold: 0 });
    subSections.forEach(function (s) { io.observe(s); });
  }

  // ---- Re-run reveal observer on newly injected .reveal elements ----
  // (main.js already added html.js-io; re-observe so they animate in)
  if ('IntersectionObserver' in window) {
    var reveals = root.querySelectorAll('.reveal');
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          rio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(function (el) { rio.observe(el); });
    // safety timeout (same guarantee as main.js)
    setTimeout(function () {
      reveals.forEach(function (el) { el.classList.add('is-visible'); });
    }, 1200);
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
});
