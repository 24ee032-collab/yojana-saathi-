// Read-only catalogue helpers: config for the frontend, scheme search, usage counters.
const { tracksOf } = require('./engine');

function buildConfig(categories, fields, schemes) {
  const cats = categories.map(c => ({ ...c, count: schemes.filter(s => tracksOf(s).includes(c.id)).length }));
  return { categories: cats, fields, totals: { schemes: schemes.length, categories: cats.length, languages: 3 } };
}

// simple relevance search over names, benefits and descriptions in all three languages
function search(schemes, { q = '', track = '' } = {}) {
  const words = String(q).toLowerCase().split(/\s+/).filter(Boolean).slice(0, 6);
  return schemes
    .filter(s => !track || tracksOf(s).includes(track))
    .map(s => {
      if (!words.length) return { s, score: 0 };
      const name = s.name.join(' ').toLowerCase(), rest = (s.benefit.join(' ') + ' ' + s.about.join(' ')).toLowerCase();
      let score = 0;
      for (const w of words) {
        if (name.includes(w)) score += 3; else if (rest.includes(w)) score += 1; else return { s, score: -1 };
      }
      return { s, score };
    })
    .filter(x => x.score >= 0)
    .sort((a, b) => b.score - a.score)
    .map(x => x.s);
}

// anonymous counters only (no personal data): shown on /api/stats
const usage = { since: new Date().toISOString(), matches: 0, voiceAnswers: 0, freeSpeech: 0, byCategory: {} };
const bump = {
  match(track) { usage.matches++; if (track) usage.byCategory[track] = (usage.byCategory[track] || 0) + 1; },
  voice() { usage.voiceAnswers++; },
  free() { usage.freeSpeech++; }
};
module.exports = { buildConfig, search, usage, bump };
