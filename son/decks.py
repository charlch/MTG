# Son's decks: the card groups, lands, notes and the DECKS list for the index page.
# Card photos are in son/cards/ and tokens in son/tokens-and-extras/; the .dck files are in son/decks/.
from deckkit import C, land_tile, land_box

creatures = {
 '1 mana': [C('Emergency Phytomedic','emergency-phytomedic.jpg','{G/W}','1/1 that enters prepared: a cheap +1/+1 counter and 1 life'),
            C('Liliana the Faultless','liliana-the-faultless.jpg','{W}','1/1 that gains you 1 life whenever another creature or planeswalker enters')],
 '2 mana': [C('Campus Crier','campus-crier.jpg','{1}{W}','3/1; can later make a Jace planeswalker'),
            C('Marwyn, the Preserver','marwyn-the-preserver.jpg','{1}{G}','3/2 for two; can return lands'),
            C('Sureshot Sower','sureshot-sower.jpg','{1}{G}','3/1 with reach, or discard to kill a flyer'),
            C('Solarium Sentry','solarium-sentry.jpg','{G}{W}','3/3 for two; gains 2 life when an opponent casts a cheap spell'),
            C('Living Library','living-library.jpg','{2}','0/4 blocker; late on, sacrifice it for 6 to shuffle away their best creature')],
 '3 mana': [C('Lyra, Archangel of Dawn','lyra-archangel-of-dawn.jpg','{2}{W}','3/3 flyer that grows every time you gain life, and so do your other Angels'),
            C('Keeper of the Quiet Hour','keeper-of-the-quiet-hour.jpg','{3}','3/2 colourless; makes a Jace planeswalker')],
 '4 mana': [C('Blossom-Blessed Angel','blossom-blessed-angel.jpg','{3}{W}','2/4 flying, vigilance; its prepared spell gains life'),
            C('Jiang Yanggu, Never Alone','jiang-yanggu-never-alone.jpg','{3}{G}','2/2 that makes Mowu, a 3/3 Dog, and untaps your tokens')],
 'X and big': [C('Fblthp, Knows the Way','fblthp-knows-the-way.jpg','{X}{G}{G}','Fetches X basic lands with different names; power equals the land types you have'),
               C('Ruric Thar, Magecrusher','ruric-thar-magecrusher.jpg','{5}{G}{G}','7/7 reach, vigilance, trample; cannot be countered')],
}
spells = {
 'Removal': [C('Prophesied End','prophesied-end.jpg','{1}{W}','Destroy a creature (they draw a card unless it was attacking)'),
             C('Compel Brutality','compel-brutality.jpg','{1}{G}','Your creature deals damage to theirs')],
 'Tricks': [C('Tethermage\'s Advantage','tethermages-advantage.jpg','{G}','+2/+2 and reach, and untap it'),
            C('Ferocity of the Hunt','ferocity-of-the-hunt.jpg','{1}{G}','Flash aura: +1/+0, deathtouch, and it comes back if it dies'),
            C('Predictive Preparations','predictive-preparations.jpg','{1}{W}','Counters on two creatures, with flashback')],
 'Lifegain and value': [C('Something Worth Saving','something-worth-saving.jpg','{1}{G}','Mill four, take a permanent, gain 1 life'),
                        C('Restore with Empathy','restore-with-empathy.jpg','{2}{G}','Return any permanent, gain 4 life'),
                        C('Way of the Mentor','way-of-the-mentor.jpg','{2}{W}','Makes a Jace with 5 loyalty; your life gain adds loyalty to it'),
                        C('Hexhaven Battalion','hexhaven-battalion.jpg','{4}{W}{W}','Three 2/2 Cadets and a Jace; discard for 2 to fetch a basic land')],
}
side = {
 'Sideboard': [C('No Admittance','no-admittance.jpg','{1}{R}','3 damage to anything. Needs a red source, so only if you add a few Mountains (Fblthp and Hexhaven can fetch them).'),
               C('Konstrari Charm','konstrari-charm.jpg','{R}{G}','6 damage to a flyer, or a counters-and-trample trick. Same red problem as No Admittance.'),
               C('Primal Witchstalker','primal-witchstalker.jpg','{1}{B}{G}','2/1 menace that mills four and returns a land. Needs black.'),
               C('Avatar of Burgeoning Echoes','avatar-of-burgeoning-echoes.jpg','{G}{U}','Pumps your planeswalkers and draws; needs blue.')],
}

LANDS_GW = [land_tile('vigorbloom-annex.jpg', 'Vigorbloom Annex', 'Green/white land; enters tapped unless you control a planeswalker'),
            land_box('9 Forest', 'all 9 to add'), land_box('8 Plains', 'all 8 to add')]

NOTE_GW = ('This is every playable green, white and colourless card in the collection, so there is no real choice left: 22 spells and 18 lands, '
           'because only 22 cards fit the two colours. The Jace tokens from Campus Crier, Keeper of the Quiet Hour, Way of the Mentor and Hexhaven Battalion draw and surveil, '
           'and Lyra and Way of the Mentor reward every life you gain. Fblthp can fetch basics, so the 18 lands can still hit seven mana for Ruric Thar. '
           'Living Library is the weakest card; swap it for a splashed No Admittance if you add Mountains.')

DECKS = [
 dict(id='green-white', title='Green-White Lifegain', file='green-white-lifegain.dck',
      intro='Cheap green bodies and white lifegain, with Lyra and Way of the Mentor turning every point of life into counters and cards.',
      data=(creatures, spells, side), lands=LANDS_GW, note=NOTE_GW),
]
