"""Собирает статический сайт ООО «АСУ-ЭКСПЕРТ» в папку ../site.

    python3 src/extract.py   # один раз: чистит HTML старого сайта -> data/content.json
    python3 src/build.py     # генерирует страницы

Никаких зависимостей кроме стандартной библиотеки.
"""
import html
import json
import os
import re
import shutil
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'site'))
DATA = os.path.join(HERE, 'data')

CONTENT = {int(k): v for k, v in json.load(open(os.path.join(DATA, 'content.json'), encoding='utf-8')).items()}
NEWS_RAW = json.load(open(os.path.join(DATA, 'news.json'), encoding='utf-8'))

YEAR = date.today().year
PHONE = '+7 (3822) 99-33-03'
PHONE_HREF = '+73822993303'
FAX = '(3822) 52-37-02'
EMAIL = 'info@asu-expert.ru'
ADDRESS = '634041, г. Томск, ул. Красноармейская, 92/1, офис 010'
ADDRESS_NOTE = 'Цокольный этаж, вход слева со стороны ул. Красноармейской'

e = html.escape

# ---------------------------------------------------------------- каталог

CATEGORIES = [
    {
        'slug': 'registrators', 'id': 49, 'num': '01',
        'title': 'Регистрирующая аппаратура',
        'short': 'Регистраторы',
        'lead': 'Каротажные лаборатории, регистраторы и система глубины: запись, калибровка и обработка данных ГИС в реальном времени.',
        'img': 'ba03a947ccb50c6f471ee1153a7d5dd1.JPG',
        'products': ['geofit-1003', 'geofit-1108', 'depth-system', 'bktp-m2', 'dig'],
    },
    {
        'slug': 'electric', 'id': 55, 'num': '02',
        'title': 'Электрический и комплексный каротаж',
        'short': 'Электрокаротаж',
        'lead': 'Приборы для каротажа рудных и водяных скважин: все измерения за один спуско-подъём, цифровая передача по одножильному кабелю.',
        'img': 'a5e6a9fbcf6c0f5f048e1b099a5400df.jpg',
        'products': ['kp-51e', 'kp-52e', 'kp-61e', 'kp-71egtr', 'kp-71egrtvp-02', 'kp-81eg', 'kp-91eg',
                     'kp-82bkr', 'kp-242eg', 'zk-01msk'],
    },
    {
        'slug': 'perforation', 'id': 57, 'num': '03',
        'title': 'Контроль перфорации и муфтовых соединений',
        'short': 'Перфорация и муфты',
        'lead': 'Прихватоопределители, шаблоны и локаторы муфт, приборы комплексного каротажа для обсаженных скважин.',
        'img': '2bbef266a794dccf60c566aa9d65bf59.jpg',
        'products': ['kp-240gtr', 'kp-241gtrl'],
    },
    {
        'slug': 'video', 'id': 58, 'num': '04',
        'title': 'Видеокаротаж и телеинспекция',
        'short': 'Видеокаротаж',
        'lead': 'Визуальный контроль эксплуатационных колонн, фильтров и забоя: видеосъёмка через одножильный кабель длиной до 4000 м.',
        'img': '4c1cf32543c2215e1acea458a562dfb7.jpg',
        'products': ['kp-410vk', 'kp-511vk', 'kp-512vk'],
    },
]

