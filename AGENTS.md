# AGENTS.md

This repo holds photos of my Fate Reforged Arena (FRA) cards, deck lists built from them, and a static GitHub Pages site that shows the decks.

## Layout

- `cards/`: one photo per card, named after the card (foil and non-foil copies are marked in the file name).
- `tokens-and-extras/`: tokens, the emblem and the counter sticker sheet.
- `photos/`: the original photos the card images were cut from.
- `thumbs/`: small versions of the card images used by the page. `tools/build_site.py` creates them.
- `*.dck`: one deck file per deck, in the Forge format (`[metadata]`, `[Main]`, `[Sideboard]`, lines like `1 Card Name`).
- `index.html`: the deck page. It is generated, so don't edit it by hand.
- `tools/build_site.py` and `tools/site.css.html`: the generator for `index.html`. It needs Python with OpenCV (`cv2`).
- The card details are in the Google Sheet "MTG card list - FRA collection".

## When a new deck is suggested

Whenever you suggest a new deck, also add it to the repo in the same change:

1. Write a `.dck` file for it in the repo root. Use plain card names with no set codes. The main deck must be 40 cards including lands, and the sideboard lists the swap-in options.
2. Add a tab for it on the index page by adding a deck entry to `DECKS` in `tools/build_site.py`. Each entry needs an id, a title, the `.dck` file name, an intro, its cards grouped for display, its lands and a note. The `.dck` link at the top of each tab comes from the entry's file name.
3. Run `python3 tools/build_site.py` to rebuild `index.html` and the thumbnails, then check the new tab in a browser at desktop and phone widths.
4. Commit and push to `main`.

If you only swap a few cards in an existing deck to make a variant, treat it as a new deck and follow the same steps.

## Notes

- Every card image used on the page must exist in `cards/`. If the generator fails on a missing file, check the file name against the list in `cards/`.
- The only basic lands photographed so far are one foil Forest, two Plains and a full-art Mountain. All other basics in a deck list are lands still to be added.
