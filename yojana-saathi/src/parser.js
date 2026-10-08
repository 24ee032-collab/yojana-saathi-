// Turns spoken or typed text (English, Hindi, Tamil) into a profile.
// Also answers single interview questions ("what is your age?" -> 45).

const { convert } = require('./numwords');
const TA_DIGITS = '௦௧௨௩௪௫௬௭௮௯';
const HI_DIGITS = '०१२३४५६७८९';

function normalise(raw) {
  const s = String(raw).toLowerCase()
    .replace(/[०-९]/g, d => HI_DIGITS.indexOf(d))
    .replace(/[௦-௯]/g, d => TA_DIGITS.indexOf(d))
    .replace(/,(?=\d{3})/g, '');
  return convert(s);   // number words -> digits (Tamil, Hindi, English)
}

/* ---------- field detectors (each takes normalised text) ---------- */
const OCC = [
  ['farmer',   /farm|kisan|किसान|खेती|விவசாய|உழவர்|விவசாயி/],
  ['student',  /student|college|छात्र|विद्यार्थी|पढ़|மாணவ|கல்லூரி/],
  ['vendor',   /vendor|hawker|ठेला|रेहड़ी|फेरी|தெருவோர|தள்ளுவண்டி|சாலையோர/],
  ['artisan',  /artisan|carpenter|potter|weaver|tailor|barber|blacksmith|कारीगर|बढ़ई|दर्जी|कुम्हार|बुनकर|नाई|लोहार|கைவினை|தச்சர்|குயவர்|நெசவாளர்|தையல்|முடி\s?திருத்/],
  ['business', /startup|start-up|shop|business|entrepreneur|दुकान|व्यापार|व्यवसाय|उद्यमी|स्टार्टअप|கடை|வணிக|வியாபார|தொழில்|ஸ்டார்ட்\s?அப்/],
  ['labour',   /labou?r|daily wage|मज़दूर|मजदूर|दिहाड़ी|கூலி|தொழிலாளி|தினக்கூலி/],
  ['unemp',    /unemploy|बेरोज़गार|बेरोजगार|வேலை\s?இல்லா|வேலையில்லா/]
];
const TRACK_OF = { farmer: 'f', student: 's', vendor: 'e', artisan: 'e', business: 'e', unemp: 'e', labour: 'e' };

