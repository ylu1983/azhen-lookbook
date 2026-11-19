"""Check catalog completeness and every generated internal link without dependencies."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
DATA = json.loads((ROOT / 'content/outfits.json').read_text())


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class LookbookTests(unittest.TestCase):
    def test_all_27_outfits_have_required_content(self):
        self.assertEqual([o['id'] for o in DATA], list(range(1, 28)))
        for o in DATA:
            self.assertTrue(o['name'] and o['copy'] and o['occasions'])
            self.assertNotIn('\ufffd', o['name'] + o['copy'])
            self.assertTrue(set(o['occasions']) <= {'日常', '通勤', '休閒', '正式', '假日'})
        self.assertEqual(DATA[22]['name'], '粉色打結襯衫＋藕紫色層次長裙')

    def test_brief_concern_tags_and_combined_results(self):
        concerns = {o['id']: o['concerns'] for o in DATA if o['concerns']}
        self.assertEqual(concerns, {
            10: ['小腹明顯'], 12: ['手臂粗不敢穿無袖'],
            14: ['只敢穿黑怕亮色顯老'], 17: ['只敢穿黑怕亮色顯老'],
            20: ['只敢穿黑怕亮色顯老'], 21: ['只敢穿黑怕亮色顯老'],
        })
        def matching(occasion, concern):
            return [o['id'] for o in DATA if occasion in o['occasions'] and concern in o['concerns']]
        self.assertEqual(matching('日常', '手臂粗不敢穿無袖'), [12])
        self.assertEqual(matching('通勤', '小腹明顯'), [10])
        self.assertEqual(matching('正式', '手臂粗不敢穿無袖'), [])

    def test_homepage_has_exactly_27_linked_cards_and_verbatim_intro(self):
        text = (DOCS / 'index.html').read_text()
        doc = Document(text)
        self.assertEqual(sum('outfit-card' in a.get('class', '').split() for _, a in doc.tags), 27)
        self.assertIn(json.loads((ROOT / 'content/shop.json').read_text())['intro'], text)
        chips = [a for tag, a in doc.tags if tag == 'button' and 'data-filter' in a]
        self.assertEqual(len(chips), 10)
        self.assertEqual(sum(a['aria-pressed'] == 'true' for a in chips), 2)

    def test_each_outfit_has_full_copy_photo_and_instagram_cta(self):
        for o in DATA:
            text = (DOCS / f'outfits/{o["id"]:02d}/index.html').read_text()
            doc = Document(text)
            ctas = [a for tag, a in doc.tags if tag == 'a' and 'inquiry-button' in a.get('class', '')]
            self.assertEqual(len(ctas), 1)
            self.assertEqual(ctas[0]['href'], 'https://www.instagram.com/azhen_2026/')
            self.assertIn('私訊問價', text)
            hook, _, rest = o['copy'].partition('。')
            self.assertIn(hook + '。', text)
            self.assertIn(rest, text)
            self.assertTrue((DOCS / f'assets/outfit-{o["id"]:02d}-large.webp').exists())
            self.assertTrue((DOCS / f'assets/outfit-{o["id"]:02d}-small.webp').exists())

    def test_all_internal_pages_and_assets_exist(self):
        for page in DOCS.rglob('*.html'):
            text = page.read_text()
            self.assertNotIn('\ufffd', text)
            self.assertIn('lang="zh-Hant-TW"', text)
            for tag, attrs in Document(text).tags:
                for attr in ('href', 'src'):
                    raw = attrs.get(attr)
                    if not raw or raw.startswith('#'):
                        continue
                    url = urlsplit(raw)
                    if url.scheme or url.netloc:
                        continue
                    path = unquote(url.path)
                    target = DOCS / path.removeprefix('/azhen-lookbook/') if path.startswith('/') else page.parent / path
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), f'{page}: {raw}')

    def test_images_are_small_enough_for_mobile(self):
        self.assertEqual(len(list((DOCS / 'assets').glob('outfit-*-small.webp'))), 27)
        self.assertEqual(len(list((DOCS / 'assets').glob('outfit-*-medium.webp'))), 27)
        for photo in (DOCS / 'assets').glob('*-small.webp'):
            self.assertLess(photo.stat().st_size, 65_000)
        for photo in (DOCS / 'assets').glob('*-medium.webp'):
            self.assertLess(photo.stat().st_size, 90_000)
        for photo in (DOCS / 'assets').glob('*-large.webp'):
            self.assertLess(photo.stat().st_size, 200_000)

    def test_responsive_candidates_exist_and_grid_keeps_native_lazy_loading(self):
        for page in DOCS.rglob('*.html'):
            images = [a for tag, a in Document(page.read_text()).tags if tag == 'img' and 'srcset' in a]
            for attrs in images:
                self.assertEqual((attrs['width'], attrs['height']), ('1080', '1350'))
                candidates = [candidate.strip().split() for candidate in attrs['srcset'].split(',')]
                self.assertEqual([width for _, width in candidates], ['480w', '640w', '1080w'])
                for source, _ in candidates:
                    self.assertTrue((page.parent / source).is_file(), f'{page}: {source}')
        home = Document((DOCS / 'index.html').read_text())
        photos = [a for tag, a in home.tags if tag == 'img' and 'srcset' in a]
        grid = photos[2:]
        self.assertEqual(len(grid), 27)
        self.assertEqual([img['loading'] for img in grid], ['eager'] * 2 + ['lazy'] * 25)
        self.assertIn('(max-width: 700px) calc((100vw - 50px) / 2)', grid[0]['sizes'])

    def test_static_social_previews_and_icon_fallbacks(self):
        pages = [(DOCS / 'index.html', '', 7)] + [
            (DOCS / f'outfits/{o["id"]:02d}/index.html', f'outfits/{o["id"]:02d}/', o['id'])
            for o in DATA
        ]
        for page, path, number in pages:
            with self.subTest(page=page):
                tags = Document(page.read_text()).tags
                meta = {a.get('property'): a.get('content') for tag, a in tags if tag == 'meta'}
                self.assertTrue(meta['og:title'])
                self.assertTrue(meta['og:description'])
                self.assertEqual(meta['og:url'], f'https://ylu1983.github.io/azhen-lookbook/{path}')
                self.assertEqual(meta['og:image'], f'https://ylu1983.github.io/azhen-lookbook/assets/share-{number:02d}.jpg')
                self.assertEqual(meta['og:image:type'], 'image/jpeg')
                self.assertEqual((meta['og:image:width'], meta['og:image:height']), ('1200', '630'))
                self.assertTrue(meta['og:image:alt'])
                photo = DOCS / f'assets/share-{number:02d}.jpg'
                self.assertTrue(photo.read_bytes().startswith(b'\xff\xd8\xff'))
                self.assertLess(photo.stat().st_size, 250_000)
                icons = [a['href'] for tag, a in tags if tag == 'link' and a.get('rel') in {'icon', 'apple-touch-icon'}]
                for filename in ('favicon.ico', 'favicon-32.png', 'favicon.svg', 'apple-touch-icon.png'):
                    self.assertTrue(any(url.endswith('/' + filename) for url in icons))


if __name__ == '__main__':
    unittest.main()
