/* Yojana Saathi - frontend (English / Hindi / Tamil). Talks to the backend at /api/* */
const $ = id => document.getElementById(id);
let li = 0, vocab = null, data = null, schemes = [], CL = {};   // CL = per-card language overrides

const t = (k, l = li) => T[k][l];
const fill = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);
const inr = x => '₹' + Number(x).toLocaleString('en-IN');

/* ---------- on-device storage (never leaves the phone/browser) ---------- */
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch { /* ignore */ } }
};
const BLANK = { track: '', occ: '', age: null, income: null, land: null, gender: '', cat: '', course: '', stage: '', edu: '', bpl: '', home: '', tgid: '', svc: '', pension: '', ward: '', level: '', medal: '', dis: null, udid: '' };
const SP = Object.assign({}, BLANK, store.get('ys.profile') || {});   // SP = the saved profile
const save = () => store.set('ys.profile', SP);

/* ---------- categories and bio-data fields come from the backend (/api/config) ---------- */
let CATS = [], FLD = {}, FIELDS = {}, ALL = ['track'];
const D = ['', '—', '—', '—'];
const OPT = {}, NUM = [];
function loadConfig(cfg) {
  CATS = cfg.categories; FLD = cfg.fields;
  OPT.track = [['', 'Choose…', 'चुनें', 'தேர்ந்தெடுங்கள்'], ...CATS.map(c => [c.id, ...c.name])];
  NUM.length = 0; ALL = ['track'];
  for (const [k, f] of Object.entries(FLD)) { ALL.push(k); if (f.type === 'num') NUM.push(k); else OPT[k] = [D, ...f.options]; }
  OPT.occE = [D, ...FLD.occ.options.filter(o => FLD.occ.pick.includes(o[0]))];   // what an entrepreneur can pick
  CATS.forEach(c => { FIELDS[c.id] = c.fields; });
}
const catOf = id => CATS.find(c => c.id === id);
// some questions only apply after an earlier answer (e.g. course only for college students)
const fieldOn = (k, p = SP) => { const w = FLD[k] && FLD[k].when; return !w || p[w.field] !== w.ne; };
const trackPatch = v => ({ track: v, occ: v === 'f' ? 'farmer' : v === 's' ? 'student' : v === 'y' ? 'unemp' : '' });

function disp(k, v) {
  if (OPT[k]) { const f = OPT[k].find(x => x[0] === v); return f ? f[1 + li] : v; }
  return k === 'income' ? inr(v) : k === 'dis' ? v + '%' : v;
}

/* ---------- profile: form + saved chips ---------- */
function collect() {   // form -> SP
  ALL.forEach(k => {
    const el = $(k); if (!el || !$('fields').contains(el)) return;
    SP[k] = NUM.includes(k) ? (el.value === '' ? null : +el.value) : el.value;
  });
}
function buildForm(over) {   // SP -> form
  if (!CATS.length) return;
  if (over) Object.assign(SP, over);
  const tr = SP.track || '', ix = 1 + li;
  const lab = k => (k === 'income' ? t('income_' + tr) : k === 'occ' ? t('occE') : t(k));
  const num = k => `<div><label for="${k}">${lab(k)}</label><input type="number" inputmode="numeric" min="0"${FLD[k].max ? ` max="${FLD[k].max}"` : ''} id="${k}"></div>`;
  const sel = k => `<div><label for="${k}">${lab(k)}</label><select id="${k}">${(k === 'occ' ? OPT.occE : OPT[k]).map(o => `<option value="${o[0]}">${o[ix]}</option>`).join('')}</select></div>`;
  const fs = tr ? FIELDS[tr].filter(k => fieldOn(k)) : [];
  $('fields').innerHTML = `<div class="full">${sel('track')}</div>` + (tr ? fs.map(k => (NUM.includes(k) ? num(k) : sel(k))).join('') : `<p class="note full">${t('pick')}</p>`);
  ALL.forEach(k => { const el = $(k); if (el && $('fields').contains(el) && SP[k] != null) el.value = SP[k]; });
  $('find').hidden = !tr;
  renderCat();
}
function renderCat() {   // the category badge in the page header
  const c = catOf(SP.track), box = $('catpill'); if (!box) return;
  box.hidden = !c;
  if (c) box.innerHTML = `<span class="cp-ic" style="--c:${c.color}">${iconSVG(c.icon)}</span><span class="cp-t"><small>${t('yourCat')}</small><b>${c.name[li]}</b></span><a href="/" class="cp-ch">${t('changeCat')}</a>`;
}
const REBUILD = ['track', 'stage'];   // choosing these changes which other questions are shown
const onField = e => { collect(); if (e.target.id === 'track') Object.assign(SP, trackPatch(SP.track)); save(); renderChips(); if (REBUILD.includes(e.target.id)) buildForm(); };
$('fields').addEventListener('input', onField);
$('fields').addEventListener('change', onField);

