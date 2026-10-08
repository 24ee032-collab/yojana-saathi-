/* Yojana Saathi - home page: choose a language and a category. Everything else happens on finder.html */
const $ = id => document.getElementById(id);
let li = 0, cats = [];
const t = (k, l = li) => T[k][l];
const fill = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } }
};

function render() {
  document.documentElement.lang = LANGS[li];
  document.querySelectorAll('[data-t]').forEach(e => { e.textContent = t(e.dataset.t); });
  document.querySelectorAll('[data-ta]').forEach(e => e.setAttribute('aria-label', t(e.dataset.ta)));
  $('ttl').textContent = ['Yojana Saathi', 'योजना साथी', 'யோஜனா சாத்தி'][li];
  [0, 1, 2].forEach(k => { $('l-' + k).classList.toggle('on', k === li); $('l-' + k).setAttribute('aria-pressed', k === li); });
  $('grid').innerHTML = cats.map((c, n) => `<a class="cc" href="/finder.html?c=${c.id}" data-c="${c.id}" style="--c:${c.color}">
      <span class="cc-n" aria-hidden="true">${String(n + 1).padStart(2, '0')}</span>
      <span class="cc-ic">${iconSVG(c.icon)}</span>
      <h3>${c.name[li]}</h3><p>${c.desc[li]}</p>
      <span class="cc-f"><span>${fill(t('count'), { n: c.count })}</span><b aria-hidden="true">→</b></span></a>`).join('');
}
[0, 1, 2].forEach(k => { $('l-' + k).onclick = () => { li = k; store.set('ys.lang', k); cancelSpeech(); render(); }; });

/* reading aids, same as the finder page */
let fs = 16;
const setFs = n => { fs = Math.min(22, Math.max(14, n)); document.documentElement.style.setProperty('--fs', fs + 'px'); };
$('fs-').onclick = () => setFs(fs - 2); $('fs+').onclick = () => setFs(fs + 2); $('fs0').onclick = () => setFs(16);
$('contrast').onclick = e => {
  const on = document.documentElement.dataset.contrast !== '1';
  document.documentElement.dataset.contrast = on ? '1' : '0'; e.currentTarget.setAttribute('aria-pressed', on);
};

/* voice: read the categories aloud, or say who you are */
let speaking = false;
$('hlisten').onclick = async () => {
  if (speaking) { cancelSpeech(); speaking = false; return; }
  speaking = true; await speak(t('homeSpoken')); speaking = false;
};
let rec = null;
function open(id) {
  const c = cats.find(x => x.id === id); if (!c) return;
  const card = document.querySelector(`[data-c="${id}"]`); if (card) card.classList.add('go');
  $('hmsg').textContent = t('homeOpen') + ': ' + c.name[li];
  setTimeout(() => { location.href = '/finder.html?c=' + id; }, 650);
}
$('hsay').onclick = async () => {
  if (rec) { rec.stop(); return; }
  if (!SR) { $('hmsg').textContent = t('iNoMic'); return; }
  cancelSpeech(); await speak(t('homeAsk'));
  let got = '', candidates = [], err = '';
  const r = new SR(); rec = r;
  r.lang = LCODE[li]; r.interimResults = true; r.continuous = false; r.maxAlternatives = 5;
  r.onstart = () => { $('hsay').classList.add('rec'); $('hmsg').textContent = t('iListen'); };
  r.onresult = e => { let s = ''; for (const x of e.results) s += x[0].transcript; got = s; const last = e.results[e.results.length - 1]; if (last && last.isFinal) candidates = Array.from(last).map(x => String(x.transcript || '').trim()).filter(Boolean); $('hmsg').textContent = '“' + s.replace(/[<>]/g, '') + '”'; };
  r.onerror = e => { err = e.error; };
  r.onend = async () => {
    rec = null; $('hsay').classList.remove('rec');
    const k = ({ 'not-allowed': 'eMic', 'service-not-allowed': 'eMic', 'language-not-supported': 'eLang', network: 'eNet', 'audio-capture': 'eNoMic' })[err];
    if (k) { $('hmsg').textContent = t(k); return; }
    if (!got.trim()) { $('hmsg').textContent = t('homeNo'); return; }
    try {
      const choices = [...new Set([...candidates, got].map(x => x.trim()).filter(Boolean))].slice(0, 5);
      const answers = await Promise.all(choices.map(async text => { try { const res = await fetch('/api/answer', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ field: 'track', text }) }); return { text, ...(await res.json()) }; } catch { return { patch: null }; } }));
      const best = answers.find(x => x.patch && x.patch.track);
      if (best) return open(best.patch.track);
    } catch { /* fall through */ }
    $('hmsg').textContent = t('homeNo'); speak(t('homeNo'));
  };
  try { r.start(); } catch { rec = null; }
};

(async () => {
  const sl = store.get('ys.lang'); if (sl === 0 || sl === 1 || sl === 2) li = sl;
  try { cats = await (await fetch('/api/categories')).json(); } catch { $('grid').innerHTML = `<p class="empty">${t('err')}</p>`; }
  render();
})();
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
