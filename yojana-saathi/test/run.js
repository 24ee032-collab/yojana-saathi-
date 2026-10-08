// Checks for the parser, rules engine, answer parsing and translations: npm test
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { extract, answer } = require('../src/parser');
const { match } = require('../src/engine');
const schemes = require('../data/schemes.json');
const vocab = require('../data/vocab.json');
const T = require('../public/js/i18n.js');
const base = { track:'', age:null, income:null, land:null, gender:'', occ:'', cat:'', course:'' };
const status = (p, id) => match({ ...base, ...p }, schemes).results.find(r => r.id === id).status;

/* --- parser: English, Hindi, Tamil --- */
const f = extract('I am a 45 year old farmer. I have 2 acres of land, income 80 thousand rupees per year, OBC category.');
assert.deepStrictEqual([f.age, f.occ, f.land, f.income, f.cat, f.track], [45, 'farmer', 2, 80000, 'OBC', 'f']);
const h = extract('मैं 20 साल की छात्रा हूँ। परिवार की सालाना आय 3 लाख है। अनुसूचित जाति');
assert.deepStrictEqual([h.age, h.occ, h.gender, h.income, h.cat], [20, 'student', 'female', 300000, 'SC']);
const ta = extract('நான் 45 வயது விவசாயி. எனக்கு 2 ஏக்கர் நிலம் உள்ளது. ஆண்டு வருமானம் 80 ஆயிரம். பிற்படுத்தப்பட்ட வகுப்பு.');
assert.deepStrictEqual([ta.age, ta.occ, ta.land, ta.income, ta.cat, ta.track], [45, 'farmer', 2, 80000, 'OBC', 'f']);
const ts = extract('நான் 20 வயது மாணவி, கல்லூரியில் பொறியியல் படிக்கிறேன். குடும்ப ஆண்டு வருமானம் 3 லட்சம். நான் ஆதிதிராவிடர் பிரிவு.');
assert.deepStrictEqual([ts.age, ts.occ, ts.gender, ts.income, ts.cat, ts.course], [20, 'student', 'female', 300000, 'SC', 'tech']);
const te = extract('நான் 32 வயது ஆண், சிறிய கடை நடத்துகிறேன். தொழில் கடன் வேண்டும். ஆண்டு வருமானம் 2 லட்சம்.');
assert.deepStrictEqual([te.age, te.gender, te.occ, te.income], [32, 'male', 'business', 200000]);
assert.strictEqual(extract('ஆண்டு வருமானம் 2 லட்சம்').gender, undefined, '"ஆண்டு" (year) must not read as male');
assert.strictEqual(extract('விவசாயி 50 சென்ட் நிலம்').land, 0.5);
assert.strictEqual(extract('வயது ௪௫ விவசாயி').age, 45);
assert.strictEqual(extract('I am a student doing engineering').course, 'tech');

/* --- interview answers --- */
assert.deepStrictEqual(answer('age', '45'), { age: 45 });
assert.deepStrictEqual(answer('age', 'நான் 45 வயது'), { age: 45 });
assert.strictEqual(answer('age', 'hello'), null);
assert.deepStrictEqual(answer('income', '3 lakh'), { income: 300000 });
assert.deepStrictEqual(answer('income', '3 லட்சம்'), { income: 300000 });
assert.deepStrictEqual(answer('income', '250000'), { income: 250000 });
assert.strictEqual(answer('income', '5'), null, 'a bare small number is ambiguous, so ask again');
assert.deepStrictEqual(answer('land', '2'), { land: 2 });
assert.deepStrictEqual(answer('track', 'I run a tea shop'), { track: 'e', occ: 'business' });
assert.deepStrictEqual(answer('track', 'நான் ஒரு மாணவர்'), { track: 's', occ: 'student' });
assert.deepStrictEqual(answer('gender', 'महिला'), { gender: 'female' });
assert.deepStrictEqual(answer('cat', 'MBC'), { cat: 'OBC' });
assert.deepStrictEqual(answer('cat', 'பழங்குடி'), { cat: 'ST' });
assert.deepStrictEqual(answer('age', 'I am 45 and have 2 acres'), { age: 45, land: 2 });
assert.strictEqual(answer('nonsense', 'x'), null);

/* --- rules engine --- */
assert.strictEqual(status({ occ:'farmer', land:2 }, 'pmkisan'), 'yes');
assert.strictEqual(status({ occ:'farmer' }, 'pmkisan'), 'maybe');
assert.strictEqual(status({ occ:'student', income:300000, cat:'SC' }, 'pms'), 'no');
assert.strictEqual(status({ occ:'student', income:200000, cat:'SC' }, 'pms'), 'yes');
assert.strictEqual(status({ occ:'business', gender:'female' }, 'standup'), 'yes');
const m = match({ ...base, occ:'farmer', land:2, track:'f' }, schemes);
assert.strictEqual(m.totals.yearly, 6000);
assert.strictEqual(status({ occ:'student', gender:'female', income:300000, course:'tech' }, 'pragati'), 'yes');
assert.strictEqual(status({ occ:'student', gender:'female', income:300000, course:'other' }, 'pragati'), 'no');
assert.strictEqual(status({ occ:'student', gender:'female', income:300000 }, 'pragati'), 'maybe');

