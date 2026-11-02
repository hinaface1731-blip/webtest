"""Превращает HTML старого сайта (data/pages.json) в чистые фрагменты (data/content.json).

Старые страницы свёрстаны таблицами, а описания приборов вставлены из Word
со стилями mso-*. Здесь оставляем только смысловую разметку: заголовки,
абзацы, списки, таблицы, изображения и ссылки.
"""
import json
import os
import re
import urllib.parse

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
IMG_DIR = os.path.join(HERE, 'static', 'img')

KEEP = {'p', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
        'img', 'a', 'strong', 'em', 'br', 'sub', 'sup', 'iframe'}
RENAME = {'b': 'strong', 'i': 'em', 'h1': 'h2', 'h5': 'h4', 'h6': 'h4'}
DROP = {'script', 'style', 'head', 'meta', 'link', 'title', 'form', 'input', 'noscript', 'xml', 'object'}

# id старой страницы -> slug новой
SLUGS = {
    1: 'index', 2: 'company', 3: 'contacts', 7: 'company', 76: 'company', 59: 'certificates',
    49: 'registrators', 51: 'catalog', 55: 'electric', 57: 'perforation', 58: 'video',
    52: 'geofit-1003', 53: 'geofit-1108', 77: 'depth-system', 89: 'bktp-m2', 90: 'dig',
    81: 'kp-51e', 82: 'kp-52e', 83: 'kp-61e', 79: 'kp-71egtr', 80: 'kp-82bkr', 84: 'kp-81eg',
    85: 'kp-91eg', 86: 'kp-242eg', 78: 'zk-01msk', 91: 'kp-71egrtvp-02',
    92: 'kp-240gtr', 93: 'kp-241gtrl', 87: 'kp-511vk', 64: 'kp-512vk', 88: 'kp-410vk',
}


def local_img(src):
    name = os.path.basename(urllib.parse.unquote(src.split('?')[0]))
    return name if os.path.exists(os.path.join(IMG_DIR, name)) else None


def rewrite_href(href):
    m = re.search(r'module=mod_content&(?:amp;)?id=(\d+)', href)
    if m:
        return SLUGS.get(int(m.group(1)), 'catalog') + '.html'
    if 'mod_news' in href:
        return 'news.html'
    if 'mod_customer' in href:
        return 'clients.html'
    if href.startswith('http') and 'asu-expert.ru' not in href:
        return href.rstrip('[')
    return None


def is_bullet_para(p):
    style = p.get('style', '') or ''
    return 'mso-list' in style


