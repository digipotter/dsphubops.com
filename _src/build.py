#!/usr/bin/env python3
"""Build the dsphubops.com pages from _src.

Every page shares one head, top bar, header and footer. Page bodies come from
_src/pages (hand-written HTML), _src/resources (articles) and _src/content.py
(services, client groups, FAQ and careers). Links inside page bodies use
{{root}}, which becomes the right relative prefix for each page, so the site
works on dsphubops.com and in a GitHub Pages project folder.

Usage: python3 -I _src/build.py
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import content  # noqa: E402

DOMAIN = "https://dsphubops.com/"
# GitHub serves 404.html at every depth, so it needs absolute links. Set this
# to "/" once dsphubops.com points at GitHub Pages.
BASE_404 = "/dsphubops.com/"
PHONE = "1-866-744-6870"
PHONE_TEL = "+18667446870"
ADDRESS = ["12108 Parker Hill Dr", "Bakersfield, CA 93311"]
UPDATED = "October 31, 2026"
FONTS = ("https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;600;700"
         "&family=Public+Sans:wght@600;700;800&display=swap")
NAV = [
    ("services/", "Services", "services"),
    ("who-we-serve/", "Who we serve", "segments"),
    ("resources/", "Resources", "resources"),
    ("about/", "About", "about"),
    ("contact/", "Contact", "contact"),
]

# Logo colours come from the stylesheet (.mk-*), so they follow the palette.
MARK = ('<svg viewBox="0 0 64 64" aria-hidden="true"><g class="mk-line" stroke-width="1.3">'
        '<line x1="32" y1="32" x2="47" y2="17"/><line x1="32" y1="32" x2="47" y2="47"/>'
        '<line x1="32" y1="32" x2="17" y2="47"/><line x1="32" y1="32" x2="17" y2="17"/></g>'
        '<g class="mk-a"><polygon points="32,4 28,28 32,32"/><polygon points="60,32 36,28 32,32"/>'
        '<polygon points="32,60 36,36 32,32"/><polygon points="4,32 28,36 32,32"/></g>'
        '<g class="mk-b"><polygon points="32,4 36,28 32,32"/><polygon points="60,32 36,36 32,32"/>'
        '<polygon points="32,60 28,36 32,32"/><polygon points="4,32 28,28 32,32"/></g>'
        '<circle class="mk-hub" cx="32" cy="32" r="5" stroke-width="2"/></svg>')
# Colour options the owners are comparing. Visitors only see one when a link
# carries ?theme=<slug>; the slugs and labels are repeated in site.js.
THEMES = [
    ("current", "Pine and brass", "The approved palette: deep pine green with brass highlights."),
    ("signal", "Green and orange", "Keeps the green, brightens it, and adds high-visibility orange."),
    ("harbor", "Navy and amber", "Classic logistics navy with warm amber highlights."),
    ("cobalt", "Blue and coral", "A brighter, more modern blue with coral highlights."),
    ("plum", "Plum and gold", "A deep plum that stands apart from blue and green competitors."),
    ("fleet", "Multi-color", "Keeps the pine and brass, and gives each part of the business its own color."),
]
# Runs before the page paints so a previewed palette never flashes green first.
THEME_BOOT = ('<script>try{var t=new URLSearchParams(location.search).get("theme");'
              'if(t===null)t=sessionStorage.getItem("dsp-theme");else sessionStorage.setItem("dsp-theme",t);'
              'if(t&&/^[a-z]+$/.test(t))document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>')
WORDMARK = ('<span class="wordmark"><span class="w">DSP</span><span class="dot"></span>'
            '<span class="w">HUB</span><span class="dot"></span><span>OPS</span></span>')

SERVICE_BY_SLUG = {s["slug"]: s for s in content.SERVICES}


def esc(text):
    return html.escape(text, quote=True)


def root_for(path):
    if path == "404":
        return BASE_404
    return "../" * path.count("/")


# Layout -----------------------------------------------------------------

def head(page, root):
    url = DOMAIN + (page["path"] if page["path"] != "404" else "")
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        "  <title>%s</title>" % esc(page["title"]),
        '  <meta name="description" content="%s">' % esc(page["description"]),
    ]
    if page.get("robots"):
        lines.append('  <meta name="robots" content="%s">' % esc(page["robots"]))
    else:
        lines.append('  <link rel="canonical" href="%s">' % url)
    lines += [
        '  <meta property="og:type" content="%s">' % page.get("og_type", "website"),
        '  <meta property="og:title" content="%s">' % esc(page.get("og_title") or page["title"]),
        '  <meta property="og:description" content="%s">' % esc(page["description"]),
        '  <meta property="og:url" content="%s">' % url,
        '  <meta property="og:image" content="%sassets/img/og-image.png">' % DOMAIN,
        '  <meta name="twitter:card" content="summary_large_image">',
        '  <link rel="icon" href="%sassets/img/favicon.svg" type="image/svg+xml">' % root,
        '  <link rel="apple-touch-icon" href="%sassets/img/apple-touch-icon.png">' % root,
        '  <link rel="preconnect" href="https://fonts.googleapis.com">',
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '  <link rel="stylesheet" href="%s">' % FONTS,
        "  " + THEME_BOOT,
        '  <link rel="stylesheet" href="%sassets/css/site.css">' % root,
        '  <script src="%sassets/js/site.js" defer></script>' % root,
    ]
    for data in page.get("jsonld", []):
        lines.append('  <script type="application/ld+json">%s</script>'
                     % json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    lines.append("</head>")
    return "\n".join(lines)


def topbar(root):
    return """  <div class="topbar">
    <div class="container">
      <div class="topbar-info"><a href="tel:%s">%s</a><span>Bakersfield, California</span></div>
      <a class="topbar-cta" href="%scontact/">Request pricing</a>
    </div>
  </div>""" % (PHONE_TEL, PHONE, root)


def header(root, page):
    links = []
    for href, label, key in NAV:
        attrs = ""
        if page["path"] == href:
            attrs = ' aria-current="page"'
        elif page.get("nav") == key:
            attrs = ' class="is-section"'
        links.append('        <a href="%s%s"%s>%s</a>' % (root, href, attrs, label))
    return """  <header class="site-header">
    <div class="container">
      <a class="logo" href="%s" aria-label="DSP Hub Ops home">
        %s
        %s
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
      <nav id="site-nav" class="nav" aria-label="Main">
