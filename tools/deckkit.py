# Helpers used by the per-person deck files (dad/decks.py, son/decks.py).
# They only build plain data; tools/build_site.py turns it into HTML.

def C(name, file, cost, note=''):
    """A card in a deck: display name, image file in <person>/cards/, mana cost like '{1}{G}', short note."""
    return dict(name=name, file=file, cost=cost, note=note)

def land_tile(file, name, note):
    """A land photo shown in the Lands section (file is in <person>/cards/)."""
    return ('tile', file, name, note)

def land_box(big, small):
    """A text box in the Lands section, e.g. land_box('10 Forest', '1 owned, 9 to add')."""
    return ('box', big, small)
