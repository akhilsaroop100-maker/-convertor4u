# Convertor4U advertising launch checklist

Use this order. Do not enable advertising before the privacy page and consent message are live.

## 1. Deploy this release

- Upload the changed project files to the GitHub repository.
- Wait for the Render deployment to finish successfully.
- Open `https://convertor4u.com/privacy/` and confirm the sections **Google advertising and cookies** and **Consent choices** are visible.

## 2. Add the public identity in Render

Add these environment variables to the web service:

- `PUBLIC_OPERATOR_NAME` — the real owner or registered business name.
- `PUBLIC_EDITOR_NAME` — the real person responsible for editorial review.
- `PUBLIC_CONTACT_EMAIL` — a working public address, preferably on `@convertor4u.com`.

Redeploy and confirm the details appear on About, Accuracy, Contact, Privacy, and the footer.

## 3. Verify Search Console

- Create a Domain property for `convertor4u.com`.
- Copy Google's TXT verification value into a new GoDaddy DNS TXT record with the name `@`.
- After verification, submit `https://convertor4u.com/sitemap.xml`.
- Request indexing for the homepage, all 17 category pages, and the strongest reviewed conversion pages.
- Check **Pages** and **Sitemaps** for crawl or canonical errors after Google has processed the site.

If you use Google's HTML meta-tag method instead, put only the tag's `content` value in Render as `GOOGLE_SITE_VERIFICATION` and redeploy.

## 4. Connect AdSense without serving ads yet

- Add `convertor4u.com` to AdSense.
- Set `ADSENSE_PUBLISHER_ID` in Render to Google's exact `ca-pub-...` value.
- Keep `ADSENSE_ENABLED=False`.
- Redeploy and check that `https://convertor4u.com/ads.txt` contains the matching `pub-...` line.

## 5. Publish Google's certified consent message

- In AdSense, open **Privacy & messaging**.
- Create a **European regulations** message for `convertor4u.com`.
- Use the privacy-policy URL `https://convertor4u.com/privacy/`.
- Give visitors clear consent, reject, and manage-options choices.
- Publish the message and test it in a private browser session from an eligible region or with Google's testing tools.
- Confirm visitors can review or revoke their choices later through the privacy-options link supplied by Google's message.

## 6. Enable ads

- Set `ADSENSE_ENABLED=True` in Render only after the previous steps pass.
- Redeploy and confirm the Google script appears on the live site.
- Keep ads off routes whose page markup says `data-ads-eligible="false"`.
- Start with restrained placements that do not obscure the converter or outweigh the page's editorial content.

## 7. Final live checks

- Calculator, swap, copy, favorite, remove favorite, clear-history and clear-favorites controls.
- Compound query: `5 ft 11 in to cm`.
- Currency result, provider status, multi-convert, and 30-day chart.
- Contact-form validation and one real end-to-end report.
- `/privacy/`, `/about/`, `/accuracy/`, `/contact/`, `/robots.txt`, `/sitemap.xml`, `/ads.txt`, and a non-existent URL.
- One reviewed conversion in each of the 17 categories on desktop and mobile.
- Canonical URLs point to `https://convertor4u.com`.

## 8. Disable the Render fallback hostname

After `convertor4u.com` and `www.convertor4u.com` pass all tests, go to Render **Settings → Custom Domains** and disable **Render Subdomain**. Then verify `https://convertor4u.onrender.com` no longer serves the site while the custom domain remains healthy.
