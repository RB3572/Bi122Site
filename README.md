# Bi122Site

Course resources site for **Bi 122: Genetics** (Caltech, BBE) — Fall 2025.

Static site: plain HTML and CSS, no build step, no JavaScript. Deploys to
[bi122resources.rishib.com](https://bi122resources.rishib.com) via Vercel on push to `main`.

```
index.html      landing page — course facts and links to each section
materials.html  lecture handouts, with the in-page document viewer
deadlines.html  problem set due dates, points, grade weighting
staff.html      instructor, TAs, office hours
schedule.html   week-by-week lecture topics, plus calendar subscription
syllabus.html   description, text, grading scale, collaboration policy
styles.css      design tokens and layout, shared by every page
schedule.json   source of truth for the lecture schedule
schedule.ics    generated calendar feed (do not edit by hand)
tools/          build-schedule.py, regenerates the table and the feed
vercel.json     serving headers for the calendar feed and materials
materials/      20 lecture handouts and review decks (PDF, ~113 MB)
images/         teaching staff portraits, plus thumbs/ for handout covers
```

## Changing the lecture schedule

`schedule.json` is the single source of truth. Edit it, then:

```bash
python3 tools/build-schedule.py
```

That rewrites both the table in `schedule.html` and the subscribable feed `schedule.ics`, so the
two can never drift apart. Commit and push as usual; Vercel redeploys and subscribers pick the
change up on their calendar app's next refresh.

**Bump `_sequence` in `schedule.json` whenever you change the date, time or title of a lecture that
already exists.** Calendar clients ignore an update to an event whose `SEQUENCE` has not increased,
so without it subscribers keep the stale version. Adding or removing lectures does not need it.

Refresh is not instant: Google Calendar re-polls external feeds on its own schedule, usually within
a few hours but occasionally up to a day. Announce time-critical changes by email as well.

There is no build step and no templating, so the `<nav>` and `<footer>` blocks are duplicated
across the six pages. Editing one means editing all six — the nav marks the current page with
`class="active"` and `aria-current="page"`, so keep that in sync too.

## Materials

Handouts mirror the weekly modules of the
[course Canvas page](https://caltech.instructure.com/courses/9095) and are named `w<week>-<topic>.pdf`.
Images inside them were recompressed for faster loading; page counts and text are unchanged. The
two review decks were converted from `.pptx` to PDF so they open in the browser.

Deliberately **not** mirrored, because they are third-party copyrighted works: the Griffiths
textbook and the two assigned *Atlantic* articles. Those stay on Canvas, as do problem sets and
solutions.

When updating a handout, replace the file and update the matching `file-meta` line in
`index.html` (page count and size) so the listing stays accurate.