%s
        <a class="btn btn--primary" href="%scontact/">Get pricing</a>
      </nav>
    </div>
  </header>""" % (root or "./", MARK, WORDMARK,
                  "\n".join(links), root)


def footer(root):
    services = "\n".join('            <li><a href="%sservices/%s/">%s</a></li>' % (root, s["slug"], s["name"])
                         for s in content.SERVICES)
    segments = "\n".join('            <li><a href="%swho-we-serve/%s/">%s</a></li>' % (root, g["slug"], g["name"])
                         for g in content.SEGMENTS)
    return """  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <a class="logo" href="%(home)s" aria-label="DSP Hub Ops home">
            %(mark)s
            %(wordmark)s
          </a>
          <p class="footer-tagline">Logistics operations for last-mile delivery. Based in Bakersfield, California.</p>
          <ul class="footer-contact">
            <li><a href="tel:%(tel)s">%(phone)s</a></li>
            <li>%(addr0)s<br>%(addr1)s</li>
            <li><a href="%(root)scontact/">Request pricing</a></li>
          </ul>
        </div>
        <div>
          <h2>Services</h2>
          <ul>
%(services)s
          </ul>
        </div>
        <div>
          <h2>Who we serve</h2>
          <ul>
%(segments)s
          </ul>
        </div>
        <div>
          <h2>Company</h2>
          <ul>
            <li><a href="%(root)sabout/">About</a></li>
            <li><a href="%(root)scareers/">Careers</a></li>
            <li><a href="%(root)sresources/">Resources</a></li>
            <li><a href="%(root)sfaq/">FAQ</a></li>
            <li><a href="%(root)scontact/">Contact</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-legal">
        <span>© 2026 DSP Hub Ops LLC</span>
        <span class="footer-links"><a href="%(root)sprivacy/">Privacy policy</a><a href="%(root)sterms/">Terms of use</a></span>
        <span>DSP Hub Ops is an independent company and is not affiliated with Amazon.</span>
      </div>
    </div>
  </footer>""" % {
        "home": root or "./", "root": root, "tel": PHONE_TEL, "phone": PHONE,
        "addr0": ADDRESS[0], "addr1": ADDRESS[1], "services": services, "segments": segments,
        "mark": MARK, "wordmark": WORDMARK,
    }


def render(page):
    root = root_for(page["path"])
    main = page["main"].replace("{{root}}", root)
    main_class = ' class="%s"' % page["main_class"] if page.get("main_class") else ""
    doc = "\n".join([
        head(page, root),
        "<body>",
        '  <a class="skip-link" href="#main">Skip to content</a>',
        "",
        topbar(root),
        "",
        header(root, page),
        "",
        '  <main id="main"%s>' % main_class,
        main.rstrip(),
        "  </main>",
        "",
        footer(root),
        "</body>",
        "</html>",
        "",
    ])
    out = os.path.join(SITE, "404.html" if page["path"] == "404" else os.path.join(page["path"], "index.html"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return out


# Shared blocks ------------------------------------------------------------

def crumbs(items):
    parts = []
    for href, label in items[:-1]:
        parts.append('<a href="{{root}}%s">%s</a><span aria-hidden="true">/</span>' % (href, esc(label)))
    parts.append('<span aria-current="page">%s</span>' % esc(items[-1][1]))
    return '<nav class="crumbs" aria-label="Breadcrumb">%s</nav>' % "".join(parts)


def cta_band(title="Tell us about your operation",
             text="Send a few details and we’ll reply with pricing for the services you need."):
    return """    <section class="section section--pine">
      <div class="container cta">
        <div>
          <h2>%s</h2>
          <p>%s</p>
        </div>
        <a class="btn btn--light" href="{{root}}contact/">Get pricing</a>
      </div>
    </section>""" % (title, text)


def photo(name, width, height, alt, cls="wide-photo"):
    small = {"office-phone": 700, "team-laptop": 700}.get(name, 800)
    large = {"office-phone": 1200, "team-laptop": 1200, "hero-depot": 2400}.get(name, 1600)
    if name == "hero-depot":
        small = 1200
    return ('<div class="%s reveal"><img src="{{root}}assets/img/%s-%d.jpg" srcset="{{root}}assets/img/%s-%d.jpg %dw, '
            '{{root}}assets/img/%s-%d.jpg %dw" sizes="(max-width: 1200px) 100vw, 1120px" width="%d" height="%d" '
            'loading="lazy" alt="%s"></div>' % (cls, name, small, name, small, small, name, large, large, width, height, esc(alt)))


def faq_items(pairs):
    return "\n".join('          <details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in pairs)


def article_card(a, cls="res-card"):
    return """          <a class="%s" data-cat="%s" href="{{root}}resources/%s/">
            <span class="res-cat">%s</span>
            <h3>%s</h3>
            <p>%s</p>
            <span class="res-meta">%s minute read</span>
          </a>""" % (cls, a["category"].lower(), a["slug"], esc(a["category"]), esc(a["title"]), esc(a["dek"]),
                     a["minutes"])


# Generated pages -----------------------------------------------------------

def service_page(s):
    related = "\n".join('            <li><a href="{{root}}services/%s/">%s</a></li>' % (r, SERVICE_BY_SLUG[r]["name"])
                        for r in s["related"])
    problems = "\n".join("            <li>%s</li>" % esc(p) for p in s["problems"])
    handles = "\n".join("            <li>%s</li>" % esc(h) for h in s["handles"])
    weekly = "\n".join("            <li>%s</li>" % esc(w) for w in s["weekly"])
    steps = "\n".join('            <li class="step"><span class="step-num">%d</span><h3>%s</h3><p>%s</p></li>'
                      % (i + 1, esc(t), esc(d)) for i, (t, d) in enumerate(s["steps"]))
    main = """    <section class="page-head page-head--detail">
      <div class="container">
        %(crumbs)s
        <h1>%(name)s</h1>
        <p class="lead">%(lead)s</p>
        <div class="btn-row">
          <a class="btn btn--primary" href="{{root}}contact/">Get pricing</a>
          <a class="btn btn--secondary" href="tel:%(tel)s">Call %(phone)s</a>
        </div>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container">
        %(photo)s
        <div class="detail">
          <div class="detail-main">
            <section class="detail-block reveal">
              <h2>%(problems_title)s</h2>
              <ul class="dash-list">
