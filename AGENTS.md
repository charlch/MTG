# AGENTS.md

This repo holds photos of our Reality Fracture (FRA) cards, deck lists built from them, and a static GitHub Pages site that shows the decks. There are two separate collections: Dad's (`dad/`) and Son's (`son/`). They never share cards, decks or files, so a deck is only ever built from the cards in its own person's folder.

## Layout

```
index.html              generated page: Dad / Son tabs on top, that person's decks below
tools/                  shared by both people
  build_site.py         generator for index.html and the thumbnails (needs Python with OpenCV, cv2)
  deckkit.py            small helpers used by each person's decks.py
  site.css.html         page styles
dad/  and  son/         identical layout, one per person
  decks.py              card data, lands, notes and the DECKS list for this person's tab
  decks/                one .dck file per deck, in the Forge format ([metadata], [Main], [Sideboard], lines like `1 Card Name`)
  cards/                one photo per card, named after the card (foil and non-foil copies are marked in the file name)
  tokens-and-extras/    tokens, emblems and counter sticker sheets
  photos/               the original photos the card images were cut from
  thumbs/               small card images used by the page; build_site.py creates them
  README.md             index of this person's card photos
```

- `index.html` is generated, so don't edit it by hand. Run `python3 tools/build_site.py` from anywhere in the repo; it rebuilds both people at once.
- Dad's card details are in the Google Sheet "MTG card list - FRA collection". Son's sheet isn't linked here yet.
- A person with an empty `DECKS` list shows "No decks here yet." on their tab.

## Official card images

The page has an "Official | Our photos" switch (Official is the default, the choice is remembered in the browser). Official images are looked up on Scryfall by the visitor's browser when the page loads (one batch request, cached for a week), not stored in the repo. If Scryfall can't be reached, a card isn't found, or an image fails to load, that card shows our own photo instead.

- The lookup uses the card's `name` and `set` (default `fra`). So `name` in `C(...)` must be the real card name, and for a card from another set pass `set='xyz'`.
- A name that has several art variants (basic lands) can pass `cn='123'` (the collector number) to pick one, or `official=False` to always show our own photo. The photographed basics in `dad/decks.py` use `official=False` because their collector numbers aren't known yet.
- `land_tile(...)` takes the same options, plus `card='Real Name'` if the label on the page differs from the card name.
- Nothing in the build needs internet. It was tested against a mocked Scryfall only, so after changing the lookup code, open the live page and check that official images appear.

## Which person is it for?

Work out whose cards or deck it is before touching anything, and only edit that person's folder. If it isn't clear, ask. Don't copy files between `dad/` and `son/`, and don't use one person's card photos in the other's deck.

## When a new deck is suggested

Whenever you suggest a new deck, also add it to the repo in the same change. `<p>` below means `dad` or `son`.

1. Write a `.dck` file for it in `<p>/decks/`. Use plain card names with no set codes. The main deck must be 40 cards including lands (23 spells and 17 lands, or 22 and 18 if there are not enough playable cards), and the sideboard lists the swap-in options.
2. Add a deck entry to `DECKS` in `<p>/decks.py`. Each entry needs an id (unique within that person), a title, the `.dck` file name, an intro, its cards grouped for display, its lands and a note. The `.dck` link at the top of each tab comes from the entry's file name. Use `C(...)`, `land_tile(...)` and `land_box(...)` from `deckkit`, as `dad/decks.py` does. Use each card's real name so the official image can be found.
3. Run `python3 tools/build_site.py` to rebuild `index.html` and the thumbnails, then check the new tab in a browser at desktop and phone widths. Links to a deck look like `index.html#dad/black-green`.
4. Commit and push to `main`.

If you only swap a few cards in an existing deck to make a variant, treat it as a new deck and follow the same steps.

## Adding photos for a new set of cards

Put the card photos in `<p>/cards/` (tokens and the like in `<p>/tokens-and-extras/`) and the originals in `<p>/photos/`. Add the new cards to that person's `README.md` index. The "All cards" tab on each person's page is generated from the tables in that README (Dad's `| Item | Image | Photo |` layout or Son's `| Card | Copies | Image | Set / notes | Photos |` layout), so keep those tables accurate and rebuild with `tools/build_site.py`; anything under a "Not in the latest photos" heading is left out.

## Notes

- Every card image used on the page must exist in that person's `cards/` folder. If the generator fails on a missing file, check the file name against the list in `<p>/cards/`.
- The generator also checks that each deck has 23 spells (22 is allowed when a collection has too few playable cards in its colours; the page then shows 18 lands) and that its `.dck` file exists in `<p>/decks/`.
- Dad: the only basic lands photographed so far are one foil Forest, two Plains and a full-art Mountain. All other basics in a deck list are lands still to be added.
