import os, html, cv2
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
os.makedirs(f'{R}/thumbs', exist_ok=True)
def thumb(fn):
    out = f'{R}/thumbs/{fn}'
    if not os.path.exists(out):
        im = cv2.imread(f'{R}/cards/{fn}'); h, w = im.shape[:2]
        cv2.imwrite(out, cv2.resize(im, (360, int(h * 360 / w)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 80])
# (name, file, cost, note, qty-label)
C = lambda n, f, c, note='': dict(name=n, file=f, cost=c, note=note)
creatures = {
 '1 mana': [C('Emergency Phytomedic','emergency-phytomedic.jpg','{G/W}','Enters prepared: a cheap +1/+1 counter and 1 life')],
 '2 mana': [C('Carnivorous Cultivator','carnivorous-cultivator.jpg','{1}{G}','Deathtouch 2/3 that gets lands back'),
            C('Marwyn, the Preserver','marwyn-the-preserver.jpg','{1}{G}','3/2 for two; can return lands'),
            C('Sureshot Sower','sureshot-sower.jpg','{1}{G}','Reach, or discard to kill a flyer'),
            C('Konstrari Improviser','konstrari-improviser.jpg','{1}{R/G}','Hybrid, so green pays for it; makes a Heartwood')],
 '3 mana': [C('Greenhouse Propagator','greenhouse-propagator.jpg','{2}{G}','Mana creature that gains life'),
            C('Budding Insurgent','budding-insurgent.jpg','{2}{G}','3/3 vigilance; can destroy an artifact or enchantment'),
            C('Tinybones, Pocket Nuisance','tinybones-pocket-nuisance.jpg','{2}{B}','Makes the opponent discard'),
            C('Theoretical Necromancer','theoretical-necromancer.jpg','{2}{B}','4/1; later returns a creature from the graveyard')],
 '4 mana': [C('Rampart Hunter','rampart-hunter.jpg','{3}{B}','Deathtouch 3/3 with a combat trick'),
            C('Teyo, Diamondblade Mage','teyo-diamondblade-mage.jpg','{3}{B}','Flash 3/1; gives deathtouch'),
            C('Titanbones, Towering Heart','titanbones-towering-heart.jpg','{3}{G}','Grows whenever you gain life')],
 '5 mana': [C('Hungering Puppetbeast','hungering-puppetbeast.jpg','{3}{G}{G}','5/5 that makes a Heartwood token'),
            C('Wrecking Gecko','wrecking-gecko.jpg','{4}{G}','5/5 with ward; can fetch a basic land'),
            C('Hapatra, the Desert Fang','hapatra-the-desert-fang.jpg','{2}{B}{B}{G}','Shrinks an opposing creature')],
 '6+ mana': [C('Apex Witchstalker','apex-witchstalker.jpg','{4}{B}{B}','6/4 menace; gains life; can fetch a basic land'),
             C('Ruric Thar, Magecrusher','ruric-thar-magecrusher.jpg','{5}{G}{G}','7/7 reach, vigilance, trample')],
}
spells = {
 'Removal': [C('Silence the Echo','silence-the-echo.jpg','{1}{B}','Destroy a creature or planeswalker'),
             C('Compel Brutality','compel-brutality.jpg','{1}{G}','Your creature deals damage to theirs'),
             C('Extended Absence','extended-absence-foil.jpg','{3}{B}','Exile a creature (foil copy)'),
             C('Extended Absence','extended-absence-non-foil.jpg','{3}{B}','Exile a creature (non-foil copy)')],
 'Value': [C('Restore with Empathy','restore-with-empathy.jpg','{2}{G}','Return any permanent, gain 4 life'),
           C('Bestial Incursion','bestial-incursion.jpg','{3}{G}','4/4 trampler, with flashback')],
}
side = {
 'Sideboard': [C('Solve for Disappointment','solve-for-disappointment.jpg','{1}{B}','Take their best nonland card'),
               C('Cast Away Doubt','cast-away-doubt.jpg','{2}{B}','Draw two; 2 damage to each player'),
               C('Puppet Crafting','puppet-crafting.jpg','{1}{G}','Needs an artifact or enchantment to target'),
               C('Yargle, Glutton of Urborg','yargle-glutton-of-urborg.jpg','{4}{B}','9/3 with no abilities')],
 'Also considered': [C('Loot, the Anomaly','loot-the-anomaly.jpg','{2}{B}','Printed -2/4; plays as a 2/4 attacker'),
                     C('Stingerquill Voxmancer','stingerquill-voxmancer.jpg','{R/B}','Hybrid one-drop that pings the opponent'),
                     C('Eye of Jace','eye-of-jace.jpg','{1}','Colourless; needs a full graveyard')],
}
thumb('forest-foil-full-art.jpg')
def mv(cost):
    import re
    n = 0
    for s in re.findall(r'\{([^}]+)\}', cost):
        n += int(s) if s.isdigit() else 1
    return n

import copy
def make_eddy():
    cr, sp, sd = copy.deepcopy(creatures), copy.deepcopy(spells), copy.deepcopy(side)
    prop = [c for c in cr['3 mana'] if c['name'] == 'Greenhouse Propagator'][0]
    cr['3 mana'].remove(prop)
    yar = [c for c in sd['Sideboard'] if c['name'].startswith('Yargle')][0]
    sd['Sideboard'].remove(yar)
    cr['5 mana'].append(yar)
    sd['Sideboard'].insert(0, prop)
    return cr, sp, sd

def land_tile(f, name, note):
    thumb(f)
    return ('<figure class="card land-card"><button type="button" data-full="cards/%s" data-name="%s"><img loading="lazy" src="thumbs/%s" alt="%s"></button>'
            '<figcaption><b>%s</b><em>%s</em></figcaption></figure>' % (f, name, f, name, name, note))
def land_box(big, small):
    return '<div class="landbox"><b>%s</b><span>%s</span></div>' % (big, small)
LANDS_BG = ('<div class="lands">' + land_tile('forest-foil-full-art.jpg', 'Forest (foil)', 'The one basic land I have so far')
            + land_box('10 Forest', '1 owned, 9 to add') + land_box('7 Swamp', 'all 7 to add') + '</div>')
LANDS_WU = ('<div class="lands">' + land_tile('plains.jpg', 'Plains', 'One of my two Plains')
            + land_tile('plains-full-art.jpg', 'Plains (full-art)', 'The other Plains I have')
            + land_box('9 Plains', '2 owned, 7 to add') + land_box('8 Island', 'all 8 to add') + '</div>')

wu_creatures = {
 '2 mana': [C('Fatehold Chronologist','fatehold-chronologist.jpg','{1}{W/U}','1/2 flyer; its prepared spell makes a 2/2 and surveils'),
            C('Campus Crier','campus-crier.jpg','{1}{W}','3/1; can later make a Jace planeswalker'),
            C('Tomik, Orzhov Lawmage','tomik-orzhov-lawmage-foil.jpg','{1}{W}','2/1 flyer (foil copy)'),
            C('Tomik, Orzhov Lawmage','tomik-orzhov-lawmage-non-foil.jpg','{1}{W}','2/1 flyer (non-foil copy)'),
            C('Surveillance Phantasm','surveillance-phantasm.jpg','{1}{U}','2/3 flyer; attacks once you surveil'),
            C('Teyo, Lightshield Expert','teyo-lightshield-expert.jpg','{1}{W}','Flash; protects a permanent from removal')],
 '3 mana': [C('Rescue Girl, First Responder','rescue-girl-first-responder.jpg','{2}{W}','1/3 flyer that can rebuy enter effects'),
            C('Graft Surgeon','graft-surgeon.jpg','{2}{W}','2/2 that passes its counters on when it dies'),
            C('Divining Duelist','divining-duelist.jpg','{2}{U}','Flash 3/2; taps a blocker or loots')],
 '4 mana': [C('Semester Foreseer','semester-foreseer.jpg','{3}{U}','3/4 that surveils and makes a 2/2'),
            C('Blossom-Blessed Angel','blossom-blessed-angel.jpg','{3}{W}','2/4 flying, vigilance'),
            C('Desperate Futurescribe','desperate-futurescribe.jpg','{2}{W}{U}','3/4 flyer that buffs a creature each combat')],
 '5 mana': [C('Saheeli, Consul of Oversight','saheeli-consul-of-oversight.jpg','{3}{W}{W}','4/4 flyer; makes Thopters when you surveil'),
            C('Undulating Witness','undulating-witness.jpg','{4}{U}','3/5 flyer; can fetch a basic land'),
            C('Fateshaper Aspirant','fateshaper-aspirant.jpg','{4}{W}','3/4 that rebuys a legendary card or protects a creature')],
 '6 mana': [C('Ruric Thar, Biomagus','ruric-thar-biomagus.jpg','{4}{U}{U}','4/6 flying, prowess; draws when targeted')],
}
wu_spells = {
 'Removal': [C('Memory Trap','memory-trap.jpg','{2}{W}','Exile a nonland permanent while it stays out (foil)'),
             C('Gideon\'s Memorial','gideons-memorial.jpg','{1}{W}','Boosts tokens; discard it for 4 damage to an attacker or blocker')],
 'Value': [C('Way of the Mind Sculptor','way-of-the-mind-sculptor.jpg','{4}{U}','Makes a Jace that surveils and draws (foil)'),
           C('Sphinx\'s Approach','sphinxs-approach.jpg','{1}{U}{U}','Instant: draw two cards'),
           C('Predictive Preparations','predictive-preparations.jpg','{1}{W}','Counters on two creatures, with flashback'),
           C('Unsummon','unsummon.jpg','{U}','Cheap tempo trick'),
           C('Eye of Jace','eye-of-jace.jpg','{1}','Surveils every turn')],
}
wu_side = {
 'Sideboard': [C('Refute Destiny','refute-destiny.jpg','{1}{W}','Exiles a green or blue creature; surveils'),
               C('Precise Redaction','precise-redaction.jpg','{1}{U}','Counters a white or black spell'),
               C('Generous Revival','generous-revival.jpg','{2}{W}','Brings back a cheap creature, with flashback'),
               C('Afterthought Sentry','afterthought-sentry.jpg','{2}','Colourless 2/2 that can fly')],
}
NOTE_WU = ('Undulating Witness can fetch a basic land. If your opponents have lots of green or blue creatures, '
           'bring in Refute Destiny. Samut, Tyrant of Naktamun and Emergency Phytomedic are the next cuts to consider.')
NOTE_BG = ('Apex Witchstalker and Wrecking Gecko can fetch a basic land, which helps if the mana goes wrong. '
        'For a more consistent version, play 11 Forest and 6 Swamp and swap Hapatra and Apex Witchstalker '
        'for Loot, the Anomaly and Stingerquill Voxmancer.')
LANDS_WR = ('<div class="lands">' + land_tile('dedicated-commons.jpg', 'Dedicated Commons', 'Red/white land; enters tapped unless you control a planeswalker')
            + land_tile('plains.jpg', 'Plains', 'One of my two Plains')
            + land_tile('plains-full-art.jpg', 'Plains (full-art)', 'The other Plains I have')
            + land_tile('mountain-full-art.jpg', 'Mountain (full-art)', 'The one Mountain I have so far')
            + land_box('9 Plains', '2 owned, 7 to add') + land_box('7 Mountain', '1 owned, 6 to add') + land_box('1 Dedicated Commons', 'owned') + '</div>')

wr_creatures = {
 '1 mana': [C('Stingerquill Voxmancer','stingerquill-voxmancer.jpg','{R/B}','Hybrid, so red pays for it; pings the opponent each turn'),
            C('Marwyn, the Clearcutter','marwyn-the-clearcutter.jpg','{R}','2/1 for one; a legend, so it makes Wrath of the Bloodmane cheaper')],
 '2 mana': [C('Campus Crier','campus-crier.jpg','{1}{W}','3/1; can later make a Jace planeswalker'),
            C('Tomik, Orzhov Lawmage','tomik-orzhov-lawmage-foil.jpg','{1}{W}','2/1 flyer; a legend (foil copy)'),
            C('Fatehold Chronologist','fatehold-chronologist.jpg','{1}{W/U}','Hybrid, so white pays for it; 1/2 flyer whose prepared spell makes a 2/2 and surveils'),
            C('Teyo, Lightshield Expert','teyo-lightshield-expert.jpg','{1}{W}','Flash; protects a creature from removal and grows it')],
 '3 mana': [C('Rescue Girl, First Responder','rescue-girl-first-responder.jpg','{2}{W}','1/3 flyer that can rebuy enter effects'),
            C('Graft Surgeon','graft-surgeon.jpg','{2}{W}','2/2 that passes its counters on when it dies'),
            C('Hallway Heckler','hallway-heckler.jpg','{2}{R}','2/3 that loots every turn'),
            C('Pyre Rhymer','pyre-rhymer.jpg','{1}{R}{R}','3/3 with prowess; the double red is the hardest cost in the deck')],
 '4 mana': [C('Heartstring Puller','heartstring-puller-foil.jpg','{3}{R}','Trample, and makes a 2/2 Cadet (foil copy)'),
            C('Heartstring Puller','heartstring-puller-non-foil.jpg','{3}{R}','Trample, and makes a 2/2 Cadet (non-foil copy)'),
            C('Blossom-Blessed Angel','blossom-blessed-angel.jpg','{3}{W}','2/4 flying, vigilance')],
 '5 mana': [C('Saheeli, Consul of Oversight','saheeli-consul-of-oversight.jpg','{3}{W}{W}','4/4 flyer; makes Thopters when you surveil'),
            C('Fateshaper Aspirant','fateshaper-aspirant.jpg','{4}{W}','3/4 that rebuys a legendary card or protects a creature')],
}
wr_spells = {
 'Removal': [C('No Admittance','no-admittance.jpg','{1}{R}','3 damage to any target; adds to your Jace'),
             C('Wrath of the Bloodmane','wrath-of-the-bloodmane.jpg','{2}{R}','4 damage; one cheaper with a legend (Marwyn, Tomik, Teyo, Rescue Girl, Saheeli)'),
             C('Memory Trap','memory-trap.jpg','{2}{W}','Exile a nonland permanent while it stays out (foil)'),
             C('Gideon\'s Memorial','gideons-memorial.jpg','{1}{W}','Boosts your tokens; discard it for 4 damage to an attacker or blocker')],
 'Tricks and value': [C('Charge the Sanctum','charge-the-sanctum.jpg','{2}{R/W}','Hybrid; team pump, or a +1/+1 counter with first strike'),
                      C('Blazing Crescendo','blazing-crescendo.jpg','{1}{R}','+3/+1 and you may play the top card of your library'),
                      C('Predictive Preparations','predictive-preparations.jpg','{1}{W}','Counters on two creatures, with flashback'),
                      C('Generous Revival','generous-revival.jpg','{2}{W}','Brings back a cheap creature, with flashback')],
}
wr_side = {
 'Sideboard': [C('Refute Destiny','refute-destiny.jpg','{1}{W}','Exiles a green or blue creature; surveils'),
               C('Tomik, Orzhov Lawmage','tomik-orzhov-lawmage-non-foil.jpg','{1}{W}','The second copy; a legend, so only the first one stays in play'),
               C('Artifist Acumen','artifist-acumen.jpg','{R}','First strike for your team and a card'),
               C('Afterthought Sentry','afterthought-sentry.jpg','{2}','Colourless 2/2 that can fly')],
}
NOTE_WR = ('This is the strongest 40 I can make from the cards left after the black-green deck, so it shares its white cards with the White-Blue Flyers deck: build one at a time. '
           'Pyre Rhymer needs two red sources and there are only 8, so cut it for Afterthought Sentry if the red does not show up. '
           'Bring in Refute Destiny against green or blue creatures. Dedicated Commons enters untapped once you have a Jace from Campus Crier or No Admittance.')
DECKS = [
 dict(id='black-green', title='Black-Green', data=(creatures, spells, side), file='black-green.dck', lands=LANDS_BG, note=NOTE_BG,
      intro='A 40-card deck built from my Reality Fracture cards. Green carries the early game and the big finishers. Black adds removal and graveyard value. Tap any card to see it full size.'),
 dict(id='eddy', title='Eddy', data=make_eddy(), file='eddy.dck', lands=LANDS_BG, note=NOTE_BG,
      intro='The same deck with one swap: Yargle, Glutton of Urborg comes in for Greenhouse Propagator. That trades a mana creature for a big 9/3 body. Tap any card to see it full size.'),
 dict(id='white-blue', title='White-Blue Flyers', data=(wu_creatures, wu_spells, wu_side), file='white-blue-flyers.dck', lands=LANDS_WU, note=NOTE_WU,
      intro='A different deck from the same cards: ten flyers and a surveil theme. Saheeli turns every surveil into a Thopter, and Way of the Mind Sculptor and Campus Crier make Jace planeswalkers that surveil and draw. It has less removal than the black-green decks, so it wins by evasion and card quality. Tap any card to see it full size.'),
 dict(id='white-red', title='White-Red', data=(wr_creatures, wr_spells, wr_side), file='white-red.dck', lands=LANDS_WR, note=NOTE_WR,
      intro='The best deck I can build from everything except the black-green cards. White supplies the best creatures: a run of cheap flyers, Blossom-Blessed Angel and Saheeli. Red adds the burn (No Admittance and Wrath of the Bloodmane, with Memory Trap and Gideon\'s Memorial from white) and two Heartstring Pullers. Tap any card to see it full size.'),
]
for d in DECKS:
    for grp in d['data']:
        for cards in grp.values():
            for c in cards:
                thumb(c['file']); assert os.path.exists(f"{R}/cards/{c['file']}"), c

def sym(cost):
    import re
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
def tile(c):
    n = html.escape(c['name'])
    return ('<figure class="card"><button type="button" data-full="cards/%s" data-name="%s">'
            '<img loading="lazy" src="thumbs/%s" alt="%s"></button>'
            '<figcaption><b>%s</b><span class="cost">%s</span><em>%s</em></figcaption></figure>'
            % (c['file'], n, c['file'], n, n, sym(c['cost']), html.escape(c['note'])))
def group_html(groups):
    h = ''
    for g, cs in groups.items():
        head_ = '' if g == 'Sideboard' else '<h3>%s <small>%d</small></h3>' % (html.escape(g), len(cs))
        h += head_ + '<div class="grid">%s</div>' % ''.join(tile(c) for c in cs)
    return h
SIDE_SUB = 'Swap these in against a specific opponent, or if the main deck is not working.'
PANEL = '''<div class="panel" id="panel-@ID@" role="tabpanel" aria-labelledby="tab-@ID@" hidden>
<p class="dl"><a href="@FILE@" download>@FILE@</a> <span>(deck file, .dck format)</span></p>
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
def render(d):
    cr, sp, sd = d['data']
    main_cards = [c for g in (cr, sp) for cs in g.values() for c in cs]
    assert len(main_cards) == 23, (d['id'], len(main_cards))
    curve = {}
    for c in main_cards:
        m = min(mv(c['cost']), 7); curve[m] = curve.get(m, 0) + 1
    ch = ''.join('<div class="bar"><span style="height:%dpx"></span><b>%d</b><i>%s</i></div>' % (curve.get(m, 0) * 96 // max(curve.values()), curve.get(m, 0), '7+' if m == 7 else m) for m in range(1, 8))
    rep = {'@ID@': d['id'], '@INTRO@': html.escape(d['intro']), '@FILE@': d['file'],
           '@NC@': str(sum(len(v) for v in cr.values())), '@NS@': str(sum(len(v) for v in sp.values())),
           '@CURVE@': ch, '@CREATURES@': group_html(cr), '@SPELLS@': group_html(sp), '@SIDE@': group_html(sd),
           '@SIDESUB@': SIDE_SUB, '@NOTE@': html.escape(d['note']), '@LANDS@': d['lands']}
    out = PANEL
    for k, v in rep.items(): out = out.replace(k, v)
    return out
tabs = ''.join('<button role="tab" id="tab-%s" aria-controls="panel-%s" aria-selected="false" data-id="%s">%s</button>' % (d['id'], d['id'], d['id'], d['title']) for d in DECKS)
panels = ''.join(render(d) for d in DECKS)
CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.css.html')).read()
PAGE = '''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MTG Decks</title>
<meta name="description" content="40-card decks built from my Reality Fracture cards.">
@CSS@</head><body><main>
<header><h1>MTG Decks</h1></header>
<div class="tabs" role="tablist" aria-label="Decks">@TABS@</div>
@PANELS@
</main>
<dialog id="dlg"><img alt=""></dialog>
<script>
const dlg=document.getElementById('dlg'),img=dlg.querySelector('img');
document.addEventListener('click',e=>{const b=e.target.closest('button[data-full]');if(b){img.src=b.dataset.full;img.alt=b.dataset.name;dlg.showModal();}else if(e.target===dlg||e.target===img){dlg.close();}});
const tabs=[...document.querySelectorAll('[role=tab]')];
function show(id){if(!tabs.some(t=>t.dataset.id===id))id=tabs[0].dataset.id;tabs.forEach(t=>{const on=t.dataset.id===id;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;document.getElementById('panel-'+t.dataset.id).hidden=!on;});document.title=tabs.find(t=>t.dataset.id===id).textContent+' | MTG Decks';}
tabs.forEach((t,i)=>{t.addEventListener('click',()=>{history.replaceState(null,'','#'+t.dataset.id);show(t.dataset.id);});t.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){const n=tabs[(i+(e.key==='ArrowRight'?1:tabs.length-1))%tabs.length];n.focus();n.click();}});});
window.addEventListener('hashchange',()=>show(location.hash.slice(1)));
show(location.hash.slice(1));
</script></body></html>'''
page = PAGE.replace('@CSS@', CSS).replace('@TABS@', tabs).replace('@PANELS@', panels)
open(R + '/index.html', 'w').write(page)
open(R + '/.nojekyll', 'w').write('')
print(len(page))