%(problems)s
              </ul>
            </section>
            <section class="detail-block reveal">
              <h2>What we handle</h2>
              <ul class="checklist">
%(handles)s
              </ul>
              <p class="keep"><strong>Stays with you:</strong> %(keep)s</p>
            </section>
            <section class="detail-block reveal">
              <h2>How it runs</h2>
              <ol class="steps steps--stack">
%(steps)s
              </ol>
            </section>
            <section class="detail-block reveal">
              <h2>In your weekly report</h2>
              <ul class="checklist">
%(weekly)s
              </ul>
            </section>
            <section class="detail-block reveal">
              <h2>Questions</h2>
              <div class="faq">
%(faqs)s
              </div>
            </section>
          </div>
          <aside class="detail-aside">
            <div class="aside-card">
              <h2>Get pricing</h2>
              <p>Tell us about your operation and we’ll reply with a quote for %(name_lower)s.</p>
              <a class="btn btn--primary" href="{{root}}contact/">Get pricing</a>
              <p class="aside-phone">Or call <a href="tel:%(tel)s">%(phone)s</a></p>
            </div>
            <div class="aside-card aside-card--plain">
              <h2>Related services</h2>
              <ul class="aside-links">
%(related)s
                <li><a href="{{root}}services/">All services</a></li>
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </section>

