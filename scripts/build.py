#!/usr/bin/env python3
"""Build the dependency-free, GitHub Pages-ready lookbook into docs/."""
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
OUTFITS = json.loads((ROOT / 'content/outfits.json').read_text())
SHOP = json.loads((ROOT / 'content/shop.json').read_text())
OCCASIONS = ['日常', '通勤', '休閒', '正式', '假日']
CONCERNS = ['手臂粗不敢穿無袖', '小腹明顯', '只敢穿黑怕亮色顯老']
SITE = 'https://ylu1983.github.io/azhen-lookbook/'
# Keep these slot widths aligned with the grid's breakpoints, gutters and gaps.
# Overstating a 171.5px tile as 46vw makes a DPR 2.75 phone skip the 480px file.
CARD_SIZES = '(max-width: 360px) calc((100vw - 38px) / 2), (max-width: 700px) calc((100vw - 50px) / 2), (max-width: 1000px) calc((100vw - 88px) / 3), (max-width: 1320px) calc((100vw - 152px) / 4), 292px'


def esc(value):
    return html.escape(str(value), quote=True)


ARROW = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
IG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.5"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'


def image(outfit, prefix='', extra='', eager=False):
    n = outfit['id']
    return f'<img src="{prefix}assets/outfit-{n:02d}-large.webp" srcset="{prefix}assets/outfit-{n:02d}-small.webp 480w, {prefix}assets/outfit-{n:02d}-medium.webp 640w, {prefix}assets/outfit-{n:02d}-large.webp 1080w" sizes="{extra or CARD_SIZES}" width="1080" height="1350" alt="{esc(outfit["name"])}" loading="{"eager" if eager else "lazy"}" decoding="async">'


def header(prefix='', home=False):
    return f'''<header class="site-header wrap">
      <a class="brand" href="{prefix or './'}" aria-label="阿蓁の衣舖子，回首頁"><img src="{prefix}assets/shop-logo-badge.png" width="284" height="66" alt="阿蓁の衣舖子"></a>
      <nav aria-label="主要導覽"><a class="nav-link" href="{prefix}#collection">穿搭型錄</a><a class="nav-link about-nav" href="{prefix}#about">關於阿蓁</a><a class="instagram-link" href="{SHOP['instagram']}" target="_blank" rel="noopener noreferrer" aria-label="前往阿蓁的 Instagram（另開分頁）">{IG}<span>逛逛 IG</span>{ARROW}</a></nav>
    </header>'''


def footer(prefix=''):
    return f'''<footer class="site-footer"><div class="wrap footer-top"><a class="footer-brand" href="{prefix or './'}">阿蓁の衣舖子<span>台北內湖・用心挑選，陪妳穿搭</span></a><div class="footer-social"><a href="{SHOP['instagram']}" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="{SHOP['threads']}" target="_blank" rel="noopener noreferrer">Threads ↗</a></div></div><div class="wrap footer-bottom"><p>{SHOP['disclosure']}</p><a href="#top">回到頂端 ↑</a></div></footer>'''


def shell(title, description, body, prefix='', path='', detail=False, photo='assets/share-07.jpg'):
    return f'''<!doctype html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#f7f4ed"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{SITE}{path}">
<meta property="og:locale" content="zh_TW"><meta property="og:type" content="website"><meta property="og:site_name" content="阿蓁の衣舖子"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:image" content="{SITE}{photo}"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(title)}"><meta property="og:url" content="{SITE}{path}">
<link rel="icon" href="{prefix}assets/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="{prefix}assets/favicon-32.png" type="image/png" sizes="32x32"><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png" sizes="180x180"><link rel="stylesheet" href="{prefix}style.css"><script src="{prefix}app.js" defer></script></head>
<body id="top"{' class="detail-page"' if detail else ''}><a class="skip-link" href="#main">跳至主要內容</a>{body}</body></html>'''


def card(outfit, prefix='', eager=False):
    n = outfit['id']
    return f'''<article class="outfit-card" data-occasions="{esc('|'.join(outfit['occasions']))}" data-concerns="{esc('|'.join(outfit['concerns']))}"><a class="outfit-link" href="{prefix}outfits/{n:02d}/"><div class="card-photo">{image(outfit, prefix, eager=eager)}<span class="photo-number">{n:02d}</span><span class="photo-open" aria-hidden="true">{ARROW}</span></div><div class="card-meta"><p>{'・'.join(outfit['occasions'])}</p><h3>{esc(outfit['name'])}</h3></div></a></article>'''