PRODUCTS = {
    'geofit-1003': dict(id=52, name='ГЕОФИТ 1003', kind='Каротажная лаборатория',
                        tag='Полный комплекс ГИС при строительстве и эксплуатации нефтяных и газовых скважин, задачи рудной и гидрогеологии.',
                        img='ba03a947ccb50c6f471ee1153a7d5dd1.JPG', chips=['ЕАЭС', 'Реальное время', 'Архивация ГИС']),
    'geofit-1108': dict(id=53, name='ГЕОФИТ 1108', kind='Каротажный регистратор',
                        tag='Геофизические и гидродинамические исследования при контроле за разработкой месторождений и перфорации.',
                        img='f5200091078762563d2779ae3fe599b4.png', chips=['Контроль разработки', 'Перфорация']),
    'depth-system': dict(id=77, name='Система глубины', kind='ГЕОФИТ',
                         tag='Глубина, скорость, натяжение и магнитные метки кабеля — совместно с любым каротажным регистратором.',
                         img='fb8703be4f6ba354f76544f88bdce1a8.jpg', chips=['1- и 3-жильный кабель', 'ЕАЭС']),
    'bktp-m2': dict(id=89, name='БКТП-М2', kind='Блок контроля технологических параметров',
                    tag='Измерение глубины, скорости, натяжения и считывание магнитных меток с любыми датчиками.',
                    img='a490ac4775be5fe49136d0843b0c9c76.png', chips=['Глубина', 'Натяжение', 'Метки']),
    'dig': dict(id=90, name='ДИГ', kind='Датчик импульсов глубины',
                tag='Преобразует вращение мерного ролика в сигналы о глубине и направлении движения скважинного прибора.',
                img='49d035b264bdd6019296257654f46cc3.png', chips=['ТФЖК 3.352.001']),
    'kp-51e': dict(id=81, name='КП-51Э', kind='Прибор электрического каротажа',
                   tag='Градиент- и потенциал-зонд, ПС за один спуско-подъём, цифровая передача по одножильному кабелю.',
                   img='b5146403a26ba40ad42e262bfd244cf9.jpg', chips=['Ø 48 мм', '−40…+80 °C', '20 МПа', '1 жила']),
    'kp-52e': dict(id=82, name='КП-52Э', kind='Серия приборов электрического каротажа',
                   tag='Боковое каротажное зондирование (БКЗ) с классическим кабель-зондом, методы КС и ПС.',
                   img='a01d62855903586eb626afe6025ed376.jpg', chips=['БКЗ', 'КС', 'ПС', '+80 °C']),
    'kp-61e': dict(id=83, name='КП-61ЭРТ', kind='Прибор электрического каротажа',
                   tag='КС, ПС, проводимость и температура скважинной жидкости за один спуско-подъём.',
                   img='663221f46d5f09bca79c33addc921f8a.png', chips=['КС', 'ПС', 'Резистивиметр', 'Термометр']),
    'kp-71egtr': dict(id=79, name='КП-71ЭГРТ', kind='Прибор электрического каротажа',
                      tag='Электрический и гамма-каротаж, резистивиметрия и термометрия в скважинах с промывочной жидкостью 0,03…10 Ом·м.',
                      img='a63c9a728a4af8dfa6b9517ae8ccfb71.jpg', chips=['КС', 'ГК', 'Резистивиметр', 'Термометр']),
    'kp-71egrtvp-02': dict(id=91, name='КП-71ЭГРТВП-02', kind='Прибор электрического каротажа',
                           tag='БКЗ и вызванная поляризация (ВП) потенциал-зондом за один спуско-подъём.',
                           img='7d620425ff54ff07f14ee19b2b815a4e.jpg', chips=['БКЗ', 'ВП', 'ГК']),
    'kp-81eg': dict(id=84, name='КП-81ЭГ', kind='Прибор электрического и гамма-каротажа',
                    tag='БКЗ градиент- и потенциал-зондом, ПС и ПС2, естественное гамма-излучение двумя зондами.',
                    img='84a3b8659d8d115245dd07c4a1ab56c4.jpg', chips=['БКЗ', 'ПС', '2 × ГК']),
    'kp-91eg': dict(id=85, name='КП-91ЭГ', kind='Прибор электрического каротажа',
                    tag='КС, гамма-каротаж и ПС2 относительно головки кабеля, цифровая передача по одножильному кабелю.',
                    img='84a3b8659d8d115245dd07c4a1ab56c4.jpg', chips=['КС', 'ГК', 'ПС']),
    'kp-82bkr': dict(id=80, name='КП-82БКР', kind='Прибор бокового и радиоактивного каротажа',
                     tag='Трёхэлектродный боковой каротаж и гамма-каротаж одновременно — современный аналог БКР-3М.',
                     img='3f6d975a08de5a1c338f63ba2f1b0082.jpg', chips=['БК', 'ГК', 'ГГК']),
    'kp-242eg': dict(id=86, name='КП-242ЭГ', kind='Комплексный скважинный прибор',
                     tag='Гамма-каротаж и токовый каротаж, работа через трёхжильный бронированный кабель.',
                     img='df88800c148d5b9799b5883361061bae.png', chips=['ГК', 'Токовый каротаж', '+80 °C']),
    'zk-01msk': dict(id=78, name='ЗК-01МСК', kind='Зонд каротажный МСК, МЭП и ПС',
                     tag='Скважинная электроразведка при поисках, оценке и разведке рудных месторождений.',
                     img='06be02f767da1252dbb0795a961c970b.jpg', chips=['МСК', 'МЭП', 'ПС']),
    'kp-240gtr': dict(id=92, name='КП-240ГТР', kind='Прибор комплексного каротажа',
                      tag='Гамма-излучение, удельное сопротивление и температура скважинной жидкости, телесистема «Манчестер-2».',
                      img='2bbef266a794dccf60c566aa9d65bf59.jpg', chips=['ГК', 'Резистивиметр', 'Термометр']),
    'kp-241gtrl': dict(id=93, name='КП-241ГТРЛ', kind='Прибор комплексного каротажа',
                       tag='Четыре параметра за спуско-подъём: ГК, сопротивление, температура и локация муфт.',
                       img='2bbef266a794dccf60c566aa9d65bf59.jpg', chips=['ГК', 'Термометр', 'Локатор муфт']),
    'kp-410vk': dict(id=88, name='КП-410ВК2', kind='Прибор визуального контроля скважин',
                     tag='Видеосъёмка эксплуатационных колонн и фильтров вне зависимости от характеристик кабеля.',
                     img='dd109cd8d4388bff73d27966f219675d.gif', chips=['До 4000 м', '200 м/ч', '90 кд']),
    'kp-511vk': dict(id=87, name='КП-511ВК', kind='Прибор визуального контроля скважин',
                     tag='Визуальный контроль колонн, фильтров нагнетательных скважин и области забоя.',
                     img='11cc76ae2f1ca090471f399fd0474304.jpg', chips=['Видеокаротаж', 'Забой']),
    'kp-512vk': dict(id=64, name='КП-512ВК', kind='Прибор визуального контроля скважин',
                     tag='Фронтальная или боковая видеосъёмка ствола скважины.',
                     img='4c1cf32543c2215e1acea458a562dfb7.jpg', chips=['Фронтальная', 'Боковая съёмка']),
}
for c in CATEGORIES:
    for s in c['products']:
        PRODUCTS[s]['cat'] = c

# кадры, снятые нашими приборами видеокаротажа
WELL_FRAMES = ['ba951de225f5685b2383ecc0fe64f6ce.png', '04f973d653cbdf4ce1fdd0f4dc83f97d.png', '8cf62954d33382af36615d80acf99e5a.png', 'ac3b945362e7589de11262d1c85dbe9e.png',
               '0f3b99fe24253df7782f19dee6f46f71.jpg', 'b8492c59dc7778bcf6763a5cbd29d5f4.gif',
               '11cc76ae2f1ca090471f399fd0474304.jpg', 'bca970c31d2f1830a36c48f5e870e577.png',
               '965c49e3b0650be2c92607c413f72dce.jpg', 'c76a382cc5c804c32361ad1989775b7c.jpg',
               '552c5fe26b8489434e3c5ae4ec1a5123.jpg', 'ece9d6f5ed2f47f7c2b90d7d3b8c2748.jpg']

VIDEOS = [
    ('https://www.youtube.com/watch?v=0_UAwwtG09w', 'Фильтры нагнетательной скважины', 'Площадка АО «Хиагда»'),
    ('https://www.youtube.com/watch?v=pIQr3gBgCY8', 'Аварийная метановая газовая скважина', 'г. Ленинск-Кузнецкий'),
    ('https://youtu.be/mhYapXPIiHE', 'Аварийная скважина', 'г. Железногорск'),
]

CLIENTS = [
    ('НПЦ по геологии', 'Республика Беларусь, г. Минск'),
    ('АО «КузбассРазрезУголь»', 'г. Кемерово'),
    ('АО «Сибирский химический комбинат»', 'г. Северск'),
    ('АО «Сибирское ПГО»', 'г. Красноярск'),
    ('АО «Узбекгеологоразведка»', 'Республика Узбекистан, г. Ташкент'),
    ('АО «Узеньпромгеофизика»', 'Республика Казахстан, г. Жанаозень'),
    ('АО «Хиагда»', 'г. Чита'),
    ('ГБУ «Мосгоргеотрест»', 'г. Москва'),
    ('МП «Томскводоканал»', 'г. Томск'),
    ('ООО «Бурсиб-Н»', 'г. Новосибирск'),
    ('ООО «Велко»', 'г. Москва'),
    ('ООО «Газпромнефть НоябрьскНефтегазГеофизика»', 'г. Ноябрьск'),
    ('ООО «Геомайн»', 'г. Кемерово'),
    ('ООО «Ленинск-Кузнецкая геофизическая партия»', 'г. Ленинск-Кузнецкий'),
    ('ООО «Октябрьский завод каротажного оборудования» ВНИИГИС', 'г. Октябрьский'),
    ('ООО «Распадская угольная компания»', 'г. Новокузнецк'),
    ('ООО «Техногео»', 'Скважинные приборы электрического каротажа'),
    ('ООО «Юганскнефтегазгеофизика»', 'г. Нефтеюганск'),
    ('ООО «Южно-Кузбасское ГРУ»', 'г. Новокузнецк'),
    ('ТОО «Акпан»', 'Республика Казахстан, г. Актобе'),
    ('ФГУП «ГидроСпецГеология»', 'г. Москва'),
    ('ФГУП «НО РАО», Железногорский филиал', 'г. Железногорск'),
]