function chipKeys() { return ['track', ...(FIELDS[SP.track] || []).filter(k => fieldOn(k))]; }
let slipPrev = {}, slipReady = false;
function renderChips() {
  const ks = chipKeys(), got = ks.filter(k => SP[k] !== '' && SP[k] != null);
  $('chips').innerHTML = ks.map(k => {
    const has = got.includes(k), v = has ? disp(k, SP[k]) : '';
    const flash = slipReady && has && slipPrev[k] !== String(SP[k]);   // highlight a row only when its value just changed
    return `<li class="${has ? 'on' : ''}${flash ? ' flash' : ''}"><span class="k">${t('l_' + k)}</span><i aria-hidden="true"></i><b class="v">${has ? v : '—'}</b></li>`;
  }).join('');
  slipPrev = {}; got.forEach(k => { slipPrev[k] = String(SP[k]); }); slipReady = true;
  $('slip-hint').hidden = got.length > 0;
  $('clear').hidden = !got.length;
}
function setProfile(patch) { Object.assign(SP, patch); save(); buildForm(); renderChips(); }
function resetKeepCat() { const tr = SP.track; Object.assign(SP, BLANK, tr ? trackPatch(tr) : {}); }
$('clear').onclick = () => { resetKeepCat(); save(); IV.done.clear(); buildForm(); renderChips(); };

function profile() {   // what is sent to the backend: only the fields that belong to this category
  collect();
  const tr = SP.track, f = (FIELDS[tr] || []).filter(k => fieldOn(k)), o = { track: tr };
  ALL.slice(1).forEach(k => { o[k] = f.includes(k) ? SP[k] : (NUM.includes(k) ? null : ''); });
  o.occ = tr === 'e' ? SP.occ : trackPatch(tr).occ;
  if (tr === 'w') o.gender = 'female';
  if (tr === 't') o.gender = 'other';
  if (tr === 's' && SP.stage === 'school') o.course = 'other';   // school students are not on a degree or diploma
  return o;
}

/* ---------- language + accessibility ---------- */
function applyLang() {
  document.documentElement.lang = LANGS[li];
  document.querySelectorAll('[data-t]').forEach(e => { e.textContent = t(e.dataset.t); });
  document.querySelectorAll('[data-ta]').forEach(e => e.setAttribute('aria-label', t(e.dataset.ta)));
  $('say').placeholder = t('ph'); $('nov').textContent = t('nov');
  if (!listening) $('micT').textContent = t('mic');
  [0, 1, 2].forEach(k => { $('l-' + k).classList.toggle('on', k === li); $('l-' + k).setAttribute('aria-pressed', k === li); });
  $('ttl').textContent = ['Yojana Saathi', 'योजना साथी', 'யோஜனா சாத்தி'][li];
  $('iv-ok').textContent = t('iEnter');
  CL = {};
  buildForm(); renderChips(); renderLib(); renderVoiceCheck(); if (data) render();
  if (IV.on) ivAsk();
}
[0, 1, 2].forEach(k => { $('l-' + k).onclick = () => { li = k; store.set('ys.lang', k); applyLang(); }; });

