// Rules engine. Each rule returns true / false / null (null = not enough information).
function evalRule(r, p) {
  if (r.op === 'any') {
    const v = r.rules.map(x => evalRule(x, p));
    return v.includes(true) ? true : v.includes(null) ? null : false;
  }
  const x = p[r.field];
  if (x === '' || x == null) return null;
  switch (r.op) {
    case 'eq': return x === r.value;
    case 'in': return r.value.includes(x);
    case 'gt': return x > r.value;
    case 'gte': return x >= r.value;
    case 'lte': return x <= r.value;
    case 'between': return x >= r.value[0] && x <= r.value[1];
    default: return null;
  }
}

// every field a rule looks at (used to tell the person which detail would settle a "check this")
function fieldsOf(r) {
  return r.op === 'any' ? r.rules.flatMap(fieldsOf) : [r.field];
}

// a scheme can belong to several categories: `tracks` (new) or the single `track` (original)
const tracksOf = s => s.tracks || [s.track];

function match(profile, schemes) {
  const results = schemes
    .filter(s => !profile.track || tracksOf(s).includes(profile.track))
    .map(s => {
      const checks = s.rules.map(r => ({ label: r.label, result: evalRule(r, profile) }));
      const status = checks.some(c => c.result === false) ? 'no'
        : checks.some(c => c.result === null) ? 'maybe' : 'yes';
      // confidence = share of the conditions already confirmed (0 once a condition fails)
      const sure = checks.filter(c => c.result === true).length;
      const confidence = status === 'no' ? 0 : checks.length ? Math.round((sure / checks.length) * 100) : 100;
      const missing = status === 'maybe'
        ? [...new Set(s.rules.filter(r => evalRule(r, profile) === null).flatMap(fieldsOf))] : [];
      const { rules, ...info } = s;
      return { ...info, tracks: tracksOf(s), status, confidence, missing, checks };
    });
  const yes = results.filter(r => r.status === 'yes');
  const totals = {
    yearly: yes.filter(r => !r.once).reduce((a, r) => a + (r.cash || 0), 0),
    once: yes.filter(r => r.once).reduce((a, r) => a + (r.cash || 0), 0)
  };
  // qualified first, then "check this" (most confirmed first), then by rupee value
  const rank = { yes: 0, maybe: 1, no: 2 };
  results.sort((a, b) => rank[a.status] - rank[b.status] || b.confidence - a.confidence || (b.cash || 0) - (a.cash || 0));

  const summary = { yes: yes.length, maybe: results.filter(r => r.status === 'maybe').length, no: results.filter(r => r.status === 'no').length };
  // the one or two details that would settle the most "check this" schemes
  const tally = {};
  results.filter(r => r.status === 'maybe').forEach(r => r.missing.forEach(f => { tally[f] = (tally[f] || 0) + 1; }));
  const askNext = Object.keys(tally).sort((a, b) => tally[b] - tally[a]).slice(0, 3).map(f => ({ field: f, schemes: tally[f] }));
  // documents to collect first: the ones that unlock the most schemes
  const need = {};
  results.filter(r => r.status !== 'no').forEach(r => r.docs.forEach(d => { (need[d] = need[d] || []).push(r.id); }));
  const checklist = Object.keys(need).map(d => ({ doc: d, count: need[d].length, schemes: need[d] }))
    .sort((a, b) => b.count - a.count || a.doc.localeCompare(b.doc));
  return { results, totals, summary, askNext, checklist };
}
module.exports = { match, evalRule, tracksOf };
