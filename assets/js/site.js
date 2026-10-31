// DSP Hub Ops: mobile menu, hero slider, scroll reveals and forms.

document.documentElement.classList.add('js');

(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Hero slider: rotates every 7 seconds, pauses on hover, focus or the pause
  // button, and never auto-plays for visitors who prefer reduced motion.
  var slider = document.querySelector('.hero-slider');
  if (slider) {
    var slides = slider.querySelectorAll('.hslide');
    var dots = slider.querySelectorAll('.hero-dot');
    var pauseButton = slider.querySelector('.hero-pause');
    var current = 0;
    var timer = null;
    var paused = reduceMotion;

    var show = function (index) {
      slides[current].classList.remove('is-on');
      slides[current].setAttribute('aria-hidden', 'true');
      dots[current].removeAttribute('aria-current');
      current = (index + slides.length) % slides.length;
      slides[current].classList.add('is-on');
      slides[current].removeAttribute('aria-hidden');
      dots[current].setAttribute('aria-current', 'true');
    };
    var stop = function () { clearInterval(timer); timer = null; };
    var start = function () {
      stop();
      if (!paused) timer = setInterval(function () { show(current + 1); }, 7000);
    };
    var setPaused = function (value) {
      paused = value;
      pauseButton.setAttribute('aria-label', paused ? 'Play highlights' : 'Pause highlights');
      pauseButton.innerHTML = paused
        ? '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 1.5v9l7-4.5z" fill="currentColor"/></svg>'
        : '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 1.5h2v9H3zM7 1.5h2v9H7z" fill="currentColor"/></svg>';
      start();
    };

    dots.forEach(function (dot, index) {
      dot.addEventListener('click', function () { show(index); start(); });
    });
    pauseButton.addEventListener('click', function () { setPaused(!paused); });
    slider.addEventListener('mouseenter', stop);
    slider.addEventListener('mouseleave', start);
    slider.addEventListener('focusin', stop);
    slider.addEventListener('focusout', start);
    setPaused(paused);
  }

  // Sections fade up as they scroll into view.
  var revealed = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    revealed.forEach(function (el) { observer.observe(el); });
  } else {
    revealed.forEach(function (el) { el.classList.add('visible'); });
  }

  // Forms post to FormSubmit. Without JavaScript they fall back to a normal
  // POST and FormSubmit redirects to /contact/thanks/. With JavaScript we use
  // FormSubmit's AJAX endpoint and show the result in place.
  document.querySelectorAll('form[data-formsubmit]').forEach(function (form) {
    var status = document.getElementById(form.dataset.status);
    var button = form.querySelector('button[type="submit"]');
    var label = button.textContent;
    form.addEventListener('submit', function (event) { send(event, form, status, button, label); });
  });

  function send(event, form, status, button, label) {
    event.preventDefault();
    button.disabled = true;
    button.textContent = 'Sending…';

    var data = new FormData(form);
    if (form.querySelector('[name="services"]')) {
      var services = data.getAll('services');
      data.delete('services');
      data.set('services', services.length ? services.join(', ') : 'Not specified');
    }

    var endpoint = form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/');
    fetch(endpoint, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: data
    })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function (body) {
        if (body.success === false || body.success === 'false') throw new Error(body.message || 'Rejected');
        form.hidden = true;
        status.className = 'form-status form-status--ok';
        status.innerHTML = '<h2></h2><p></p>';
        status.querySelector('h2').textContent = form.dataset.doneTitle;
        status.querySelector('p').textContent = form.dataset.doneText;
        status.hidden = false;
        status.focus();
      })
      .catch(function (error) {
        console.error('Form failed:', error);
        status.className = 'form-status form-status--error';
        status.textContent = 'We couldn’t send that. Please try again in a minute.';
        status.hidden = false;
        button.disabled = false;
        button.textContent = label;
      });
  }
})();