function detectOcc(s) {
  for (const [k, r] of OCC) if (r.test(s)) return k;
  return null;
}
function detectGender(s) {
  if (/woman|female|lady|girl|mother|wife|महिला|औरत|लड़की|पत्नी|माँ|छात्रा|பெண்|மகள்|மனைவி|அம்மா|தாய்|மாணவி/.test(s)) return 'female';
  if (/\bman\b|\bmale\b|\bboy\b|father|husband|पुरुष|आदमी|लड़का|पिता|ஆண்(?!டு)|மகன்|கணவர்|அப்பா|தந்தை/.test(s)) return 'male';
  if (/\bother\b|transgender|third gender|अन्य|ट्रांसजेंडर|மற்றவர்|திருநங்கை|மூன்றாம் பாலினம்/.test(s)) return 'other';
  return null;
}
function detectCat(s) {
  if (/\bsc\b|scheduled caste|दलित|अनुसूचित जाति|ஆதிதிராவிடர்|பட்டியல் இன|பட்டியலின|எஸ்\s?சி/.test(s)) return 'SC';
  if (/\bst\b|scheduled tribe|tribal|आदिवासी|अनुसूचित जनजाति|பழங்குடி|எஸ்\s?டி/.test(s)) return 'ST';
  if (/obc|\bm?bc\b|backward|पिछड़ा|पिछड़े|பிற்படுத்தப்பட்ட|மிகவும் பிற்படுத்த|ஓ\s?பி\s?சி|பி\s?சி/.test(s)) return 'OBC';
  if (/general|\boc\b|open category|सामान्य|பொது|ஓ\s?சி/.test(s)) return 'General';
  return null;
}
function detectCourse(s) {
  if (/engineer|b\.?tech|diploma|polytechnic|pharmacy|\biti\b|technical|इंजीनियर|डिप्लोमा|तकनीकी|बीटेक|பொறியியல்|டிப்ளமோ|தொழில்நுட்ப|மருந்தியல்|பாலிடெக்னிக்/.test(s)) return 'tech';
  if (/\bb\.?a\b|b\.?sc|b\.?com|degree|graduation|bachelor|arts|बीए|बीएससी|बीकॉम|स्नातक|இளங்கலை|பட்டப்படிப்பு|கலை/.test(s)) return 'other';
  return null;
}
function detectAge(s) {
  let m = s.match(/(?:age|aged|उम्र|வயது|வயசு)\D{0,6}(\d{1,3})/) ||
          s.match(/(\d{1,3})\s*(?:years?|yrs?|साल|वर्ष|बरस|வயது|வயசு)/);
  return m && +m[1] > 0 && +m[1] < 111 ? +m[1] : null;
}
function detectIncome(s, bareOk) {
  const LAKH = /(\d+(?:\.\d+)?)\s*(?:lakh|lac|लाख|லட்ச(?:ம்|த்து|த்தி)?|லக்ஷ(?:ம்|த்து)?)/;
  const THOU = /(\d+(?:\.\d+)?)\s*(?:thousand|k\b|हजार|हज़ार|ஆயிர(?:ம்|த்து))/;
  let m, inc = null;
  const lk = s.match(LAKH), th = s.match(THOU);
  if (lk || th) inc = (lk ? +lk[1] * 100000 : 0) + (th ? +th[1] * 1000 : 0);
  else if ((m = s.match(/(?:income|earn|salary|आय|कमाई|कमाता|कमाती|வருமானம்|சம்பளம்|சம்பாதிக்)\D{0,20}(\d{4,9})/))) inc = +m[1];
  else if (bareOk && (m = s.match(/(\d{4,9})/))) inc = +m[1];
  if (inc == null) return null;
  const monthly = /per month|monthly|a month|महीने|प्रति माह|मासिक|महीना|மாதம்|மாதத்திற்கு|மாத\s/.test(s);
  const yearly = /per year|yearly|annual|सालाना|वार्षिक|ஆண்டு|வருடம்|வருட/.test(s);
  if (monthly && !yearly) inc *= 12;
  return Math.round(inc);
}
function detectLand(s, bareOk) {
  let m = s.match(/(\d+(?:\.\d+)?)\s*(acres?|एकड़|hectares?|हेक्टेयर|bigha|बीघा|ஏக்கர்|ஹெக்டேர்|cents?|சென்ட்)/);
  if (m) {
    let a = +m[1];
    if (/hect|हेक्टेयर|ஹெக்டேர்/.test(m[2])) a *= 2.47;
    else if (/bigha|बीघा/.test(m[2])) a *= 0.6;
    else if (/cent|சென்ட்/.test(m[2])) a *= 0.01;
    return Math.round(a * 100) / 100;
  }
  if (bareOk && (m = s.match(/(\d+(?:\.\d+)?)/))) return +m[1];
  return null;
}