%(cta)s
""" % {
        "crumbs": crumbs([("services/", "Services"), ("", s["name"])]),
        "name": esc(s["name"]), "name_lower": esc(s["name"].lower()), "lead": esc(s["lead"]),
        "tel": PHONE_TEL, "phone": PHONE,
        "photo": photo(*s["photo"]),
        "problems_title": esc(s["problems_title"]), "problems": problems, "handles": handles,
        "keep": esc(s["keep"]), "steps": steps, "weekly": weekly, "faqs": faq_items(s["faqs"]),
        "related": related, "cta": cta_band(),
    }
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faqs"]]}
    service_ld = {"@context": "https://schema.org", "@type": "Service", "name": s["name"],
                  "description": s["description"], "areaServed": "US",
                  "provider": {"@type": "Organization", "name": "DSP Hub Ops LLC", "url": DOMAIN}}
    return {"path": "services/%s/" % s["slug"], "title": s["title"], "description": s["description"],
            "nav": "services", "main": main, "jsonld": [service_ld, faq_ld]}


def segments_hub():
    cards = []
    for g in content.SEGMENTS:
        name, width, height, alt = g["photo"]
        small = 1200 if name == "hero-depot" else 800
        cards.append("""          <a class="seg-card reveal" href="{{root}}who-we-serve/%s/">
            <img src="{{root}}assets/img/%s-%d.jpg" width="%d" height="%d" loading="lazy" alt="%s">
            <div class="seg-card-body">
              <h2>%s</h2>
              <p>%s</p>
              <span class="more-link">How we help</span>
            </div>
          </a>""" % (g["slug"], name, small, width, height, esc(alt), esc(g["name"]), esc(g["short"])))
    main = """    <section class="page-head">
      <div class="container">
        <h1>Who we serve</h1>
        <p class="lead">Last-mile delivery businesses of every size, from a single station to fleets spread across several states.</p>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container">
        <div class="seg-grid">
%s
        </div>
      </div>
    </section>

    <section class="section section--tint">
      <div class="container">
        <div class="section-head reveal">
          <h2>The same start for every client</h2>
          <p class="lead">Whatever the size of your operation, we begin by learning how it runs today.</p>
        </div>
        <ol class="steps reveal">
%s
        </ol>
      </div>
    </section>

