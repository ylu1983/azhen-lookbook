# 阿蓁の衣舖子 — Outfit Lookbook

A mobile-first Traditional Chinese outfit catalog for 阿蓁の衣舖子 in Neihu, Taipei. All 27 supplied looks have a direct, shareable detail page, their original copy, and an Instagram inquiry link. This is a lookbook, not a shop checkout.

**Public site:** https://ylu1983.github.io/azhen-lookbook/

## Run locally

Python 3.10 or newer is enough. No JavaScript toolchain, server application, database, or third-party runtime dependency is required.

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. Each outfit also works as a static page with JavaScript disabled. JavaScript enhances the homepage with immediately combined occasion/concern filters, URL-preserved selections, result counts, and an empty state.

## Content and assets

- `content/outfits.json`: the 27 names, exact supplied descriptions, and filter tags
- `content/shop.json`: the exact supplied shop introduction and social links
- `src/style.css`, `src/app.js`: responsive presentation and filter behavior
- `scripts/build.py`: standard-library static generator
- `docs/`: the complete published site, including generated outfit pages and optimized photographs

Images were converted to responsive 480px/1080px WebP variants without cropping or stretching. The original photos and the full brief remain in the user's original upload, not duplicated in the public repository. The supplied logo is retained. The malformed replacement characters in outfit 23's name were corrected to `＋`; outfit copy and all concern tags are otherwise unchanged.

To update content or styles, edit the source and run the build command. Commit the generated `docs/` changes along with the source. Photograph rights remain with their respective owners; the repository does not grant a license to reuse them.

## GitHub Pages

In repository **Settings → Pages**, use **Deploy from a branch**, branch **main**, folder **/docs**. GitHub publishes the committed static output; no build secrets or custom domain are needed. `.nojekyll` prevents unwanted Jekyll processing. Detail-page URLs use real folders, so opening or refreshing a shared URL works on Pages.

## Checks

The tests validate all 27 entries, exact concern tags and representative intersection counts, supplied copy, inquiry destinations, internal links, and mobile image budgets. The `Validate site` workflow rebuilds with Python, runs these tests, and rejects stale generated output.