/* --- every scheme, document, step and label exists in all three languages --- */
const full = a => Array.isArray(a) && a.length === 3 && a.every(x => typeof x === 'string' && x.trim());
const walk = (rules, id) => rules.forEach(r => { if (r.label) assert(full(r.label), `${id}: rule label`); if (r.rules) walk(r.rules, id); });
for (const s of schemes) {
  for (const k of ['name', 'benefit', 'about']) assert(full(s[k]), `${s.id}.${k} needs en/hi/ta`);
  walk(s.rules, s.id);
  s.docs.forEach(d => assert(vocab.docs[d], `${s.id}: unknown doc ${d}`));
  s.steps.forEach(x => assert(vocab.steps[x], `${s.id}: unknown step ${x}`));
}
for (const g of ['tracks', 'docs', 'steps']) for (const k in vocab[g]) assert(full(vocab[g][k]), `vocab.${g}.${k}`);

/* --- interface text: complete, and every key used in the page exists --- */
for (const k in T) assert(full(T[k]), `i18n key ${k} needs en/hi/ta`);
const rd = f => fs.readFileSync(path.join(__dirname, '../public/' + f), 'utf8');
const html = rd('finder.html') + rd('index.html');
const js = rd('js/app.js') + rd('js/home.js');
const used = new Set([...html.matchAll(/data-t[a]?="(\w+)"/g)].map(x => x[1]));
for (const x of js.matchAll(/\bt\('(\w+)'/g)) used.add(x[1]);
for (const x of js.matchAll(/t\('(q_|income_|l_)'\s*\+/g)) used.add(x[1]);
['q_track','q_occ','q_age','q_gender','q_cat','q_income_f','q_income_s','q_income_e','q_land','q_course',
 'income_f','income_s','income_e','l_track','l_occ','l_age','l_gender','l_cat','l_income','l_land','l_course'].forEach(k => used.add(k));
// every category and bio-data field needs its form label, short label and spoken question in all 3 languages
const categories = require('../data/categories.json'), fields = require('../data/fields.json');
for (const f of Object.keys(fields)) { used.add(f === 'income' ? 'income_f' : f === 'occ' ? 'occE' : f); used.add('l_' + f); used.add('q_' + f === 'q_income' ? 'q_income_f' : 'q_' + f); }
for (const c of categories) { used.add('income_' + c.id); used.add('q_income_' + c.id); }
for (const k of used) if (/^\w+$/.test(k) && !k.endsWith('_')) assert(T[k], `missing translation key: ${k}`);

console.log('All tests passed');

/* --- spoken number WORDS (what speech recognition often returns) --- */
const n = (field, text) => { const r = answer(field, text); return r && r[field]; };
// Tamil
assert.strictEqual(n('age', 'நாற்பத்தைந்து'), 45);
assert.strictEqual(n('age', 'நாற்பத்தி ஐந்து வயது'), 45);
assert.strictEqual(n('age', 'முப்பத்து இரண்டு'), 32);
assert.strictEqual(n('age', 'இருபத்தொன்று'), 21);
assert.strictEqual(n('age', 'தொண்ணூற்றைந்து'), 95);
assert.strictEqual(n('income', 'எண்பதாயிரம்'), 80000);
assert.strictEqual(n('income', 'எண்பது ஆயிரம்'), 80000);
assert.strictEqual(n('income', 'மூன்று லட்சம்'), 300000);
assert.strictEqual(n('income', 'ஒரு லட்சம்'), 100000);
assert.strictEqual(n('income', 'இரண்டு லட்சத்து ஐம்பதாயிரம்'), 250000);
assert.strictEqual(n('income', 'ஒன்றரை லட்சம்'), 150000);
assert.strictEqual(n('land', 'இரண்டு ஏக்கர்'), 2);
assert.strictEqual(n('land', 'அரை ஏக்கர்'), 0.5);
assert.deepStrictEqual(answer('track', 'நான் ஒரு விவசாயி'), { track: 'f', occ: 'farmer' });   // "ஒரு" = "a", not 1
// Hindi
assert.strictEqual(n('age', 'पैंतालीस'), 45);
assert.strictEqual(n('income', 'दो लाख'), 200000);
assert.strictEqual(n('income', 'अस्सी हजार'), 80000);
assert.strictEqual(n('land', 'एक एकड़'), 1);
assert.strictEqual(n('land', 'दो एकड़'), 2);                    // "एकड़" must never be read as "एक"
assert.strictEqual(n('age', 'मैं एक किसान हूँ और 45 साल का'), 45);
// English
assert.strictEqual(n('age', 'forty-five years'), 45);
assert.strictEqual(n('income', 'two lakh'), 200000);
assert.strictEqual(n('income', 'eighty thousand'), 80000);
assert.deepStrictEqual(answer('track', 'I am one of the farmers'), { track: 'f', occ: 'farmer' });
assert.strictEqual(extract('income 2 lakh 50 thousand').income, 250000);
console.log('Number-word tests passed');

/* --- ten categories: data is valid and every category has schemes --- */
const { validate } = require('../src/validate');
assert.deepStrictEqual(validate({ schemes, vocab, categories, fields }), []);
assert.strictEqual(categories.length, 10);
for (const c of categories) assert(schemes.filter(x => (x.tracks || [x.track]).includes(c.id)).length >= 10, 'category ' + c.id + ' needs at least 10 schemes');
const st = (p, id) => match({ ...base, ...p }, schemes).results.find(r => r.id === id).status;
const ex = { bpl:'', home:'', tgid:'', svc:'', pension:'', ward:'', level:'', medal:'', dis:null, udid:'', stage:'', edu:'' };
const stx = (p, id) => st({ ...ex, ...p }, id);
assert.strictEqual(stx({ track:'w', age:45, bpl:'yes' }, 'ignwps'), 'yes');
assert.strictEqual(stx({ track:'w', age:30, bpl:'yes' }, 'ignwps'), 'no');
assert.strictEqual(stx({ track:'o', age:72 }, 'vayvandana'), 'yes');
assert.strictEqual(stx({ track:'o', age:65 }, 'vayvandana'), 'no');
assert.strictEqual(stx({ track:'d', dis:30 }, 'udid'), 'no');
assert.strictEqual(stx({ track:'d', dis:85, age:40, bpl:'yes' }, 'igndps'), 'yes');
assert.strictEqual(stx({ track:'y', age:22, edu:'grad', income:300000 }, 'pminternship'), 'yes');
assert.strictEqual(stx({ track:'y', age:30, edu:'grad', income:300000 }, 'pminternship'), 'no');
assert.strictEqual(stx({ track:'x', pension:'yes' }, 'echs'), 'yes');
assert.strictEqual(stx({ track:'x', pension:'no' }, 'echs'), 'no');
assert.strictEqual(stx({ track:'p', level:'intl' }, 'tops'), 'yes');
assert.strictEqual(stx({ track:'p', level:'state' }, 'tops'), 'no');
assert.strictEqual(stx({ track:'t', tgid:'no', age:25 }, 'smile'), 'no');
assert.strictEqual(stx({ track:'t', tgid:'yes', age:25 }, 'smile'), 'yes');
assert.strictEqual(stx({ track:'s', occ:'student', stage:'school', income:300000 }, 'nmmss'), 'yes');
assert.strictEqual(stx({ track:'f', occ:'farmer', age:30, land:3 }, 'kmy'), 'yes');
assert.strictEqual(stx({ track:'f', occ:'farmer', age:50, land:3 }, 'kmy'), 'no');
// a scheme in several categories shows in each of them
assert(match({ ...base, ...ex, track:'y' }, schemes).results.some(r => r.id === 'mudra'));
assert(!match({ ...base, ...ex, track:'f' }, schemes).results.some(r => r.id === 'mudra'));
// match returns confidence, what to ask next and a document checklist
const mm = match({ ...base, ...ex, track:'d', dis:60, age:30, gender:'female' }, schemes);
assert(mm.checklist.length && mm.checklist[0].count >= mm.checklist[mm.checklist.length - 1].count);
assert(mm.results.every(r => r.confidence >= 0 && r.confidence <= 100));
assert(mm.askNext.every(a => fields[a.field] || a.field === 'occ'));

/* --- parser: new categories and fields --- */
assert.strictEqual(extract('I am a widow, 45 years old, BPL family').track, 'w');
assert.strictEqual(extract('मैं 62 साल का सेवानिवृत्त सैनिक हूँ, पेंशन मिलती है').pension, 'yes');
assert.strictEqual(extract('நான் 35 வயது மாற்றுத்திறனாளி, 60 சதவீதம்').track, 'd');
assert.strictEqual(extract('I have 60 percent disability', 'd').dis, 60);
assert.strictEqual(extract('I am a widow', 'f').track, undefined, 'a chosen category is never overwritten');
assert.deepStrictEqual(answer('track', 'transgender'), { track:'t', occ:'' });
assert.deepStrictEqual(answer('track', 'I am unemployed'), { track:'y', occ:'unemp' });
assert.deepStrictEqual(answer('bpl', 'no'), { bpl:'no' });
assert.deepStrictEqual(answer('bpl', 'हाँ'), { bpl:'yes' });
assert.deepStrictEqual(answer('udid', 'இல்லை'), { udid:'no' });
assert.deepStrictEqual(answer('level', 'national'), { level:'nat' });
assert.deepStrictEqual(answer('edu', 'I passed 12th'), { edu:'12th' });
assert.deepStrictEqual(answer('dis', '40 percent'), { dis:40 });
assert.deepStrictEqual(answer('svc', 'subedar'), { svc:'jco' });
console.log('Category tests passed');
