# Convertor4U

A retro-minimal unit conversion site for [convertor4u.com](https://convertor4u.com), built with Django and vanilla JavaScript/CSS.

Currency conversions use the free, keyless Frankfurter API and cache reference rates server-side for six hours. Rates are informational reference data, not transaction quotes.

Currency multi-convert uses Frankfurter's batch rates endpoint, and currency detail pages show a cached 30-day reference trend. The included `refresh_currency_rates` management command refreshes all configured pairs in batches. The Render blueprint schedules it every six hours; on Railway, create a small cron service with `python manage.py refresh_currency_rates` and the schedule `15 */6 * * *`.

The seeded editorial layer includes substantial guides for all 17 categories, source-backed definitions for all 124 units, and 53 curated conversion pages with examples, precision advice, regional notes, mistakes, and visible FAQs. Twenty priority conversion routes also have hand-written, pair-specific explanations, use cases, cautions, and FAQs. Other valid pair URLs remain useful calculators but are marked `noindex,follow`, omitted from the XML sitemap, and flagged as ineligible for advertising until an editor approves them in Django admin.

## Local setup (Windows / VS Code)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_units
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser. To create an admin login, run `python manage.py createsuperuser`, then visit `/admin/`.

If `python` points to an unusual system installation, select a standard Python 3.11+ interpreter in VS Code before creating `.venv`. Always install with `python -m pip` after activation so packages go into the selected environment.

## Editorial workflow

- Edit category guides, regional notes, rounding advice, mistakes, FAQs, reviewer, and review date under **Categories** in Django admin.
- Edit a unit's definition, primary source, and verification date under **Units**.
- Approve only substantial pair pages under **Featured conversions**. The **Editorially reviewed** checkbox controls indexing, sitemap inclusion, and future ad eligibility; **Show on homepage** and **Homepage order** control the editor-selected homepage directory.
- Review reader reports under **Correction reports**, investigate them against primary standards, update the affected content, and mark them resolved.
- Rerun `python manage.py seed_units` only when you want to restore or update the built-in editorial dataset.

## Maintenance and error pages

Set `MAINTENANCE_MODE=True` to serve the friendly maintenance page with HTTP 503 while keeping `/healthz/`, static files, and Django admin available. Set it back to `False` after maintenance. Custom 404 and 500 pages are enabled automatically when `DEBUG=False`.

## Production

Set `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SITE_URL`, and `SECURE_SSL_REDIRECT=True`. Run `python manage.py migrate && python manage.py seed_units && python manage.py collectstatic --noinput` during deployment and start with `gunicorn config.wsgi:application`.

Set `PUBLIC_OPERATOR_NAME`, `PUBLIC_EDITOR_NAME`, and `PUBLIC_CONTACT_EMAIL` to the real details that should appear on the About, Accuracy, Contact, Privacy, and footer areas. Do not publish a private email address.

## Google Search Console and advertising

1. Add a Domain property for `convertor4u.com` in Google Search Console. Add the TXT value supplied by Google to GoDaddy DNS; this verifies all protocols and subdomains. As an alternative, set `GOOGLE_SITE_VERIFICATION` to the content value from Google's HTML meta tag.
2. Submit `https://convertor4u.com/sitemap.xml`, then inspect and request indexing for the homepage, the 17 category pages, and the strongest reviewed conversion pages.
3. Create or connect the site in AdSense. In **Privacy & messaging**, publish Google's European regulations message for `convertor4u.com`, include consent, reject, and manage-options choices, and keep the privacy-policy URL set to `https://convertor4u.com/privacy/`.
4. Set `ADSENSE_PUBLISHER_ID` to the exact `ca-pub-...` identifier supplied by AdSense. This enables the account-verification meta tag and makes `/ads.txt` publish the matching `pub-...` seller line; it returns 404 while a publisher ID is unconfigured.
5. Leave `ADSENSE_ENABLED=False` until the Google-certified consent message is published and the live privacy page has been checked. Then set it to `True` to load the AdSense script.
6. Do not place ads on pages marked `data-ads-eligible="false"`. Those utility routes are intentionally excluded from indexing and advertising until editorial review.

The privacy page discloses Google advertising cookies, web beacons, IP/device identifiers, third-party vendors, personalized advertising, consent, and opt-out choices. Account-side CMP publication cannot be completed from source code; it must be published inside the site's AdSense account.

## SEO launch checklist

1. Set `SITE_URL=https://convertor4u.com`, without a trailing slash.
2. Redirect every alternate hostname and HTTP request to that single canonical HTTPS hostname.
3. Add the domain to Google Search Console and submit `https://your-domain.com/sitemap.xml`.
4. Add the domain to Bing Webmaster Tools and submit the same sitemap.
5. Request indexing for the homepage, each category hub, and the most important conversion pages after launch.
6. Keep conversion definitions accurate, add genuinely useful unit explanations, and earn relevant links. Metadata helps discovery and presentation but cannot guarantee a first-page ranking.