def filters(group, label, options):
    buttons = ''.join(f'<button type="button" class="filter-chip{" is-active" if not value else ""}" data-filter="{group}" data-value="{value}" aria-pressed="{"false" if value else "true"}">{value or "全部"}</button>' for value in ['', *options])
    return f'<div class="filter-row"><span class="filter-label" id="{group}-label">{label}<span class="filter-hint" aria-hidden="true">左右滑動</span></span><div class="filter-options" role="group" aria-labelledby="{group}-label">{buttons}</div></div>'


def arm_guidance(prefix='', hidden=False):
    # These two looks explicitly include an outer layer; keep supplied concern tags intact.
    links = ''.join(f'<a class="guidance-link" href="{prefix}outfits/{n:02d}/?occasion=通勤">{n:02d} {esc(OUTFITS[n - 1]["name"])}{ARROW}</a>' for n in [6, 27])
    return f'<aside id="arm-guidance" class="arm-guidance" aria-label="有外搭的穿搭靈感"{" hidden" if hidden else ""}><h3>想先有袖子，從外搭開始</h3><p>這組靈感包含無袖款。若妳想先遮住手臂，也可以看看這兩套有外搭的通勤穿搭。</p>{links}</aside>'


def home():
    body = header(home=True) + f'''<main id="main"><section class="hero wrap" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow"><span></span>台北內湖・相伴 19 年</p><h1 id="hero-title">穿喜歡的衣服，<br>做自在的<span class="serif-accent">自己。</span></h1><p class="hero-description">每一件，都是阿蓁用心挑選。<br>從日常到假日，找到妳喜歡的穿搭。</p><a class="primary-button" href="#collection">看看 27 套穿搭{ARROW}</a><p class="hero-note">韓版服飾・用心選品・店面試穿</p></div><div class="hero-visual" aria-label="阿蓁精選穿搭"><div class="hero-photo hero-photo-main">{image(OUTFITS[6], extra='(max-width: 600px) 44vw, 300px', eager=True)}<span>清爽日常</span></div><div class="hero-photo hero-photo-second">{image(OUTFITS[22], extra='(max-width: 600px) 36vw, 240px', eager=True)}<span>溫柔色調</span></div><div class="hero-caption">把喜歡，穿成日常。<span>阿蓁の穿搭筆記</span></div></div></section>
    <section id="collection" class="collection" aria-labelledby="collection-title"><div class="wrap collection-heading"><div><p class="eyebrow">阿蓁の穿搭提案</p><h2 id="collection-title">今天，想怎麼穿？</h2></div><p class="collection-help">依場合、依困擾，慢慢挑。</p></div><div class="filter-bar"><div class="wrap">{filters('occasion', '想穿去哪', OCCASIONS)}{filters('concern', '在意什麼', CONCERNS)}<div class="results-line"><p id="result-count" tabindex="-1" role="status" aria-live="polite" aria-atomic="true">共 <strong>27</strong> 套穿搭</p><button id="clear-filters" class="text-button" type="button" hidden>清除篩選 ×</button></div></div></div><div class="wrap collection-results">{arm_guidance(hidden=True)}<div class="outfit-grid" id="outfit-grid">{''.join(card(o, eager=i < 2) for i, o in enumerate(OUTFITS))}</div><div id="empty-state" class="empty-state" hidden><span aria-hidden="true">✧</span><h3>這個組合暫時沒有穿搭</h3><p>目前沒有同時符合這兩個條件的穿搭。可以先保留一個條件，繼續找靈感。</p><div id="empty-alternatives" class="empty-alternatives"></div><button type="button" class="primary-button" id="empty-reset">看看全部穿搭{ARROW}</button></div><p class="collection-end" id="collection-end">慢慢看，找到喜歡的，再來聊聊。<span>喜歡哪一套？私訊詢問就好。</span></p></div></section>
    <section id="about" class="about-section"><div class="wrap about-layout"><div><p class="eyebrow">關於阿蓁</p><h2>19 年的熟悉，<br>從一件衣服開始。</h2><span class="about-signature">阿蓁の衣舖子</span></div><div class="about-copy"><p>{SHOP['intro']}</p><a class="text-link" href="{SHOP['instagram']}" target="_blank" rel="noopener noreferrer">到 Instagram 和阿蓁聊聊{ARROW}</a></div></div></section></main>''' + footer()
    (OUT / 'index.html').write_text(shell('阿蓁の衣舖子｜找到妳喜歡的日常穿搭', '台北內湖，阿蓁の衣舖子相伴 19 年。27 套用心挑選的穿搭，依場合與穿搭困擾找靈感，喜歡就到 Instagram 私訊詢問。', body))


