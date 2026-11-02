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

# ---------------------------------------------------------------- фотографии из открытых коллекций

CREDITS = json.load(open(os.path.join(DATA, 'photo-credits.json'), encoding='utf-8'))
PHOTO_FILES = {
    'commons:135488664': 'tomsk-krasnoarmeyskaya-92.jpg',
    'commons:141490687': 'drill-core-boxes.jpg',
    'commons:101524389': 'core-drill-rig-1968.jpg',
    'commons:160072267': 'drilling-rig.jpg',
    'commons:7259897': 'taiga-torch.jpg',
    'commons:11409674': 'well-log-usgs-1981.jpg',
    'commons:26031515': 'tomsk-view.jpg',
    'commons:52624830': 'borehole-camera.webm',
}


def photo(name):
    return 'photos/' + name


def credits_html():
    rows = []
    for c in CREDITS:
        rows.append(f'<a href="{e(c["page"])}" target="_blank" rel="noopener">{e(c["title"])}</a> — {e((c["creator"] or "автор не указан")[:60])}, {e(c["license"])}')
    return 'Фото: ' + '; '.join(rows) + ', Wikimedia Commons.'


# методы для подбора прибора (по описаниям приборов)
METHODS = [
    ('ks', 'КС и ПС'), ('gk', 'Гамма-каротаж'), ('rt', 'Резистивиметрия и термометрия'),
    ('vp', 'Вызванная поляризация'), ('lm', 'Локация муфт'), ('video', 'Видеокаротаж'), ('reg', 'Регистрация и глубина'),
]
PRODUCT_METHODS = {
    'geofit-1003': 'reg', 'geofit-1108': 'reg', 'depth-system': 'reg', 'bktp-m2': 'reg', 'dig': 'reg',
    'kp-51e': 'ks', 'kp-52e': 'ks', 'kp-61e': 'ks rt', 'kp-71egtr': 'ks gk rt', 'kp-71egrtvp-02': 'ks gk vp',
    'kp-81eg': 'ks gk', 'kp-91eg': 'ks gk', 'kp-82bkr': 'ks gk', 'kp-242eg': 'ks gk', 'zk-01msk': 'ks',
    'kp-240gtr': 'gk rt', 'kp-241gtrl': 'gk rt lm', 'kp-410vk': 'video', 'kp-511vk': 'video', 'kp-512vk': 'video',
}

# ---------------------------------------------------------------- шаблон

LOGO = '''<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true">
<rect width="48" height="48" class="lm-bg"/>
<text x="7" y="23" class="lm-e">E</text><text x="17" y="38" class="lm-pert">PERT</text>
<path d="M10 39 L29 12 L27 22 L39 5 L22 31 L24 21 Z" class="lm-bolt"/></svg>'''


