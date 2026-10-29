"""Builds index.html (and the thumbnails) for every person listed in OWNERS.

Each person has a folder (dad/, son/) with the same layout:
  <person>/decks.py             the DECKS list and card data for that person
  <person>/decks/*.dck          deck files (Forge format)
  <person>/cards/               one photo per card
  <person>/tokens-and-extras/   tokens, emblems, sticker sheets
  <person>/photos/              the original photos the card images were cut from
  <person>/thumbs/              small card images used by the page (created here)

Run from anywhere:  python3 tools/build_site.py   (needs Python with OpenCV, cv2)
"""
import os, sys, re, html, runpy, json
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)  # repo root
sys.path.insert(0, HERE)   # so each <person>/decks.py can `from deckkit import ...`

OWNERS = [('dad', 'Dad'), ('son', 'Son')]  # (folder, tab label)


def thumb(owner, fn):
    out = f'{R}/{owner}/thumbs/{fn}'
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = cv2.imread(f'{R}/{owner}/cards/{fn}'); h, w = im.shape[:2]
        cv2.imwrite(out, cv2.resize(im, (360, int(h * 360 / w)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 80])


def mv(cost):
    n = 0
    for s in re.findall(r'\{([^}]+)\}', cost):
        n += int(s) if s.isdigit() else (0 if s == 'X' else 1)
    return n


def sym(cost):
    out = ''
    for s_ in re.findall(r'\{([^}]+)\}', cost):
        cls = 'n'
        if s_ == 'G': cls = 'g'
        elif s_ == 'B': cls = 'b'
        elif s_ in ('G/W', 'R/G'): cls = 'hg'
        elif s_ == 'R/B': cls = 'hb'
        elif s_ == 'R': cls = 'r'
        elif s_ == 'W': cls = 'w'
        elif s_ == 'R/W': cls = 'hrw'
        elif s_ == 'U': cls = 'u'
        elif s_ == 'W/U': cls = 'hwu'
        out += '<i class="s %s">%s</i>' % (cls, html.escape(s_.replace('/', '')))
    return out


def sf_attrs(card, set_, cn, official):
    """data attributes the page script uses to look up the official image on Scryfall (none = always own photo)."""
    if not official:
        return ''
    a = ' data-sf-set="%s"' % html.escape(set_.lower())
    return a + (' data-sf-cn="%s"' % html.escape(str(cn)) if cn else ' data-sf-name="%s"' % html.escape(card))


def tile(o, c):
    n = html.escape(c['name'])
    return ('<figure class="card"><button type="button" data-full="%s/cards/%s" data-own-full="%s/cards/%s" data-name="%s">'
            '<img loading="lazy" src="%s/thumbs/%s" data-own="%s/thumbs/%s" alt="%s"%s></button>'
            '<figcaption><b>%s</b><span class="cost">%s</span><em>%s</em></figcaption></figure>'
            % (o, c['file'], o, c['file'], n, o, c['file'], o, c['file'], n,
               sf_attrs(c['name'], c['set'], c['cn'], c['official']), n, sym(c['cost']), html.escape(c['note'])))


def group_html(o, groups):
    h = ''
    for g, cs in groups.items():
        head_ = '' if g == 'Sideboard' else '<h3>%s <small>%d</small></h3>' % (html.escape(g), len(cs))
        h += head_ + '<div class="grid">%s</div>' % ''.join(tile(o, c) for c in cs)
    return h


def lands_html(o, items):
    h = '<div class="lands">'
    for it in items:
        if it[0] == 'tile':
            _, f, name, note, opt = it
            h += ('<figure class="card land-card"><button type="button" data-full="%s/cards/%s" data-own-full="%s/cards/%s" data-name="%s">'
                  '<img loading="lazy" src="%s/thumbs/%s" data-own="%s/thumbs/%s" alt="%s"%s></button>'
                  '<figcaption><b>%s</b><em>%s</em></figcaption></figure>'
                  % (o, f, o, f, html.escape(name), o, f, o, f, html.escape(name),
                     sf_attrs(opt['card'], opt['set'], opt['cn'], opt['official']), html.escape(name), html.escape(note)))
        else:
            _, big, small = it
            h += '<div class="landbox"><b>%s</b><span>%s</span></div>' % (html.escape(big), html.escape(small))
    return h + '</div>'


SIDE_SUB = 'Swap these in against a specific opponent, or if the main deck is not working.'
PANEL = '''<div class="panel" id="panel-@OID@-@ID@" role="tabpanel" aria-labelledby="tab-@OID@-@ID@" hidden>
<p class="dl"><a href="@OID@/decks/@FILE@" download>@FILE@</a> <span>(deck file, .dck format)</span></p>
<p class="intro">@INTRO@</p>
<div class="stats"><div class="stat"><b>@NSP@</b><span>spells</span></div><div class="stat"><b>@NC@</b><span>creatures</span></div><div class="stat"><b>@NS@</b><span>non-creature spells</span></div><div class="stat"><b>@NL@</b><span>lands</span></div><div class="stat"><b>40</b><span>cards in total</span></div></div>
<div class="curve" role="img" aria-label="Mana curve of the @NSP@ spells">@CURVE@</div>
<p class="sub">Mana value of the @NSP@ spells.</p>
<h2>Main deck</h2>
<h2 class="h2s">Creatures (@NC@)</h2>@CREATURES@
<h2 class="h2s">Spells (@NS@)</h2>@SPELLS@
<h2 class="h2s">Lands (@NL@)</h2>
@LANDS@
<h2>Sideboard</h2><p class="sub">@SIDESUB@</p>@SIDE@
<p class="note">@NOTE@</p>
<div class="setup" data-setup="@SETUP@" data-basics="@BASICS@"><h2>Card numbers</h2><p class="sub">Just the collector numbers, by set, to pull this deck quickly.</p><div class="setup-out" aria-live="polite"></div></div>
</div>'''

BASIC_RE = re.compile(r'(forest|plains|island|swamp|mountain)\b', re.I)


def setup_data(d):
    """What the 'Card numbers' list at the bottom of a deck needs: [set, card name, collector number or None, 'm' main / 's' sideboard]
    for every non-basic card (the page fills in numbers it does not know from Scryfall), plus the basic land counts as text."""
    cr, sp, sd = d['data']
    rows = []
    for g in (cr, sp):
        for cs in g.values():
            rows += [[c['set'].lower(), c['name'], c['cn'], 'm'] for c in cs]
    for it in d['lands']:
        if it[0] == 'tile' and not BASIC_RE.match(it[4]['card']):
            rows.append([it[4]['set'].lower(), it[4]['card'], it[4]['cn'], 'm'])
    rows += [[c['set'].lower(), c['name'], c['cn'], 's'] for c in sd.get('Sideboard', [])]
    basics = [it[1] for it in d['lands'] if it[0] == 'box' and re.match(r'\d+ (Forest|Plains|Island|Swamp|Mountain)$', it[1])]
    return rows, ', '.join(basics)


def render(o, d):
    cr, sp, sd = d['data']
    main_cards = [c for g in (cr, sp) for cs in g.values() for c in cs]
    # normally 23 spells + 17 lands; a person with too few playable cards may run 22 + 18
    assert len(main_cards) in (22, 23), (o, d['id'], len(main_cards))
    curve = {}
    for c in main_cards:
        m = min(mv(c['cost']), 7); curve[m] = curve.get(m, 0) + 1
    ch = ''.join('<div class="bar"><span style="height:%dpx"></span><b>%d</b><i>%s</i></div>' % (curve.get(m, 0) * 96 // max(curve.values()), curve.get(m, 0), '7+' if m == 7 else m) for m in range(1, 8))
    assert os.path.exists(f"{R}/{o}/decks/{d['file']}"), (o, d['file'])
    rep = {'@NSP@': str(len(main_cards)), '@NL@': str(40 - len(main_cards)), '@OID@': o, '@ID@': d['id'], '@INTRO@': html.escape(d['intro']), '@FILE@': d['file'],
           '@NC@': str(sum(len(v) for v in cr.values())), '@NS@': str(sum(len(v) for v in sp.values())),
           '@CURVE@': ch, '@CREATURES@': group_html(o, cr), '@SPELLS@': group_html(o, sp), '@SIDE@': group_html(o, sd),
           '@SIDESUB@': SIDE_SUB, '@NOTE@': html.escape(d['note']), '@LANDS@': lands_html(o, d['lands'])}
    rows, basics = setup_data(d)
    rep['@SETUP@'] = html.escape(json.dumps(rows, separators=(',', ':')))
    rep['@BASICS@'] = html.escape(basics)
    out = PANEL
    for k, v in rep.items(): out = out.replace(k, v)
    return out


def load(o):
    """Load <o>/decks.py, make sure every image it uses exists and has a thumbnail."""
    decks = runpy.run_path(f'{R}/{o}/decks.py')['DECKS']
    ids = [d['id'] for d in decks]
    assert len(ids) == len(set(ids)), f'duplicate deck id in {o}/decks.py'
    for d in decks:
        files = [c['file'] for grp in d['data'] for cards in grp.values() for c in cards]
        files += [it[1] for it in d['lands'] if it[0] == 'tile']
        for f in files:
            assert os.path.exists(f'{R}/{o}/cards/{f}'), (o, f)
            thumb(o, f)
    return decks



NO_OFFICIAL = ('forest', 'plains', 'island', 'swamp', 'mountain')


def read_inventory(o):
    """Every card and token listed in <o>/README.md tables -> (cards, tokens), each a list of dicts.
    Accepts both layouts: Dad's  | Item | Image | Photo |  and Son's  | Card | Copies | Image | Set / notes | Photos |."""
    cards, tokens = [], []
    text = open(f'{R}/{o}/README.md', encoding='utf-8').read()
    text = text.split('## Not in the latest photos')[0]  # cards that are no longer in the collection are not listed
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.startswith('|') else []
        m = next((re.match(r'\[(.+?)\]\((.+?)\)$', c) for c in cells if re.match(r'\[.+?\]\(.+?\)$', c)), None)
        if not m or not cells:
            continue
        path = m.group(2)
        name = cells[0]
        idx = cells.index(m.group(0))
        copies = int(cells[1]) if idx == 2 and cells[1].isdigit() else 1
        notes = cells[3] if idx == 2 and len(cells) > 3 else ''
        assert os.path.exists(f'{R}/{o}/{path}'), (o, path)
        base = re.sub(r'\s*\(.*?\)', '', name).strip()
        base = re.sub(r'\s+token$', '', base) if path.startswith('tokens') else base
        label = name
        setcode = (notes.split(',')[0].split(' ')[0].strip().lower() if notes else 'fra') or 'fra'
        tag = ', '.join(x for x in [notes] if x)
        if 'foil' in name.lower() and 'foil' not in tag.lower():
            tag = (tag + ', ' if tag else '') + ('non-foil' if 'non-foil' in name.lower() else 'foil')
        official = (path.startswith('cards/') and setcode not in ('spg',) and base.lower() not in NO_OFFICIAL
                    and not re.search(r'full-art', name.lower()))
        rec = dict(name=label, card=base, file=path, copies=copies, set=setcode, tag=tag or 'FRA', official=official)
        (tokens if path.startswith('tokens') else cards).append(rec)
    key = lambda r: re.sub(r'[^a-z0-9]', '', r['card'].lower() + r['name'].lower())
    return sorted(cards, key=key), sorted(tokens, key=key)


def all_thumb(o, rel):
    out = f'{R}/{o}/thumbs/{rel}'
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = cv2.imread(f'{R}/{o}/{rel}'); h, w = im.shape[:2]
        cv2.imwrite(out, cv2.resize(im, (360, int(h * 360 / w)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 80])


def all_tile(o, r):
    all_thumb(o, r['file'])
    n = html.escape(r['name'])
    cnt = '<span class="cost">&times;%d</span>' % r['copies'] if r['copies'] > 1 else ''
    return ('<figure class="card" data-search="%s" data-sort-name="%s" data-sort-set="%s"><button type="button" data-full="%s/%s" data-own-full="%s/%s" data-name="%s">'
            '<img loading="lazy" src="%s/thumbs/%s" data-own="%s/thumbs/%s" alt="%s"%s></button>'
            '<figcaption><b>%s</b>%s<em>%s</em><small class="meta"></small></figcaption></figure>'
            % (html.escape((r['name'] + ' ' + r['tag']).lower()), html.escape(r['card']), html.escape(r['set']), o, r['file'], o, r['file'], n, o, r['file'], o, r['file'], n,
               sf_attrs(r['card'], r['set'], None, r['official']), n, cnt, html.escape(r['tag'])))


def render_all(o, label):
    cards, tokens = read_inventory(o)
    total = sum(r['copies'] for r in cards)
    stats = ('<div class="stats"><div class="stat"><b>%d</b><span>cards in total</span></div><div class="stat"><b>%d</b><span>different cards</span></div>'
             '<div class="stat"><b>%d</b><span>tokens and extras</span></div></div>' % (total, len(cards), len(tokens)))
    h = ('<div class="panel" id="panel-%s-all" role="tabpanel" aria-labelledby="tab-%s-all" hidden>'
         '<p class="intro">Every card in %s\'s collection, in alphabetical order. Tap a card to see it larger. &times;2 means there are two copies.</p>%s'
         '<div class="find"><label class="sortl">Sort by <select data-sort aria-label="Sort cards by">'
         '<option value="name">Name</option><option value="mv">Mana value</option><option value="power">Power</option><option value="toughness">Toughness</option>'
         '<option value="rarity">Rarity</option><option value="price">Price</option><option value="color">Colour</option><option value="type">Card type</option><option value="set">Set</option></select></label> '
         '<button type="button" class="dir" data-dir aria-label="Reverse the sort order">A to Z</button> '
         '<input type="search" data-filter placeholder="Search by name or set (for example TLA or foil)" aria-label="Search cards"> <span class="found" aria-live="polite"></span></div>'
         '<p class="sub sortnote" aria-live="polite"></p>'
         % (o, o, html.escape(label), stats))
    h += '<h2 class="h2s">Cards (%d)</h2><div class="grid">%s</div>' % (total, ''.join(all_tile(o, r) for r in cards))
    if tokens:
        h += '<h2 class="h2s">Tokens and extras (%d)</h2><div class="grid">%s</div>' % (sum(r['copies'] for r in tokens), ''.join(all_tile(o, r) for r in tokens))
    return h + '</div>'


owner_tabs, owner_sections = '', ''
for o, label in OWNERS:
    decks = load(o)
    owner_tabs += ('<button role="tab" id="otab-%s" aria-controls="owner-%s" aria-selected="false" data-owner-tab data-owner="%s">%s</button>'
                   % (o, o, o, html.escape(label)))
    dtabs = ''.join('<button role="tab" id="tab-%s-%s" aria-controls="panel-%s-%s" aria-selected="false" data-deck-tab data-owner="%s" data-deck="%s">%s</button>'
                    % (o, d['id'], o, d['id'], o, d['id'], html.escape(d['title'])) for d in decks)
    dtabs += ('<button role="tab" id="tab-%s-all" aria-controls="panel-%s-all" aria-selected="false" data-deck-tab data-owner="%s" data-deck="all">All cards</button>' % (o, o, o))
    inner = ('<div class="tabs decks" role="tablist" aria-label="%s\'s decks and cards">%s</div>%s%s'
             % (html.escape(label), dtabs, ''.join(render(o, d) for d in decks), render_all(o, label)))
    owner_sections += '<section class="owner" id="owner-%s" role="tabpanel" aria-labelledby="otab-%s" hidden>%s</section>' % (o, o, inner)

CSS = open(os.path.join(HERE, 'site.css.html')).read()
PAGE = '''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MTG Decks</title>
<meta name="description" content="40-card decks built from our Reality Fracture cards.">
@CSS@</head><body><main>
<header><h1>MTG Decks</h1>
<div class="imgmode"><div role="radiogroup" aria-label="Card images"><button type="button" role="radio" data-mode="official" aria-checked="true">Official</button><button type="button" role="radio" data-mode="mine" aria-checked="false">Our photos</button></div><span id="imgstatus" aria-live="polite"></span></div></header>
<div class="tabs owners" role="tablist" aria-label="Whose decks">@OWNERTABS@</div>
@SECTIONS@
<footer class="legal">Official card images come from <a href="https://scryfall.com">Scryfall</a>, loaded in your browser. Magic: The Gathering card images are &copy; Wizards of the Coast.</footer>
</main>
<dialog id="dlg"><img alt=""></dialog>
<script>
const dlg=document.getElementById('dlg'),img=dlg.querySelector('img');
document.addEventListener('click',e=>{const b=e.target.closest('button[data-full]');if(b){img.dataset.fb=b.dataset.ownFull;img.src=b.dataset.full;img.alt=b.dataset.name;dlg.showModal();}else if(e.target===dlg||e.target===img){dlg.close();}});
img.addEventListener('error',()=>{if(img.dataset.fb&&img.getAttribute('src')!==img.dataset.fb)img.src=img.dataset.fb;});
const otabs=[...document.querySelectorAll('[data-owner-tab]')],dtabs=[...document.querySelectorAll('[data-deck-tab]')],last={};
function show(h){
  let [o,d]=h.split('/');
  if(!otabs.some(t=>t.dataset.owner===o)){const m=dtabs.find(t=>t.dataset.deck===o);if(m){d=o;o=m.dataset.owner;}else{o=otabs[0].dataset.owner;d=null;}} /* bare #deck links from before the Dad/Son split */
  const mine=dtabs.filter(t=>t.dataset.owner===o);
  if(!mine.some(t=>t.dataset.deck===d))d=mine.length?mine[0].dataset.deck:null;
  last[o]=d;
  otabs.forEach(t=>{const on=t.dataset.owner===o;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;document.getElementById('owner-'+t.dataset.owner).hidden=!on;});
  dtabs.forEach(t=>{const on=t.dataset.owner===o&&t.dataset.deck===d;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;document.getElementById('panel-'+t.dataset.owner+'-'+t.dataset.deck).hidden=!on;});
  const on=otabs.find(t=>t.dataset.owner===o).textContent,dt=mine.find(t=>t.dataset.deck===d);
  document.title=(dt?dt.textContent+' | ':'')+on+' | MTG Decks';
}
function go(h){history.replaceState(null,'','#'+h);show(h);}
function wire(list,hash){list.forEach((t,i)=>{t.addEventListener('click',()=>go(hash(t)));t.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){const g=list.filter(x=>x.parentNode===t.parentNode),k=g.indexOf(t),n=g[(k+(e.key==='ArrowRight'?1:g.length-1))%g.length];n.focus();n.click();}});});}
wire(otabs,t=>t.dataset.owner+(last[t.dataset.owner]?'/'+last[t.dataset.owner]:''));
wire(dtabs,t=>t.dataset.owner+'/'+t.dataset.deck);
document.querySelectorAll('[data-filter]').forEach(inp=>inp.addEventListener('input',()=>{const p=inp.closest('.panel'),q=inp.value.trim().toLowerCase(),fs=[...p.querySelectorAll('figure[data-search]')];let n=0;fs.forEach(f=>{const on=!q||f.dataset.search.includes(q);f.hidden=!on;if(on)n++;});p.querySelector('.found').textContent=q?n+' shown':'';}));
window.addEventListener('hashchange',()=>show(location.hash.slice(1)));
show(location.hash.slice(1));
/* Official card images: looked up on Scryfall in the browser (one batch request, cached for a week).
   Any problem (offline, blocked, card not found, image fails) falls back to our own photo. */
const MODE_KEY='mtg-img-mode',CACHE_KEY='mtg-official-v3',TTL=7*864e5;
const store={get(k){try{return localStorage.getItem(k);}catch(e){return null;}},set(k,v){try{localStorage.setItem(k,v);}catch(e){}}};
let mode=store.get(MODE_KEY)==='mine'?'mine':'official',failed=false,cache={};
try{cache=JSON.parse(store.get(CACHE_KEY)||'{}')||{};}catch(e){cache={};}
const cardImgs=[...document.querySelectorAll('img[data-own]')],sfImgs=cardImgs.filter(i=>i.dataset.sfSet);
const sfId=(set,cn,name)=>cn?'c|'+set+'|'+cn:'n|'+set+'|'+name.toLowerCase();
const idOf=i=>sfId(i.dataset.sfSet,i.dataset.sfCn,i.dataset.sfName);
/* "Card numbers" list at the bottom of each deck: [set, name, collector number or null, 'm' main / 's' sideboard] per card */
const setups=[...document.querySelectorAll('.setup')].map(el=>({el,rows:JSON.parse(el.dataset.setup),basics:el.dataset.basics,out:el.querySelector('.setup-out')}));
let looked=false;
const modeBtns=[...document.querySelectorAll('[data-mode]')],statusEl=document.getElementById('imgstatus');
function apply(){
  let missing=0;
  cardImgs.forEach(i=>{
    const b=i.closest('button'),c=i.dataset.sfSet&&cache[idOf(i)];
    if(mode==='official'&&i.dataset.sfSet&&!(c&&c.n))missing++;
    const hit=mode==='official'&&c&&c.n&&!i.dataset.bad;
    const src=hit?c.n:i.dataset.own;
    if(i.getAttribute('src')!==src)i.src=src;
    b.dataset.full=hit?(c.l||c.n):b.dataset.ownFull;
  });
  modeBtns.forEach(b=>b.setAttribute('aria-checked',b.dataset.mode===mode));
  statusEl.textContent=mode!=='official'?'':failed?'Could not reach Scryfall, showing our photos.':missing?missing+' card'+(missing>1?'s have':' has')+' no official image yet, showing our photo.':'';
}
cardImgs.forEach(i=>i.addEventListener('error',()=>{if(i.getAttribute('src')!==i.dataset.own){i.dataset.bad='1';apply();}}));
async function lookup(){
  const need=new Map();
  const want=[...sfImgs.map(i=>[i.dataset.sfSet,i.dataset.sfCn,i.dataset.sfName]),...setups.flatMap(s=>s.rows.map(r=>[r[0],r[2],r[1]]))];
  want.forEach(([set,cn,name])=>{const id=sfId(set,cn,name),c=cache[id];if(!c||Date.now()-c.t>TTL)need.set(id,cn?{set,collector_number:cn}:{name,set});});
  const list=[...need.entries()];
  failed=false;
  for(let s=0;s<list.length;s+=75){
    const chunk=list.slice(s,s+75);
    try{
      const r=await fetch('https://api.scryfall.com/cards/collection',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({identifiers:chunk.map(e=>e[1])})});
      if(!r.ok)throw new Error('HTTP '+r.status);
      const j=await r.json(),by=new Map();
      for(const c of j.data||[]){
        const u=c.image_uris||(c.card_faces&&c.card_faces[0]&&c.card_faces[0].image_uris);
        if(!u||!u.normal)continue;
        const f0=c.card_faces&&c.card_faces[0]||{},pr=c.prices||{};
        const rec={n:u.normal,l:u.large||u.normal,t:Date.now(),cn:c.collector_number,m:{cmc:c.cmc,p:c.power!=null?c.power:f0.power,th:c.toughness!=null?c.toughness:f0.toughness,r:c.rarity,c:(c.colors||f0.colors||[]).join(''),ty:c.type_line||'',usd:parseFloat(pr.usd||pr.usd_foil||pr.usd_etched)||null}},nm=c.name.toLowerCase();
        by.set('c|'+c.set+'|'+c.collector_number,rec);by.set('n|'+c.set+'|'+nm,rec);by.set('n|'+c.set+'|'+nm.split(' // ')[0],rec);
      }
      chunk.forEach(([id])=>{cache[id]=by.get(id)||{n:null,t:Date.now()};});
    }catch(e){failed=true;}
    if(s+75<list.length)await new Promise(r=>setTimeout(r,120));
  }
  if(list.length&&!failed)store.set(CACHE_KEY,JSON.stringify(cache));
  looked=true;
  apply();sortAll();renderSetups();
}
/* Card numbers: grouped by three-letter set code, numbers in order, "x2" when a deck has two copies of the same card. */
const cnKey=n=>{const v=parseInt(n,10);return [isNaN(v)?1e9:v,String(n)];};
function setupText(rows,want){
  const bySet=new Map(),unknown=[];
  rows.filter(r=>r[3]===want).forEach(r=>{
    const c=cache[sfId(r[0],r[2],r[1])],cn=r[2]||(c&&c.cn);
    if(!cn){unknown.push(r[1]);return;}
    const m=bySet.get(r[0])||new Map();m.set(cn,(m.get(cn)||0)+1);bySet.set(r[0],m);
  });
  const sets=[...bySet.keys()].sort((a,b)=>(a==='fra'?'':a).localeCompare(b==='fra'?'':b)); /* FRA first, as it is most of the cards */
  return {sets:sets.map(s=>({set:s.toUpperCase(),nums:[...bySet.get(s).entries()].sort((a,b)=>{const x=cnKey(a[0]),y=cnKey(b[0]);return x[0]-y[0]||x[1].localeCompare(y[1]);}).map(([n,k])=>k>1?n+' ×'+k:n).join(', ')})),unknown};
}
function renderSetups(){
  setups.forEach(s=>{
    const main=setupText(s.rows,'m'),side=setupText(s.rows,'s'),miss=main.unknown.length+side.unknown.length;
    const line=t=>t.sets.map(x=>'<div class="setrow"><b>'+x.set+'</b><span>'+x.nums+'</span></div>').join('');
    let h='<h3>Main deck</h3>'+line(main)+(s.basics?'<p class="sub">Plus the basic lands: '+s.basics.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</p>':'');
    if(side.sets.length)h+='<h3>Sideboard</h3>'+line(side);
    if(miss)h+='<p class="sub">'+(looked?(failed?'Could not reach Scryfall, so '+miss+' card number'+(miss>1?'s are':' is')+' missing.':miss+' card'+(miss>1?'s were':' was')+' not found on Scryfall: '+main.unknown.concat(side.unknown).map(n=>n.replace(/&/g,'&amp;').replace(/</g,'&lt;')).join(', ')+'.'):'Looking up card numbers…')+'</p>';
    s.out.innerHTML=h;
  });
}
modeBtns.forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.mode;store.set(MODE_KEY,mode);apply();if(mode==='official')lookup();}));
apply();
renderSetups();
lookup();
/* All cards tab: sorting. Name and set always work; the rest use the card data Scryfall returns (mana value, power, rarity, price...). */
const RAR={common:1,uncommon:2,rare:3,mythic:4,special:5,bonus:5},COL='WUBRG',TYPES=['Land','Creature','Planeswalker','Artifact','Enchantment','Instant','Sorcery'];
const colorRank=c=>c===''?100:c.length>1?50+c.length:COL.indexOf(c)+1;
const typeRank=t=>{const i=TYPES.findIndex(x=>t.includes(x));return i<0?99:i;};
const num=v=>{const n=parseFloat(v);return isNaN(n)?null:n;};
const KEYS={
  name:{get:f=>f.dataset.sortName,lo:'A to Z',hi:'Z to A',txt:1},
  set:{get:f=>f.dataset.sortSet,lo:'A to Z',hi:'Z to A',txt:1},
  mv:{get:(f,m)=>m&&m.cmc!=null?m.cmc:null,lo:'Low to high',hi:'High to low'},
  power:{get:(f,m)=>m?num(m.p):null,lo:'Low to high',hi:'High to low',first:'hi'},
  toughness:{get:(f,m)=>m?num(m.th):null,lo:'Low to high',hi:'High to low',first:'hi'},
  rarity:{get:(f,m)=>m&&m.r?RAR[m.r]||0:null,lo:'Common first',hi:'Rarest first',first:'hi'},
  price:{get:(f,m)=>m&&m.usd!=null?m.usd:null,lo:'Cheapest first',hi:'Most valuable first',first:'hi'},
  color:{get:(f,m)=>m?colorRank(m.c):null,lo:'W U B R G, then gold',hi:'Gold first',first:'lo'},
  type:{get:(f,m)=>m?typeRank(m.ty):null,lo:'Lands first',hi:'Lands last',first:'lo'}
};
const metaOf=f=>{const i=f.querySelector('img[data-sf-set]'),c=i&&cache[idOf(i)];return c&&c.m||null;};
function metaText(m){
  const b=[];
  if(m.cmc!=null)b.push('MV '+m.cmc);
  if(m.p!=null&&m.th!=null)b.push(m.p+'/'+m.th);
  if(m.r)b.push(m.r[0].toUpperCase()+m.r.slice(1));
  if(m.usd!=null)b.push('$'+m.usd.toFixed(2));
  return b.join(' · ');
}
function sortAll(){
  document.querySelectorAll('.panel[id$="-all"]').forEach(p=>{
    const sel=p.querySelector('[data-sort]'),btn=p.querySelector('[data-dir]'),k=KEYS[sel.value],note=p.querySelector('.sortnote'),grid=p.querySelector('.grid');
    const figs=[...grid.children];
    figs.forEach(f=>{const m=metaOf(f);f.querySelector('.meta').textContent=m?metaText(m):'';});
    const desc=btn.dataset.desc==='1';
    btn.textContent=desc?k.hi:k.lo;
    let nodata=0;
    const rows=figs.map((f,i)=>{const v=k.get(f,metaOf(f));if(v==null)nodata++;return {f,i,v};});
    rows.sort((a,b)=>{
      if(a.v==null||b.v==null)return a.v==null&&b.v==null?a.i-b.i:a.v==null?1:-1;  /* cards without data always go last */
      let d=k.txt?a.v.localeCompare(b.v,'en',{sensitivity:'base'}):a.v-b.v;
      if(d===0)d=a.f.dataset.sortName.localeCompare(b.f.dataset.sortName,'en',{sensitivity:'base'});
      return desc?(k.txt?-d:-d):d;
    });
    rows.forEach(r=>grid.appendChild(r.f));
    note.textContent=k.txt?'':nodata===figs.length?'Sorting by this needs card details from Scryfall, which could not be loaded right now.':nodata?nodata+' card'+(nodata>1?'s have':' has')+' no Scryfall details (basic lands and special printings), so they are listed last.':'';
  });
}
document.querySelectorAll('.panel[id$="-all"] [data-sort]').forEach(sel=>sel.addEventListener('change',()=>{const p=sel.closest('.panel'),btn=p.querySelector('[data-dir]'),k=KEYS[sel.value];btn.dataset.desc=k.first==='hi'?'1':'0';sortAll();}));
document.querySelectorAll('.panel[id$="-all"] [data-dir]').forEach(btn=>btn.addEventListener('click',()=>{btn.dataset.desc=btn.dataset.desc==='1'?'0':'1';sortAll();}));
sortAll();
</script></body></html>'''
page = PAGE.replace('@CSS@', CSS).replace('@OWNERTABS@', owner_tabs).replace('@SECTIONS@', owner_sections)
open(R + '/index.html', 'w').write(page)
open(R + '/.nojekyll', 'w').write('')
print(len(page))
