# Yojana Saathi - Government Scheme Finder (v3)

**10 citizen categories, 78 central schemes, English / Hindi / Tamil, voice-first.**

Categories: Farmer, Students, Widows, Unemployed youth, Transgender persons, Entrepreneurs, Ex-servicemen,
Sports persons, Persons with disabilities, Senior citizens. (The tenth, Senior citizens, was added to complete
the set of ten; to swap it, edit `tools/build_config.py`.)

## What is new in v3
- **Home page (`/`)**: only language and category. Click a card, or tap "Say who you are" and speak it.
  "Listen" reads the categories aloud.
- **Finder page (`/finder.html?c=<category>`)**: the original voice interview, speak-freely, form, results and
  scheme library, now with **different bio-data questions per category** (served by the backend).
- **Backend**: `/api/config` (categories + question flow), category-aware matching with a confidence score,
  "tell us this to confirm more schemes" hints, a **document checklist** ranked by how many schemes each paper
  unlocks, scheme search/filter, anonymous usage stats, data validation at start-up, CSP and security headers,
  JSON request log, tidy error handling.
- Everything from v2 is kept: voice interview, number words in 3 languages, online voice fallback, high
  contrast, text size, PWA, privacy (details stay on the device).

## Run
```bash
npm install
npm start          # http://localhost:3000
npm test           # parser, rules, data validity, translation completeness, 10 categories
```
Node.js 18+. Voice input works in Chrome / Edge on localhost or HTTPS.

## Bio-data questions per category (data/categories.json)
| Category | Questions |
|---|---|
| Farmer | age, gender, category, income, land |
| Students | age, gender, category, income, study level, course |
| Widows | age, category, income, BPL, pucca house |
| Unemployed youth | age, gender, category, income, education |
| Transgender | age, education, category, income, certificate, BPL, house |
| Entrepreneurs | work type, age, gender, category, income |
| Ex-servicemen | age, rank group, pension, income, child in professional course |
| Sports persons | age, gender, category, income, level played, international medal |
| Persons with disabilities | age, gender, category, income, education, disability %, UDID, BPL |
| Senior citizens | age, gender, category, income, BPL, house |

## Structure
```
server.js              Express server and API routes
src/engine.js          Rules engine (true/false/unknown), confidence, ask-next, document checklist
src/parser.js          Free text / one answer -> profile (EN / HI / TA), all categories
src/catalog.js         Config builder, scheme search, anonymous counters
src/validate.js        Start-up data check (translations, fields, documents, steps)
data/categories.json   The 10 categories and their question order
data/fields.json       Every bio-data field and its options in 3 languages
data/schemes.json      78 schemes (generated, see tools/)   data/vocab.json  documents, steps
public/index.html      Home: language + category          public/finder.html  the finder
public/js/speech.js    Shared voice engine   public/js/home.js, app.js, icons.js, i18n.js
tools/                 build_config.py, build_schemes.py (+ pristine base files); `npm run build:data`
```

## API
| Method | Path | Purpose |
|---|---|---|
| GET | /api/health, /api/stats | Server check; counts and anonymous usage |
| GET | /api/config, /api/categories | Categories, fields and options |
| GET | /api/schemes `?q=&track=` , /api/schemes/:id | Search / one scheme |
| GET | /api/vocab | Documents, steps, category names |
| POST | /api/parse `{text, track}` | Free text to profile |
| POST | /api/answer `{field, text}` | One interview answer to `{patch}` |
| POST | /api/match `{profile}` | Matches, reasons, totals, summary, askNext, checklist |
| GET | /api/tts `?l=ta&q=text` | Online voice fallback |

## Add a scheme
Add an `add(...)` entry in `tools/build_schemes.py` (texts as English, Hindi, Tamil; `tracks` lists the categories
it appears in), then run `npm run build:data` and `npm test`. Or edit `data/schemes.json` directly using the same shape.

## Important
- Amounts and conditions are indicative; confirm on each official portal. "All schemes in India" is not possible in
  one dataset (thousands of central and state schemes): this covers the main central schemes per category and is
  built so state schemes can be added the same way.