let fs = 16;
const setFs = n => { fs = Math.min(22, Math.max(14, n)); document.documentElement.style.setProperty('--fs', fs + 'px'); };
$('fs-').onclick = () => setFs(fs - 2); $('fs+').onclick = () => setFs(fs + 2); $('fs0').onclick = () => setFs(16);
$('contrast').onclick = e => {
  const on = document.documentElement.dataset.contrast !== '1';
  document.documentElement.dataset.contrast = on ? '1' : '0'; e.currentTarget.setAttribute('aria-pressed', on);
};

/* ---------- tabs ---------- */
function tab(name) {
  ['i', 'v', 'f'].forEach(k => {
    $('p-' + k).classList.toggle('on', k === name);
    $('t-' + k).classList.toggle('on', k === name);
    $('t-' + k).setAttribute('aria-selected', k === name);
  });
}
$('t-i').onclick = () => tab('i'); $('t-v').onclick = () => tab('v'); $('t-f').onclick = () => tab('f');

/* voice output lives in js/speech.js (speak, cancelSpeech, ttsMode, SR, synth, TTS) */
window.onSpeechDone = () => renderVoiceCheck();
window.onVoices = () => { renderVoiceCheck(); if (IV.on) ivRender(); };

/* ---------- voice check panel + recognition errors ---------- */
function renderVoiceCheck() {
  const m = ttsMode(li);
  $('vc-s').textContent = t(m === 'device' ? 'vcSpeakDev' : m === 'online' ? 'vcSpeakNet' : 'vcSpeakNo');
  $('vc-s').className = m === 'none' ? 'bad' : 'ok';
  $('vc-l').textContent = t(SR ? 'vcListenOk' : 'vcListenNo');
  $('vc-l').className = SR ? 'ok' : 'bad';
  $('vc-tip').hidden = m === 'device';
}
$('vc-test').onclick = async () => { TTS.online[li] = undefined; await speak(t('vcSample')); renderVoiceCheck(); };
const errKey = e => ({ 'not-allowed': 'eMic', 'service-not-allowed': 'eMic', 'language-not-supported': 'eLang', network: 'eNet', 'audio-capture': 'eNoMic' })[e] || null;

async function api(path, body) {
  const res = await fetch(path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : undefined);
  if (!res.ok) throw new Error(res.status);
  return res.json();
}

/* ---------- guided voice interview ---------- */
const TRACKQ = { f: 'track', kind: 'choice', opts: () => OPT.track.slice(1), patch: trackPatch };
const qDef = f => {
  const d = FLD[f];
  if (d.type === 'num') return { f, kind: 'num', max: d.max, qk: f === 'income' ? p => 'q_income_' + (p.track || 'e') : null };
  return { f, kind: 'choice', opts: () => (f === 'occ' ? OPT.occE : OPT[f]).slice(1), when: d.when ? p => fieldOn(f, p) : null };
};
// the question list depends on the category: the category question is only asked if none was chosen yet
const qList = () => [...(SP.track ? [] : [TRACKQ]), ...(FIELDS[SP.track] || []).map(qDef)].filter(q => !q.when || q.when(SP));
const IV = { on: null, q: null, done: new Set(), hist: [], tok: 0, rec: null, tries: 0, st: '' };
const nextQ = () => qList().find(q => !IV.done.has(q.f));
const qText = q => t(q.qk ? q.qk(SP) : 'q_' + q.f);