def clean_news():
    out, seen = [], set()
    for n in NEWS_RAW:
        t = n['text']
        t = re.split(r'\s*<<\s*В начало', t)[0]
        t = re.split(r'\s+\d{1,2} [А-Яа-я]+ -1\b', t)[0]
        t = re.sub(r'\s+', ' ', t).strip(' "')
        if not t or (n['iso'], t) in seen:
            continue
        seen.add((n['iso'], t))
        out.append({'iso': n['iso'], 'date': n['date'], 'text': t, 'year': n['iso'][:4]})
    return out


NEWS = clean_news()

# ---------------------------------------------------------------- шаблон

LOGO = '''<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true">
<rect width="48" height="48" rx="11" class="lm-bg"/>
<text x="7" y="23" class="lm-e">E</text><text x="17" y="38" class="lm-pert">PERT</text>
<path d="M10 39 L29 12 L27 22 L39 5 L22 31 L24 21 Z" class="lm-bolt"/></svg>'''


def nav_html(active):
    items = [('catalog', 'Каталог'), ('company', 'О компании'), ('clients', 'Заказчики'),
             ('news', 'Новости'), ('certificates', 'Сертификаты'), ('contacts', 'Контакты')]
    mega = ''.join(
        f'''<div class="mega-col"><a class="mega-cat" href="{c['slug']}.html"><span class="mono">{c['num']}</span>{e(c['title'])}</a>
<ul>{''.join(f'<li><a href="{s}.html">{e(PRODUCTS[s]["name"])}</a></li>' for s in c['products'])}</ul></div>'''
        for c in CATEGORIES)
    links = []
    for slug, label in items:
        cls = ' class="is-active"' if slug == active else ''
        if slug == 'catalog':
            links.append(f'''<li class="has-mega"><a href="catalog.html"{cls}>{label}<svg viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4"/></svg></a>
<div class="mega"><div class="mega-inner">{mega}</div></div></li>''')
        else:
            links.append(f'<li><a href="{slug}.html"{cls}>{label}</a></li>')
    return ''.join(links)


def page(slug, title, body, desc='', active=None, extra_head='', extra_js=''):
    full_title = 'ООО «АСУ-ЭКСПЕРТ» — геофизические приборы' if slug == 'index' else f'{title} — АСУ-ЭКСПЕРТ'
    desc = desc or 'Научно-производственное предприятие ООО «АСУ-ЭКСПЕРТ», Томск: скважинные геофизические приборы, каротажные лаборатории, регистраторы и видеокаротаж.'
    mobile_cats = ''.join(f'<a href="{c["slug"]}.html">{e(c["short"])}</a>' for c in CATEGORIES)
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#05080d">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/main.css">
<script>document.documentElement.classList.add('js')</script>
{extra_head}
</head>
<body class="page-{slug}">
<a class="skip" href="#main">К содержимому</a>
<header class="hdr" id="hdr">
  <div class="hdr-in">
    <a class="logo" href="index.html" aria-label="АСУ-ЭКСПЕРТ — на главную">{LOGO}<span class="logo-txt"><b>АСУ-ЭКСПЕРТ</b><small>научно-производственное предприятие</small></span></a>
    <nav class="nav" aria-label="Основное меню"><ul>{nav_html(active)}</ul></nav>
    <a class="hdr-phone mono" href="tel:{PHONE_HREF}">{PHONE}</a>
    <a class="btn btn-sm btn-red hdr-cta" href="contacts.html#request">Запросить КП</a>
    <button class="burger" id="burger" aria-label="Открыть меню" aria-expanded="false" aria-controls="mnav"><span></span><span></span></button>
  </div>
</header>
<div class="mnav" id="mnav" hidden>
  <nav class="mnav-in" aria-label="Мобильное меню">
    <p class="mono mnav-lbl">Каталог</p>
    <div class="mnav-cats">{mobile_cats}</div>
    <p class="mono mnav-lbl">Компания</p>
    <a href="company.html">О компании</a><a href="clients.html">Заказчики</a><a href="news.html">Новости</a>
    <a href="certificates.html">Сертификаты и отзывы</a><a href="contacts.html">Контакты</a>
    <div class="mnav-contacts"><a class="mono" href="tel:{PHONE_HREF}">{PHONE}</a><a class="mono" href="mailto:{EMAIL}">{EMAIL}</a></div>
  </nav>
</div>
<aside class="gauge" aria-hidden="true">
  <span class="gauge-lbl mono">ГЛУБИНА</span>
  <div class="gauge-track"><div class="gauge-ticks"></div><div class="gauge-probe"></div></div>
  <span class="gauge-val mono"><b id="depthVal">0000.0</b> м</span>
</aside>
<main id="main">
{body}
</main>
<footer class="ftr">
  <div class="wrap">
    <div class="ftr-cta">
      <p class="eyebrow mono">связь с производством</p>
      <h2 class="ftr-title">Подберём прибор под вашу скважину</h2>
      <div class="ftr-actions">
        <a class="btn btn-red" href="mailto:{EMAIL}?subject=Запрос%20с%20сайта">Написать инженеру</a>
        <a class="btn btn-ghost" href="tel:{PHONE_HREF}">{PHONE}</a>
      </div>
    </div>
    <div class="ftr-grid">
      <div class="ftr-brand">
        <a class="logo" href="index.html">{LOGO}<span class="logo-txt"><b>АСУ-ЭКСПЕРТ</b><small>научно-производственное предприятие</small></span></a>
        <p>Разработка и производство скважинных геофизических приборов и регистрирующей аппаратуры с 2009 года.</p>
      </div>
      <div><p class="mono ftr-h">Каталог</p>{''.join(f'<a href="{c["slug"]}.html">{e(c["short"])}</a>' for c in CATEGORIES)}</div>
      <div><p class="mono ftr-h">Компания</p><a href="company.html">О компании</a><a href="clients.html">Заказчики</a><a href="news.html">Новости</a><a href="certificates.html">Сертификаты</a></div>
      <div><p class="mono ftr-h">Контакты</p><a href="tel:{PHONE_HREF}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><span>{ADDRESS}</span></div>
    </div>
    <div class="ftr-bottom mono"><span>© 2009–{YEAR} ООО «АСУ-ЭКСПЕРТ»</span><span>ИНН 7017251277 · ОГРН 1097017020627</span></div>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js" defer></script>
