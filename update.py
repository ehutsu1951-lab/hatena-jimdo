import json, html, re, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import requests
from bs4 import BeautifulSoup

BLOG='https://stoputsunomiyalrt.hatenablog.com/'
BASE=Path(__file__).resolve().parent
DB=BASE/'articles.json'
PAGE=BASE/'index.html'
HEAD={'User-Agent':'Mozilla/5.0 (compatible; HatenaJimdoArchive/2.0)'}

def safeurl(src):
    url=urljoin(BLOG,src or '')
    return url if urlparse(url).scheme in ('http','https') else ''

def get_archive():
    if DB.exists():
        return {x['url']:x for x in json.loads(DB.read_text(encoding='utf-8'))}
    return {}

def collect():
    session=requests.Session(); session.headers.update(HEAD)
    found={}; seen=set(); target=BLOG
    for number in range(1,201):
        if not target or target in seen: break
        seen.add(target)
        response=session.get(target,timeout=30); response.raise_for_status()
        soup=BeautifulSoup(response.text,'html.parser')
        entries=soup.select('article.entry, article.hentry, .hentry')
        for a in entries:
            t=a.select_one('.entry-title a, a.entry-title-link, h1.entry-title a, h2.entry-title a')
            if not t: continue
            url=safeurl(t.get('href'))
            if not url.startswith(BLOG+'entry/'):continue
            content=a.select_one('.entry-content')
            paras=[p.get_text(' ',strip=True) for p in content.select('p')] if content else []
            excerpt=next((p for p in paras if len(p)>15),'')
            if not excerpt and content: excerpt=content.get_text(' ',strip=True)
            pic=content.select_one('img') if content else None
            img=safeurl(pic.get('data-src') or pic.get('src')) if pic else ''
            dt=a.select_one('time[datetime], .entry-date, .date')
            date=(dt.get('datetime') or dt.get_text(' ',strip=True)) if dt else ''
            date=date[:10].replace('/','-')
            found[url]={'url':url,'title':t.get_text(' ',strip=True),'date':date,'excerpt':excerpt[:200],'image':img}
        nextlink=soup.select_one('a.pager-next, a[rel="next"], .pager-next a, .pagination-next a')
        nxt=safeurl(nextlink.get('href')) if nextlink else ''
        if nxt and urlparse(nxt).netloc!=urlparse(BLOG).netloc:nxt=''
        if not nxt and entries:
            # Hatena's page links use a cursor rather than /page/2.
            nextlink=next((e for e in soup.select('a[href]') if '次のページ' in e.get_text(' ',strip=True)),None)
            nxt=safeurl(nextlink.get('href')) if nextlink else ''
        target=nxt
        if number%15==0: print('Scanned',number,'pages:',len(found),'articles')
        if not entries:break
        time.sleep(.1)
    if not found:raise RuntimeError('記事を取得できませんでした。公開ページまたは記事HTMLを確認してください。')
    return found