function setSt(s) {
  IV.st = s;
  const m = { speak: 'iSpeak', listen: 'iListen', think: 'iThink', wait: 'iWait', manual: 'iManual' };
  $('iv-status').textContent = t(m[s] || 'iWait');
  $('iv-mic').classList.toggle('rec', s === 'listen');
  $('iv-micT').textContent = s === 'listen' ? t('stop') : t('iMicBtn');
}
function ivRender() {
  const q = IV.q; if (!q) return;
  const list = qList(), total = list.length || 1;
  const n = Math.min(total, list.filter(x => IV.done.has(x.f)).length + 1);
  $('iv-n').textContent = fill(t('iQn'), { n, m: total });
  $('iv-fill').style.width = Math.round(((n - 1) / total) * 100) + '%';
  $('iv-bar').setAttribute('aria-valuenow', Math.round(((n - 1) / total) * 100));
  $('iv-q').textContent = qText(q);
  $('iv-chips').innerHTML = q.kind === 'choice' ? q.opts().map(o => `<button type="button" class="opt" data-v="${o[0]}">${o[1 + li]}</button>`).join('') : '';
  $('iv-num').hidden = q.kind !== 'num';
  if (q.kind === 'num') { $('iv-in').value = SP[q.f] != null ? SP[q.f] : ''; $('iv-in').max = q.max || ''; }
  if (ttsMode(li) === 'none') $('iv-msg').textContent = t('iNoVoice');
  setSt(IV.st || 'wait');
}
function stopRec() { if (IV.rec) { try { IV.rec.abort(); } catch { /* ignore */ } IV.rec = null; } }