- Hindi and Tamil text should be reviewed by native speakers before a public launch.
- Independent project, not an official government site. No national emblem is used.

## Voice: how Tamil and Hindi speech works
- **Listening** uses the browser's speech recognition (Chrome or Edge, needs internet and microphone permission).
  Specific problems are shown on screen (no internet, microphone blocked, language not supported).
- **Speaking** uses a voice installed on the device when there is one for the language. Many Windows PCs have
  no Tamil voice, so the app then plays an **online voice** through `GET /api/tts`, which relays short sentences
  to Google Translate's public speech endpoint. That endpoint is unofficial and can change or be rate limited.
  For a public launch replace it with Azure Neural TTS (`ta-IN-PallaviNeural`) or Google Cloud Text-to-Speech
  inside `server.js`, or switch it off with the environment variable `TTS_FALLBACK=off`
  (the question is then shown on screen only).
- The **Voice check** box on the interview tab shows which voice will be used and has a test button.

## Design notes
Plain HTML, CSS and JS (no build step). The look follows anti-template design guidance (Taste Skill ideas):
one memorable element (the turmeric microphone), a "paper slip" that fills in as the person speaks,
lists instead of identical shadowed cards, Anek type family for headings (one design across Latin, Devanagari
and Tamil) over Noto Sans for body text, sentence-case labels, and motion only in response to an action.
Colours and fonts are set as variables at the top of `public/css/style.css`.

## Saved details and privacy
Answers are saved automatically **on the user's own device** (browser localStorage) so they do not
have to repeat them. They are sent to the server only to find matches and are **not stored there**.
"Clear saved data" deletes them. The server keeps no database.

## API
| Method | Path | Purpose |
|---|---|---|
| GET | /api/health | Server check |
| GET | /api/vocab | Documents, steps, group names (3 languages) |
| GET | /api/tts `?l=ta&q=text` | Online voice fallback (audio/mpeg) |
| GET | /api/schemes | Scheme list with `about` and `conditions`, without rules |
| POST | /api/parse `{text}` | Free text to profile |
| POST | /api/answer `{field, text}` | One interview answer to `{patch}` (or `null` if not understood) |
| POST | /api/match `{profile}` | Matched schemes, reasons, totals |

Profile fields: `track` (f/s/e), `age`, `income` (yearly ₹), `land` (acres), `gender`, `occ`, `cat`, `course`.

## Add a scheme
Add an object to `data/schemes.json`. Every text is an array **`[English, Hindi, Tamil]`**:
`name`, `benefit`, `about`, and each rule `label`. A rule is `{field, op, value, label}` with ops
`eq, in, gt, gte, lte, between`, or `{op:"any", rules:[...]}` for OR conditions.
Use existing ids from `data/vocab.json` for `docs` and `steps`. `npm test` fails if any language is missing.

## Add or change interface text
Edit `public/js/i18n.js` (`key: [en, hi, ta]`). The tests check that every key used in the page exists in all three languages.

## Deploy
Any Node host works (Render, Railway, Azure App Service). Set `PORT` if needed. No database is required.

## Notes
- Eligibility comes from plain rules, not AI, so answers are predictable.
- Amounts and conditions are indicative. Verify against each official portal before publishing.
  Tamil and Hindi text was written for clarity; have a native speaker review it before a public launch.
- Spoken answers: numbers are understood as digits ("45", "3 lakh") **and as words** in Tamil, Hindi and
  English ("நாற்பத்தைந்து", "எண்பது ஆயிரம்", "पैंतालीस", "forty five", "2 lakh 50 thousand").
  See `src/numwords.js`. Numbers above 99 are only understood together with lakh / thousand.
- This is an independent project, not an official government site. Do not use the national emblem.

## Install on a phone / make an APK
1. Deploy to a host with HTTPS (Render: connect the repo, it reads `render.yaml`).
2. Open the live link in Chrome on Android and choose **Add to Home screen** to install it as an app.
3. For a real APK: go to pwabuilder.com, enter the live link, choose **Android**, and download the package.
   The package opens your site in Chrome (Trusted Web Activity), so voice input keeps working.
