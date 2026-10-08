// Turns spoken number WORDS into digits so the parser can read them.
// Speech recognition often returns "நாற்பத்தைந்து" / "पैंतालीस" / "forty five" instead of "45".
// Only numbers 0-99 and halves are converted. Multipliers (lakh, thousand, acre ...) stay as words.

/* ---------------- Tamil ---------------- */
const SIGN = { 'அ': '', 'ஆ': 'ா', 'இ': 'ி', 'ஈ': 'ீ', 'உ': 'ு', 'ஊ': 'ூ', 'எ': 'ெ', 'ஏ': 'ே', 'ஐ': 'ை', 'ஒ': 'ொ', 'ஓ': 'ோ' };
const TA_UNITS = {
  'ஒன்று': 1, 'ஒண்ணு': 1, 'இரண்டு': 2, 'ரெண்டு': 2, 'மூன்று': 3, 'மூணு': 3, 'நான்கு': 4, 'நாலு': 4,
  'ஐந்து': 5, 'அஞ்சு': 5, 'ஆறு': 6, 'ஏழு': 7, 'எட்டு': 8, 'ஒன்பது': 9, 'ஒம்பது': 9
};
const TA_BASE = {
  'பூஜ்யம்': 0, 'பூஜ்ஜியம்': 0, 'பத்து': 10, 'பதினொன்று': 11, 'பன்னிரண்டு': 12, 'பன்னிரெண்டு': 12,
  'பதிமூன்று': 13, 'பதின்மூன்று': 13, 'பதினான்கு': 14, 'பதினைந்து': 15, 'பதினாறு': 16, 'பதினேழு': 17,
  'பதினெட்டு': 18, 'பத்தொன்பது': 19,
  'இருபது': 20, 'இருவது': 20, 'முப்பது': 30, 'நாற்பது': 40, 'நாப்பது': 40, 'ஐம்பது': 50, 'அம்பது': 50,
  'அறுபது': 60, 'அறுவது': 60, 'எழுபது': 70, 'எழுவது': 70, 'எண்பது': 80, 'எம்பது': 80, 'தொண்ணூறு': 90
};
// joined bases used to build 21-99: twenty- , thirty- ...
const TA_JOIN = { 20: 'இருபத்து', 30: 'முப்பத்து', 40: 'நாற்பத்து', 50: 'ஐம்பத்து', 60: 'அறுபத்து', 70: 'எழுபத்து', 80: 'எண்பத்து', 90: 'தொண்ணூற்று' };
const TA_AMBIG = new Set(['ஒன்று', 'ஒண்ணு', 'ஒரு', 'அரை']);   // 1 and 1/2 are only numbers when followed by a unit
const TA_HALF = { 'ஒன்றரை': 1.5, 'இரண்டரை': 2.5, 'மூன்றரை': 3.5, 'நாலரை': 4.5, 'நான்கரை': 4.5, 'ஐந்தரை': 5.5 };

const TA = new Map();
for (const [w, v] of Object.entries(TA_UNITS)) TA.set(w, v);
for (const [w, v] of Object.entries(TA_BASE)) TA.set(w, v);
for (const [w, v] of Object.entries(TA_HALF)) TA.set(w, v);
TA.set('ஒரு', 1); TA.set('அரை', 0.5);
for (const [tens, jb] of Object.entries(TA_JOIN)) {
  const ji = jb.slice(0, -2) + 'தி';                  // நாற்பத்தி  (spoken "நாற்பத்தி ஐந்து")
  for (const [w, u] of Object.entries(TA_UNITS)) {
    const val = +tens + u;
    TA.set(jb + w, val); TA.set(ji + w, val);
    const sign = SIGN[w[0]];
    if (sign !== undefined) TA.set(jb.slice(0, -1) + sign + w.slice(1), val);   // நாற்பத்தைந்து
  }
}
// "எண்பதாயிரம்" = எண்பது + ஆயிரம்
for (const [w, v] of [...TA.entries()]) if (w.endsWith('ு') && v >= 2) TA.set(w.slice(0, -1) + 'ாயிரம்', v + ' ஆயிரம்');