async function ivAsk() {
  const tok = ++IV.tok; stopRec(); cancelSpeech();
  $('iv-said').hidden = true;
  const q = nextQ(); if (!q) return ivFinish();
  IV.q = q; IV.tries = 0; IV.on = true;
  setSt('speak'); ivRender();
  await speak(qText(q));
  if (tok !== IV.tok || !IV.on) return;
  listen(tok);
}
function listen(tok) {
  if (!SR) { setSt('manual'); $('iv-msg').textContent = t('iNoMic'); return; }
  let got = '', candidates = [], err = '';
  const r = new SR(); IV.rec = r;
  r.lang = LCODE[li]; r.interimResults = true; r.continuous = false; r.maxAlternatives = 5;
  // Ask the browser for several hypotheses; the server-side field parser will select one that fits the question.
  r.onstart = () => { if (tok === IV.tok) { setSt('listen'); $('iv-msg').textContent = ''; } };
  r.onresult = e => {
    const result = e.results[e.results.length - 1];
    const s = Array.from(e.results).map(x => x[0].transcript).join(' ').trim();
    got = s;
    if (result && result.isFinal) candidates = Array.from(result).map(x => String(x.transcript || '').trim()).filter(Boolean);
    if (tok === IV.tok) { $('iv-said').hidden = false; $('iv-said').textContent = t('iSaid') + ': “' + s.replace(/[<>]/g, '') + '”'; }
  };
  r.onerror = e => { err = e.error; };
  r.onend = () => {
    if (tok !== IV.tok || !IV.on) return;
    IV.rec = null;
    const k = errKey(err);
    if (k) { setSt('manual'); $('iv-msg').textContent = t(k); return; }   // say exactly what went wrong
    const choices = [...new Set([...(candidates || []), got].map(x => x.trim()).filter(Boolean))];
    choices.length ? handleText(choices, tok) : retry(tok);
  };
  try { r.start(); } catch { setSt('manual'); }
}
async function retry(tok) {
  if (++IV.tries >= 3) { setSt('manual'); return; }   // the status line already says: tap an option or type
  setSt('speak'); await speak(t('iSorry'));
  if (tok === IV.tok && IV.on) listen(tok);
}
async function handleText(texts, tok) {
  setSt('think');
  const choices = Array.isArray(texts) ? texts : [texts];
  try {
    // Validate recognition hypotheses against the actual question instead of blindly saving the first transcript.
    const results = await Promise.all(choices.slice(0, 5).map(async text => {
      try { return { text, ...(await api('/api/answer', { field: IV.q.f, text })) }; }
      catch { return { text, patch: null }; }
    }));
    if (tok !== IV.tok || !IV.on) return;
    const best = results.find(x => x.patch && Object.keys(x.patch).length);
    if (best) { $('iv-said').hidden = false; $('iv-said').textContent = t('iSaid') + ': “' + best.text.replace(/[<>]/g, '') + '”'; return commit(best.patch); }
  } catch { $('iv-msg').textContent = t('err'); }
  if (tok === IV.tok && IV.on) retry(tok);
}
function commit(patch) {
  const q = IV.q;
  setProfile(patch);
  IV.done.add(q.f); Object.keys(patch).forEach(k => IV.done.add(k)); IV.hist.push(q.f);
  stopRec(); cancelSpeech(); IV.tok++;
  const shown = Object.keys(patch).filter(k => patch[k] !== '' && patch[k] != null).map(k => `${t('l_' + k)}: ${disp(k, patch[k])}`).join(' · ');
  $('iv-msg').textContent = '✔ ' + t('iSaved') + (shown ? ' — ' + shown : '');
  const tok = IV.tok;
  setTimeout(() => { if (tok === IV.tok && IV.on) ivAsk(); }, 750);
}
async function ivFinish() {
  IV.on = false; IV.q = null; IV.tok++;
  $('iv-run').hidden = true; $('iv-done').hidden = false; $('iv-start').hidden = true;
  $('iv-dp').hidden = false;
  const run = runMatch(true), tok = IV.tok;
  await speak(t('iDone'));
  const d = await run; $('iv-dp').hidden = true;
  if (!d || tok !== IV.tok) return;
  const ok = d.results.filter(r => r.status !== 'no');
  speak(ok.length ? fill(t('spokenRes'), { n: ok.length, names: ok.slice(0, 3).map(r => r.name[li]).join(', ') }) : t('spokenNone'));
}
function ivReset(clearData) {
  IV.tok++; stopRec(); cancelSpeech(); IV.on = null; IV.q = null; IV.st = '';
  IV.done = new Set(); IV.hist = [];
  if (clearData) { resetKeepCat(); save(); buildForm(); renderChips(); }
  $('iv-run').hidden = true; $('iv-done').hidden = true; $('iv-start').hidden = false;
}
function ivBegin() {
  IV.done = new Set(); IV.hist = [];
  $('iv-start').hidden = true; $('iv-done').hidden = true; $('iv-run').hidden = false;
  ivAsk();
}
$('iv-go').onclick = ivBegin;
$('iv-again').onclick = () => { ivReset(true); ivBegin(); };
$('iv-restart').onclick = () => { ivReset(true); ivBegin(); };
$('iv-stop').onclick = () => ivReset(false);
$('iv-rep').onclick = () => ivAsk();
$('iv-skip').onclick = () => { if (!IV.q) return; IV.done.add(IV.q.f); IV.hist.push(IV.q.f); ivAsk(); };
$('iv-back').onclick = () => { const f = IV.hist.pop(); if (f) IV.done.delete(f); ivAsk(); };
$('iv-mic').onclick = () => {
  if (IV.st === 'listen' && IV.rec) { IV.rec.stop(); return; }
  const tok = ++IV.tok; cancelSpeech(); stopRec(); IV.tries = 0; listen(tok);
};
$('iv-chips').onclick = e => {
  const b = e.target.closest('.opt'); if (!b || !IV.q) return;
  commit(IV.q.patch ? IV.q.patch(b.dataset.v) : { [IV.q.f]: b.dataset.v });
};
function submitNum() {
  const q = IV.q, v = $('iv-in').value; if (!q || v === '' || +v < 0 || (q.max && +v > q.max) || (q.f === 'age' && +v < 1)) return;
  commit({ [q.f]: +v });
}
$('iv-ok').onclick = submitNum;
$('iv-in').onkeydown = e => { if (e.key === 'Enter') submitNum(); };

