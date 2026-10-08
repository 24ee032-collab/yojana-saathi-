// Fails fast at start-up if the data files are inconsistent (missing translation, unknown field/document/step).
const full = a => Array.isArray(a) && a.length === 3 && a.every(x => typeof x === 'string' && x.trim());
const OPS = ['eq', 'in', 'gt', 'gte', 'lte', 'between', 'any'];

function validate({ schemes, vocab, categories, fields }) {
  const errors = [];
  const catIds = categories.map(c => c.id);
  const known = new Set(['track', 'occ', ...Object.keys(fields)]);
  const seen = new Set();
  // only the outer rule is shown to people, so only it needs a label (inner rules of an "any" need none)
  const walk = (rules, id, top = true) => rules.forEach(r => {
    if (!OPS.includes(r.op)) errors.push(`${id}: bad op ${r.op}`);
    if (top && !full(r.label)) errors.push(`${id}: rule label needs en/hi/ta`);
    if (r.op === 'any') return walk(r.rules, id, false);
    if (!known.has(r.field)) errors.push(`${id}: unknown field ${r.field}`);
  });
  for (const s of schemes) {
    if (seen.has(s.id)) errors.push(`duplicate scheme id ${s.id}`);
    seen.add(s.id);
    for (const k of ['name', 'benefit', 'about']) if (!full(s[k])) errors.push(`${s.id}.${k} needs en/hi/ta`);
    (s.tracks || [s.track]).forEach(t => { if (!catIds.includes(t)) errors.push(`${s.id}: unknown category ${t}`); });
    if (!/^https:\/\//.test(s.url || '')) errors.push(`${s.id}: url must be https`);
    walk(s.rules, s.id);
    s.docs.forEach(d => { if (!vocab.docs[d]) errors.push(`${s.id}: unknown doc ${d}`); });
    s.steps.forEach(x => { if (!vocab.steps[x]) errors.push(`${s.id}: unknown step ${x}`); });
  }
  for (const c of categories) {
    if (!full(c.name) || !full(c.desc)) errors.push(`category ${c.id}: name/desc need en/hi/ta`);
    c.fields.forEach(f => { if (!fields[f]) errors.push(`category ${c.id}: unknown field ${f}`); });
    if (!vocab.tracks[c.id]) errors.push(`vocab.tracks.${c.id} missing`);
  }
  for (const [k, f] of Object.entries(fields)) {
    if (f.type === 'choice') f.options.forEach(o => { if (o.length !== 4 || o.some(x => !x)) errors.push(`field ${k}: option ${o[0]} needs value+en/hi/ta`); });
  }
  for (const g of ['tracks', 'docs', 'steps']) for (const k in vocab[g]) if (!full(vocab[g][k])) errors.push(`vocab.${g}.${k}`);
  return errors;
}
module.exports = { validate, full };