def nav_html(active):
    items = [('catalog', 'Каталог'), ('company', 'О компании'), ('clients', 'Заказчики'),
             ('news', 'Новости'), ('contacts', 'Контакты')]
    mega = ''.join(
        f'''<div class="mega-col"><a class="mega-cat" href="{c['slug']}.html">{e(c['title'])}</a>
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


def page(slug, title, body, desc='', active=None, foot_photo=None):
    full_title = 'ООО «АСУ-ЭКСПЕРТ» — геофизические приборы, Томск' if slug == 'index' else f'{title} — АСУ-ЭКСПЕРТ'
    desc = desc or 'Научно-производственное предприятие ООО «АСУ-ЭКСПЕРТ», Томск: скважинные геофизические приборы, каротажные лаборатории, регистраторы и видеокаротаж.'
    fp, fcap = foot_photo or ('tomsk-krasnoarmeyskaya-92.jpg', 'Томск, улица Красноармейская, 92')
    mlinks = ''.join(f'<a href="{c["slug"]}.html">{e(c["short"])}</a>' for c in CATEGORIES)
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#eef1f3">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/main.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body class="page-{slug}">
<a class="skip" href="#main">К содержимому</a>
<header class="hdr" id="hdr">
  <div class="hdr-in">
    <a class="logo" href="index.html" aria-label="АСУ-ЭКСПЕРТ, на главную">{LOGO}<span class="logo-txt">АСУ-ЭКСПЕРТ</span></a>
    <nav class="nav" aria-label="Основное меню"><ul>{nav_html(active)}</ul></nav>
    <a class="hdr-phone" href="tel:{PHONE_HREF}">{PHONE}</a>
    <a class="btn btn-sm btn-red hdr-cta" href="contacts.html#request">Запросить КП</a>
    <button class="burger" id="burger" aria-label="Открыть меню" aria-expanded="false" aria-controls="mnav"><span></span><span></span></button>
  </div>
</header>
<div class="mnav" id="mnav" hidden>
  <nav class="mnav-in" aria-label="Мобильное меню">
    <a href="catalog.html">Каталог</a>{mlinks}<a href="company.html">О компании</a><a href="clients.html">Заказчики</a>
    <a href="news.html">Новости</a><a href="certificates.html">Сертификаты</a><a href="contacts.html">Контакты</a>
    <div class="mnav-contacts"><a href="tel:{PHONE_HREF}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </nav>
</div>
<main id="main">
{body}
</main>
<footer class="ftr">
  <figure class="ftr-photo"><img src="{photo(fp)}" alt="{e(fcap)}" loading="lazy"><figcaption>{e(fcap)}</figcaption></figure>
  <div class="ftr-menu">
    <a class="logo" href="index.html" aria-label="АСУ-ЭКСПЕРТ, на главную">{LOGO}<span class="logo-txt">АСУ-ЭКСПЕРТ</span></a>
    <nav class="ftr-links" aria-label="Разделы сайта">
      <a href="catalog.html">Каталог</a><a href="company.html">О компании</a><a href="clients.html">Заказчики</a>
      <a href="news.html">Новости</a><a href="certificates.html">Сертификаты</a><a href="contacts.html">Контакты</a>
    </nav>
    <div class="ftr-info">
      <div><a href="tel:{PHONE_HREF}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></div>
      <div>{ADDRESS}</div>
    </div>
    <div class="ftr-legal"><p>© 2009–{YEAR} ООО «АСУ-ЭКСПЕРТ», ИНН 7017251277, ОГРН 1097017020627</p><p>{credits_html()}</p></div>
  </div>
</footer>
<script src="js/main.js" defer></script>
</body>
</html>
'''


def crumbs(*items):
    parts = ['<a href="index.html">Главная</a>']
    for href, label in items:
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span aria-current="page">{e(label)}</span>')
    return '<nav class="crumbs" aria-label="Навигация">' + '<span aria-hidden="true">/</span>'.join(parts) + '</nav>'


def tags(p):
    return '<p class="tags">' + ' · '.join(e(c) for c in p['chips']) + '</p>'


def product_card(slug, i=0):
    p = PRODUCTS[slug]
    return f'''<a class="pcard rv" href="{slug}.html" style="--d:{i % 3}">
  <div class="pcard-img"><img src="img/{p['img']}" alt="{e(p['name'])}" loading="lazy"></div>
  <div class="pcard-body">
    <h3 class="pcard-name">{e(p['name'])}</h3>
    <p class="pcard-kind">{e(p['kind'])}</p>
    <p class="pcard-tag">{e(p['tag'])}</p>
    {tags(p)}
  </div>
</a>'''


def page_hero(title, lead, crumb_html, media, extra=''):
    """media: (src, alt, caption, kind) — kind 'object' для фото прибора на белом."""
    src, alt, cap, kind = media
    figcap = f'<figcaption>{e(cap)}</figcaption>' if cap else ''
    return f'''<section class="phero">
  <div class="phero-text">
    {crumb_html}
    <h1 class="phero-title{' big' if len(title) <= 22 else ''} rv">{title}</h1>
    <p class="phero-lead rv" style="--d:1">{lead}</p>
    {extra}
  </div>
  <figure class="phero-media {kind}"><img src="{src}" alt="{e(alt)}">{figcap}</figure>
</section>'''


def band(items):
    """Лента из трёх фотографий перед подвалом: (файл, подпись), файл из photos/ или img/."""
    figs = ''.join(f'<figure class="rv" style="--d:{i}"><img src="{src}" alt="{e(cap)}"><figcaption>{e(cap)}</figcaption></figure>'
                   for i, (src, cap) in enumerate(items))
    return f'<section class="band" aria-label="Фотографии">{figs}</section>'


BAND_FIELD = [(photo('drilling-rig.jpg'), 'Буровая установка'), (photo('drill-core-boxes.jpg'), 'Керн в ящиках после бурения'),
              ('img/ba951de225f5685b2383ecc0fe64f6ce.png', 'Кадр видеокаротажа АСУ-ЭКСПЕРТ')]
BAND_WELL = [(photo('core-drill-rig-1968.jpg'), 'Колонковое бурение, 1968 год'), (photo('taiga-torch.jpg'), 'Западная Сибирь, начало 1980-х'),
             ('img/04f973d653cbdf4ce1fdd0f4dc83f97d.png', 'Кадр видеокаротажа АСУ-ЭКСПЕРТ')]


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
    return doc_html, f'<nav class="toc" aria-label="Содержание"><h2>Содержание</h2><ol>{items}</ol></nav>'


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


# ---------------------------------------------------------------- страницы

def build_product(slug):
    p = PRODUCTS[slug]
    c = p['cat']
    doc = CONTENT[p['id']]['html']
    doc, toc = toc_from(doc)
    related = [s for s in c['products'] if s != slug][:3]
    extra = f'''{tags(p)}
    <div class="prod-actions rv" style="--d:2">
      <a class="btn btn-red" href="mailto:{EMAIL}?subject={e('Запрос: ' + p['name'])}">Запросить стоимость</a>
      <a class="btn btn-tone" href="#spec">Характеристики</a>
    </div>'''
    body = page_hero(e(p['name']), e(p['tag']),
                     crumbs(('catalog.html', 'Каталог'), (c['slug'] + '.html', c['short']), (None, p['name'])),
                     ('img/' + p['img'], p['name'] + ', ' + p['kind'].lower(), '', 'object'), extra)
    body += f'''
<div class="doc-grid" id="spec">
  <aside class="doc-aside">
    {toc}
    <div class="ask"><h2>Нужна консультация?</h2><p>Инженер подскажет комплектацию и совместимость с вашим регистратором.</p>
    <a class="btn btn-sm btn-red" href="mailto:{EMAIL}?subject={e('Вопрос по ' + p['name'])}">Задать вопрос</a></div>
  </aside>
  <article class="doc rv"><h2>Техническое описание</h2>{doc}</article>
</div>
<section class="section">
  <div class="sec-head"><h2 class="sec-title rv">{e(c['short'])}: другие приборы</h2><a class="link" href="{c['slug']}.html">Весь раздел</a></div>
  <div class="pgrid">{''.join(product_card(s, i) for i, s in enumerate(related))}</div>
</section>'''
    write(slug, page(slug, p['name'] + ' — ' + p['kind'], body, desc=p['tag'], active='catalog'))


def build_category(c):
    doc = CONTENT[c['id']]['html']
    doc, toc = toc_from(doc)
    cards = ''.join(product_card(s, i) for i, s in enumerate(c['products']))
    others = ''.join(f'<a href="{o["slug"]}.html">{e(o["title"])}</a>' for o in CATEGORIES if o is not c)
    n = len(c['products'])
    body = page_hero(e(c['short']), e(c['title']) + '. ' + e(c['lead']), crumbs(('catalog.html', 'Каталог'), (None, c['short'])),
                     ('img/' + c['img'], c['title'], '', 'object'),
                     f'<p class="phero-count">{n} {plural(n, "модель", "модели", "моделей")} в разделе</p>')
    body += f'''
<section class="section">
  <div class="sec-head"><h2 class="sec-title rv">Модели</h2></div>
  <div class="pgrid">{cards}</div>
</section>
<div class="doc-grid">
  <aside class="doc-aside">{toc}<nav class="catlinks" aria-label="Другие разделы"><h2>Другие разделы</h2>{others}</nav></aside>
  <article class="doc rv"><h2>Обзор раздела</h2>{doc}</article>
</div>''' + band(BAND_WELL)
    write(c['slug'], page(c['slug'], c['title'], body, desc=c['lead'], active='catalog'))


def build_catalog():
    blocks = ''
    for c in CATEGORIES:
        items = ''.join(f'<li><a href="{s}.html"><span>{e(PRODUCTS[s]["name"])}</span><small>{e(PRODUCTS[s]["kind"])}</small></a></li>'
                        for s in c['products'])
        blocks += f'''<article class="catblock">
  <a class="catblock-media rv" href="{c['slug']}.html" aria-label="{e(c['title'])}"><img src="img/{c['img']}" alt="" loading="lazy"></a>
  <div class="catblock-body">
    <h2 class="rv"><a href="{c['slug']}.html">{e(c['title'])}</a></h2>
    <p class="rv" style="--d:1">{e(c['lead'])}</p>
    <ul class="catblock-list rv" style="--d:2">{items}</ul>
    <a class="link" href="{c['slug']}.html">Открыть раздел</a>
  </div>
</article>'''
    body = page_hero('Каталог продукции',
                     'Каротажные лаборатории, регистраторы, система глубины и скважинные приборы. На приборы оформлены декларации о соответствии ТР ТС / ЕАЭС.',
                     crumbs((None, 'Каталог')),
                     (photo('drill-core-boxes.jpg'), 'Ящики с керном', 'Керн в ящиках после бурения', ''))
    body += f'<section class="section catblocks">{blocks}</section>' + band(BAND_WELL)
    write('catalog', page('catalog', 'Каталог продукции', body, active='catalog'))


def stats_html():
    years = YEAR - 2009
    return f'''<section class="stats" aria-label="Предприятие в цифрах">
    <div class="stat rv"><b class="count" data-to="{years}">{years}</b>лет разрабатываем и производим аппаратуру ГИС</div>
    <div class="stat rv" style="--d:1"><b class="count" data-to="{len(PRODUCTS)}">{len(PRODUCTS)}</b>моделей приборов и регистраторов в каталоге</div>
    <div class="stat rv" style="--d:2"><b class="count" data-to="{len(NEWS)}">{len(NEWS)}</b>отгрузок, тендеров и событий в ленте новостей</div>
    <div class="stat rv" style="--d:3"><b class="count" data-to="4">4</b>страны поставок: Россия, Казахстан, Узбекистан, Беларусь</div>
</section>'''


def build_company():
    req = CONTENT[2]['html']
    body = page_hero('О компании',
                     'ООО «АСУ-ЭКСПЕРТ» — научно-производственное предприятие из Томска. С 2009 года разрабатываем и выпускаем скважинные геофизические приборы и наземную регистрирующую аппаратуру.',
                     crumbs((None, 'О компании')),
                     (photo('tomsk-view.jpg'), 'Вид на Томск', 'Томск', ''))
    body += f'''
<section class="section split-2">
  <div>
    <h2 class="sec-title rv">Программа ГЕОФИТ</h2>
    <p class="lead rv" style="--d:1">Регистрирующая аппаратура поставляется с программным обеспечением ГЕОФИТ. Оно позволяет:</p>
    <ul class="ticks rv" style="--d:2">
      <li>мониторинг в реальном времени и архивация данных ГИС, акустического каротажа и технологических параметров;</li>
      <li>расчёт геофизических параметров по заданным формулам;</li>
      <li>калибровка каналов измерения и корректировка глубины по магнитным меткам;</li>
      <li>оперативная оценка качества каротажа, автоматическое и ручное редактирование без изменения исходного файла.</li>
    </ul>
    <p class="rv" style="--d:3">Ремонт и техническое обслуживание поставленных приборов выполняем сами.</p>
  </div>
  <figure class="figure rv" style="--d:1"><img src="img/fa5c25733eb8f5628b78791ae5e265a2.JPG" alt="Каротажная диаграмма, записанная регистратором ГЕОФИТ" loading="lazy"><figcaption>Каротажная диаграмма, записанная в программе ГЕОФИТ</figcaption></figure>
</section>
{stats_html()}
<section class="section split-2">
  <div>
    <h2 class="sec-title rv">Оценка условий труда</h2>
    <p class="lead rv" style="--d:1">Результаты специальной оценки условий труда (СОУТ) на рабочих местах предприятия.</p>
  </div>
  <figure class="figure rv" style="--d:1"><img src="img/f5149feb3befe75edadcf171a02759d7.JPG" alt="Сводная ведомость результатов СОУТ" loading="lazy"></figure>
</section>
<div class="doc-grid" id="requisites">
  <aside class="doc-aside"><div class="ask"><h2>Директор</h2><p>Муратов Сергей Алексеевич, действует на основании устава</p><a class="btn btn-sm btn-tone" href="contacts.html">Все контакты</a></div></aside>
  <article class="doc rv">{req}</article>
</div>'''
    write('company', page('company', 'О компании', body, active='company', foot_photo=('core-drill-rig-1968.jpg', 'Колонковое бурение, 1968 год')))


def build_contacts():
    body = page_hero('Контакты', 'Ответим на вопросы по приборам, комплектации, ремонту и поставке.',
                     crumbs((None, 'Контакты')),
                     (photo('tomsk-krasnoarmeyskaya-92.jpg'), 'Деревянный дом на улице Красноармейской, 92 в Томске', 'Томск, улица Красноармейская, 92', ''))
    body += f'''
<section class="section contact-grid">
  <div class="contact-cards">
    <a class="ccard rv" href="tel:{PHONE_HREF}"><h2>Телефон</h2><b>{PHONE}</b><small>Тел./факс: {FAX}</small></a>
    <a class="ccard rv" style="--d:1" href="mailto:{EMAIL}"><h2>Почта</h2><b>{EMAIL}</b><small>Общий адрес предприятия</small></a>
    <div class="ccard rv" style="--d:2"><h2>Адрес</h2><p>{ADDRESS}</p><small>{ADDRESS_NOTE}</small>
      <a class="scheme" href="img/e56ac6fcd237ee31fefe92e1e12cca1c.png" target="_blank" rel="noopener"><img src="img/e56ac6fcd237ee31fefe92e1e12cca1c.png" alt="Схема проезда к офису на Красноармейской, 92/1" loading="lazy"></a></div>
    <div class="people rv" style="--d:3">
      <div class="person"><span>Директор</span><b>Муратов Сергей Алексеевич</b><a href="mailto:MuratovSA@asu-expert.ru">MuratovSA@asu-expert.ru</a></div>
      <div class="person"><span>Зам. директора по геофизической аппаратуре</span><b>Журиков Сергей Александрович</b><a href="mailto:GurikovSA@asu-expert.ru">GurikovSA@asu-expert.ru</a></div>
    </div>
  </div>
  <div class="map rv" style="--d:1"><iframe src="https://yandex.ru/map-widget/v1/-/CCUuY2HrhA" title="АСУ-ЭКСПЕРТ на Яндекс Картах" loading="lazy" allowfullscreen></iframe></div>
</section>
<section class="section" id="request">
  <form class="rform" id="rform" novalidate>
    <div class="rform-head"><h2 class="sec-title rv">Опишите задачу</h2>
    <p>Форма откроет вашу почтовую программу с готовым письмом на {EMAIL}.</p></div>
    <label><span>Имя и организация</span><input name="name" required autocomplete="organization"></label>
    <label><span>Телефон или почта</span><input name="contact" required autocomplete="email"></label>
    <label class="full"><span>Прибор</span><select name="product"><option value="">Пока не знаю, нужна консультация</option>{''.join(f'<option>{e(p["name"])} — {e(p["kind"])}</option>' for p in PRODUCTS.values())}</select></label>
    <label class="full"><span>Задача: тип скважин, глубина, кабель, регистратор</span><textarea name="msg" rows="5"></textarea></label>
    <button class="btn btn-red" type="submit">Сформировать письмо</button>
  </form>
</section>''' + band(BAND_FIELD)
    write('contacts', page('contacts', 'Контакты', body, active='contacts', foot_photo=('tomsk-view.jpg', 'Томск')))


def build_clients():
    items = ''.join(f'<li><b>{e(n)}</b><small>{e(c)}</small></li>' for n, c in CLIENTS)
    body = page_hero('Заказчики', 'Горнодобывающие и нефтесервисные компании, геологоразведка, атомная отрасль и водоканалы.',
                     crumbs((None, 'Заказчики')),
                     (photo('taiga-torch.jpg'), 'Факел попутного газа в тайге Западной Сибири', 'Западная Сибирь, начало 1980-х', ''))
    body += f'''
<section class="section split-2 geo">
  <div><h2 class="sec-title rv">География поставок</h2>
  <p class="lead rv" style="--d:1">Приборы работают на угольных разрезах Кузбасса, урановых месторождениях Забайкалья, в нефтесервисе Западной Сибири и на объектах атомной отрасли.</p></div>
  <figure class="figure rv" style="--d:1"><img src="img/ea7df1cb27ff50326722117e778418a5.png" alt="Карта: заказчики в России, Казахстане, Узбекистане и Беларуси" loading="lazy"></figure>
</section>
<section class="section">
  <div class="sec-head"><h2 class="sec-title rv">Список заказчиков</h2></div>
  <ul class="clients-names rv">{items}</ul>
</section>''' + band(BAND_FIELD)
    write('clients', page('clients', 'Заказчики', body, active='clients'))


def build_news():
    years = sorted({n['year'] for n in NEWS}, reverse=True)
    chips = '<button class="ychip is-on" data-y="all">Все</button>' + ''.join(
        f'<button class="ychip" data-y="{y}">{y}</button>' for y in years)
    groups = ''
    for y in years:
        rows = ''.join(f'<li class="nrow"><time datetime="{n["iso"]}">{e(n["date"])}</time><p>{e(n["text"])}</p></li>'
                       for n in NEWS if n['year'] == y)
        groups += f'<section class="ngroup" data-y="{y}"><h2 class="ngroup-y rv">{y}</h2><ol class="rv" style="--d:1">{rows}</ol></section>'
    body = page_hero('Новости',
                     f'{len(NEWS)} {plural(len(NEWS), "запись", "записи", "записей")} с 2010 года: поставки приборов, выигранные тендеры, ремонт и новые разработки.',
                     crumbs((None, 'Новости')),
                     (photo('core-drill-rig-1968.jpg'), 'Геологи у колонковой буровой установки', 'Колонковое бурение, 1968 год', ''))
    body += f'''
<section class="section">
  <div class="nfilter"><input type="search" id="nsearch" placeholder="Прибор или заказчик" aria-label="Поиск по новостям"><div class="ychips" role="group" aria-label="Год">{chips}</div></div>
  <p class="nempty" id="nempty" hidden>Ничего не найдено</p>
  <div class="ngroups">{groups}</div>
</section>''' + band(BAND_FIELD)
    write('news', page('news', 'Новости', body, active='news'))


def build_certificates():
    imgs = re.findall(r'src="img/([^"]+)"', CONTENT[59]['html'])
    certs, reviews = imgs[:5], imgs[5:]

    def gal(lst, kind):
        return ''.join(f'<a class="cert rv" href="img/{i}" data-lightbox style="--d:{k % 5}"><img src="img/{i}" alt="{kind}, страница {k + 1}" loading="lazy"></a>'
                       for k, i in enumerate(lst))
    body = page_hero('Сертификаты и отзывы',
                     'Декларации о соответствии ТР ТС / ЕАЭС и письма заказчиков. Нажмите на документ, чтобы открыть его крупно.',
                     crumbs((None, 'Сертификаты')),
                     ('img/' + certs[0], 'Декларация о соответствии', '', 'object'))
    body += f'''
<section class="section">
  <div class="sec-head"><h2 class="sec-title rv">Сертификаты</h2></div>
  <div class="certs">{gal(certs, 'Сертификат')}</div>
</section>
<section class="section">
  <div class="sec-head"><h2 class="sec-title rv">Отзывы заказчиков</h2></div>
  <div class="certs">{gal(reviews, 'Отзыв заказчика')}</div>
</section>
''' + band(BAND_WELL) + '''
<div class="lightbox" id="lightbox" hidden><button aria-label="Закрыть">×</button><img alt=""></div>'''
    write('certificates', page('certificates', 'Сертификаты и отзывы', body))


def build_index():
    n_cat = lambda c: f"{len(c['products'])} {plural(len(c['products']), 'модель', 'модели', 'моделей')}"
    dirs = ''.join(f'''<li class="rv" style="--d:{i}"><a href="{c['slug']}.html"><b>{e(c['title'])}</b><span>{n_cat(c)}</span><small>{e(c['lead'])}</small></a></li>'''
                   for i, c in enumerate(CATEGORIES))
    electric = ['kp-51e', 'kp-71egtr', 'kp-82bkr', 'kp-81eg']
    inline = ''.join(f'<a href="{s}.html"><img src="img/{PRODUCTS[s]["img"]}" alt="" loading="lazy"><span><b>{e(PRODUCTS[s]["name"])}</b>{e(PRODUCTS[s]["kind"])}</span></a>'
                     for s in electric)
    video_models = ''.join(f'<a href="{s}.html"><img src="img/{PRODUCTS[s]["img"]}" alt="" loading="lazy"><span><b>{e(PRODUCTS[s]["name"])}</b>{e(PRODUCTS[s]["kind"])}</span></a>'
                           for s in ['kp-410vk', 'kp-511vk', 'kp-512vk'])
    methods = ''.join(f'<button type="button" data-m="{k}" aria-pressed="false">{e(t)}</button>' for k, t in METHODS)
    plist = ''.join(f'''<li data-m="{PRODUCT_METHODS[s]}"><a href="{s}.html"><img src="img/{p['img']}" alt="" loading="lazy"><span><b>{e(p['name'])}</b>{e(p['kind'])}</span></a></li>'''
                    for s, p in PRODUCTS.items())
    f = WELL_FRAMES
    frames = (
        f'<figure class="m-tall"><img src="img/{f[0]}" alt="Перфорированная колонна, вид камерой вниз по стволу" loading="lazy"></figure>'
        f'<figure class="m-pair"><div><img src="img/{f[1]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></div><div><img src="img/{f[2]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></div></figure>'
        f'<figure class="m-wide"><img src="img/{f[5]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></figure>'
        f'<figure class="m-pair"><div><img src="img/{f[3]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></div><div><img src="img/{f[4]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></div></figure>'
        f'<figure class="m-tall"><img src="img/{f[6]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></figure>'
        f'<figure class="m-wide"><img src="img/{f[8]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></figure>'
        f'<figure class="m-pair"><div><img src="img/{f[9]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></div><div><img src="img/{f[10]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></div></figure>'
        f'<figure class="m-tall"><img src="img/{f[11]}" alt="Кадр видеокаротажа, ствол скважины" loading="lazy"></figure>'
    )
    videos = ''.join(f'<a href="{u}" target="_blank" rel="noopener"><b>{e(t)}</b><span>{e(s)}, видео на YouTube</span></a>' for u, t, s in VIDEOS)
    news = ''.join(f'<li class="rv" style="--d:{i}"><time datetime="{n["iso"]}">{e(n["date"])}</time><p>{e(n["text"])}</p></li>' for i, n in enumerate(NEWS[:6]))
    names = ''.join(f'<li><b>{e(n)}</b><small>{e(c)}</small></li>' for n, c in CLIENTS)
    cable = '<i></i>' * 40

    stage = [
        (photo('drilling-rig.jpg'), 'Буровая установка', 'Буровая установка', ''),
        (photo('drill-core-boxes.jpg'), 'Керн в ящиках', 'Керн в ящиках после бурения', ''),
        (photo('well-log-usgs-1981.jpg'), 'Каротажная диаграмма', 'Каротажная диаграмма скважины, 1981 год', 'paper'),
        (photo('core-drill-rig-1968.jpg'), 'Геологи у буровой установки', 'Колонковое бурение, 1968 год', ''),
        ('VIDEO', 'Съёмка камерой в скважине', 'Камера в скважине, рудник в ЮАР, 2015 год', ''),
        (photo('taiga-torch.jpg'), 'Факел попутного газа в тайге', 'Западная Сибирь, начало 1980-х', ''),
    ]
    def stage_media(i, s, a):
        if s == 'VIDEO':
            return (f'<video muted loop playsinline preload="none" poster="{photo("borehole-camera.jpg")}" aria-label="{e(a)}">'
                    f'<source src="{photo("borehole-camera.webm")}" type="video/webm"></video>')
        return f'<img src="{s}" alt="{e(a)}"{"" if i == 0 else " loading=\"lazy\""}>'
    stage_html = ''.join(f'<figure class="{k}{" is-on" if i == 0 else ""}" data-stage="{i}">{stage_media(i, s, a)}<figcaption>{e(c)}</figcaption></figure>'
                         for i, (s, a, c, k) in enumerate(stage))

    body = f'''<div class="stage-page">
  <div class="reading">
    <section class="r-sec hero-card" data-stage="0">
      <div class="cable" aria-hidden="true">{cable}</div>
      <h1 class="hero-title rv">Приборы для каротажа скважин</h1>
      <p class="hero-lead rv" style="--d:1">Томское предприятие АСУ-ЭКСПЕРТ с 2009 года выпускает скважинные приборы электрического, гамма- и видеокаротажа, каротажные лаборатории и регистраторы.</p>
      <div class="hero-actions rv" style="--d:2">
        <a class="btn btn-red" href="#picker">Подобрать прибор</a>
        <a class="link" href="catalog.html">Весь каталог</a>
      </div>
      <nav class="hero-links rv" style="--d:3" aria-label="Быстрые ссылки"><a href="geofit-1003.html">Лаборатория ГЕОФИТ</a><a href="video.html">Видеокаротаж</a><a href="news.html">Отгрузки</a><a href="contacts.html">Контакты</a></nav>
    </section>

    <section class="r-sec" data-stage="1" aria-labelledby="h-dirs">
      <h2 class="sec-title rv" id="h-dirs">Что мы выпускаем</h2>
      <ul class="dirlist">{dirs}</ul>
    </section>

    <section class="r-sec" data-stage="2" aria-labelledby="h-geofit">
      <h2 class="sec-title rv" id="h-geofit">Лаборатория ГЕОФИТ</h2>
      <p class="lead rv" style="--d:1">Комплексные исследования нефтяных, рудных и газовых скважин: запись, калибровка и обработка в одном комплексе.</p>
      <ul class="facts rv" style="--d:2">
        <li><b>Настройка</b>таблицы параметров скважинных приборов, макеты по видам исследований, оформление рабочего экрана</li>
        <li><b>Запись</b>калибровки, данные ГИС, акустического каротажа и технологических параметров в реальном времени по глубине или времени</li>
        <li><b>Расчёт</b>геофизические параметры по линейным и нелинейным характеристикам</li>
        <li><b>Контроль</b>оперативная оценка качества каротажа, правка без изменения исходного файла данных</li>
      </ul>
      <div class="r-actions rv" style="--d:3"><a class="btn btn-ink" href="geofit-1003.html">ГЕОФИТ 1003</a><a class="btn btn-tone" href="geofit-1108.html">ГЕОФИТ 1108</a><a class="btn btn-tone" href="depth-system.html">Система глубины</a></div>
    </section>

    <section class="r-sec" data-stage="3" aria-labelledby="h-el">
      <h2 class="sec-title rv" id="h-el">Все измерения за один спуск</h2>
      <p class="lead rv" style="--d:1">Приборы электрического и гамма-каротажа измеряют и передают на поверхность параметры всеми зондами во всём диапазоне за один спуско-подъём.</p>
      <p class="rv" style="--d:2">Передача цифровая, по одножильному каротажному кабелю, код «Манчестер-2». Калибровка и настройка перед записью не нужны, наземной панели нет. Приборы сопрягаются со всеми выпускаемыми каротажными регистраторами.</p>
      <div class="inline-models rv" style="--d:3">{inline}</div>
    </section>

    <section class="r-sec" data-stage="4" aria-labelledby="h-video">
      <h2 class="sec-title rv" id="h-video">Видеокаротаж</h2>
      <p class="lead rv" style="--d:1">Прибор опускается на одножильном кабеле до 4000 м и снимает колонну, фильтры и забой. На записи видно:</p>
      <ul class="defects rv" style="--d:2">
        <li>смятие труб и трещины</li><li>отсутствие сальника</li><li>деформацию надфильтровой трубы</li>
        <li>песчаную пробку</li><li>заусенцы внутри труб</li><li>недоворот муфт</li><li>качество сварных швов</li>
      </ul>
      <div class="inline-models rv" style="--d:3">{video_models}</div>
    </section>

    <section class="r-sec" data-stage="5" aria-labelledby="h-cement">
      <h2 class="sec-title rv" id="h-cement">Контроль цементирования</h2>
      <p class="lead rv" style="--d:1">Станция для нефтяных скважин с датчиками расхода, давления, плотности и температуры. Установка опрессована на 40 МПа по требованиям Госгортехнадзора РФ.</p>
      <p class="rv" style="--d:2">Программа показывает заливку ствола в реальном времени, чтобы оператор мог вмешаться до аварии. По результатам формируются отчёты в графической и табличной форме.</p>
      <p class="rv" style="--d:3"><a class="link" href="mailto:{EMAIL}?subject=Станция%20контроля%20цементирования">Запросить описание станции</a></p>
    </section>
  </div>
  <div class="stage" aria-hidden="false">{stage_html}</div>
</div>

<section class="picker" id="picker" aria-labelledby="h-picker">
  <div class="picker-in">
    <div class="picker-side">
      <h2 id="h-picker" class="rv">Подбор прибора</h2>
      <p class="picker-lead rv" style="--d:1">Отметьте методы, которые нужны на скважине. Останутся приборы, которые выполняют все отмеченные.</p>
      <div class="methods rv" style="--d:2" role="group" aria-label="Методы исследования">{methods}</div>
      <p class="picker-count" id="pickerCount" aria-live="polite">Все приборы каталога: {len(PRODUCTS)}</p>
    </div>
    <ul class="picker-list" id="pickerList">{plist}</ul>
  </div>
</section>

<section class="frames-sec" aria-labelledby="h-frames">
  <div class="frames-head"><h2 class="sec-title rv" id="h-frames">Кадры из скважин</h2><p class="rv" style="--d:1">Сняты нашими приборами видеокаротажа на объектах заказчиков. Лента прокручивается вбок.</p></div>
  <div class="frames-row" tabindex="0" aria-label="Кадры видеокаротажа">{frames}</div>
  <div class="videos">{videos}<a class="more" href="video.html"><b>Приборы видеокаротажа</b><span>КП-410ВК2, КП-511ВК, КП-512ВК</span></a></div>
</section>

<section class="proof" aria-labelledby="h-proof">
  <div><h2 id="h-proof" class="rv">Заказчики</h2><a class="link" href="clients.html">География поставок</a></div>
  <ul class="names rv" style="--d:1">{names}</ul>
</section>

<section class="nsec" aria-labelledby="h-news">
  <div class="nsec-head"><h2 id="h-news" class="rv">Отгрузки</h2><a class="link" href="news.html">Все {len(NEWS)} {plural(len(NEWS), "запись", "записи", "записей")}</a></div>
  <ol class="nrows">{news}</ol>
</section>

<section class="contact" aria-labelledby="h-contact">
  <div><h2 id="h-contact" class="rv">Напишите инженеру</h2><p class="rv" style="--d:1">Опишите скважину, глубину, кабель и регистратор. Подберём прибор и пришлём предложение.</p></div>
  <a class="contact-mail rv" style="--d:2" href="mailto:{EMAIL}?subject=Подбор%20прибора">{EMAIL}</a>
  <div class="contact-foot"><span><a href="tel:{PHONE_HREF}">{PHONE}</a>, тел./факс {FAX}</span><span>{ADDRESS}</span></div>
</section>'''
    write('index', page('index', 'Главная', body, foot_photo=('drill-core-boxes.jpg', 'Керн в ящиках после бурения')))


def write(slug, text):
    with open(os.path.join(OUT, slug + '.html'), 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for sub in ('css', 'js', 'photos'):
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