/* ---------- free speech tab ---------- */
let rec = null, listening = false;
if (!SR) $('nov').hidden = false;
$('mic').onclick = () => {
  if (!SR) { $('say').focus(); return; }
  if (listening) { rec.stop(); return; }
  rec = new SR(); rec.lang = LCODE[li]; rec.interimResults = true; rec.continuous = true; rec.maxAlternatives = 5;
  const base = $('say').value ? $('say').value + ' ' : '';
  rec.onresult = e => { let s = ''; for (const r of e.results) s += r[0].transcript; $('say').value = base + s; };
  rec.onstart = () => { listening = true; $('mic').classList.add('rec'); $('micT').textContent = t('stop'); };
  rec.onend = () => { listening = false; $('mic').classList.remove('rec'); $('micT').textContent = t('mic'); };
  rec.onerror = e => { const k = errKey(e.error); if (k) { $('nov').textContent = t(k); $('nov').hidden = false; } rec.onend(); };
  rec.start();
};
let exi = 0;
const EX = [
  ['I am a 45 year old farmer. I have 2 acres of land, income 80 thousand rupees per year, OBC category.', 'I am a 20 year old girl student in college. My family income is 3 lakh per year. I am SC category.', 'I am a 32 year old man running a small shop. I want a business loan. Income 2 lakh per year.'],
  ['मैं 45 साल का किसान हूँ, मेरे पास 2 एकड़ जमीन है, सालाना आय 80 हजार रुपये, ओबीसी।', 'मैं 20 साल की छात्रा हूँ, कॉलेज में पढ़ती हूँ। परिवार की सालाना आय 3 लाख है। मैं अनुसूचित जाति से हूँ।', 'मैं 32 साल का व्यापारी हूँ, छोटी दुकान चलाता हूँ। मुझे व्यवसाय ऋण चाहिए। सालाना आय 2 लाख।'],
  ['நான் 45 வயது விவசாயி. எனக்கு 2 ஏக்கர் நிலம் உள்ளது. ஆண்டு வருமானம் 80 ஆயிரம். பிற்படுத்தப்பட்ட வகுப்பு.', 'நான் 20 வயது மாணவி, கல்லூரியில் பொறியியல் படிக்கிறேன். குடும்ப ஆண்டு வருமானம் 3 லட்சம். நான் ஆதிதிராவிடர் பிரிவு.', 'நான் 32 வயது ஆண், சிறிய கடை நடத்துகிறேன். தொழில் கடன் வேண்டும். ஆண்டு வருமானம் 2 லட்சம்.']
];
$('ex').onclick = () => { $('say').value = EX[li][exi++ % 3]; };