<script src="js/main.js" defer></script>
{extra_js}
</body>
</html>
'''


def crumbs(*items):
    parts = ['<a href="index.html">Главная</a>']
    for href, label in items:
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span aria-current="page">{e(label)}</span>')
    return '<nav class="crumbs mono" aria-label="Навигация">' + '<i>/</i>'.join(parts) + '</nav>'


def product_card(slug, i=0):
    p = PRODUCTS[slug]
    chips = ''.join(f'<li>{e(c)}</li>' for c in p['chips'][:3])
    return f'''<a class="pcard reveal" href="{slug}.html" style="--i:{i}">
  <div class="pcard-img"><img src="img/{p['img']}" alt="{e(p['name'])}" loading="lazy"></div>
  <div class="pcard-body">
    <p class="pcard-kind mono">{e(p['kind'])}</p>
    <h3 class="pcard-name">{e(p['name'])}</h3>
    <p class="pcard-tag">{e(p['tag'])}</p>
    <ul class="chips">{chips}</ul>
  </div>
  <span class="pcard-go" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
</a>'''


def page_hero(eyebrow, title, lead='', crumb_html='', extra=''):
    return f'''<section class="phero">
  <canvas class="phero-log" aria-hidden="true"></canvas>
  <div class="wrap">
    {crumb_html}
    <p class="eyebrow mono">{eyebrow}</p>
    <h1 class="phero-title split">{title}</h1>
    {f'<p class="phero-lead">{lead}</p>' if lead else ''}
    {extra}
  </div>
</section>'''


def toc_from(doc_html):
    heads = re.findall(r'<h3>(.*?)</h3>', doc_html)
    if len(heads) < 2:
        return doc_html, ''
    idx = [0]

    def rep(m):
        idx[0] += 1
        return f'<h3 id="s{idx[0]}">{m.group(1)}</h3>'
    doc_html = re.sub(r'<h3>(.*?)</h3>', rep, doc_html)
    items = ''.join(f'<li><a href="#s{i + 1}">{re.sub("<[^>]+>", "", h)}</a></li>' for i, h in enumerate(heads))
    return doc_html, f'<nav class="toc"><p class="mono">Содержание</p><ol>{items}</ol></nav>'


# ---------------------------------------------------------------- страницы

def build_product(slug):
    p = PRODUCTS[slug]
    c = p['cat']
    doc = CONTENT[p['id']]['html']
    doc, toc = toc_from(doc)
    chips = ''.join(f'<li>{e(x)}</li>' for x in p['chips'])
    related = [s for s in c['products'] if s != slug][:3]
    idx = c['products'].index(slug)
    body = f'''<section class="prod-hero">
  <canvas class="phero-log" aria-hidden="true"></canvas>
  <div class="wrap prod-hero-grid">
    <div>
      {crumbs(('catalog.html', 'Каталог'), (c['slug'] + '.html', c['short']), (None, p['name']))}
      <p class="eyebrow mono">{c['num']}.{idx + 1:02d} · {e(p['kind'])}</p>
      <h1 class="prod-title split">{e(p['name'])}</h1>
      <p class="phero-lead">{e(p['tag'])}</p>
      <ul class="chips chips-lg">{chips}</ul>
      <div class="prod-actions">
        <a class="btn btn-red" href="mailto:{EMAIL}?subject={e('Запрос: ' + p['name'])}">Запросить стоимость</a>
        <a class="btn btn-ghost" href="#spec">Характеристики</a>
      </div>
    </div>
    <figure class="prod-plate reveal">
      <span class="plate-corner mono">{e(p['name'])}</span>
      <img src="img/{p['img']}" alt="{e(p['name'])}">
      <span class="plate-scan" aria-hidden="true"></span>
    </figure>
  </div>
</section>
<section class="doc-section" id="spec">
  <div class="wrap doc-grid">
    <aside class="doc-aside">
      {toc}
      <div class="ask">
        <p class="mono">Нужна консультация?</p>
        <p>Инженер подскажет комплектацию и совместимость с вашим регистратором.</p>
        <a class="btn btn-sm btn-red" href="mailto:{EMAIL}?subject={e('Вопрос по ' + p['name'])}">Задать вопрос</a>
      </div>
    </aside>
    <article class="doc reveal">
      <div class="doc-head mono"><span>ТЕХНИЧЕСКОЕ ОПИСАНИЕ</span><span>{e(p['name'])}</span></div>
      {doc}
    </article>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="sec-head"><p class="eyebrow mono">в том же разделе</p><h2 class="sec-title">{e(c['title'])}</h2>
    <a class="link-arrow" href="{c['slug']}.html">Весь раздел</a></div>
    <div class="pgrid">{''.join(product_card(s, i) for i, s in enumerate(related))}</div>
  </div>
</section>'''
    write(slug, page(slug, p['name'] + ' — ' + p['kind'], body, desc=p['tag'], active='catalog'))


def build_category(c):
    doc = CONTENT[c['id']]['html']
    doc, toc = toc_from(doc)
    cards = ''.join(product_card(s, i) for i, s in enumerate(c['products']))
    others = ''.join(
        f'<a class="catlink" href="{o["slug"]}.html"><span class="mono">{o["num"]}</span>{e(o["title"])}</a>'
        for o in CATEGORIES if o is not c)
    body = page_hero(f'{c["num"]} · раздел каталога', e(c['title']), e(c['lead']),
                     crumbs(('catalog.html', 'Каталог'), (None, c['short'])),
                     f'<p class="phero-count mono">{len(c["products"])} {plural(len(c["products"]), "модель", "модели", "моделей")} в разделе</p>')
    body += f'''<section class="section">
  <div class="wrap"><div class="pgrid">{cards}</div></div>
</section>
<section class="doc-section">
  <div class="wrap doc-grid">
    <aside class="doc-aside">{toc}<div class="catlinks"><p class="mono">Другие разделы</p>{others}</div></aside>
    <article class="doc reveal">
      <div class="doc-head mono"><span>ОБЗОР РАЗДЕЛА</span><span>{e(c['short'])}</span></div>
      {doc}
    </article>
  </div>
</section>'''
    write(c['slug'], page(c['slug'], c['title'], body, desc=c['lead'], active='catalog'))


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def build_catalog():
    blocks = ''
    for c in CATEGORIES:
        items = ''.join(f'<li><a href="{s}.html"><span>{e(PRODUCTS[s]["name"])}</span><small>{e(PRODUCTS[s]["kind"])}</small></a></li>'
                        for s in c['products'])
        blocks += f'''<article class="catblock reveal">
  <a class="catblock-media" href="{c['slug']}.html"><img src="img/{c['img']}" alt="" loading="lazy"><span class="mono">{c['num']}</span></a>
  <div class="catblock-body">
    <h2><a href="{c['slug']}.html">{e(c['title'])}</a></h2>
    <p>{e(c['lead'])}</p>
    <ul class="catblock-list">{items}</ul>
    <a class="link-arrow" href="{c['slug']}.html">Открыть раздел</a>
  </div>