def inquiry(outfit):
    number = outfit['id']
    message = f'阿蓁您好，我想詢問第 {number:02d} 套：{outfit["name"]}\n{SITE}outfits/{number:02d}/'
    return f'''<div class="detail-action" id="inquiry"><p>喜歡這一套？先複製資訊，再到 Instagram 貼上詢問。</p>
    <label class="inquiry-label" for="inquiry-message">這一套的詢問內容</label><textarea id="inquiry-message" class="inquiry-message" rows="4" readonly>{esc(message)}</textarea>
    <button class="copy-inquiry" type="button" hidden>複製穿搭資訊</button><p id="copy-status" class="copy-status" role="status" aria-live="polite"></p>
    <a class="primary-button inquiry-button" href="https://ig.me/m/azhen_2026" aria-label="私訊問價，開啟與 @azhen_2026 的 Instagram 對話">{IG}私訊問價{ARROW}</a>
    <p class="inquiry-note">需要登入 Instagram 才能傳送訊息。<br>未開啟對話？<a href="{SHOP['instagram']}" target="_blank" rel="noopener noreferrer">開啟 @azhen_2026 個人檔案（另開分頁）</a>，再點「發送訊息」。<br>若仍無法開啟，請用右上角選單改用外部瀏覽器，或在 Instagram 搜尋 @azhen_2026。<br>資訊不會自動傳送，請貼上後再送出。</p></div>'''


def detail(outfit):
    n = outfit['id']
    prefix = '../../'
    hook, sep, rest = outfit['copy'].partition('。')
    hook += sep
    tags = ''.join(f'<span>{esc(tag)}</span>' for tag in outfit['occasions'] + outfit['concerns'])
    following = [OUTFITS[(n + offset) % len(OUTFITS)] for offset in range(3)]
    guidance = arm_guidance(prefix) if '手臂粗不敢穿無袖' in outfit['concerns'] else ''
    body = header(prefix) + f'''<main id="main"><div class="wrap"><div class="detail-navigation"><a class="back-link" data-back-link href="../../#collection">← 回到穿搭型錄</a><a class="back-link" href="#inquiry">私訊問這套 ↓</a></div><section class="detail-layout" aria-labelledby="outfit-title"><div class="detail-photo">{image(outfit, prefix, '(max-width: 700px) 100vw, 55vw', eager=True)}</div><div class="detail-copy"><p class="eyebrow">阿蓁の穿搭提案 <span class="outfit-no">{n:02d} / 27</span></p><h1 id="outfit-title">{esc(outfit['name'])}</h1><div class="detail-tags">{tags}</div>{guidance}<div class="outfit-description"><h2>{esc(hook)}</h2><p>{esc(rest)}</p></div>{inquiry(outfit)}<p class="detail-disclosure">{SHOP['disclosure']}</p></div></section><section class="related-section" aria-labelledby="related-title"><div class="related-heading"><h2 id="related-title">再看看其他穿搭</h2><a class="text-link" data-back-link href="../../#collection">全部穿搭{ARROW}</a></div><div class="outfit-grid related-grid">{''.join(card(o, prefix) for o in following)}</div></section></div></main>''' + footer(prefix)
    dest = OUT / f'outfits/{n:02d}'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'index.html').write_text(shell(outfit['name'] + '｜阿蓁の衣舖子', outfit['copy'], body, prefix, f'outfits/{n:02d}/', True, f'assets/share-{n:02d}.jpg'))


def build():
    OUT.mkdir(exist_ok=True)
    for file in ['style.css', 'app.js']:
        shutil.copyfile(ROOT / 'src' / file, OUT / file)
    (OUT / '.nojekyll').write_text('')
    (OUT / 'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#6d6648"/><text x="32" y="46" fill="#fff" font-family="serif" font-size="42" text-anchor="middle">蓁</text></svg>')
    home()
    for outfit in OUTFITS:
        detail(outfit)
    error = header('/azhen-lookbook/') + '<main id="main" class="wrap not-found"><p class="eyebrow">阿蓁の衣舖子</p><h1>這一頁暫時找不到</h1><p>回到型錄，繼續看看喜歡的穿搭。</p><a class="primary-button" href="/azhen-lookbook/">回到穿搭型錄 →</a></main>' + footer('/azhen-lookbook/')
    (OUT / '404.html').write_text(shell('找不到頁面｜阿蓁の衣舖子', '回到阿蓁的穿搭型錄', error, prefix='/azhen-lookbook/'))
    urls = [SITE] + [f'{SITE}outfits/{o["id"]:02d}/' for o in OUTFITS]
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>')
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + SITE + 'sitemap.xml\n')
    print(f'Built the homepage and {len(OUTFITS)} outfit pages into docs/.')


if __name__ == '__main__':
    build()
