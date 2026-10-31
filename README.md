# dsphubops.com

Static site for DSP Hub Ops LLC. Plain HTML, one stylesheet (`assets/css/site.css`) and one small script (`assets/js/site.js`). No build step.

## Preview locally

```bash
python3 -m http.server 4192 --directory site
```

Then open http://localhost:4192.

## Things to change before launch

| What | Where |
|---|---|
| Phone number | `1-866-744-6870` is temporary until the main number is approved. It appears in the footer of each page and in the contact box on `contact/index.html` (search for `tel:`). |
| Form inbox | The `action` on the form in `contact/index.html`. It currently points to a temporary test Gmail. |

### Contact form

The form posts to [FormSubmit](https://formsubmit.co), which emails each submission.

1. The first submission to a new address sends an activation email to that inbox. Click the link once.
2. After activation, FormSubmit offers a random alias for the address. Swap it into the form `action` so the real email isn't visible in the page source.
3. To change inboxes later, edit the address in the form `action` and activate again.

## Deploy on GitHub Pages

The repository is `digipotter/dsphubops.com`, published from the `main` branch, root folder. All links are relative, so the site works on the temporary `digipotter.github.io/dsphubops.com/` address and on the real domain.

To move to dsphubops.com:

1. At the domain registrar, add:
   - `A` records for `dsphubops.com` pointing to `185.199.108.153`, `185.199.109.153`, `185.199.110.153` and `185.199.111.153`
   - a `CNAME` record for `www` pointing to `digipotter.github.io`
2. Add a file named `CNAME` at the repository root containing `dsphubops.com`, or type the domain under Settings > Pages > Custom domain.
3. Tick "Enforce HTTPS" once the certificate is issued.

## Photos

Stock photos from Unsplash, free for commercial use under the Unsplash License:

- `hero-vans-*`: https://unsplash.com/photos/white-vans-parked-in-mossingen-3vlGNkDep4E
- `ops-aisle-*`: https://unsplash.com/photos/women-walking-through-warehouse-aisle-ZlOlRnWk8zU
- `office-phone-*`: https://unsplash.com/photos/woman-talking-on-phone-while-working-on-laptop-in-office-ttGPlhrPiZs
- `team-laptop-*`: https://unsplash.com/photos/two-men-sitting-at-a-table-looking-at-a-laptop-nbEX3qxtmuA

## Brand

- Colors: pine `#10362F`, sea sage `#5B8F86`, brass `#B39463`, mist `#B7CFC9`, porcelain `#F1F4F3`
- Type: Public Sans for headings and the wordmark, Atkinson Hyperlegible Next for body text
