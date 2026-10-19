from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime
import html
import requests
from bs4 import BeautifulSoup

BLOG = 'https://stoputsunomiyalrt.hatenablog.com/'
OUT = Path(__file__).parent / 'docs' / 'index.html'
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; HatenaJimdoReader/1.0)'}


def clean_image(url):
    if not url: return ''
    if url.startswith('//'): url='https:' + url
    url=urljoin(BLOG,url)
    return url if urlparse(url).scheme in ('https','http') else ''


def fetch():
    result = []
    for page in [BLOG, BLOG + '?page=2']:
        if len(result)>=10: break
        response=requests.get(page,headers=HEADERS,timeout=25)
        response.raise_for_status()
        soup=BeautifulSoup(response.text,'html.parser')
        for entry in soup.select('article.entry, .hentry'):
            title_node=entry.select_one('.entry-title a, .entry-title-link, h1.entry-title a')
            if not title_node: continue
            link=urljoin(BLOG,title_node.get('href',''))
            if not link.startswith(BLOG+'entry/'): continue
            if any(x['link']==link for x in result): continue
            body=entry.select_one('.entry-content')
            # Prefer an actual paragraph to image captions/metadata.
            paragraphs=[p.get_text(' ',strip=True) for p in body.select('p')] if body else []
            excerpt=next((p for p in paragraphs if len(p)>15), '')
            if not excerpt and body: excerpt=body.get_text(' ',strip=True)
            image_node=body.select_one('img') if body else None
            image=clean_image(image_node.get('data-src') or image_node.get('src')) if image_node else ''
            date_node=entry.select_one('time[datetime], .date a, .entry-date a, time')
            date=(date_node.get('datetime') or date_node.get_text(' ',strip=True)) if date_node else ''
            date=date[:10].replace('/','-')
            result.append({'title':title_node.get_text(' ',strip=True),'link':link,'excerpt':excerpt[:135],'date':date,'image':image})
            if len(result)>=10: break
    if not result:
        raise RuntimeError('記事が取得できませんでした。はてなブログのHTML構造を確認してください。')
    return result


def build(articles):
    blocks=[]
    for a in articles:
        title=html.escape(a['title']); date=html.escape(a['date']); excerpt=html.escape(a['excerpt'])
        url=html.escape(a['link'],quote=True)
        img=f'<img src="{html.escape(a["image"],quote=True)}" alt="" loading="lazy">' if a['image'] else ''
        blocks.append(f'''<article class="item">{img}<div class="content"><div class="date">{date}</div><h2>{title}</h2><p>{excerpt}</p><a href="{url}" target="_blank" rel="noopener noreferrer">記事を読む →</a></div></article>''')
    updated=datetime.now().strftime('%Y-%m-%d')
    page='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>最新記事｜宇都宮市の公共交通を考える会</title><style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#fff;color:#25302b;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif}.wrap{max-width:900px;margin:0 auto;padding:12px}header{border-left:6px solid #19754b;padding-left:15px;margin:8px 0 18px}header h1{font-size:23px;margin:0}.item{display:flex;gap:18px;border-bottom:1px solid #dbe6de;padding:20px 0;align-items:flex-start}.item img{width:180px;height:115px;object-fit:cover;border-radius:7px;flex:none}.content{min-width:0;flex:1}.date{color:#68776f;font-size:13px}.item h2{font-size:19px;line-height:1.5;margin:2px 0 7px}.item p{font-size:14px;margin:0 0 7px;color:#44544b}.item a,.all a{color:#096e49;font-weight:700;text-decoration:none}.item a:hover,.all a:hover{text-decoration:underline}.all{text-align:center;padding:25px 0}.all a{border:1px solid #0f704a;border-radius:6px;padding:10px 20px;display:inline-block}@media(max-width:520px){.item{gap:12px}.item img{width:100px;height:80px}.item h2{font-size:16px}.item p{font-size:13px}}
</style></head><body><main class="wrap"><header><h1>最新ブログ記事</h1></header>'''
    page+=''.join(blocks)
    page+=f'<div class="all"><a href="{BLOG}" target="_blank" rel="noopener noreferrer">はてなブログの記事をすべて見る →</a></div></main></body></html>'
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(page,encoding='utf-8')
    print(f'Updated {len(articles)} articles to {OUT} ({updated})')

if __name__ == '__main__': build(fetch())