$('parse').onclick = async () => {
  const h = $('heard');
  try {
    const { profile: o } = await api('/api/parse', { text: $('say').value, track: SP.track });
    const keys = Object.keys(o); h.hidden = false;
    if (!keys.length) { h.textContent = t('nothing'); tab('f'); return; }
    setProfile(o);
    h.innerHTML = `<b>${t('heard')}</b><br>` + keys.filter(k => o[k] !== '').map(k => `${t('l_' + k)}: <b>${disp(k, o[k])}</b>`).join(' &nbsp;|&nbsp; ');
    tab('f'); h.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch { h.hidden = false; h.textContent = t('err'); }
};

/* ---------- matching ---------- */
async function runMatch(scroll) {
  if (!SP.track) { $('out').innerHTML = `<p class="empty">${t('pick')}</p>`; return null; }
  try {
    data = await api('/api/match', { profile: profile() });
    render();
    if (scroll) $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    return data;
  } catch { $('out').innerHTML = `<p class="empty">${t('err')}</p>`; return null; }
}
$('find').onclick = () => runMatch(true);

/* ---------- scheme card (used in results and in the library) ---------- */
function cardHTML(r, ctx, open) {
  const L = CL[ctx + r.id] != null ? CL[ctx + r.id] : li, st = r.status, lg = LANGS[L];
  const pills = PILL.map((n, k) => `<button type="button" class="lp${k === L ? ' on' : ''}" data-pl="${ctx}|${r.id}|${k}" aria-pressed="${k === L}" lang="${LANGS[k]}">${n}</button>`).join('');
  const checks = r.checks
    ? r.checks.map(k => `<li class="${k.result ? 'ok' : k.result === false ? 'bad' : 'unk'}"><b>${k.result ? '✓' : k.result === false ? '✗' : '?'}</b>${k.label[L]}</li>`).join('')
    : r.conditions.map(c => `<li><b>•</b>${c[L]}</li>`).join('');
  return `<details class="card ${st || ''}" data-id="${r.id}"${open ? ' open' : ''}>
    <summary lang="${lg}"><span class="s-main"><h3>${r.name[L]}</h3><span class="ben">${r.benefit[L]}</span></span><span class="s-meta">${st ? `<span class="badge">${t(st, L)}</span><span class="conf">${r.confidence}% ${t('cfT', L)}</span>` : ''}<span class="tag">${vocab.tracks[r.track][L]}</span></span></summary>
    <div class="body" lang="${lg}">
      <div class="pills" role="group" aria-label="${t('readIn')}"><span class="pl-l">${t('readIn')}</span>${pills}</div>
      <h4>${t('about', L)}</h4><p class="about">${r.about[L]}</p>
      <h4>${st ? t('why', L) : t('elig', L)}</h4><ul>${checks}</ul>
      <h4>${t('proc', L)}</h4><ol class="proc">${r.steps.map(s => `<li>${vocab.steps[s][L]}</li>`).join('')}</ol>
      <h4>${t('docs', L)}</h4><ul>${r.docs.map(d => `<li><b>•</b>${vocab.docs[d][L]}</li>`).join('')}</ul>
      <div class="acts"><a class="btn pri" href="${r.url}" target="_blank" rel="noopener noreferrer">${t('apply', L)}</a><button class="btn" data-say="${ctx}|${r.id}" type="button"><span aria-hidden="true">🔊</span> ${t('read', L)}</button></div>
    </div></details>`;
}
const lookup = (ctx, id) => (ctx === 'res' ? data.results : schemes).find(r => r.id === id);
function speakScheme(r, L) {
  const conds = (r.conditions || r.checks.map(c => c.label)).map(c => c[L]).join(', ');
  speak(`${r.name[L]}. ${r.about[L]} ${t('benefitL', L)}: ${r.benefit[L]}. ${t('elig', L)}: ${conds}. ${t('proc', L)}: ${r.steps.map(s => vocab.steps[s][L]).join('. ')}. ${t('docs', L)}: ${r.docs.map(d => vocab.docs[d][L]).join(', ')}.`, L);
}
function cardEvents(box) {
  box.addEventListener('click', e => {
    const p = e.target.closest('[data-pl]');
    if (p) {
      const [c, id, k] = p.dataset.pl.split('|'); CL[c + id] = +k;
      const el = p.closest('details'), tmp = document.createElement('div');
      tmp.innerHTML = cardHTML(lookup(c, id), c, el.open); el.replaceWith(tmp.firstElementChild); return;
    }
    const s = e.target.closest('[data-say]');
    if (s) { const [c, id] = s.dataset.say.split('|'); speakScheme(lookup(c, id), CL[c + id] != null ? CL[c + id] : li); }
  });
}
cardEvents($('out')); cardEvents($('libOut'));

/* ---------- results ---------- */
function render() {
  const ok = data.results.filter(r => r.status !== 'no'), no = data.results.filter(r => r.status === 'no');
  if (!ok.length) { $('out').innerHTML = `<p class="empty">${t('none')}</p>` + noList(no); return; }
  const { yearly: yr, once: one } = data.totals;
  const cash = (yr || one) ? `<p class="sum-l">${t('youmay')}</p><p class="sum-v">${yr ? inr(yr) + ' ' + t('peryr') : ''}${yr && one ? ' ' + t('plus') + ' ' : ''}${one ? inr(one) + ' ' + t('once') : ''}</p>` : '';
  const txt = 'Yojana Saathi\n' + ok.map(r => '• ' + r.name[li] + ' - ' + r.benefit[li] + '\n  ' + r.url).join('\n');
  $('out').innerHTML = `<div class="sum">${cash}<p class="sum-n">${ok.length} ${t('found')}</p></div>` +
    ok.map((r, n) => cardHTML(r, 'res', n === 0)).join('') +
    checklistHTML() + askHTML() +
    `<div class="row"><a class="btn pri" target="_blank" rel="noopener noreferrer" href="https://wa.me/?text=${encodeURIComponent(txt)}">${t('share')}</a><button class="btn" id="prt" type="button">${t('print')}</button></div>` + noList(no);
  const ed = $('ask-edit'); if (ed) ed.onclick = () => { tab('f'); $('finder').scrollIntoView({ behavior: 'smooth' }); };
  $('prt').onclick = () => { document.querySelectorAll('#out .card').forEach(c => c.open = true); window.print(); };
}
function checklistHTML() {   // papers that unlock the most schemes, from the backend
  const c = (data.checklist || []).slice(0, 8); if (!c.length) return '';
  return `<div class="ck"><h3>${t('ckT')}</h3><p class="note">${t('ckP')}</p><ul>` +
    c.map(x => `<li><b>${vocab.docs[x.doc][li]}</b><span>${fill(t('ckN'), { n: x.count })}</span></li>`).join('') + '</ul></div>';
}
function askHTML() {   // the details that would settle the most "check this" schemes
  const a = (data.askNext || []).filter(x => T['l_' + x.field]); if (!a.length) return '';
  return `<div class="ask"><p>${t('missT')} <b>${a.map(x => t('l_' + x.field)).join(', ')}</b></p><button class="btn sm" id="ask-edit" type="button">${t('editDetails')}</button></div>`;
}
function noList(no) {
  if (!no.length) return '';
  return `<details class="notel"><summary>${t('notel')} (${no.length})</summary><ul>` + no.map(r => `<li>${r.name[li]}: ${r.checks.filter(k => k.result === false).map(k => k.label[li]).join(', ')}</li>`).join('') + '</ul></details>';
}

/* ---------- scheme library ---------- */
const LIB = { track: '', q: '' };
function renderLib() {
  if (!vocab) return;
  $('libFilter').innerHTML = [['', t('fAll')], ...CATS.map(c => [c.id, c.name[li]])]
    .map(([k, n]) => `<button type="button" class="chip${LIB.track === k ? ' on' : ''}" data-ft="${k}" aria-pressed="${LIB.track === k}">${n}</button>`).join('');
  $('libQ').placeholder = t('libSearch');
  const q = LIB.q.trim().toLowerCase();
  const list = schemes.filter(r => (!LIB.track || (r.tracks || [r.track]).includes(LIB.track)) &&
    (!q || (r.name.join(' ') + ' ' + r.benefit[li] + ' ' + r.about[li]).toLowerCase().includes(q)));
  $('libCount').textContent = fill(t('count'), { n: list.length });
  $('libOut').innerHTML = list.length ? list.map(r => cardHTML(r, 'lib', false)).join('') : `<p class="empty">${t('libNone')}</p>`;
}
$('libFilter').onclick = e => { const b = e.target.closest('[data-ft]'); if (!b) return; LIB.track = b.dataset.ft; renderLib(); };
$('libQ').oninput = e => { LIB.q = e.target.value; renderLib(); };

/* ---------- start ---------- */
(async () => {
  const sl = store.get('ys.lang'); if (sl === 0 || sl === 1 || sl === 2) li = sl;
  try {
    const cfg = await api('/api/config');
    loadConfig(cfg);
    [vocab, schemes] = await Promise.all([api('/api/vocab'), api('/api/schemes')]);
    // arriving from the home page: /finder.html?c=f
    const c = new URLSearchParams(location.search).get('c');
    if (c && catOf(c) && SP.track !== c) {
      const keep = { age: SP.age, gender: SP.gender, cat: SP.cat, income: SP.income };   // details that mean the same in every category
      Object.assign(SP, BLANK, keep, trackPatch(c)); save();
    }
  } catch { $('out').innerHTML = `<p class="empty">${t('err')}</p>`; }
  applyLang();
})();

if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