</article>'''
    body = page_hero('Каталог', 'Скважинная и наземная аппаратура',
                     'Каротажные лаборатории, регистраторы, система глубины и скважинные приборы. На приборы оформлены декларации о соответствии ТР ТС / ЕАЭС.',
                     crumbs((None, 'Каталог')))
    body += f'<section class="section"><div class="wrap catblocks">{blocks}</div></section>'
    write('catalog', page('catalog', 'Каталог продукции', body, active='catalog'))


def build_company():
    req = CONTENT[2]['html']
    body = page_hero('ООО «АСУ-ЭКСПЕРТ» · Томск', 'О компании',
                     'ООО «АСУ-ЭКСПЕРТ» — научно-производственное предприятие из Томска. С 2009 года разрабатываем и выпускаем скважинные геофизические приборы и наземную регистрирующую аппаратуру.',
                     crumbs((None, 'О компании')))
    body += f'''<section class="section">
  <div class="wrap split-2">
    <div class="reveal">
      <p class="eyebrow mono">что мы делаем</p>
      <h2 class="sec-title">Разработка, производство, ремонт</h2>
      <p class="lead">Регистрирующая аппаратура поставляется с программным обеспечением ГЕОФИТ. Оно позволяет:</p>
      <ul class="ticks">
        <li>мониторинг в реальном времени и архивация данных ГИС, акустического каротажа и технологических параметров;</li>
        <li>расчёт геофизических параметров по заданным формулам;</li>
        <li>калибровка каналов измерения и корректировка глубины по магнитным меткам;</li>
        <li>оперативная оценка качества каротажа, автоматическое и ручное редактирование без изменения исходного файла.</li>
      </ul>
      <p class="company-note">Ремонт и техническое обслуживание поставленных приборов выполняем сами.</p>
    </div>
    <figure class="lab-figure reveal"><img src="img/fa5c25733eb8f5628b78791ae5e265a2.JPG" alt="Каротажная диаграмма, записанная регистратором ГЕОФИТ" loading="lazy"><figcaption class="mono">Каротажная диаграмма · ПО ГЕОФИТ</figcaption></figure>
  </div>
</section>
{stats_html()}
<section class="section">
  <div class="wrap split-2">
    <div class="reveal">
      <p class="eyebrow mono">охрана труда</p>
      <h2 class="sec-title">Специальная оценка условий труда</h2>
      <p class="lead">Результаты специальной оценки условий труда (СОУТ) на рабочих местах предприятия.</p>
    </div>
    <figure class="paper-figure reveal"><img src="img/f5149feb3befe75edadcf171a02759d7.JPG" alt="Сводная ведомость результатов СОУТ" loading="lazy"></figure>
  </div>
</section>
<section class="doc-section" id="requisites">
  <div class="wrap doc-grid">
    <aside class="doc-aside"><div class="ask"><p class="mono">Директор</p><p>Муратов Сергей Алексеевич, действует на основании устава</p><a class="btn btn-sm btn-ghost" href="contacts.html">Все контакты</a></div></aside>
    <article class="doc reveal"><div class="doc-head mono"><span>РЕКВИЗИТЫ</span><span>ООО «АСУ-ЭКСПЕРТ»</span></div>{req}</article>
  </div>
</section>'''
    write('company', page('company', 'О компании', body, active='company'))


def stats_html():
    years = YEAR - 2009
    return f'''<section class="stats">
  <div class="wrap stats-grid">
    <div class="stat reveal"><b class="count" data-to="{years}">0</b><span>лет разрабатываем и производим аппаратуру ГИС</span></div>
    <div class="stat reveal"><b class="count" data-to="{len(PRODUCTS)}">0</b><span>моделей приборов и регистраторов в каталоге</span></div>
    <div class="stat reveal"><b class="count" data-to="{len(NEWS)}" data-suffix="+">0</b><span>отгрузок, тендеров и событий в ленте новостей</span></div>
    <div class="stat reveal"><b class="count" data-to="4">0</b><span>страны поставок: Россия, Казахстан, Узбекистан, Беларусь</span></div>
  </div>
</section>'''


def build_contacts():
    body = page_hero('Томск · ул. Красноармейская, 92/1', 'Контакты',
                     'Ответим на вопросы по приборам, комплектации, ремонту и поставке.', crumbs((None, 'Контакты')))
    body += f'''<section class="section">
  <div class="wrap contact-grid">
    <div class="contact-cards">
      <a class="ccard reveal" href="tel:{PHONE_HREF}"><span class="mono">Телефон</span><b>{PHONE}</b><small>Тел./факс: {FAX}</small></a>
      <a class="ccard reveal" href="mailto:{EMAIL}"><span class="mono">E-mail</span><b>{EMAIL}</b><small>Общий адрес предприятия</small></a>
      <div class="ccard ccard-addr reveal"><span class="mono">Адрес</span><b>{ADDRESS}</b><small>{ADDRESS_NOTE}</small><a class="addr-scheme" href="img/e56ac6fcd237ee31fefe92e1e12cca1c.png" target="_blank" rel="noopener"><img src="img/e56ac6fcd237ee31fefe92e1e12cca1c.png" alt="Схема проезда к офису" loading="lazy"><span class="mono">Схема проезда ↗</span></a></div>
      <div class="people reveal">
        <div class="person"><span class="mono">Директор</span><b>Муратов Сергей Алексеевич</b><a href="mailto:MuratovSA@asu-expert.ru">MuratovSA@asu-expert.ru</a></div>
        <div class="person"><span class="mono">Зам. директора по геофизической аппаратуре</span><b>Журиков Сергей Александрович</b><a href="mailto:GurikovSA@asu-expert.ru">GurikovSA@asu-expert.ru</a></div>
      </div>
    </div>
    <div class="map reveal"><iframe src="https://yandex.ru/map-widget/v1/-/CCUuY2HrhA" title="АСУ-ЭКСПЕРТ на Яндекс Картах" loading="lazy" allowfullscreen></iframe></div>
  </div>
</section>
<section class="section" id="request">
  <div class="wrap">
    <form class="rform reveal" id="rform" novalidate>
      <div class="rform-head"><p class="eyebrow mono">запрос коммерческого предложения</p><h2 class="sec-title">Опишите задачу</h2>
      <p>Форма откроет ваш почтовый клиент с готовым письмом на {EMAIL}.</p></div>
      <label><span>Имя и организация</span><input name="name" required autocomplete="organization"></label>
      <label><span>Телефон или e-mail</span><input name="contact" required autocomplete="email"></label>
      <label class="full"><span>Прибор</span><select name="product"><option value="">Пока не знаю — нужна консультация</option>{''.join(f'<option>{e(p["name"])} — {e(p["kind"])}</option>' for p in PRODUCTS.values())}</select></label>
      <label class="full"><span>Задача: тип скважин, глубина, кабель, регистратор</span><textarea name="msg" rows="5"></textarea></label>
      <button class="btn btn-red" type="submit">Сформировать письмо</button>
    </form>
  </div>
