// DSP Hub Ops: mobile menu and contact form.

(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // The form posts to FormSubmit. Without JavaScript it falls back to a normal
  // POST and FormSubmit redirects to /contact/thanks/. With JavaScript we use
  // FormSubmit's AJAX endpoint and show the result in place.
  var form = document.getElementById('pricing-form');
  if (!form) return;
  var status = document.getElementById('form-status');

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    button.textContent = 'Sending…';

    var data = new FormData(form);
    var services = data.getAll('services');
    data.delete('services');
    data.set('services', services.length ? services.join(', ') : 'Not specified');

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
        status.innerHTML = '<h2>Thanks, we have your request.</h2><p>We will reply by email with pricing for the services you picked.</p>';
        status.hidden = false;
        status.focus();
      })
      .catch(function (error) {
        console.error('Pricing form failed:', error);
        status.className = 'form-status form-status--error';
        status.textContent = 'We couldn’t send that. Please try again in a minute.';
        status.hidden = false;
        button.disabled = false;
        button.textContent = 'Send request';
      });
  });
})();