def clean(fragment):
    # Условные комментарии Word (<![if !vml]>) BeautifulSoup не понимает — убираем заранее
    fragment = re.sub(r'<!\[(?:if|endif)[^>]*\]>', '', fragment)
    fragment = re.sub(r'(?s)<!--\[if.*?<!\[endif\]-->', '', fragment)
    soup = BeautifulSoup(fragment, 'lxml')
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(list(DROP)):
        t.decompose()
    # служебные маркеры списков Word (буллеты Wingdings)
    for s in soup.find_all('span', style=re.compile(r'mso-list:\s*Ignore')):
        s.decompose()
    for t in soup.find_all(re.compile(r'^(o|v|w|m|st1):')):
        t.unwrap()

    # вложенные <b><b>…</b></b>
    for b in soup.find_all(['b', 'strong']):
        for inner in b.find_all(['b', 'strong']):
            inner.unwrap()

    # абзацы-буллеты Word -> <ul><li> (по стилю mso-list или по символу «·» в начале)
    for p in soup.find_all('p'):
        first = p.get_text()[:3].strip()
        if first.startswith(('·', '•', '§')):
            for s in p.find_all(string=True):
                if s.strip():
                    s.replace_with(re.sub(r'^\s*[·•§]\s*', '', s))
                    break
            p['style'] = 'mso-list'
        if is_bullet_para(p) and p.parent is not None:
            p.name = 'li'
            p['data-bullet'] = '1'

    # переименование и чистка атрибутов
    for t in list(soup.find_all(True)):
        if t.name in RENAME:
            t.name = RENAME[t.name]
        if t.name == 'u':
            t.name = 'strong'
        if t.name not in KEEP:
            t.unwrap()
            continue
        attrs = {}
        if t.name == 'img':
            name = local_img(t.get('src', ''))
            if not name:
                t.decompose()
                continue
            attrs = {'src': 'img/' + name, 'alt': t.get('alt', ''), 'loading': 'lazy'}
        elif t.name == 'a':
            href = rewrite_href(t.get('href', ''))
            if not href:
                t.unwrap()
                continue
            attrs = {'href': href}
            if href.startswith('http'):
                attrs.update(target='_blank', rel='noopener')
        elif t.name in ('td', 'th'):
            for k in ('colspan', 'rowspan'):
                if t.get(k) and t.get(k) != '1':
                    attrs[k] = t.get(k)
        elif t.name == 'iframe':
            attrs = {'src': t.get('src', ''), 'loading': 'lazy', 'allowfullscreen': ''}
        elif t.name == 'li' and t.get('data-bullet'):
            attrs = {'data-bullet': '1'}
        t.attrs = attrs

    for b in soup.find_all('strong'):
        for inner in b.find_all('strong'):
            inner.unwrap()

    # соседние li-буллеты собираем в <ul>
    for li in soup.find_all('li', attrs={'data-bullet': '1'}):
        if li.parent is None or li.parent.name == 'ul':
            continue
        ul = soup.new_tag('ul')
        li.insert_before(ul)
        node = li
        while node is not None and isinstance(node, Tag) and node.name == 'li' and node.get('data-bullet'):
            nxt = node.next_sibling
            while nxt is not None and isinstance(nxt, NavigableString) and not nxt.strip():
                nxt = nxt.next_sibling
            ul.append(node.extract())
            node = nxt
    for li in soup.find_all('li'):
        li.attrs.pop('data-bullet', None)
    # одиночные li без списка
    for li in soup.find_all('li'):
        if li.parent.name not in ('ul', 'ol'):
            li.name = 'p'

    # абзац из одного жирного короткого текста -> подзаголовок
    for p in soup.find_all('p'):
        txt = p.get_text(' ', strip=True)
        kids = [k for k in p.children if not (isinstance(k, NavigableString) and not k.strip())]
        if txt and len(txt) < 90 and len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name == 'strong' \
                and not p.find('img') and p.find_parent('table') is None:
            p.name = 'h3'
            p.clear()
            p.string = txt.rstrip(':')

    # пустые абзацы и ячейки-распорки
    for t in soup.find_all(['p', 'h3', 'h4', 'strong', 'em', 'li']):
        if not t.get_text(strip=True).replace('\xa0', '') and not t.find(['img', 'iframe']):
            t.decompose()
    # вложенные таблицы-обёртки старой вёрстки: таблица из одной ячейки
    for tb in soup.find_all('table'):
        cells = tb.find_all(['td', 'th'])
        if len(cells) == 1:
            tb.replace_with(*list(cells[0].contents)) if cells[0].contents else tb.decompose()
    for tb in soup.find_all('table'):
        if tb.parent and not (tb.parent.name == 'div'):
            wrap = soup.new_tag('div', attrs={'class': 'table-wrap'})
            tb.wrap(wrap)
    # таблицы-раскладки картинок (без текста) — превращаем в галерею
    for wrap in soup.find_all('div', class_='table-wrap'):
        tb = wrap.find('table')
        if tb and tb.find('img') and len(tb.get_text(strip=True)) < 40:
            g = soup.new_tag('div', attrs={'class': 'doc-gallery'})
            for im in tb.find_all('img'):
                g.append(im.extract())
            wrap.replace_with(g)

    body = soup.body or soup
    html = ''.join(str(c) for c in body.contents)
    html = re.sub(r'(\s*<br/?>\s*){2,}', '<br/>', html)
    html = re.sub(r'[ \t\r\f\v]+', ' ', html)
    html = re.sub(r'\n\s*\n+', '\n', html)
    html = html.replace('\xa0', ' ')
    html = re.sub(r'<strong>\s*_+\s*([^<_]+?)\s*_+\s*</strong>', lambda m: '<h3>' + m.group(1).capitalize() + '</h3>', html)
    # отдельная строка из жирного текста между переносами -> подзаголовок
    html = re.sub(r'(^|<br/>|\n|</ul>|</p>)\s*<strong>\s*([^<]{2,90}?)\s*:?\s*</strong>\s*(?=<br/>|\n|<ul>|<img)',
                  lambda m: m.group(1) + '<h3>' + m.group(2).strip().rstrip(':') + '</h3>', html)
    html = re.sub(r'<h3>([^<]*)</h3>\s*<br/>', r'<h3>\1</h3>', html)
    html = re.sub(r'</ul>\s*<br/>', '</ul>', html)
    html = re.sub(r'(<img [^>]*/>)\s*<br/>', r'\1', html)
    return html.strip()


def middle(page_html):
    a = page_html.find('<!-- CONTENT MIDDLE  -->')
    b = page_html.find('<!-- END CONTENT MIDDLE  -->')
    mid = page_html[a:b]
    soup = BeautifulSoup(mid, 'lxml')
    h = soup.find('h3')
    title = h.get_text(' ', strip=True) if h else ''
    cell = soup.select_one('table.c_mid td table td')
    inner = cell.decode_contents() if cell else mid
    return title, inner


def summary_of(text):
    text = re.sub(r'\s+', ' ', text)
    m = re.search(r'([^.]*предназнач[^.]*\.)', text)
    if m:
        s = m.group(1).strip()
        s = re.sub(r'^.*?(Прибор|Скважинн|Комплексн|Каротажн|Система|Блок|ДИГ|Датчик)', r'\1', s, count=1)
        return s[:260] + ('…' if len(s) > 260 else '')
    return text[:220]


def main():
    pages = json.load(open(os.path.join(DATA, 'pages.json'), encoding='utf-8'))
    out = {}
    for url, v in pages.items():
        m = re.search(r'module=mod_content&id=(\d+)$', url)
        if not m or 'html' not in v:
            continue
        pid = int(m.group(1))
        title, inner = middle(v['html'])
        html = clean(inner)
        text = BeautifulSoup(html, 'lxml').get_text(' ', strip=True)
        imgs = re.findall(r'src="img/([^"]+)"', html)
        out[pid] = {'title': title, 'html': html, 'images': imgs, 'summary': summary_of(text),
                    'slug': SLUGS.get(pid)}
    json.dump(out, open(os.path.join(DATA, 'content.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    for pid, v in sorted(out.items()):
        print(pid, v['slug'], v['title'][:40], len(v['html']), v['images'][:4])


if __name__ == '__main__':
    main()