/* ---------- detectors for the new categories and bio-data fields ---------- */
const NEG = /\b(no|not|nope|never|don'?t|do not|haven'?t|without|none)\b|नहीं|नही|नहि|இல்லை|இல்ல|வேண்டாம்/;
function detectYesNo(s) {
  if (NEG.test(s)) return 'no';
  if (/\b(yes|yeah|yep|yup|sure|have|has|own|got)\b|हाँ|हां|जी|है|हूँ|ஆம்|ஆமாம்|உண்டு|உள்ளது|இருக்கிறது|இருக்கு/.test(s)) return 'yes';
  return null;
}
// conservative: a keyword counts as "yes" only when nothing in the sentence is negative
const flag = (s, re) => (re.test(s) && !NEG.test(s) ? 'yes' : null);
function detectEdu(s) {
  if (/post\s?grad|master|\bm\.?(a|sc|com|tech|ba)\b|\bpg\b|ph\.?d|स्नातकोत्तर|एमए|एमएससी|முதுகலை|முனைவர்/.test(s)) return 'pg';
  if (/graduate|graduation|degree|bachelor|\bb\.?(a|sc|com|tech|e|ed)\b|diploma|engineering|स्नातक|डिग्री|बीए|बीएससी|बीकॉम|डिप्लोमा|பட்டம்|இளங்கலை|பட்டதாரி|டிப்ளமோ|பொறியியல்/.test(s)) return 'grad';
  if (/\b12\b|12th|twelfth|plus two|\+2|higher secondary|intermediate|१२|बारहवीं|12वीं|इंटर|பன்னிரண்டு|12ஆம்|ப்ளஸ்\s?டூ|மேல்நிலை/.test(s)) return '12th';
  if (/\b10\b|10th|tenth|matric|sslc|दसवीं|10वीं|பத்தாம்|பத்தாவது|எஸ்எஸ்எல்சி/.test(s)) return '10th';
  if (/below|primary|middle school|illiterate|uneducated|no school|never (went|studied)|\b[1-9]th\b|\bclass [1-9]\b|अनपढ़|प्राथमिक|पाँचवीं|आठवीं|படிக்கவில்லை|தொடக்க|ஐந்தாம்|எட்டாம்/.test(s)) return 'below10';
  return null;
}
function detectStage(s) {
  if (/post\s?grad|\bpg\b|master|\bm\.?(a|sc|com|tech)\b|ph\.?d|research|स्नातकोत्तर|முதுகலை|ஆய்வு/.test(s)) return 'pg';
  if (/\bug\b|under\s?grad|degree|\bb\.?(a|sc|com|tech|e)\b|diploma|\biti\b|polytechnic|bachelor|engineering|college|स्नातक|डिप्लोमा|कॉलेज|இளங்கலை|டிப்ளமோ|கல்லூரி|பொறியியல்/.test(s)) return 'ug';
  if (/school|class|\b(9|10|11|12)(th)?\b|plus two|स्कूल|कक्षा|பள்ளி|வகுப்பு/.test(s)) return 'school';
  return null;
}
function detectSvc(s) {
  if (/jco|subedar|naib|havildar|naik|sepoy|jawan|sailor|airman|other ranks?|सूबेदार|हवलदार|नायक|सिपाही|जवान|சுபேதார்|ஹவில்தார்|நாயக்|சிப்பாய்|வீரர்/.test(s)) return 'jco';
  if (/officer|colonel|major|captain|lieutenant|brigadier|अधिकारी|अफसर|कर्नल|मेजर|கர்னல்|அதிகாரி|மேஜர்/.test(s)) return 'off';
  return null;
}
function detectLevel(s) {
  if (/international|olympic|asian games|commonwealth|world|अंतरराष्ट्रीय|अंतर्राष्ट्रीय|ओलंपिक|एशियाई|विश्व|சர்வதேச|ஒலிம்பிக்|ஆசிய|உலக/.test(s)) return 'intl';
  if (/national|राष्ट्रीय|தேசிய/.test(s)) return 'nat';
  if (/state|राज्य|மாநில/.test(s)) return 'state';
  if (/district|school|college|university|local|जिला|स्कूल|विश्वविद्यालय|மாவட்ட|பள்ளி|உள்ளூர்/.test(s)) return 'dist';
  return null;
}
function detectDis(s, bareOk) {
  let m = s.match(/(\d{1,3}(?:\.\d+)?)\s*(?:%|percent|per cent|प्रतिशत|फीसदी|फ़ीसदी|சதவீதம்|சதம்)/);
  if (!m && bareOk) m = s.match(/(\d{1,3})/);
  if (!m) return null;
  const v = Math.round(+m[1]);
  return v >= 1 && v <= 100 ? v : null;
}
// which of the 10 categories the person is describing (null if unclear)
const SPECIAL = [
  ['w', /widow|विधवा|விதவை|கணவரை இழந்த|husband (died|passed|expired)/],
  ['t', /transgender|third gender|hijra|kinnar|ट्रांसजेंडर|किन्नर|हिजड़ा|திருநங்கை|மூன்றாம் பாலினம்/],
  ['x', /ex-?servicem[ae]n|veteran|retired (from )?(the )?(army|navy|air force|soldier)|army pension|पूर्व[ -]?सैनिक|भूतपूर्व|सेवानिवृत्त सैनिक|முன்னாள் (ராணுவ|படை)|ராணுவ வீரர்/],
  ['p', /sports\s?person|athlete|kabaddi|cricketer|wrestler|boxer|sprinter|footballer|खिलाड़ी|एथलीट|விளையாட்டு வீரர்|விளையாட்டு வீராங்கனை|தடகள/],
  ['d', /disab|divyang|handicap|wheelchair|\bblind|\bdeaf|visually impaired|physically challenged|दिव्यांग|विकलांग|अपंग|नेत्रहीन|மாற்றுத்திறன|ஊனம|பார்வையற்ற|காது கேளாத/],
  ['o', /senior citizen|old age|elderly|pensioner|वरिष्ठ नागरिक|बुजुर्ग|वृद्ध|முதியோர்|மூத்த குடிமக|முதியவர்/]
];
function detectTrack(s) {
  for (const [t, re] of SPECIAL) if (re.test(s)) return { track: t, occ: '' };
  const occ = detectOcc(s);
  if (occ === 'unemp') return /business|shop|startup|दुकान|व्यवसाय|கடை|தொழில்/.test(s) ? { track: 'e', occ: 'unemp' } : { track: 'y', occ: 'unemp' };
  if (occ) return { track: TRACK_OF[occ], occ };
  return null;
}

