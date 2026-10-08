/* Shared voice engine (used by the home page and the finder page): device voice first, online voice as fallback.
   Needs a global `li` (current language index) declared by the page script. */
const LANGS = ['en', 'hi', 'ta'], LCODE = ['en-IN', 'hi-IN', 'ta-IN'], PILL = ['English', 'हिन्दी', 'தமிழ்'];
/* ---------- voice output: device voice first, online voice as a fallback ---------- */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const synth = 'speechSynthesis' in window ? window.speechSynthesis : null;
const TTS = { online: {} };            // online[l] = false after the online voice failed once
let speakId = 0, stopCur = null, player = null;

const vlang = v => v.lang.toLowerCase().replace('_', '-');
function nativeVoice(l) {
  if (!synth) return null;
  const rank = v => (vlang(v) === LCODE[l].toLowerCase() ? 2 : 0) + (/natural|online|google/i.test(v.name) ? 1 : 0);
  const vs = synth.getVoices().filter(v => vlang(v).startsWith(LANGS[l])).sort((a, b) => rank(b) - rank(a));
  return vs[0] || null;
}
const ttsMode = l => (nativeVoice(l) ? 'device' : TTS.online[l] === false ? 'none' : 'online');
function voicesReady() {               // Chrome fills its voice list a moment after page load
  return new Promise(res => {
    if (!synth || synth.getVoices().length) return res();
    synth.addEventListener('voiceschanged', () => res(), { once: true });
    setTimeout(res, 1200);
  });
}
function chunks(text, max = 170) {     // short pieces: the online voice limit, and Chrome stops long speech
  const out = []; let cur = '';
  for (const part of text.match(/[^.!?।]+[.!?।]*\s*/g) || [text]) {
    if (cur && (cur + part).length > max) { out.push(cur.trim()); cur = ''; }
    cur += part;
    while (cur.length > max) { let i = cur.lastIndexOf(' ', max); if (i < 40) i = max; out.push(cur.slice(0, i).trim()); cur = cur.slice(i); }
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}
function cancelSpeech() {
  speakId++;
  if (synth) synth.cancel();
  if (player) { player.pause(); player = null; }
  if (stopCur) { const f = stopCur; stopCur = null; f(); }
}
function sayNative(text, v) {
  return new Promise(res => {
    const u = new SpeechSynthesisUtterance(text);
    u.voice = v; u.lang = v.lang; u.rate = .92;
    let done = false;
    const fin = ok => { if (!done) { done = true; clearTimeout(to); stopCur = null; res(ok); } };
    const to = setTimeout(() => fin(true), Math.max(6000, text.length * 170));
    u.onend = () => fin(true);
    u.onerror = e => fin(e.error === 'canceled' || e.error === 'interrupted');
    stopCur = () => fin(true);
    synth.speak(u);
  });
}
function sayOnline(text, l) {
  return new Promise(res => {
    const a = new Audio('/api/tts?l=' + LANGS[l] + '&q=' + encodeURIComponent(text));
    player = a;
    let done = false, guard = setTimeout(() => fin(false), 9000);       // 9 s to start playing
    const fin = ok => { if (!done) { done = true; clearTimeout(guard); stopCur = null; if (!ok) TTS.online[l] = false; res(ok); } };
    a.onplaying = () => { clearTimeout(guard); guard = setTimeout(() => fin(true), 30000); };
    a.onended = () => fin(true);
    a.onerror = () => fin(false);
    stopCur = () => fin(true);
    a.play().catch(() => fin(false));
  });
}
async function speak(text, l = li) {   // resolves when finished; never throws; silent if no voice works
  cancelSpeech();
  const id = speakId;
  await voicesReady();
  if (id !== speakId) return;
  for (const part of chunks(text)) {
    if (id !== speakId) return;
    const v = nativeVoice(l);
    const ok = v ? await sayNative(part, v) : TTS.online[l] === false ? false : await sayOnline(part, l);
    if (!ok) break;
  }
  if (window.onSpeechDone) window.onSpeechDone();
}
if (synth) synth.onvoiceschanged = () => { if (window.onVoices) window.onVoices(); };