%s
""" % ("\n".join(cards), "\n".join('          <li class="step"><span class="step-num">%d</span><h3>%s</h3><p>%s</p></li>'
                                    % (i + 1, esc(t), esc(d)) for i, (t, d) in enumerate(content.ONBOARDING_STEPS)),
       cta_band())
    return {"path": "who-we-serve/", "title": "Who we serve | DSP Hub Ops",
            "description": "DSP Hub Ops supports Amazon Delivery Service Partners, last-mile and courier fleets, and regional carriers and logistics firms.",
            "nav": "segments", "main": main}


def segment_page(g):
    challenges = "\n".join('          <div class="card"><h3>%s</h3><p>%s</p></div>' % (esc(t), esc(d))
                           for t, d in g["challenges"])
    services = "\n".join('          <article class="card"><h3>%s</h3><p>%s</p><a href="{{root}}services/%s/">Learn more</a></article>'
                         % (SERVICE_BY_SLUG[s]["name"], esc(SERVICE_BY_SLUG[s]["short"]), s) for s in g["services"])
    if len(g["services"]) % 3 == 2:
        others = [SERVICE_BY_SLUG[s]["name"].lower() for s in SERVICE_BY_SLUG if s not in g["services"]]
        services += ('\n          <article class="card card--more"><h3>Something else?</h3><p>We also handle %s. '
                     'Every service can be added on its own.</p><a href="{{root}}services/">All services</a></article>'
                     % " and ".join(others))
    steps = "\n".join('          <li class="step"><span class="step-num">%d</span><h3>%s</h3><p>%s</p></li>'
                      % (i + 1, esc(t), esc(d)) for i, (t, d) in enumerate(content.ONBOARDING_STEPS))
    note = '\n        <p class="form-note">%s</p>' % esc(g["note"]) if g["note"] else ""
    main = """    <section class="page-head page-head--detail">
      <div class="container">
        %(crumbs)s
        <h1>%(name)s</h1>
        <p class="lead">%(lead)s</p>
        <div class="btn-row">
          <a class="btn btn--primary" href="{{root}}contact/">Get pricing</a>
          <a class="btn btn--secondary" href="{{root}}services/">See all services</a>
        </div>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container">
        %(photo)s
      </div>
    </section>

    <section class="section section--tint">
      <div class="container">
        <div class="section-head reveal">
          <h2>What we hear from %(audience)s</h2>
        </div>
        <div class="values reveal">
%(challenges)s
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head reveal">
          <h2>How we help</h2>
          <p class="lead">Pick the services that take the most off your plate. Every decision stays with you.</p>
        </div>
        <div class="card-grid card-grid--3 reveal">
%(services)s
        </div>%(note)s
      </div>
    </section>

    <section class="section section--tint">
      <div class="container">
        <div class="section-head reveal">
          <h2>How we start</h2>
        </div>
        <ol class="steps reveal">
%(steps)s
        </ol>
      </div>
    </section>

%(cta)s
""" % {
        "crumbs": crumbs([("who-we-serve/", "Who we serve"), ("", g["name"])]),
        "name": esc(g["name"]), "lead": esc(g["lead"]), "photo": photo(*g["photo"]),
        "audience": esc(g["audience"]), "challenges": challenges, "services": services,
        "note": note, "steps": steps, "cta": cta_band(),
    }
    return {"path": "who-we-serve/%s/" % g["slug"], "title": g["title"], "description": g["description"],
            "nav": "segments", "main": main}


def faq_page():
    groups = []
    entities = []
    for group, pairs in content.FAQ:
        groups.append("""        <div class="faq-group reveal">
          <h2>%s</h2>
          <div class="faq">
%s
          </div>
        </div>""" % (esc(group), faq_items(pairs)))
        entities += [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]
    main = """    <section class="page-head">
      <div class="container">
        <h1>Frequently asked questions</h1>
        <p class="lead">How we work, what we handle and how pricing is set. If your question isn’t here, <a href="{{root}}contact/">ask us directly</a>.</p>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container faq-groups">
%s
      </div>
    </section>