/* ---------- full-text extraction ---------- */
function extract(raw, ctxTrack) {
  const s = normalise(raw), o = {};
  const age = detectAge(s); if (age != null) o.age = age;
  const g = detectGender(s); if (g && g !== 'other') o.gender = g;
  const tr = detectTrack(s);
  if (tr) {
    o.track = tr.track;
    if (tr.occ) o.occ = tr.occ;
    if (tr.track === 'f') o.occ = 'farmer';
    if (tr.track === 's') o.occ = 'student';
  }
  const inc = detectIncome(s, false); if (inc != null) o.income = inc;
  const land = detectLand(s, false); if (land != null) o.land = land;
  const cat = detectCat(s); if (cat) o.cat = cat;
  const eff = ctxTrack || o.track;
  if (o.occ === 'student' || eff === 's') {
    const c = detectCourse(s); if (c) o.course = c;
    const st = detectStage(s); if (st) o.stage = st;
  }
  if (['y', 't', 'd', 'w'].includes(eff)) { const e = detectEdu(s); if (e) o.edu = e; }
  if (eff === 'd') { const d = detectDis(s, false); if (d != null) o.dis = d; const u = flag(s, /udid|swavlamban|यूडीआईडी|யுடிஐடி/); if (u) o.udid = u; }
  if (eff === 'x') { const v = detectSvc(s); if (v) o.svc = v; const pn = flag(s, /pension|पेंशन|ஓய்வூதியம்/); if (pn) o.pension = pn; }
  if (eff === 'p') { const l = detectLevel(s); if (l) o.level = l; const m = flag(s, /medal|पदक|பதக்கம்/); if (m) o.medal = m; }
  const b = flag(s, /\bbpl\b|below poverty|antyodaya|गरीबी रेखा|बीपीएल|வறுமைக் கோட்டிற்கு|பிபிஎல்/); if (b) o.bpl = b;
  if (ctxTrack) {              // the person already chose a category: keep it, only add details
    delete o.track;
    if (ctxTrack !== 'e') delete o.occ;
  }
  return o;
}

/* ---------- one interview answer -> patch of profile fields (or null) ---------- */
const YN = ['bpl', 'home', 'tgid', 'pension', 'ward', 'medal', 'udid'];
const FIELDS = ['track', 'occ', 'age', 'gender', 'cat', 'income', 'land', 'course', 'stage', 'edu', 'svc', 'level', 'dis', ...YN];
function answer(field, raw) {
  if (!FIELDS.includes(field)) return null;
  const s = normalise(raw);
  if (!s.trim()) return null;
  let patch = null;
  switch (field) {
    case 'track': {
      const tr = detectTrack(s);
      if (tr) patch = tr.track === 'e' || !tr.occ ? { track: tr.track, occ: tr.occ } : { track: tr.track, occ: tr.occ === 'labour' ? 'labour' : tr.occ };
      break;
    }
    case 'occ': { const v = detectOcc(s); if (v && v !== 'farmer' && v !== 'student') patch = { occ: v }; break; }
    case 'age': { const m = s.match(/(\d{1,3})/); if (m && +m[1] > 0 && +m[1] < 111) patch = { age: +m[1] }; break; }
    case 'gender': { const v = detectGender(s); if (v) patch = { gender: v }; break; }
    case 'cat': { const v = detectCat(s); if (v) patch = { cat: v }; break; }
    case 'stage': { const v = detectStage(s); if (v) patch = { stage: v }; break; }
    case 'edu': { const v = detectEdu(s); if (v) patch = { edu: v }; break; }
    case 'svc': { const v = detectSvc(s); if (v) patch = { svc: v }; break; }
    case 'level': { const v = detectLevel(s); if (v) patch = { level: v }; break; }
    case 'dis': { const v = detectDis(s, true); if (v != null) patch = { dis: v }; break; }
    case 'course': { const v = detectCourse(s); if (v) patch = { course: v }; break; }
    case 'income': { const v = detectIncome(s, true); if (v != null) patch = { income: v }; break; }
    case 'land': { const v = detectLand(s, true); if (v != null) patch = { land: v }; break; }
  }
  if (!patch && YN.includes(field)) { const v = detectYesNo(s); if (v) patch = { [field]: v }; }
  if (!patch) return null;
  // people often volunteer more than was asked ("I am 45 and have 2 acres"); keep that too
  const extra = extract(raw);
  if (field !== 'track') { delete extra.track; if (field !== 'occ') delete extra.occ; }
  for (const k of Object.keys(extra)) if (!(k in patch) && k !== field) patch[k] = extra[k];
  return patch;
}

module.exports = { extract, answer, FIELDS };