</section>'''
    write('contacts', page('contacts', 'Контакты', body, active='contacts'))


def build_clients():
    items = ''.join(f'<li class="client reveal" style="--i:{i % 6}"><span class="mono">{i + 1:02d}</span><b>{e(n)}</b><small>{e(c)}</small></li>'
                    for i, (n, c) in enumerate(CLIENTS))
    body = page_hero('С 2009 года', 'Заказчики',
                     'Горнодобывающие и нефтесервисные компании, геологоразведка, атомная отрасль и водоканалы.',
                     crumbs((None, 'Заказчики')))
    body += f'''<section class="section"><div class="wrap">
  <div class="geo reveal"><figure class="geo-map"><img src="img/ea7df1cb27ff50326722117e778418a5.png" alt="География заказчиков на карте" loading="lazy"></figure>
  <div class="geo-text"><p class="eyebrow mono">география поставок</p><h2 class="sec-title">Россия, Казахстан, Узбекистан, Беларусь</h2>
  <p class="lead">Приборы работают на угольных разрезах Кузбасса, урановых месторождениях Забайкалья, в нефтесервисе Западной Сибири и на объектах атомной отрасли.</p></div></div>
  <ol class="clients">{items}</ol></div></section>'''
    write('clients', page('clients', 'Заказчики', body, active='clients'))


def build_news():
    years = sorted({n['year'] for n in NEWS}, reverse=True)
    chips = '<button class="ychip is-on" data-y="all">Все</button>' + ''.join(
        f'<button class="ychip" data-y="{y}">{y}</button>' for y in years)
    groups = ''
    for y in years:
        rows = ''.join(f'<li class="nrow"><time class="mono" datetime="{n["iso"]}">{e(n["date"])}</time><p>{e(n["text"])}</p></li>'
                       for n in NEWS if n['year'] == y)
        groups += f'<section class="ngroup" data-y="{y}"><h2 class="ngroup-y">{y}</h2><ol>{rows}</ol></section>'
    body = page_hero('Отгрузки · тендеры · ремонт', 'Новости',
                     f'{len(NEWS)} {plural(len(NEWS), "запись", "записи", "записей")} с 2010 года: поставки приборов, выигранные тендеры, ремонт и новые разработки.',
                     crumbs((None, 'Новости')))
    body += f'''<section class="section"><div class="wrap">
  <div class="nfilter"><input type="search" id="nsearch" placeholder="Поиск по новостям: прибор, заказчик…" aria-label="Поиск по новостям"><div class="ychips">{chips}</div></div>
  <p class="nempty" id="nempty" hidden>Ничего не найдено</p>
  <div class="ngroups">{groups}</div>
</div></section>'''
    write('news', page('news', 'Новости', body, active='news'))


def build_certificates():
    imgs = re.findall(r'src="img/([^"]+)"', CONTENT[59]['html'])
    certs, reviews = imgs[:5], imgs[5:]

    def gal(lst):
        return ''.join(f'<a class="cert reveal" href="img/{i}" data-lightbox style="--i:{k % 5}"><img src="img/{i}" alt="Документ" loading="lazy"></a>'
                       for k, i in enumerate(lst))
    body = page_hero('Документы', 'Сертификаты и отзывы',
                     'Декларации о соответствии ТР ТС / ЕАЭС и благодарственные письма заказчиков. Нажмите на документ, чтобы открыть его крупно.',
                     crumbs((None, 'Сертификаты')))
    body += f'''<section class="section"><div class="wrap">
  <div class="sec-head"><p class="eyebrow mono">декларации и сертификаты</p><h2 class="sec-title">Сертификаты</h2></div>
  <div class="certs">{gal(certs)}</div>
  <div class="sec-head" style="margin-top:clamp(56px,8vw,96px)"><p class="eyebrow mono">отзывы</p><h2 class="sec-title">Отзывы заказчиков</h2></div>
  <div class="certs">{gal(reviews)}</div>
</div></section>
<div class="lightbox" id="lightbox" hidden><button aria-label="Закрыть">×</button><img alt=""></div>'''
    write('certificates', page('certificates', 'Сертификаты и отзывы', body, active='certificates'))


def build_index():
    latest = NEWS[:6]
    ticker = ''.join(f'<span><time class="mono">{e(n["date"])}</time>{e(n["text"])}</span>' for n in NEWS[:12])
    cats = ''.join(f'''<a class="dir reveal" href="{c['slug']}.html" style="--i:{i}">
  <span class="dir-num mono">{c['num']}</span>
  <div class="dir-img"><img src="img/{c['img']}" alt="" loading="lazy"></div>
  <h3>{e(c['title'])}</h3>
  <p>{e(c['lead'])}</p>
  <span class="dir-count mono">{len(c['products'])} {plural(len(c['products']), 'модель', 'модели', 'моделей')} →</span>
</a>''' for i, c in enumerate(CATEGORIES))
    frames = ''.join(f'<figure class="frame"><img src="img/{f}" alt="Кадр видеокаротажа" loading="lazy"><figcaption class="mono">REC ● {i + 1:02d}</figcaption></figure>'
                     for i, f in enumerate(WELL_FRAMES))
    videos = ''.join(f'<a class="vid" href="{u}" target="_blank" rel="noopener"><span class="vid-play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span><b>{e(t)}</b><small class="mono">{e(s)}</small></a>'
                     for u, t, s in VIDEOS)
    news = ''.join(f'<li class="nitem reveal" style="--i:{i}"><time class="mono">{e(n["date"])}</time><p>{e(n["text"])}</p></li>'
                   for i, n in enumerate(latest))
    clients = ''.join(f'<span>{e(n)}</span>' for n, _ in CLIENTS)
    electric = ['kp-51e', 'kp-71egtr', 'kp-82bkr', 'kp-81eg']

    body = f'''<section class="hero" id="hero">
  <div class="wrap hero-grid">
    <div class="hero-in">
      <p class="eyebrow mono">Научно-производственное предприятие · Томск · с 2009 года</p>
      <h1 class="hero-title">Геофизические приборы для исследования скважин</h1>
      <p class="hero-lead">Скважинные приборы электрического, гамма- и видеокаротажа, каротажные лаборатории и регистраторы. Работаем с нефтяными, газовыми, рудными и водяными скважинами.</p>
      <div class="hero-actions">
        <a class="btn btn-red" href="catalog.html">Каталог приборов</a>
        <a class="btn btn-ghost" href="contacts.html#request">Подобрать оборудование</a>
      </div>
      <dl class="hero-facts">
        <div><dt class="mono">Кабель</dt><dd>одно- и трёхжильный</dd></div>
        <div><dt class="mono">Телеметрия</dt><dd>цифровая, «Манчестер-2»</dd></div>
        <div><dt class="mono">Документы</dt><dd>декларации ТР ТС / ЕАЭС</dd></div>
      </dl>
    </div>
    <figure class="hero-log" aria-label="Пример каротажной диаграммы: литология, ГК, КС и ПС по глубине">
      {well_log_svg()}
      <figcaption class="mono">Пример диаграммы: литология, ГК, КС, ПС</figcaption>
    </figure>
  </div>
