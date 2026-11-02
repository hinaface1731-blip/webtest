import re,html,json,urllib.request,ssl,sys,os
# Скачивает страницы asu-expert.ru в src/data/pages.json (сырые HTML в cp1251 -> utf-8)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
B='https://asu-expert.ru/'
seen={};queue=['index.php?module=mod_content&id=1','index.php?module=mod_customer','index.php?module=mod_news','index.php?module=mod_map']
imgs=set()
def get(u):
    r=urllib.request.urlopen(B+u,timeout=30).read()
    return r.decode('cp1251',errors='replace')
while queue:
    u=queue.pop(0)
    if u in seen: continue
    try: t=get(u)
    except Exception as e: seen[u]={'err':str(e)}; continue
    seen[u]={'html':t}
    for l in re.findall(r'href="\.?/?(index\.php\?module=(?:mod_content|mod_news|mod_customer)[^"#]*)"',t):
        l=html.unescape(l)
        if l not in seen and l not in queue and len(seen)+len(queue)<400: queue.append(l)
    for i in re.findall(r'(?:src|href)="\.?/?([^"]+\.(?:jpe?g|png|gif|pdf|doc|docx|mp4))"',t,re.I): imgs.add(i)
json.dump(seen,open('pages.json','w'),ensure_ascii=False)
open('assets.txt','w').write('\n'.join(sorted(imgs)))
print(len(seen),len(imgs))