%s
""" % ("\n".join(groups), cta_band("Still have a question?", "Send it through the contact form and we’ll answer it on a short call."))
    return {"path": "faq/", "title": "FAQ | DSP Hub Ops",
            "description": "Answers about DSP Hub Ops: what we handle, who we work with, how pricing works, weekly reporting and how we protect your data.",
            "nav": "", "main": main,
            "jsonld": [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}]}


def careers_page():
    roles = "\n".join("""          <article class="card role reveal">
            <h3>%s</h3>
            <p>%s</p>
            <p class="role-fit"><strong>Helpful background:</strong> %s</p>
          </article>""" % (esc(t), esc(d), esc(f)) for t, d, f in content.ROLES)
    options = "\n".join("                <option>%s</option>" % esc(t) for t, _, _ in content.ROLES)
    main = """    <section class="page-head">
      <div class="container">
        <h1>Careers</h1>
        <p class="lead">We’re building a US team that keeps delivery operations running. If you’re organized, calm under pressure and like solving practical problems, we’d like to hear from you.</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head reveal">
          <h2>Why work with us</h2>
        </div>
        <div class="values reveal">
          <article class="card"><h3>Work that matters</h3><p>Every day you help a delivery business pay its people correctly, keep its vans running and get paid for its work.</p></article>
          <article class="card"><h3>Learn the whole operation</h3><p>You’ll see how last-mile delivery works, from hiring a driver to closing the books.</p></article>
          <article class="card"><h3>Clear expectations</h3><p>Defined responsibilities, a weekly rhythm and teammates who answer questions.</p></article>
          <article class="card"><h3>Room to grow</h3><p>As the company grows, so do the roles. Good work leads to more responsibility.</p></article>
        </div>
      </div>
    </section>

    <section class="section section--tint">
      <div class="container">
        <div class="section-head reveal">
          <h2>Roles we hire for</h2>
          <p class="lead">We hire for these roles as we grow. If nothing fits exactly, send your details anyway.</p>
        </div>
        <div class="card-grid card-grid--3">
%(roles)s
          <article class="card card--more reveal">
            <h3>Don’t see your role?</h3>
            <p>If you have delivery, logistics or back-office experience and want to join a growing team, tell us what you do best.</p>
            <a href="#apply">Send your details</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="apply">
      <div class="container contact-grid">
        <div>
          <div class="section-head">
            <h2>Apply</h2>
            <p class="lead">Tell us a little about yourself. We’ll reply by email and ask for your resume if there’s a fit.</p>
          </div>
          <form id="careers-form" class="form" action="https://formsubmit.co/hharsh.mehta@gmail.com" method="POST" data-formsubmit data-status="careers-status" data-done-title="Thanks for applying." data-done-text="We read every application and will reply by email if there’s a fit.">
            <input type="hidden" name="_subject" value="Careers application from dsphubops.com">
            <input type="hidden" name="_template" value="table">
            <input type="hidden" name="_next" value="https://dsphubops.com/contact/thanks/">
            <input type="text" name="_honey" class="honey" tabindex="-1" autocomplete="off" aria-hidden="true">
            <div class="form-row">
              <div class="field"><label for="c-name">Your name</label><input id="c-name" name="name" type="text" autocomplete="name" required></div>
              <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
            </div>
            <div class="form-row">
              <div class="field"><label for="c-phone">Phone <span class="hint">(optional)</span></label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
              <div class="field"><label for="c-location">City and state</label><input id="c-location" name="location" type="text" autocomplete="address-level2" required></div>
            </div>
            <div class="field">
              <label for="c-role">Role you’re interested in</label>
              <select id="c-role" name="role">
%(options)s
                <option>Something else</option>
              </select>
            </div>
            <div class="field"><label for="c-link">LinkedIn or resume link <span class="hint">(optional)</span></label><input id="c-link" name="link" type="url" inputmode="url"></div>
            <div class="field"><label for="c-message">A few lines about your experience</label><textarea id="c-message" name="message" required></textarea></div>
            <div class="btn-row"><button class="btn btn--primary" type="submit">Send application</button></div>
            <p class="form-note">We use these details only to review your application. DSP Hub Ops is an equal opportunity employer.</p>
          </form>
          <div id="careers-status" class="form-status" role="status" tabindex="-1" hidden></div>
        </div>
        <aside class="contact-aside" aria-label="About working here">
          <div class="facts-box">
            <h2>Good to know</h2>
            <dl>
              <dt>Team</dt><dd>United States</dd>
              <dt>Office</dt><dd>Bakersfield, California</dd>
              <dt>Questions</dt><dd><a href="tel:%(tel)s">%(phone)s</a></dd>
            </dl>
          </div>
        </aside>
      </div>
    </section>
