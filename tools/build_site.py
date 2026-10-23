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
import os, sys, re, html, runpy
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
        n += int(s) if s.isdigit() else 1
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


def tile(o, c):
    n = html.escape(c['name'])
    return ('<figure class="card"><button type="button" data-full="%s/cards/%s" data-name="%s">'
            '<img loading="lazy" src="%s/thumbs/%s" alt="%s"></button>'
            '<figcaption><b>%s</b><span class="cost">%s</span><em>%s</em></figcaption></figure>'
            % (o, c['file'], n, o, c['file'], n, n, sym(c['cost']), html.escape(c['note'])))


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
            _, f, name, note = it
            h += ('<figure class="card land-card"><button type="button" data-full="%s/cards/%s" data-name="%s"><img loading="lazy" src="%s/thumbs/%s" alt="%s"></button>'
                  '<figcaption><b>%s</b><em>%s</em></figcaption></figure>'
                  % (o, f, html.escape(name), o, f, html.escape(name), html.escape(name), html.escape(note)))
        else:
            _, big, small = it
            h += '<div class="landbox"><b>%s</b><span>%s</span></div>' % (html.escape(big), html.escape(small))
    return h + '</div>'


SIDE_SUB = 'Swap these in against a specific opponent, or if the main deck is not working.'
PANEL = '''<div class="panel" id="panel-@OID@-@ID@" role="tabpanel" aria-labelledby="tab-@OID@-@ID@" hidden>
<p class="dl"><a href="@OID@/decks/@FILE@" download>@FILE@</a> <span>(deck file, .dck format)</span></p>
<p class="intro">@INTRO@</p>
<div class="stats"><div class="stat"><b>23</b><span>spells</span></div><div class="stat"><b>@NC@</b><span>creatures</span></div><div class="stat"><b>@NS@</b><span>non-creature spells</span></div><div class="stat"><b>17</b><span>lands</span></div><div class="stat"><b>40</b><span>cards in total</span></div></div>
<div class="curve" role="img" aria-label="Mana curve of the 23 spells">@CURVE@</div>
<p class="sub">Mana value of the 23 spells.</p>
<h2>Main deck</h2>
<h2 class="h2s">Creatures (@NC@)</h2>@CREATURES@
<h2 class="h2s">Spells (@NS@)</h2>@SPELLS@
<h2 class="h2s">Lands (17)</h2>
@LANDS@
<h2>Sideboard</h2><p class="sub">@SIDESUB@</p>@SIDE@
<p class="note">@NOTE@</p>
</div>'''


def render(o, d):
    cr, sp, sd = d['data']
    main_cards = [c for g in (cr, sp) for cs in g.values() for c in cs]
    assert len(main_cards) == 23, (o, d['id'], len(main_cards))
    curve = {}
    for c in main_cards:
        m = min(mv(c['cost']), 7); curve[m] = curve.get(m, 0) + 1
    ch = ''.join('<div class="bar"><span style="height:%dpx"></span><b>%d</b><i>%s</i></div>' % (curve.get(m, 0) * 96 // max(curve.values()), curve.get(m, 0), '7+' if m == 7 else m) for m in range(1, 8))
    assert os.path.exists(f"{R}/{o}/decks/{d['file']}"), (o, d['file'])
    rep = {'@OID@': o, '@ID@': d['id'], '@INTRO@': html.escape(d['intro']), '@FILE@': d['file'],
           '@NC@': str(sum(len(v) for v in cr.values())), '@NS@': str(sum(len(v) for v in sp.values())),
           '@CURVE@': ch, '@CREATURES@': group_html(o, cr), '@SPELLS@': group_html(o, sp), '@SIDE@': group_html(o, sd),
           '@SIDESUB@': SIDE_SUB, '@NOTE@': html.escape(d['note']), '@LANDS@': lands_html(o, d['lands'])}
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


owner_tabs, owner_sections = '', ''
for o, label in OWNERS:
    decks = load(o)
    owner_tabs += ('<button role="tab" id="otab-%s" aria-controls="owner-%s" aria-selected="false" data-owner-tab data-owner="%s">%s</button>'
                   % (o, o, o, html.escape(label)))
    if decks:
        dtabs = ''.join('<button role="tab" id="tab-%s-%s" aria-controls="panel-%s-%s" aria-selected="false" data-deck-tab data-owner="%s" data-deck="%s">%s</button>'
                        % (o, d['id'], o, d['id'], o, d['id'], html.escape(d['title'])) for d in decks)
        inner = '<div class="tabs decks" role="tablist" aria-label="%s\'s decks">%s</div>%s' % (html.escape(label), dtabs, ''.join(render(o, d) for d in decks))
    else:
        inner = '<p class="empty">No decks here yet.</p>'
    owner_sections += '<section class="owner" id="owner-%s" role="tabpanel" aria-labelledby="otab-%s" hidden>%s</section>' % (o, o, inner)

CSS = open(os.path.join(HERE, 'site.css.html')).read()
PAGE = '''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MTG Decks</title>
<meta name="description" content="40-card decks built from our Reality Fracture cards.">
@CSS@</head><body><main>
<header><h1>MTG Decks</h1></header>
<div class="tabs owners" role="tablist" aria-label="Whose decks">@OWNERTABS@</div>
@SECTIONS@
</main>
<dialog id="dlg"><img alt=""></dialog>
<script>
const dlg=document.getElementById('dlg'),img=dlg.querySelector('img');
document.addEventListener('click',e=>{const b=e.target.closest('button[data-full]');if(b){img.src=b.dataset.full;img.alt=b.dataset.name;dlg.showModal();}else if(e.target===dlg||e.target===img){dlg.close();}});
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
window.addEventListener('hashchange',()=>show(location.hash.slice(1)));
show(location.hash.slice(1));
</script></body></html>'''
page = PAGE.replace('@CSS@', CSS).replace('@OWNERTABS@', owner_tabs).replace('@SECTIONS@', owner_sections)
open(R + '/index.html', 'w').write(page)
open(R + '/.nojekyll', 'w').write('')
print(len(page))
