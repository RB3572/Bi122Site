# Bi122Site

Course resources site for **Bi 122: Genetics** (Caltech, BBE) — Fall 2025.

Static site: plain HTML and CSS, no build step, no JavaScript. Deploys to
[bi122resources.rishib.com](https://bi122resources.rishib.com) via Vercel on push to `main`.

```
index.html    the whole page
styles.css    design tokens and layout
materials/    20 lecture handouts and review decks (PDF, ~113 MB)
images/       teaching staff portraits
```

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
