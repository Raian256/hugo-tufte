# Tufte Hugo Theme, for a personal site

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](code_of_conduct.md)

A theme for the [static site generator Hugo](https://gohugo.io) built on [Tufte-css](https://github.com/edwardtufte/tufte-css): wide margins, sidenotes, ET Book, and not much else.

This fork is meant for a **personal site** rather than a plain blog. It is somewhere to keep short essays on whatever you are thinking about, set with the care of a printed book, next to a record of what you read and watch. It gives you:

- **A home page like a book's opening.** A motto, a few lines about you, then your posts gathered under topic headings, each with a gloss in the margin.
- **Essays with margins.** Sidenotes, margin notes, epigraphs and KaTeX math, as in Tufte's own books.
- **A reading log.** Books you have finished, with ratings, a line or two of review, and a link to the full essay when there is one, all kept in a single data file.
- **A film diary.** Your [Letterboxd](https://letterboxd.com/) diary pulled in at build time: posters, ratings, likes and reviews, with the posters served from your own site.
- **A way home.** A small running head on every inner page, with the site title and menu, like the header on a book's page.

The theme holds everything that isn't yours: layouts, styles, fonts, the post archetype. Your site holds only content (posts, `content/_index.md`, `data/books.toml`) and configuration (the motto, topics, menus, usernames). To make a site like the author's with your own writing, you shouldn't need a single template of your own.

## Lineage

Hugo-Tufte has changed hands a few times:

- The original: [shawnohare/hugo-tufte](https://github.com/shawnohare/hugo-tufte)
- Then [slashformotion/hugo-tufte](https://github.com/slashformotion/hugo-tufte)
- Then [loikein/hugo-tufte](https://github.com/loikein/hugo-tufte), which became the _de facto_ third repo
- This fork, [Raian256/hugo-tufte](https://github.com/Raian256/hugo-tufte), which keeps it working on current Hugo and adds the personal-site features above

## Quickstart

### Prerequisite: Hugo Extended

You'll need Hugo **Extended**, since this theme uses SCSS. The reading log and film diary need version **0.156 or newer**.

- On Windows, with [Chocolatey](https://chocolatey.org/):
  ```shell
  choco install hugo-extended # remember, you might need admin privs
  ```
- On macOS, with [Homebrew](https://brew.sh/):
  ```shell
  brew install hugo
  ```
- On Linux, download the `hugo_extended` release from [GitHub](https://github.com/gohugoio/hugo/releases), or use your package manager if it ships a recent enough version.

### Check out the example site

```shell
git clone https://github.com/Raian256/hugo-tufte.git
cd hugo-tufte/exampleSite
hugo server --buildDrafts --disableFastRender
```

Then open `localhost:1313` or wherever it says in browser.

The showcase pages are:

- `The big old test page`
- `Tufte CSS`
- `Books`, the reading log
- The home page itself, configured under `params.home` in `exampleSite/config.yaml`

### For a new site

```shell
hugo new site <your-site-name>
cd <your-site-name>
git submodule add https://github.com/Raian256/hugo-tufte.git themes/hugo-tufte
```

Add `theme: 'hugo-tufte'` to your `config.yaml` to let your site know to actually use _this_ theme, specifically.

Then run `hugo server --buildDrafts --disableFastRender` and open `localhost:1313` or wherever it says in browser.

New posts made with `hugo new posts/<name>.md` start from the theme's archetype, which has a `categories` field for placing the post under a home page topic.

For small styling changes of your own, add `static/css/hugo-tufte-override.css` to your site; it is loaded after the theme's CSS.

## Features

### Home page

The home page is, top to bottom:

1. The site title and menu.
2. A **motto** in large type, with an optional gloss in the margin.
3. An **intro**: the body of your `content/_index.md`.
4. **Topics**: one heading per topic, each listing the newest posts in the matching category, with the topic's gloss in the margin. A topic can also show your latest books or Letterboxd posters. An empty topic reads "Forthcoming."

Everything is configured under `params.home`, and every part is optional:

```toml
[params.home]
  motto = "γνῶθι σεαυτόν"
  mottoLang = "grc"          # optional language tag, for correct hyphenation and fonts
  mottoGloss = "*Know thyself.* Inscribed at Delphi."
  topicsTitle = "Loci communes"
  topicsGloss = "Notes kept under subject headings. Elsewhere: [films](https://letterboxd.com/you/)."
  postsPerTopic = 3          # default 3

  [[params.home.topics]]
  key = "philosophy"         # a value of `categories` in your posts' front matter
  name = "Philosophia"       # the heading; links to the category page once it has posts
  gloss = "Plato first, then wherever the argument leads."   # Markdown

  [[params.home.topics]]
  key = "books"
  name = "Libri"
  books = "/books/"          # also show the 3 latest books, linking to this page

  [[params.home.topics]]
  key = "film"
  name = "Cinema"
  diary = "/films/"          # also show recent Letterboxd posters, linking to this page
```

Topics appear in the order they are listed. `books` needs the [reading log](#reading-log-books) set up and `diary` the [Letterboxd diary](#letterboxd-diary).

The motto is set in [GFS Didot](https://fonts.google.com/specimen/GFS+Didot), which covers Latin and polytonic Greek. It is only loaded on the home page, and only when a motto is set.

### Margin notes in headings

A `marginnote` or `sidenote` can sit inside a heading; the heading is then narrowed to the text column so the note lands in the margin instead of off-screen.

### Math

In this version, I use [Yihui Xie's method](https://yihui.org/en/2018/07/latex-math-markdown/) to support (almost) seamless LaTeX rendering with [KaTeX](https://katex.org/).

For usage and examples, refer to [./exampleSite/content/posts/tufte-features.md ](exampleSite/content/posts/tufte-features.md).

Downside: LaTeX in post title is no longer supported.

KaTeX is loaded from `https://cdn.jsdelivr.net/npm`, version `0.16.22`, unless you set `KaTeXCDN` / `KaTeXVersion`.

### Running head

Every single page (posts, the About page, the books and Letterboxd pages) starts with a small header line: the site title, which links back to the home page, followed by the entries of the `nav` menu, set in small caps above a hairline rule. The menu entry with `identifier: home` is left out, since the title already goes home, and the entry for the current page is highlighted.

It replaces the menu the theme used to put at the very bottom of single pages. To go back to that, set `hideRunningHead: true`.

### Reading log (books)

A page listing the books you have read, grouped by year, newest first. Each entry shows the title, author, an optional star rating, an optional short review, and an optional link to a post you wrote about the book.

1. List your books in `data/books.toml`:

   ```toml
   [[books]]
   title = "Euthyphro"                # required
   author = "Plato"                   # required
   finished = "2026-09-20"            # required, YYYY-MM-DD
   rating = 4.5                       # optional, 0.5 to 5, halves allowed
   review = "Short and *unresolved*." # optional, Markdown allowed
   post = "posts/euthyphro"           # optional, path under content/
   ```

   Order doesn't matter; entries are sorted by `finished`. The `post` link only appears once that page exists and is published (or when you build with `--buildDrafts`); otherwise the build prints a `books: no published page at …` warning and the book is shown without the link.

2. Create the page, e.g. `content/books.md`:

   ```yaml
   ---
   title: "Books"
   subtitle: "What I have read."
   layout: books
   ---
   ```

The [home page](#home-page) can show your latest books under a topic. To use the list anywhere else, call the partial, which returns the entries newest first:

```go-html-template
{{ range first 3 (partialCached "books.html" . "books") }}
  <em>{{ .title }}</em>, {{ .author }} {{ .stars }} {{ .finished.Format "2 Jan 2006" }}
  {{ with .page }}<a href="{{ .RelPermalink }}">full note</a>{{ end }}
{{ end }}
```

Each entry has the fields from the data file, with `finished` parsed as a date, plus `stars` (the rating as text, e.g. `★★★★½`) and `page` (the linked post, or empty).

### Letterboxd diary

Shows the films you log on [Letterboxd](https://letterboxd.com/), read from your public RSS feed when the site is built. Set your username:

```yaml
params:
  letterboxd: your_username
```

**Diary page.** A page with `layout: letterboxd` (e.g. `content/films.md`) lists the entries grouped by month watched: title, year, rating, ♥ for liked, ↻ for a rewatch, the date, and your review text if you wrote one, with the poster in the margin. A summary line on top gives the number of films, reviews, likes and the mean rating.

**Poster strip.** A row of recent posters linking to Letterboxd, for use in your own templates:

```go-html-template
{{ partial "letterboxd-strip.html" (dict "count" 6 "diary" "/films/") }}
```

`count` defaults to 6; `diary`, if given, adds a link to your diary page.

**Data.** `partialCached "letterboxd.html" . "letterboxd"` returns the entries, most recently watched first, with the fields `title`, `year`, `link`, `watched` (a date), `rating`, `stars`, `liked`, `rewatch`, `poster` (a resized image resource, or empty) and `review` (HTML, only for reviews).

Things to know:

- Posters are downloaded and resized to small WebP images at build time, so visitors never load anything from Letterboxd.
- If the feed can't be fetched, the build still succeeds with a warning: the strip is left out and the diary page says it couldn't load.
- The site only changes when it is rebuilt. Hugo reuses the downloaded feed until its cache expires; set how long in your site config, and schedule regular rebuilds on your host to keep the diary current:

  ```yaml
  caches:
    getresource:
      maxAge: 3h
  ```

- The feed only holds your most recent diary entries (about 50), so the summary describes recent months, not your whole history.

### Site Parameters

`params` for this theme are:

- `subtitle` string: If set, displayed under the main title.
- `showPoweredBy` boolean: If `true`, display a shoutout to Hugo and this theme.
- `copyrightHolder` string: Inserts the value in the default copyright notice.
- `copyright` string: Custom copyright notice.
- `math` boolean: Site wide kill switch for Latex support
- `codeBlocksDark` boolean: If `true`, code blocks will use a dark theme.
- `marginNoteInd` string: (NEW) Custom indicator for margin notes, with suggestions in comment. (Only displayed on mobile devices or inside `cols` shortcode.)
- `sansSubtitle` boolean: If `true`, all subtitles (`h2` \& `h3`) will use up-right and sans-serif font. (As seen in _Visual Display of Quantitative Information_.)
- (`centerArticle` boolean: Not implemented yet)
- `KaTeXVersion` string: KaTeX version to load. Default `0.16.22`.
- `KaTeXCDN` string: Base URL KaTeX is loaded from. Default `https://cdn.jsdelivr.net/npm`.
- `hideRunningHead` boolean: If `true`, drop the [running head](#running-head) and show the menu at the bottom of single pages instead.
- `letterboxd` string: Your Letterboxd username, for the [Letterboxd diary](#letterboxd-diary).
- `home` map: The [home page](#home-page): motto and topics.

**Socials**

_(The followings have not been tested for this repo, use at your own risk.)_

You can add links to your social media profile by using thoses parameters:

- `github`: string
- `gitlab`: string
- `twitter`: string
- `linkedin`: string
- `patreon`: string
- `youtube`: string
- `medium`: string
- `reddit`: string
- `stackoverflow`: string
- `instagram`: string
- `mastodon`: string
- `orcid`: string
- `google_scholar`: string

Please see [`exampleSite/config.yaml`](exampleSite/config.yaml) to see the full implementation with exemples.

### Page Parameters

- `math` boolean: If `true`, try to render the page's LaTeX code using KaTeX.
- `meta` boolean: If `true`, display page metadata such as author, date, categories.
  + `hideDate` boolean: If `true`, do not display a page date in metadata.
  + `hideReadTime` boolean: if `true`, do not display the page's reading time
  estimate in metadata.
- `toc` boolean: if true, display the table of contents for the page.
- Layout parameters: (NEW)
  + For more information, see [Hugo's Lookup Order | Hugo](https://gohugo.io/templates/lookup-order/).
  + `type` string: If set to `book`, layout files in [./layouts/book/](layouts/book/) will be prioritised.
  + `layout` string: If set, layout files with the name of this field's value will be prioritised.

### Shortcodes

This theme provides the following shortcodes in an attempt to completely
support all the features present in the [Tufte-css](https://github.com/edwardtufte/tufte-css) project.

For usage and examples, refer to [./exampleSite/content/posts/tufte-features.md ](exampleSite/content/posts/tufte-features.md).

- `blockquote`
- `div`
- `epigraph`
- `marginnote`
- `sidenote`

## License

This theme is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE.md). If you distribute a modified version of the theme, or run one on a network where others use it, you must make its source available under the same license. Your site's content is not covered.

The theme is based on earlier versions of hugo-tufte released under the MIT License; their copyright notice is kept in [LICENSE-MIT.md](LICENSE-MIT.md).
