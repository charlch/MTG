# Helpers used by the per-person deck files (dad/decks.py, son/decks.py).
# They only build plain data; tools/build_site.py turns it into HTML.
#
# Official card images: the page looks each card up on Scryfall in the browser, by name and set
# (default set 'fra', Reality Fracture). For a card from another set pass set='xyz'. When a name
# matches several art variants (basic lands), pass cn='123' (the collector number) to pick one,
# or official=False to always show your own photo for that card.

DEFAULT_SET = 'fra'


def C(name, file, cost, note='', set=DEFAULT_SET, cn=None, official=True):
    """A card in a deck: display name (must be the real card name for the official image),
    image file in <person>/cards/, mana cost like '{1}{G}', short note."""
    return dict(name=name, file=file, cost=cost, note=note, set=set, cn=cn, official=official)


def land_tile(file, name, note, set=DEFAULT_SET, cn=None, official=True, card=None):
    """A land photo shown in the Lands section (file is in <person>/cards/).
    `name` is the label on the page; pass card='Plains' if the real card name differs from the label."""
    return ('tile', file, name, note, dict(set=set, cn=cn, official=official, card=card or name))


def land_box(big, small):
    """A text box in the Lands section, e.g. land_box('10 Forest', '1 owned, 9 to add')."""
    return ('box', big, small)
