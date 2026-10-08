// Yojana Saathi - backend (Node.js + Express)
const express = require('express');
const path = require('path');
const { extract, answer, FIELDS } = require('./src/parser');
const { match } = require('./src/engine');
const schemes = require('./data/schemes.json');
const vocab = require('./data/vocab.json');
const categories = require('./data/categories.json');
const fields = require('./data/fields.json');
const { validate } = require('./src/validate');
const { buildConfig, search, usage, bump } = require('./src/catalog');
const { tracksOf } = require('./src/engine');

const problems = validate({ schemes, vocab, categories, fields });
if (problems.length) { console.error('Data check failed:\n - ' + problems.join('\n - ')); process.exit(1); }
const config = buildConfig(categories, fields, schemes);
const started = Date.now();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: '10kb' }));
app.use((req, res, next) => {
  res.set({
    'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'SAMEORIGIN', 'Referrer-Policy': 'no-referrer',
    'Permissions-Policy': 'microphone=(self), geolocation=(), camera=()',
    'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; media-src 'self'; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
  });
  next();
});
// one JSON log line per API request (no request bodies, so no personal data is logged)
app.use('/api', (req, res, next) => {
  const t0 = Date.now();
  res.on('finish', () => { if (process.env.QUIET !== '1') console.log(JSON.stringify({ t: new Date().toISOString(), m: req.method, p: req.path, s: res.statusCode, ms: Date.now() - t0 })); });
  next();
});

// simple in-memory rate limit: 120 requests per minute per IP
const hits = new Map();
setInterval(() => { const now = Date.now(); for (const [k, v] of hits) if (!v.some(t => now - t < 60000)) hits.delete(k); }, 60000).unref();
app.use('/api', (req, res, next) => {
  const now = Date.now(), ip = req.ip;
  const arr = (hits.get(ip) || []).filter(t => now - t < 60000);
  arr.push(now); hits.set(ip, arr);
  if (arr.length > 120) return res.status(429).json({ error: 'Too many requests. Please wait a minute.' });
  next();
});

// keep only known fields with the right type (the allowed values come from data/fields.json)
function clean(p) {
  const num = (v, max) => (v === '' || v == null || isNaN(v) || v < 0 || (max && v > max) ? null : Number(v));
  const out = { track: categories.some(c => c.id === p.track) ? p.track : '' };
  for (const [k, f] of Object.entries(fields)) {
    out[k] = f.type === 'num' ? num(p[k], f.max) : (f.options.some(o => o[0] === p[k]) ? p[k] : '');
  }
  return out;
}

app.get('/api/health', (req, res) => res.json({ ok: true, schemes: schemes.length, categories: categories.length, uptime: Math.round((Date.now() - started) / 1000) }));
// everything the frontend needs to build the 10 categories and their bio-data questions
app.get('/api/config', (req, res) => res.json(config));
app.get('/api/categories', (req, res) => res.json(config.categories));
app.get('/api/stats', (req, res) => res.json({ ...config.totals, usage }));
app.get('/api/vocab', (req, res) => res.json(vocab));
// scheme list for the "All schemes" library; conditions = the eligibility labels from the rules
const pub = ({ rules, ...s }) => ({ ...s, tracks: tracksOf(s), conditions: rules.map(r => r.label) });
app.get('/api/schemes', (req, res) => {
  const q = String(req.query.q || '').slice(0, 80), track = String(req.query.track || '');
  res.json(search(schemes, { q, track }).map(pub));
});
app.get('/api/schemes/:id', (req, res) => {
  const s = schemes.find(x => x.id === req.params.id);
  s ? res.json(pub(s)) : res.status(404).json({ error: 'Scheme not found' });
});
app.post('/api/parse', (req, res) => {
  const text = String((req.body && req.body.text) || '').slice(0, 1000);
  const track = categories.some(c => c.id === (req.body && req.body.track)) ? req.body.track : '';
  bump.free();
  res.json({ profile: extract(text, track) });
});
app.post('/api/answer', (req, res) => {
  const field = String((req.body && req.body.field) || '');
  const text = String((req.body && req.body.text) || '').slice(0, 300);
  if (!FIELDS.includes(field)) return res.status(400).json({ error: 'Unknown field' });
  bump.voice();
  res.json({ patch: answer(field, text) });
});
app.post('/api/match', (req, res) => {
  const profile = clean((req.body && req.body.profile) || {});
  bump.match(profile.track);
  res.json(match(profile, schemes));
});

// Online voice fallback for devices that have no Tamil / Hindi text-to-speech voice (common on Windows PCs).
// It relays short sentences to Google Translate's public speech endpoint. That endpoint is unofficial,
// so for a production launch swap it for Azure Neural TTS (ta-IN-PallaviNeural) or Google Cloud Text-to-Speech.
// Turn it off with the environment variable TTS_FALLBACK=off.
const TTS_LANG = { en: 'en-IN', hi: 'hi', ta: 'ta' };
const ttsCache = new Map();
app.get('/api/tts', async (req, res) => {
  if (process.env.TTS_FALLBACK === 'off') return res.status(503).json({ error: 'Online voice is switched off' });
  const l = String((req.query && req.query.l) || ''), q = String((req.query && req.query.q) || '').trim().slice(0, 200);
  if (!TTS_LANG[l] || !q) return res.status(400).json({ error: 'Bad request' });
  const key = l + '|' + q;
  let audio = ttsCache.get(key);
  if (!audio) {
    try {
      const r = await fetch('https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=' + TTS_LANG[l] + '&q=' + encodeURIComponent(q), {
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; YojanaSaathi)', Referer: 'https://translate.google.com/' },
        signal: AbortSignal.timeout(8000)
      });
      if (!r.ok) throw new Error('status ' + r.status);
      audio = Buffer.from(await r.arrayBuffer());
      if (ttsCache.size >= 300) ttsCache.delete(ttsCache.keys().next().value);
      ttsCache.set(key, audio);
    } catch (e) {
      return res.status(502).json({ error: 'Online voice is unavailable right now' });
    }
  }
  res.set({ 'Content-Type': 'audio/mpeg', 'Cache-Control': 'public, max-age=86400' });
  res.end(audio);
});

app.use(express.static(path.join(__dirname, 'public')));
app.use((req, res) => res.status(404).json({ error: 'Not found' }));
app.use((err, req, res, next) => {   // bad JSON, oversized bodies, anything unexpected
  const code = err.status && err.status < 500 ? err.status : 500;
  res.status(code).json({ error: code === 500 ? 'Something went wrong' : 'Bad request' });
});

if (require.main === module) app.listen(PORT, () => console.log(`Yojana Saathi running on http://localhost:${PORT}`));
module.exports = app;
