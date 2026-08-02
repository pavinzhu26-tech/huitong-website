// main.js — progressive enhancement only.
// The site is fully functional without JS; this file adds polish.
document.addEventListener('DOMContentLoaded', function () {

  // 1. Mobile menu toggle
  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close menu when a link is tapped (mobile)
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        links.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 2. Sticky header shadow on scroll
  var nav = document.getElementById('nav');
  if (nav) {
    var onScroll = function () {
      if (window.scrollY > 10) nav.classList.add('nav--scrolled');
      else nav.classList.remove('nav--scrolled');
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // 3. Scroll-reveal animations
  // Progressive enhancement: content is visible by default (see styles.css).
  // Only when IntersectionObserver is supported do we enable the hidden start
  // state (via html.js-io) and animate elements in as they enter the viewport.
  // A 1.2s safety timeout guarantees nothing stays hidden if the observer
  // fails to fire (e.g. some embedded/headless webviews).
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && reveals.length) {
    document.documentElement.classList.add('js-io');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(function (el) { io.observe(el); });
    setTimeout(function () {
      reveals.forEach(function (el) { el.classList.add('is-visible'); });
    }, 1200);
  }

  // 4. Footer year
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
});