def generate(items):
    data=json.dumps(items,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>公共交通を考える会｜ブログ記事</title><style>
:root{color-scheme:light;--green:#0a6651;--ink:#173229}*{box-sizing:border-box}html{scroll-behavior:smooth}body{font-family:system-ui,"Yu Gothic",Meiryo,sans-serif;margin:0;color:var(--ink);background:linear-gradient(145deg,#e5f3eb,#f5f8f4 50%,#e7effb)}main{max-width:1100px;margin:0 auto;padding:27px 18px 65px}.hero{padding:34px 32px;border-radius:25px;background:linear-gradient(120deg,#0d6858,#0c8174 65%,#3ab094);box-shadow:0 16px 35px #07543f36,inset 0 1px #ffffff70;color:white;position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-85px;top:-120px;width:320px;height:320px;border-radius:50%;background:#fff2;pointer-events:none}h1{font-size:clamp(1.35rem,3vw,2.1rem);margin:5px 0 10px}.hero p{margin:0;line-height:1.75}.eyebrow{font-size:.81rem;letter-spacing:.12em;font-weight:700;opacity:.87}.controls{display:flex;gap:12px;flex-wrap:wrap;margin:25px 0 8px}.controls input,.controls select{font:inherit;border:1px solid #d6e8dc;border-radius:15px;background:white;box-shadow:0 5px 14px #1e644112;padding:14px 16px;min-width:185px;outline-offset:3px}.controls input{flex:1}.summary{color:#506d60;font-size:.92rem;margin:8px 0 20px}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.article-card{background:white;border-radius:20px;border:1px solid #ffffffb8;overflow:hidden;box-shadow:0 9px 17px #123c2923,0 2px 5px #123c2912;transition:transform .22s,box-shadow .22s;display:flex;flex-direction:column}.article-card:hover{transform:translateY(-5px);box-shadow:0 22px 30px #123c2932,0 3px 9px #123c2910}.thumb{width:100%;height:160px;object-fit:cover;background:linear-gradient(130deg,#197966,#85c9a6)}.thumb-placeholder{width:100%;height:130px;background:linear-gradient(120deg,#bfdccd,#e4f2eb);display:flex;align-items:center;justify-content:center;color:#16725f;font-size:1.06rem;font-weight:700}.card-body{padding:20px;display:flex;flex-direction:column;flex:1}.date{font-size:.76rem;color:#597266;font-weight:650}.article-card h2{font-size:1.12rem;line-height:1.65;margin:8px 0}.article-card h2 a{color:#143b2e;text-decoration:none}.article-card h2 a:hover{text-decoration:underline}.excerpt{font-size:.86rem;line-height:1.85;color:#586a5f;margin:0 0 20px;flex:1;overflow-wrap:anywhere}.go{display:inline-block;align-self:flex-start;background:linear-gradient(115deg,#08644b,#159078);color:white;text-decoration:none;border-radius:999px;padding:10px 17px;font-size:.87rem;font-weight:700;box-shadow:0 5px 10px #04583c25}.more{text-align:center;margin:24px}.more button{font:inherit;padding:13px 25px;border-radius:999px;background:white;border:1px solid #99bdaa;color:#0b674d;box-shadow:0 7px 18px #123c2920;cursor:pointer}.foot{text-align:center;margin:22px}.foot a{color:#0a6c54}.empty{text-align:center;padding:36px}.more[hidden]{display:none!important}@media(max-width:620px){main{padding:12px 10px 50px}.hero{padding:25px 20px;border-radius:19px}.cards{grid-template-columns:1fr;gap:16px}.thumb{height:170px}.controls input,.controls select{width:100%}}
</style></head><body><main><section class="hero"><div class="eyebrow">UTSUNOMIYA PUBLIC TRANSPORT</div><h1>宇都宮市の公共交通を考える会</h1><p>はてなブログの最新記事から過去記事まで。検索・年月別にご覧いただけます。</p></section><div class="controls"><input id="search" type="search" placeholder="記事タイトル・内容から検索" aria-label="記事を検索"><select id="month" aria-label="年月を選ぶ"><option value="">すべての年月</option></select></div><p class="summary" id="count" role="status"></p><div class="cards" id="results"></div><div class="more"><button id="more" type="button">過去の記事をさらに見る ↓</button></div><p class="foot"><a href="https://stoputsunomiyalrt.hatenablog.com/" target="_blank" rel="noopener noreferrer">はてなブログのサイトを開く ↗</a></p></main><script id="all-articles" type="application/json">__DATA__</script><script>
const all=JSON.parse(document.getElementById('all-articles').textContent),input=document.getElementById('search'),month=document.getElementById('month'),list=document.getElementById('results'),count=document.getElementById('count'),more=document.getElementById('more');let shown=12;for(const m of [...new Set(all.map(x=>(x.date||'').slice(0,7)).filter(Boolean))].sort().reverse()){const option=document.createElement('option');option.value=m;option.textContent=m.replace('-','年')+'月';month.append(option)}function render(){const q=input.value.trim().toLowerCase(),filtered=all.filter(x=>(!month.value||(x.date||'').startsWith(month.value))&&(!q||((x.title||'')+' '+(x.excerpt||'')).toLowerCase().includes(q)));count.textContent='表示可能な記事：'+filtered.length+'件';list.replaceChildren();if(!filtered.length){const p=document.createElement('p');p.className='empty';p.textContent='該当する記事がありません。';list.append(p)}for(const a of filtered.slice(0,shown)){const article=document.createElement('article');article.className='article-card';if(a.image){const img=document.createElement('img');img.className='thumb';img.src=a.image;img.loading='lazy';img.alt='';article.append(img)}else{const box=document.createElement('div');box.className='thumb-placeholder';box.textContent='公共交通を考える';article.append(box)}const body=document.createElement('div');body.className='card-body';const date=document.createElement('span');date.className='date';date.textContent=a.date||'日付未取得';const heading=document.createElement('h2');const titleLink=document.createElement('a');titleLink.href=a.url;titleLink.target='_blank';titleLink.rel='noopener noreferrer';titleLink.textContent=a.title;heading.append(titleLink);const excerpt=document.createElement('p');excerpt.className='excerpt';excerpt.textContent=a.excerpt||'';const link=document.createElement('a');link.className='go';link.href=a.url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='この記事を読む →';body.append(date,heading,excerpt,link);article.append(body);list.append(article)}more.hidden=filtered.length<=shown}input.addEventListener('input',()=>{shown=12;render()});month.addEventListener('change',()=>{shown=12;render()});more.addEventListener('click',()=>{shown+=12;render()});render();
</script></body></html>'''
    PAGE.write_text(template.replace('__DATA__',data),encoding='utf-8')

if __name__=='__main__':
    previous=get_archive(); current=collect(); previous.update(current)
    arr=sorted(previous.values(),key=lambda x:(x['date'],x['url']),reverse=True)
    DB.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    generate(arr)
    print('Saved',len(arr),'articles')