""" % {"roles": roles, "options": options, "tel": PHONE_TEL, "phone": PHONE}
    return {"path": "careers/", "title": "Careers | DSP Hub Ops",
            "description": "Join the DSP Hub Ops team. We hire operations, recruiting, payroll, dispatch and fleet compliance specialists in the United States.",
            "nav": "about", "main": main}


# Fragments and articles ------------------------------------------------------

def parse_fragment(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<!--(.*?)-->\n(.*)\Z", text, re.S)
    if not m:
        raise SystemExit("No front matter in %s" % path)
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, m.group(2)


def load_articles():
    folder = os.path.join(HERE, "resources")
    articles = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html"):
            continue
        meta, body = parse_fragment(os.path.join(folder, name))
        # Writers type straight apostrophes; the rest of the site uses curly ones.
        for key in ("title", "dek", "description"):
            meta[key] = re.sub(r"(?<=\w)'(?=\w)", "’", meta[key])
        meta["body"] = re.sub(r"(?<=\w)'(?=\w)", "’", body)
        meta["minutes"] = str(max(3, round(len(re.sub(r"<[^>]+>", " ", body).split()) / 200)))
        articles.append(meta)
    order = ["Finance", "Operations", "People", "Fleet", "Safety", "Compliance"]
    articles.sort(key=lambda a: (order.index(a["category"]) if a["category"] in order else 99, a["title"]))
    return articles


def article_page(a, articles):
    service = SERVICE_BY_SLUG.get(a.get("service", ""), content.SERVICES[0])
    same = [x for x in articles if x["slug"] != a["slug"] and x["category"] == a["category"]]
    other = [x for x in articles if x["slug"] != a["slug"] and x["category"] != a["category"]]
    related = (same + other)[:3]
    main = """    <section class="page-head page-head--article">
      <div class="container">
        %(crumbs)s
        <h1>%(title)s</h1>
        <p class="lead">%(dek)s</p>
        <p class="article-meta">%(minutes)s minute read. Updated %(updated)s.</p>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container article-wrap">
        <article class="prose">
%(body)s
        </article>
        <aside class="detail-aside">
          <div class="aside-card">
            <h2>Want this handled for you?</h2>
            <p>%(service_short)s</p>
            <a class="btn btn--primary" href="{{root}}services/%(service_slug)s/">%(service_name)s</a>
            <p class="aside-phone">Or <a href="{{root}}contact/">ask for pricing</a></p>
          </div>
        </aside>
      </div>
    </section>

    <section class="section section--tint">
      <div class="container">
        <div class="section-head reveal">
          <h2>More from the library</h2>
        </div>
        <div class="res-grid reveal">
%(related)s
        </div>
      </div>
    </section>

%(cta)s
""" % {
        "crumbs": crumbs([("resources/", "Resources"), ("", a["category"])]),
        "title": esc(a["title"]), "dek": esc(a["dek"]), "minutes": a["minutes"], "updated": UPDATED,
        "body": a["body"].rstrip(), "service_short": esc(service["short"]), "service_slug": service["slug"],
        "service_name": esc(service["name"]), "related": "\n".join(article_card(r) for r in related),
        "cta": cta_band(),
    }
    article_ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                  "description": a["description"], "dateModified": "2026-10-31",
                  "author": {"@type": "Organization", "name": "DSP Hub Ops"},
                  "publisher": {"@type": "Organization", "name": "DSP Hub Ops LLC", "url": DOMAIN},
                  "mainEntityOfPage": DOMAIN + "resources/%s/" % a["slug"]}
    return {"path": "resources/%s/" % a["slug"], "title": "%s | DSP Hub Ops" % a["title"],
            "description": a["description"], "og_title": a["title"], "og_type": "article",
            "nav": "resources", "main": main, "jsonld": [article_ld]}


def resources_hub(articles):
    main = """    <section class="page-head">
      <div class="container">
        <h1>Resources</h1>
        <p class="lead">Practical guides for running a last-mile delivery operation: hiring, payroll, invoices, fleet and safety. Written for owners and managers with no time to waste.</p>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container">
        <div class="res-grid">
%s
        </div>
      </div>
    </section>

