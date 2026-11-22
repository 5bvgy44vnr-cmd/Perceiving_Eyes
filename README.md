# Perceiving Eyes

Website for **Perceiving Eyes**, the Master of Fine Arts thesis of Pramod N. Medichalam
(Computer Art Department, Savannah College of Art and Design, November 2003).

> Art is everywhere and in everything. It all depends upon the one to perceive it.

The site is a single static page: statement, the zones-of-interpretation concept (interactive),
methodology, the "Days in a Week" visual reference, the full paper with footnotes, and research
material (bibliography, notes and links).

## Layout

```
site/                     The built website. Deploy this folder as-is.
  index.html
  assets/
src/
  template.html           Page design: layout, styles, animation and scripts
  build.py                Fills the template with the paper, bibliography and links
sources/2003-original/    The original 2003 thesis website, kept unchanged
```

## Build

Needs Python 3, nothing else.

```sh
python3 src/build.py sources/2003-original src/template.html site/index.html
```

The paper (`1outline.htm`) and bibliography (`2biblio.htm`) are read from the original files,
so their text is not retyped anywhere. Edit `src/template.html` for design changes and run the
build again.

## Preview

Open `site/index.html` in a browser, or serve the folder:

```sh
python3 -m http.server --directory site 8000
```

Fonts (League Gothic, Newsreader, IBM Plex Mono) load from Google Fonts.

## Links

Every resource link from the 2003 site was checked on 18 November 2026. Only two still load
their original content, and only those are linked (`WORKING_LINKS` in `src/build.py`). All other
sources remain listed as plain-text citations in the bibliography.

## Copyright

© Pramod N. Medichalam, 2003