</section>

<div class="ticker" aria-label="Последние отгрузки"><div class="ticker-track">{ticker}{ticker}</div></div>

<section class="section" id="directions">
  <div class="wrap">
    <div class="sec-head"><p class="eyebrow mono">направления</p><h2 class="sec-title split">Что мы выпускаем</h2>
    <a class="link-arrow" href="catalog.html">Весь каталог</a></div>
    <div class="dirs">{cats}</div>
  </div>
</section>

<section class="feature section">
  <div class="wrap feature-grid">
    <div class="feature-media reveal">
      <figure class="feature-photo"><img src="img/fa5c25733eb8f5628b78791ae5e265a2.JPG" alt="Каротажная диаграмма, записанная лабораторией ГЕОФИТ" loading="lazy"></figure>
      <figure class="feature-log"><img src="img/ba03a947ccb50c6f471ee1153a7d5dd1.JPG" alt="Каротажная лаборатория ГЕОФИТ 1003" loading="lazy"><figcaption class="mono">ГЕОФИТ 1003</figcaption></figure>
    </div>
    <div class="feature-text">
      <p class="eyebrow mono">регистрирующая аппаратура</p>
      <h2 class="sec-title split">Каротажная лаборатория ГЕОФИТ</h2>
      <p class="lead">Комплексные геофизические исследования нефтяных, рудных и газовых скважин — запись, калибровка и обработка в одном комплексе.</p>
      <ol class="steps">
        <li class="reveal"><b>Настройка</b>таблицы параметров скважинных приборов, макеты по видам исследований и оформление рабочего экрана</li>
        <li class="reveal"><b>Запись</b>калибровки, данные ГИС, акустического каротажа и технологических параметров в реальном времени по глубине или времени</li>
        <li class="reveal"><b>Расчёт</b>геофизические параметры по линейным и нелинейным характеристикам</li>
        <li class="reveal"><b>Контроль</b>оперативная оценка качества каротажа, правка без изменения исходного файла данных</li>
      </ol>
      <div class="feature-actions"><a class="btn btn-ghost" href="geofit-1003.html">ГЕОФИТ 1003</a><a class="btn btn-ghost" href="geofit-1108.html">ГЕОФИТ 1108</a><a class="btn btn-ghost" href="depth-system.html">Система глубины</a></div>
    </div>
  </div>
</section>

<section class="section electric">
  <div class="wrap">
    <div class="sec-head"><p class="eyebrow mono">электрический и гамма-каротаж</p><h2 class="sec-title split">Все измерения за один спуско-подъём</h2></div>
    <div class="adv">
      <div class="adv-item reveal"><span class="mono">01</span><b>Одновременно</b><p>Измерение и передача на поверхность параметров всеми зондами во всём диапазоне.</p></div>
      <div class="adv-item reveal"><span class="mono">02</span><b>Одножильный кабель</b><p>Цифровая передача данных через одножильный каротажный кабель, код «Манчестер-2».</p></div>
      <div class="adv-item reveal"><span class="mono">03</span><b>Без калибровки</b><p>Не нужна калибровка и настройка перед записью, нет наземной панели.</p></div>
      <div class="adv-item reveal"><span class="mono">04</span><b>Совместимость</b><p>Сопряжение со всеми выпускаемыми каротажными регистраторами.</p></div>
    </div>
    <div class="pgrid pgrid-4">{''.join(product_card(s, i) for i, s in enumerate(electric))}</div>
  </div>
</section>

<section class="video-sec" id="video">
  <div class="video-pin">
    <div class="wrap video-head">
      <div>
        <p class="eyebrow mono">видеокаротаж</p>
        <h2 class="sec-title split">Видеозапись состояния колонн и фильтров</h2>
      </div>
      <ul class="defects">
        <li>смятие труб, трещины в колонне</li><li>отсутствие сальника между колоннами</li><li>деформация надфильтровой трубы</li>
        <li>песчаная пробка и зернистость</li><li>заусенцы внутри труб</li><li>недоворот муфтовых соединений</li><li>качество сварных швов</li>
      </ul>
    </div>
    <div class="frames-rail"><div class="frames" id="frames">{frames}</div></div>
  </div>
  <div class="wrap videos">{videos}<a class="vid vid-more" href="video.html"><b>Приборы видеокаротажа</b><small class="mono">КП-410ВК2 · КП-511ВК · КП-512ВК →</small></a></div>
</section>

<section class="section cement">
  <div class="wrap split-2">
    <div class="reveal">
      <p class="eyebrow mono">цементирование</p>
      <h2 class="sec-title">Станция контроля цементирования нефтяных скважин</h2>
      <p class="lead">Датчики расхода, давления, плотности и температуры. Установка опрессована на 40 МПа по требованиям Госгортехнадзора РФ.</p>
      <p>Программное обеспечение контролирует заливку ствола в реальном времени и позволяет оперативно вмешаться — риск аварийной ситуации сводится к минимуму. По результатам формируются отчёты в графической и табличной форме.</p>
      <a class="btn btn-ghost" href="mailto:{EMAIL}?subject=Станция%20контроля%20цементирования">Запросить информацию</a>
    </div>
    <div class="gaugeset reveal" aria-hidden="true">
      <div class="dial" data-v="0.72"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="50"/><circle class="dial-v" cx="60" cy="60" r="50"/></svg><b class="mono">40</b><span class="mono">МПа</span></div>
      <div class="dial" data-v="0.48"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="50"/><circle class="dial-v" cx="60" cy="60" r="50"/></svg><b class="mono">ρ</b><span class="mono">плотность</span></div>
      <div class="dial" data-v="0.6"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="50"/><circle class="dial-v" cx="60" cy="60" r="50"/></svg><b class="mono">Q</b><span class="mono">расход</span></div>
      <div class="dial" data-v="0.35"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="50"/><circle class="dial-v" cx="60" cy="60" r="50"/></svg><b class="mono">T</b><span class="mono">температура</span></div>
    </div>
  </div>
</section>

{stats_html()}

<section class="section clients-sec">
  <div class="wrap"><div class="sec-head"><p class="eyebrow mono">заказчики</p><h2 class="sec-title split">Заказчики в России, Казахстане, Узбекистане и Беларуси</h2><a class="link-arrow" href="clients.html">Все заказчики</a></div></div>
  <div class="marquee"><div class="marquee-track">{clients}{clients}</div></div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head"><p class="eyebrow mono">новости</p><h2 class="sec-title split">Свежие отгрузки</h2><a class="link-arrow" href="news.html">Все новости</a></div>
    <ol class="nlist">{news}</ol>
  </div>