%s
""" % ("\n".join(article_card(a, "res-card res-card--feature" if i == 0 else "res-card")
                  for i, a in enumerate(articles)), cta_band())
    return {"path": "resources/", "title": "Resources for delivery fleet owners | DSP Hub Ops",
            "description": "Practical guides for last-mile delivery owners and managers on hiring, payroll, invoice audits, fleet maintenance, safety and compliance.",
            "nav": "resources", "main": main}


def colors_page():
    cards = []
    for slug, name, note in THEMES:
        cards.append("""          <article class="palette" data-theme="%(slug)s">
            <div class="palette-demo">
              <span class="logo">%(mark)s %(wordmark)s</span>
              <p class="hero-label">Last-mile logistics operations</p>
              <p class="palette-head">Every route. Every driver. Every dollar.</p>
              <span class="btn btn--light">Get pricing</span>
            </div>
            <div class="palette-body">
              <h2>%(name)s</h2>
              <p>%(note)s</p>
              <div class="swatches" aria-hidden="true"><span class="sw-deep"></span><span class="sw-primary"></span><span class="sw-secondary"></span><span class="sw-accent"></span><span class="sw-tint"></span></div>
              <div class="swatches swatches--fleet" aria-hidden="true"><span style="background:var(--c-blue)"></span><span style="background:var(--c-orange)"></span><span style="background:var(--c-green)"></span><span style="background:var(--c-gold)"></span><span style="background:var(--c-red)"></span><span style="background:var(--c-violet)"></span></div>
              <div class="demo-card"><span class="step-num">1</span><h3>Dispatch and routes</h3><p>Eyes on every route until the last van is home.</p></div>
              <a class="btn btn--primary" href="{{root}}?theme=%(slug)s">See the site in these colors</a>
            </div>
          </article>""" % {"slug": slug, "name": esc(name), "note": esc(note), "mark": MARK, "wordmark": WORDMARK})
    main = """    <section class="page-head">
      <div class="container">
        <h1>Color options</h1>
        <p class="lead">The same website and logo in six color palettes. Tap one to browse the whole site in it, then use the bar at the bottom of the screen to switch between options.</p>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container">
        <div class="palette-grid">
%s
        </div>
      </div>
    </section>
""" % "\n".join(cards)
    return {"path": "colors/", "title": "Color options | DSP Hub Ops",
            "description": "Color palette options for the DSP Hub Ops website.",
            "robots": "noindex", "nav": "", "main": main}


# Build -------------------------------------------------------------------

def main():
    pages = []
    articles = load_articles()
    org_ld = {"@context": "https://schema.org", "@type": "Organization", "name": "DSP Hub Ops LLC", "url": DOMAIN,
              "logo": DOMAIN + "assets/img/apple-touch-icon.png", "telephone": "+1-" + PHONE[2:],
              "address": {"@type": "PostalAddress", "streetAddress": ADDRESS[0], "addressLocality": "Bakersfield",
                          "addressRegion": "CA", "postalCode": "93311", "addressCountry": "US"}}
    folder = os.path.join(HERE, "pages")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html"):
            continue
        meta, body = parse_fragment(os.path.join(folder, name))
        page = dict(meta)
        page["main"] = body
        if page["path"] == "":
            page["jsonld"] = [org_ld]
            latest = "\n".join(article_card(a) for a in articles[:3])
            page["main"] = page["main"].replace("<!-- resources:latest -->", latest)
        pages.append(page)
    pages += [service_page(s) for s in content.SERVICES]
    pages.append(segments_hub())
    pages += [segment_page(g) for g in content.SEGMENTS]
    pages.append(faq_page())
    pages.append(careers_page())
    pages.append(resources_hub(articles))
    pages += [article_page(a, articles) for a in articles]
    pages.append(colors_page())

    for page in pages:
        render(page)

    urls = [DOMAIN + p["path"] for p in pages if not p.get("robots") and p["path"] != "404"]
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in urls:
            fh.write("  <url><loc>%s</loc><lastmod>2026-10-31</lastmod></url>\n" % url)
        fh.write("</urlset>\n")
    print("built %d pages, %d articles, %d sitemap urls" % (len(pages), len(articles), len(urls)))


if __name__ == "__main__":
    main()