/* ---------------- Hindi ---------------- */
const HI_LIST = ('शून्य एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह तेरह चौदह पंद्रह सोलह सत्रह अठारह उन्नीस बीस ' +
  'इक्कीस बाईस तेईस चौबीस पच्चीस छब्बीस सत्ताईस अट्ठाईस उनतीस तीस इकतीस बत्तीस तैंतीस चौंतीस पैंतीस छत्तीस सैंतीस अड़तीस उनतालीस चालीस ' +
  'इकतालीस बयालीस तैंतालीस चौवालीस पैंतालीस छियालीस सैंतालीस अड़तालीस उनचास पचास इक्यावन बावन तिरपन चौवन पचपन छप्पन सत्तावन अट्ठावन उनसठ साठ ' +
  'इकसठ बासठ तिरसठ चौंसठ पैंसठ छियासठ सड़सठ अड़सठ उनहत्तर सत्तर इकहत्तर बहत्तर तिहत्तर चौहत्तर पचहत्तर छिहत्तर सतहत्तर अठहत्तर उनासी अस्सी ' +
  'इक्यासी बयासी तिरासी चौरासी पचासी छियासी सत्तासी अट्ठासी नवासी नब्बे इक्यानवे बानवे तिरानवे चौरानवे पचानवे छियानवे सत्तानवे अट्ठानवे निन्यानवे').split(' ');
const HI = new Map(HI_LIST.map((w, i) => [w, i]));
for (const [w, v] of [['पांच', 5], ['पाच', 5], ['छः', 6], ['छे', 6], ['छै', 6], ['पन्द्रह', 15], ['डेढ़', 1.5], ['डेढ', 1.5], ['ढाई', 2.5]]) HI.set(w, v);
HI.delete('एक');                       // "एक" is also the article "a": only a number before a unit
const HI_AMBIG = new Set(['एक']);

/* ---------------- English ---------------- */
const EN_U = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'];
const EN_T = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'];

const UNIT_AFTER = /^(?:ஏக்கர்|சென்ட்|ஹெக்டேர்|லட்ச|லக்ஷ|ஆயிரம்|வயது|வருட|ரூபாய்|एकड़|लाख|हजार|हज़ार|साल|वर्ष|रुपये|हेक्टेयर|बीघा|acres?|lakh|lac|thousand|years?|rupees)/;

function convert(text) {
  let s = text;
  // English: "forty five", "forty-five", "two", "fifteen"
  s = s.replace(new RegExp('\\b(' + EN_T.slice(2).join('|') + ')(?:[\\s-]+(one|two|three|four|five|six|seven|eight|nine))?\\b', 'g'),
    (_, t, u) => EN_T.indexOf(t) * 10 + (u ? EN_U.indexOf(u) : 0));
  s = s.replace(new RegExp('\\b(' + EN_U.join('|') + ')\\b(\\s+\\S*)?', 'g'), (m, w, rest) => {
    if (w === 'one' && !UNIT_AFTER.test((rest || '').trim())) return m;
    return EN_U.indexOf(w) + (rest || '');
  });
  // Tamil + Hindi: token by token, so "एकड़" is never read as "एक" and "ஒரு விவசாயி" stays "a farmer"
  const parts = s.split(/(\s+)/);
  const clean = w => (w || '').replace(/[.,!?।;:]+$/g, '');
  for (let i = 0; i < parts.length; i += 2) {
    const w = clean(parts[i]); if (!w) continue;
    const next = clean(parts[i + 2]);
    const afterUnit = UNIT_AFTER.test(next);
    // two spoken words that form one number ("நாற்பத்தி ஐந்து")
    if (next && TA.has(w + next) && !TA_AMBIG.has(w)) { parts[i] = String(TA.get(w + next)); parts[i + 1] = ''; parts[i + 2] = ''; continue; }
    let v;
    if (TA.has(w)) { if (TA_AMBIG.has(w) && !afterUnit) continue; v = TA.get(w); }
    else if (HI.has(w)) v = HI.get(w);
    else if (HI_AMBIG.has(w)) { if (!afterUnit) continue; v = 1; }
    else continue;
    parts[i] = String(v) + parts[i].slice(w.length);
  }
  return parts.join('');
}

module.exports = { convert };