</section>'''
    write('index', page('index', 'Главная', body))



def well_log_svg():
    """Статичная каротажная диаграмма для первого экрана.

    Кривые согласованы с литологией: в глинах ГК выше и ПС у линии глин,
    в песчаниках ГК низкий и ПС отклоняется влево, в известняках и углях КС растёт.
    """
    import math
    import random
    rnd = random.Random(1003)
    W, H, top = 520, 760, 64
    cols = {'depth': (0, 58), 'lith': (58, 100), 'gk': (100, 240), 'ks': (240, 380), 'ps': (380, 520)}
    d0, d1 = 1200, 1290
    yd = lambda d: top + 8 + (d - d0) / (d1 - d0) * (H - top - 22)
    layers = [(1200, 1209, 'clay'), (1209, 1221, 'sand'), (1221, 1225, 'clay'), (1225, 1232, 'lime'),
              (1232, 1240, 'clay'), (1240, 1244, 'coal'), (1244, 1259, 'sand'), (1259, 1266, 'clay'),
              (1266, 1273, 'lime'), (1273, 1281, 'sand'), (1281, 1290, 'clay')]
    # значения в долях ширины трека: (ГК, КС, ПС)
    base = {'clay': (0.72, 0.18, 0.78), 'sand': (0.25, 0.42, 0.28), 'lime': (0.18, 0.78, 0.66), 'coal': (0.08, 0.92, 0.7)}

    def lith_at(d):
        for a, b, t in layers:
            if a <= d < b:
                return t
        return 'clay'

    def smooth_val(d, k):
        # сглаживаем переходы на границах пластов, чтобы кривая выглядела как запись прибора
        acc, wsum = 0.0, 0.0
        for dd in (-1.2, -0.6, 0, 0.6, 1.2):
            w = 1.6 - abs(dd)
            acc += base[lith_at(d + dd)][k] * w
            wsum += w
        return acc / wsum

    noise = {k: [rnd.uniform(-1, 1) for _ in range(400)] for k in range(3)}

    def path(k, col, amp):
        x0, x1 = cols[col]
        pts = []
        steps = 360
        for i in range(steps + 1):
            d = d0 + (d1 - d0) * i / steps
            n = noise[k][i % 400] * amp + math.sin(d * 1.7 + k) * amp * 0.6
            v = min(0.96, max(0.04, smooth_val(d, k) + n))
            pts.append(f'{x0 + 8 + v * (x1 - x0 - 16):.1f},{yd(d):.1f}')
        return 'M' + ' L'.join(pts)

    grid = []
    for d in range(d0, d1 + 1):
        y = yd(d)
        major = d % 10 == 0
        if d % 2 == 0 or major:
            grid.append(f'<line x1="{cols["lith"][1]}" x2="{W}" y1="{y:.1f}" y2="{y:.1f}" class="{"g-major" if major else "g-minor"}"/>')
        if major:
            grid.append(f'<text x="50" y="{y + 4:.1f}" class="lg-depth">{d}</text>')
            grid.append(f'<line x1="52" x2="58" y1="{y:.1f}" y2="{y:.1f}" class="g-major"/>')
    for col in ('gk', 'ks', 'ps'):
        x0, x1 = cols[col]
        for j in range(1, 4):
            x = x0 + (x1 - x0) * j / 4
            grid.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{H}" class="g-minor"/>')
    for x in (58, 100, 240, 380):
        grid.append(f'<line x1="{x}" x2="{x}" y1="0" y2="{H}" class="g-col"/>')
    lith = ''.join(f'<rect x="{cols["lith"][0]}" y="{yd(a):.1f}" width="{cols["lith"][1] - cols["lith"][0]}" height="{yd(b) - yd(a):.1f}" fill="url(#p-{t})"/>'
                   for a, b, t in layers)
    heads = [
        ('depth', 'Глуб.', 'м', ''), ('lith', 'Лит.', '', ''),
        ('gk', 'ГК', 'мкР/ч', '0 — 30'), ('ks', 'КС', 'Ом·м', '1 — 1000'), ('ps', 'ПС', 'мВ', '−80 — 20'),
    ]
    head = ''.join(f'<text x="{(cols[c][0] + cols[c][1]) / 2}" y="22" class="lg-name lg-{c}">{n}</text>'
                   f'<text x="{(cols[c][0] + cols[c][1]) / 2}" y="38" class="lg-unit">{u}</text>'
                   f'<text x="{(cols[c][0] + cols[c][1]) / 2}" y="54" class="lg-unit">{r}</text>'
                   for c, n, u, r in heads)
    return f'''<svg class="wlog" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin meet" role="img">
<defs>
<pattern id="p-sand" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" class="lt-sand"/><circle cx="2" cy="2" r=".9" class="lt-dot"/><circle cx="6" cy="6" r=".9" class="lt-dot"/></pattern>
<pattern id="p-clay" width="12" height="6" patternUnits="userSpaceOnUse"><rect width="12" height="6" class="lt-clay"/><line x1="1" x2="9" y1="3" y2="3" class="lt-line"/></pattern>
<pattern id="p-lime" width="16" height="8" patternUnits="userSpaceOnUse"><rect width="16" height="8" class="lt-lime"/><path d="M0 .5H16M0 4.5H16M4 .5V4.5M12 4.5V8" class="lt-line"/></pattern>
<pattern id="p-coal" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" class="lt-coal"/></pattern>
</defs>
<rect x="0" y="0" width="{W}" height="{top}" class="lg-headbg"/>
{head}
<line x1="0" x2="{W}" y1="{top}" y2="{top}" class="g-col"/>
{lith}
{''.join(grid)}
<path d="{path(2, 'ps', 0.018)}" class="cv cv-ps" pathLength="1"/>
<path d="{path(1, 'ks', 0.03)}" class="cv cv-ks" pathLength="1"/>
<path d="{path(0, 'gk', 0.035)}" class="cv cv-gk" pathLength="1"/>
</svg>'''


def write(slug, text):
    with open(os.path.join(OUT, slug + '.html'), 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for sub in ('css', 'js'):
        shutil.copytree(os.path.join(HERE, 'static', sub), os.path.join(OUT, sub))
    shutil.copy(os.path.join(HERE, 'static', 'favicon.svg'), OUT)
    # копируем только реально используемые изображения
    os.makedirs(os.path.join(OUT, 'img'))
    build_index()
    build_catalog()
    for c in CATEGORIES:
        build_category(c)
    for s in PRODUCTS:
        build_product(s)
    build_company()
    build_contacts()
    build_clients()
    build_news()
    build_certificates()
    used = set()
    for fn in os.listdir(OUT):
        if fn.endswith('.html'):
            used |= set(re.findall(r'img/([^"\s)]+)', open(os.path.join(OUT, fn), encoding='utf-8').read()))
    for name in used:
        src = os.path.join(HERE, 'static', 'img', name)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, 'img', name))
        else:
            print('нет изображения:', name)
    print('страниц:', len([f for f in os.listdir(OUT) if f.endswith('.html')]), 'изображений:', len(used))


if __name__ == '__main__':
    main()
