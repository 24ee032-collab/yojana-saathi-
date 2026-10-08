# Builds data/schemes.json and data/vocab.json from the pristine base files + the new schemes below.
# Run: python3 tools/build_schemes.py   (idempotent; never edits the base files)
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))

schemes = load('tools/schemes.base.json')
vocab = load('tools/vocab.base.json')
cats = load('data/categories.json')

# ---------- helpers ----------
def rupees(n):
    if n >= 100000:
        s = '%g' % (n / 100000)
        return ('₹%s lakh' % s, '₹%s लाख' % s, '₹%s லட்சம்' % s)
    s = '{:,}'.format(n)
    return ('₹' + s,) * 3
def L(en, hi, ta): return [en, hi, ta]
def age_between(a, b): return {"field":"age","op":"between","value":[a,b],"label":L('Age %d to %d'%(a,b), 'उम्र %d से %d वर्ष'%(a,b), 'வயது %d முதல் %d வரை'%(a,b))}
def age_gte(a): return {"field":"age","op":"gte","value":a,"label":L('Age %d or above'%a, 'उम्र %d वर्ष या अधिक'%a, 'வயது %d அல்லது அதற்கு மேல்'%a)}
def age_lte(a): return {"field":"age","op":"lte","value":a,"label":L('Age %d or below'%a, 'उम्र %d वर्ष तक'%a, 'வயது %d வரை'%a)}
def inc_lte(n, per_month=None):
    r = rupees(n)
    return {"field":"income","op":"lte","value":n,"label":L('Family income up to %s'%r[0], 'परिवार की आय %s तक'%r[1], 'குடும்ப வருமானம் %s வரை'%r[2])}
def dis_gte(n): return {"field":"dis","op":"gte","value":n,"label":L('Disability of %d%% or more'%n, '%d%% या अधिक दिव्यांगता'%n, '%d%% அல்லது அதற்கு மேல் மாற்றுத்திறன்'%n)}
def eq(field, val, label): return {"field":field,"op":"eq","value":val,"label":label}
def inn(field, vals, label): return {"field":field,"op":"in","value":vals,"label":label}
FARMER = L('Farmer','किसान','விவசாயி')
LAND = L('Owns farmland','खेती की जमीन है','விவசாய நிலம் உள்ளது')
STUDENT = L('Student','विद्यार्थी','மாணவர்')
FEMALE = L('Woman','महिला','பெண்')
BPL = L('Poor family (BPL / ration card holder)','गरीब परिवार (बीपीएल / राशन कार्ड धारक)','ஏழைக் குடும்பம் (BPL / குடும்ப அட்டை உள்ளவர்)')
YES = lambda en, hi, ta: L(en, hi, ta)
ALL = [c['id'] for c in cats]

def add(id, tracks, name, benefit, about, rules, docs, steps, url, cash=None, once=False):
    s = {"id":id, "track":tracks[0], "name":list(name), "benefit":list(benefit), "docs":docs, "steps":steps, "url":url, "rules":rules, "about":list(about)}
    if len(tracks) > 1: s["tracks"] = tracks
    if cash: s["cash"] = cash
    if once: s["once"] = True
    schemes.append(s)

# cross-list some existing schemes for the new categories (their rules are not changed)
cross = {'mudra':['e','y','w','t','x','d','p'], 'pmegp':['e','y','w','x','d'], 'standup':['e','y','w'], 'seedfund':['e','s','y']}
for s in schemes:
    if s['id'] in cross:
        s['tracks'] = cross[s['id']]

# ---------- vocab additions ----------
vocab['tracks'] = {c['id']: c['name'] for c in cats}
vocab['docs'].update({
 'udidc': L('Disability certificate or UDID card','दिव्यांगता प्रमाण पत्र या यूडीआईडी कार्ड','மாற்றுத்திறன் சான்றிதழ் அல்லது UDID அட்டை'),
 'bplc': L('Ration card or BPL certificate','राशन कार्ड या बीपीएल प्रमाण पत्र','குடும்ப அட்டை அல்லது BPL சான்றிதழ்'),
 'deathc': L("Husband's death certificate",'पति का मृत्यु प्रमाण पत्र','கணவரின் இறப்புச் சான்றிதழ்'),
 'esm': L('Ex-serviceman ID card or discharge book','पूर्व सैनिक पहचान पत्र या डिस्चार्ज बुक','முன்னாள் படைவீரர் அடையாள அட்டை அல்லது விடுவிப்புப் புத்தகம்'),
 'ppo': L('Pension Payment Order (PPO)','पेंशन भुगतान आदेश (पीपीओ)','ஓய்வூதியக் கொடுப்பனவு ஆணை (PPO)'),
 'sportc': L('Sports achievement certificates','खेल उपलब्धि प्रमाण पत्र','விளையாட்டு சாதனைச் சான்றிதழ்கள்'),
 'tgc': L('Transgender certificate of identity','ट्रांसजेंडर पहचान प्रमाण पत्र','திருநங்கை அடையாளச் சான்றிதழ்'),
 'educ': L('Education certificates','शैक्षिक प्रमाण पत्र','கல்விச் சான்றிதழ்கள்'),
 'ageproof': L('Age proof (birth or school certificate)','आयु प्रमाण (जन्म या स्कूल प्रमाण पत्र)','வயதுச் சான்று (பிறப்பு அல்லது பள்ளிச் சான்றிதழ்)'),
 'wardproof': L("Child's admission letter and proof of relationship",'बच्चे का प्रवेश पत्र और संबंध का प्रमाण','பிள்ளையின் சேர்க்கைக் கடிதம் மற்றும் உறவுச் சான்று'),
 'address': L('Address proof','पते का प्रमाण','முகவரிச் சான்று'),
 'medical': L("Medical records or doctor's certificate",'चिकित्सा रिकॉर्ड या डॉक्टर का प्रमाण पत्र','மருத்துவ ஆவணங்கள் அல்லது மருத்துவர் சான்றிதழ்'),
})
vocab['steps'].update({
 'panch': L('Apply at your Gram Panchayat, block office or municipal office','ग्राम पंचायत, ब्लॉक कार्यालय या नगर निकाय में आवेदन करें','கிராம ஊராட்சி, வட்டார அலுவலகம் அல்லது நகராட்சி அலுவலகத்தில் விண்ணப்பியுங்கள்'),
 'dsw': L('Apply at the District Social Welfare office','जिला समाज कल्याण कार्यालय में आवेदन करें','மாவட்ட சமூக நல அலுவலகத்தில் விண்ணப்பியுங்கள்'),
 'udidf': L('First get your disability certificate or UDID card from a government hospital or the portal','पहले सरकारी अस्पताल या पोर्टल से दिव्यांगता प्रमाण पत्र / यूडीआईडी कार्ड बनवाएँ','முதலில் அரசு மருத்துவமனை அல்லது இணையதளம் மூலம் மாற்றுத்திறன் சான்றிதழ் / UDID அட்டை பெறுங்கள்'),
 'tgp': L('Apply on the National Portal for Transgender Persons','ट्रांसजेंडर व्यक्तियों के राष्ट्रीय पोर्टल पर आवेदन करें','திருநங்கையருக்கான தேசிய இணையதளத்தில் விண்ணப்பியுங்கள்'),
 'zsb': L('Contact your Zila Sainik Board (or Rajya Sainik Board)','अपने जिला सैनिक बोर्ड (या राज्य सैनिक बोर्ड) से संपर्क करें','உங்கள் மாவட்ட சைனிக் வாரியத்தை (அல்லது மாநில சைனிக் வாரியத்தை) அணுகுங்கள்'),
 'echs': L('Visit your nearest ECHS polyclinic with your documents to get the smart card','दस्तावेज़ लेकर नज़दीकी ईसीएचएस पॉलीक्लिनिक जाएँ और स्मार्ट कार्ड बनवाएँ','ஆவணங்களுடன் அருகிலுள்ள ECHS மருந்தகத்துக்குச் சென்று ஸ்மார்ட் கார்டு பெறுங்கள்'),
 'sai': L('Apply through your sports federation, state sports department or SAI centre','अपने खेल संघ, राज्य खेल विभाग या साई केंद्र के माध्यम से आवेदन करें','உங்கள் விளையாட்டுச் சங்கம், மாநில விளையாட்டுத் துறை அல்லது SAI மையம் வழியாக விண்ணப்பியுங்கள்'),
 'post': L('Visit a post office or bank branch with your documents and open the account','दस्तावेज़ लेकर डाकघर या बैंक शाखा जाएँ और खाता खोलें','ஆவணங்களுடன் அஞ்சலகம் அல்லது வங்கிக் கிளைக்குச் சென்று கணக்குத் தொடங்குங்கள்'),
 'nsp': L('Apply on the National Scholarship Portal during the open window each year','हर साल खुली अवधि में राष्ट्रीय छात्रवृत्ति पोर्टल पर आवेदन करें','ஆண்டுதோறும் திறக்கும் காலத்தில் தேசிய உதவித்தொகை இணையதளத்தில் விண்ணப்பியுங்கள்'),
 'camp': L('Attend the assessment camp or centre where your need is checked and the item is fitted','मूल्यांकन शिविर या केंद्र में जाएँ जहाँ ज़रूरत जाँचकर उपकरण लगाया जाएगा','மதிப்பீட்டு முகாம் அல்லது மையத்துக்குச் சென்று தேவையைச் சரிபார்த்து உபகரணம் பெறுங்கள்'),
 'shg': L('Join or form a women\'s self-help group through your village or block mission office','गाँव या ब्लॉक मिशन कार्यालय के माध्यम से महिला स्वयं सहायता समूह से जुड़ें या बनाएँ','கிராம அல்லது வட்டார இயக்க அலுவலகம் வழியாக மகளிர் சுய உதவிக் குழுவில் சேருங்கள் அல்லது தொடங்குங்கள்'),
 'emp': L('Register and create your profile; the portal or centre then shows nearby training or jobs','पंजीकरण कर प्रोफ़ाइल बनाएँ; पोर्टल या केंद्र पास के प्रशिक्षण या नौकरियाँ दिखाएगा','பதிவு செய்து சுயவிவரம் உருவாக்குங்கள்; இணையதளம் அல்லது மையம் அருகிலுள்ள பயிற்சி அல்லது வேலைகளைக் காட்டும்'),
 'hosp': L('Show your card at a listed hospital; treatment is cashless','सूचीबद्ध अस्पताल में कार्ड दिखाएँ; इलाज कैशलेस होगा','பட்டியலிடப்பட்ட மருத்துவமனையில் அட்டையைக் காட்டுங்கள்; சிகிச்சை பணமின்றி கிடைக்கும்'),
 'kvk': L('Contact your block agriculture office or Krishi Vigyan Kendra','अपने ब्लॉक कृषि कार्यालय या कृषि विज्ञान केंद्र से संपर्क करें','உங்கள் வட்டார வேளாண் அலுவலகம் அல்லது கிருஷி விஞ்ஞான் மையத்தை அணுகுங்கள்'),
 'collect': L('Collect the card or certificate from the office, or download it from the portal','कार्यालय से कार्ड / प्रमाण पत्र लें या पोर्टल से डाउनलोड करें','அலுவலகத்தில் அட்டை / சான்றிதழைப் பெறுங்கள் அல்லது இணையதளத்திலிருந்து பதிவிறக்குங்கள்'),
 'help': L('Call the helpline number given on the official website','आधिकारिक वेबसाइट पर दिए हेल्पलाइन नंबर पर कॉल करें','அதிகாரப்பூர்வ இணையதளத்தில் உள்ள உதவி எண்ணை அழையுங்கள்'),
})

# =====================  FARMERS  =====================
add('kmy', ['f'],
 L('PM Kisan Maandhan Yojana','पीएम किसान मानधन योजना','பிஎம் கிசான் மான்தன் திட்டம்'),
 L('₹3,000 a month pension from age 60','60 वर्ष की उम्र से ₹3,000 मासिक पेंशन','60 வயதிலிருந்து மாதம் ₹3,000 ஓய்வூதியம்'),
 L('A voluntary pension scheme for small and marginal farmers. You pay a small monthly amount (₹55 to ₹200, depending on your age when you join) and the Government of India puts in the same amount. From age 60 you receive a fixed pension.',
   'छोटे और सीमांत किसानों के लिए स्वैच्छिक पेंशन योजना। आप जुड़ने की उम्र के अनुसार हर महीने थोड़ी राशि (₹55 से ₹200) जमा करते हैं और भारत सरकार उतनी ही राशि जमा करती है। 60 वर्ष की उम्र से तय पेंशन मिलती है।',
   'சிறு, குறு விவசாயிகளுக்கான தன்னார்வ ஓய்வூதியத் திட்டம். சேரும் வயதைப் பொறுத்து மாதம் சிறிய தொகையை (₹55 முதல் ₹200 வரை) செலுத்துவீர்கள்; இந்திய அரசும் அதே தொகையைச் செலுத்தும். 60 வயது முதல் நிலையான ஓய்வூதியம் கிடைக்கும்.'),
 [eq('occ','farmer',FARMER), age_between(18,40),
  {"field":"land","op":"between","value":[0.01,4.94],"label":L('Small or marginal farmer (up to 2 hectares, about 5 acres)','छोटा या सीमांत किसान (2 हेक्टेयर, लगभग 5 एकड़ तक)','சிறு அல்லது குறு விவசாயி (2 ஹெக்டேர், சுமார் 5 ஏக்கர் வரை)')}],
 ['aadhaar','bank','land'], ['csc','kyc','trk'], 'https://maandhan.in')

add('soilhealth', ['f'],
 L('Soil Health Card Scheme','मृदा स्वास्थ्य कार्ड योजना','மண் வள அட்டைத் திட்டம்'),
 L('Free soil test and crop-wise fertiliser advice','निःशुल्क मिट्टी जाँच और फसल के अनुसार खाद की सलाह','இலவச மண் பரிசோதனை மற்றும் பயிருக்கேற்ற உர ஆலோசனை'),
 L('Every farmer can get a free soil health card. Your soil sample is tested and the card shows which nutrients are low and how much fertiliser each crop needs, so you spend less and get a better yield.',
   'हर किसान को निःशुल्क मृदा स्वास्थ्य कार्ड मिल सकता है। आपकी मिट्टी की जाँच होती है और कार्ड बताता है कि कौन से पोषक तत्व कम हैं और हर फसल को कितनी खाद चाहिए, जिससे खर्च घटता है और पैदावार बढ़ती है।',
   'ஒவ்வொரு விவசாயியும் இலவச மண் வள அட்டை பெறலாம். உங்கள் மண் மாதிரி பரிசோதிக்கப்பட்டு, எந்த ஊட்டச்சத்து குறைவு, ஒவ்வொரு பயிருக்கும் எவ்வளவு உரம் தேவை என்பதை அட்டை காட்டும்; செலவு குறைந்து மகசூல் கூடும்.'),
 [eq('occ','farmer',FARMER)], ['aadhaar','land'], ['kvk','collect'], 'https://soilhealth.dac.gov.in')

add('pmksy', ['f'],
 L('PM Krishi Sinchayee Yojana (Per Drop More Crop)','पीएम कृषि सिंचाई योजना (पर ड्रॉप मोर क्रॉप)','பிஎம் கிருஷி சிஞ்சாயி திட்டம் (ஒவ்வொரு துளிக்கும் அதிக பயிர்)'),
 L('Subsidy on drip and sprinkler irrigation (about 55% for small farmers)','ड्रिप और स्प्रिंकलर सिंचाई पर सब्सिडी (छोटे किसानों को लगभग 55%)','சொட்டு மற்றும் தெளிப்பு நீர்ப்பாசனத்துக்கு மானியம் (சிறு விவசாயிகளுக்கு சுமார் 55%)'),
 L('Helps farmers save water and raise yield by installing drip or sprinkler systems. The government pays a large part of the cost; the exact rate depends on your state and farm size.',
   'ड्रिप या स्प्रिंकलर सिस्टम लगाकर पानी बचाने और पैदावार बढ़ाने में किसानों की मदद करती है। सरकार लागत का बड़ा हिस्सा देती है; सही दर राज्य और खेत के आकार पर निर्भर करती है।',
   'சொட்டு அல்லது தெளிப்பு நீர்ப்பாசன அமைப்பை நிறுவி தண்ணீரைச் சேமிக்கவும் மகசூலை உயர்த்தவும் உதவுகிறது. செலவின் பெரும் பகுதியை அரசு ஏற்கும்; சரியான விகிதம் மாநிலம் மற்றும் நிலத்தின் அளவைப் பொறுத்தது.'),
 [eq('occ','farmer',FARMER), {"field":"land","op":"gt","value":0,"label":LAND}],
 ['aadhaar','bank','land','photo'], ['reg','form','ver','trk'], 'https://pmksy.gov.in')

add('aif', ['f'],
 L('Agriculture Infrastructure Fund','कृषि अवसंरचना कोष','வேளாண் உள்கட்டமைப்பு நிதி'),
 L('Loans up to ₹2 crore with 3% interest relief','₹2 करोड़ तक के ऋण पर 3% ब्याज छूट','₹2 கோடி வரை கடனுக்கு 3% வட்டி மானியம்'),
 L('For building farm-gate facilities such as cold stores, warehouses, grading and packing units and small processing units. Bank loans get 3% interest relief for up to 7 years and a credit guarantee.',
   'कोल्ड स्टोर, गोदाम, ग्रेडिंग-पैकिंग और छोटी प्रसंस्करण इकाइयों जैसी खेत के पास की सुविधाएँ बनाने के लिए। बैंक ऋण पर 7 साल तक 3% ब्याज छूट और ऋण गारंटी मिलती है।',
   'குளிர்பதனக் கிடங்கு, சேமிப்புக் கிடங்கு, தரம் பிரித்தல்-பொட்டலமிடல், சிறு பதப்படுத்தும் அலகு போன்ற வயல் அருகிலான வசதிகளை அமைக்க. வங்கிக் கடனுக்கு 7 ஆண்டுகள் வரை 3% வட்டி மானியமும் கடன் உத்தரவாதமும் கிடைக்கும்.'),
 [eq('occ','farmer',FARMER)], ['aadhaar','pan','bank','land','plan'], ['plan','reg','ver','loan'], 'https://agriinfra.dac.gov.in')

add('enam', ['f'],
 L('e-NAM (National Agriculture Market)','ई-नाम (राष्ट्रीय कृषि बाज़ार)','இ-நாம் (தேசிய வேளாண் சந்தை)'),
 L('Sell your crop online to buyers across many mandis','अपनी फसल कई मंडियों के खरीदारों को ऑनलाइन बेचें','பல மண்டிகளின் வாங்குபவர்களுக்கு உங்கள் பயிரை இணையத்தில் விற்கலாம்'),
 L('An online trading platform that links mandis across India. You can register as a farmer, see prices in many markets and sell to the best bidder, with payment straight into your bank account.',
   'देश भर की मंडियों को जोड़ने वाला ऑनलाइन व्यापार मंच। आप किसान के रूप में पंजीकरण कर कई बाज़ारों के भाव देख सकते हैं और सबसे अच्छी बोली पर बेच सकते हैं; भुगतान सीधे बैंक खाते में आता है।',
   'இந்தியா முழுவதும் உள்ள மண்டிகளை இணைக்கும் இணைய வர்த்தகத் தளம். விவசாயியாகப் பதிவு செய்து பல சந்தைகளின் விலையைப் பார்த்து, சிறந்த ஏலத்துக்கு விற்கலாம்; பணம் நேரடியாக வங்கிக் கணக்கில் வரும்.'),
 [eq('occ','farmer',FARMER)], ['aadhaar','bank','land'], ['reg','form','trk'], 'https://enam.gov.in')

add('pkvy', ['f'],
 L('Paramparagat Krishi Vikas Yojana (organic farming)','परम्परागत कृषि विकास योजना (जैविक खेती)','பாரம்பரிய கிருஷி விகாஸ் திட்டம் (இயற்கை விவசாயம்)'),
 L('Support to move to certified organic farming in groups','समूह में प्रमाणित जैविक खेती अपनाने के लिए सहायता','குழுவாகச் சான்றளிக்கப்பட்ட இயற்கை விவசாயத்துக்கு மாற உதவி'),
 L('Farmers join in clusters to take up organic farming. The scheme helps with training, organic inputs, certification and marketing so that you can sell at a better price.',
   'किसान समूह बनाकर जैविक खेती अपनाते हैं। योजना प्रशिक्षण, जैविक सामग्री, प्रमाणन और विपणन में मदद करती है ताकि बेहतर दाम मिले।',
   'விவசாயிகள் குழுக்களாக இணைந்து இயற்கை விவசாயம் மேற்கொள்கிறார்கள். பயிற்சி, இயற்கை இடுபொருட்கள், சான்றிதழ், சந்தைப்படுத்தல் ஆகியவற்றில் உதவி கிடைக்கும்; சிறந்த விலை பெறலாம்.'),
 [eq('occ','farmer',FARMER), {"field":"land","op":"gt","value":0,"label":LAND}],
 ['aadhaar','bank','land'], ['kvk','form','ver','trk'], 'https://pgsindia-ncof.gov.in')

# =====================  STUDENTS  =====================
SCHOOL = L('Studying in Class 9 to 12','कक्षा 9 से 12 में पढ़ रहे हैं','9 முதல் 12 ஆம் வகுப்பில் படிக்கிறீர்கள்')
add('nmmss', ['s'],
 L('National Means-cum-Merit Scholarship','राष्ट्रीय साधन-सह-मेधा छात्रवृत्ति','தேசிய வருமான-தகுதி உதவித்தொகை'),
 L('₹12,000 a year for Class 9 to 12','कक्षा 9 से 12 के लिए ₹12,000 प्रति वर्ष','9 முதல் 12 ஆம் வகுப்பு வரை ஆண்டுக்கு ₹12,000'),
 L('For talented students of low-income families who passed Class 8, so that they do not drop out of school. Selection is through a state-level test, and the scholarship continues every year if you keep passing.',
   'कम आय वाले परिवारों के प्रतिभाशाली विद्यार्थियों के लिए, जिन्होंने कक्षा 8 पास की है, ताकि वे पढ़ाई न छोड़ें। चयन राज्य स्तरीय परीक्षा से होता है और पास होते रहने पर हर साल छात्रवृत्ति मिलती है।',
   'குறைந்த வருமானக் குடும்பங்களில் 8 ஆம் வகுப்பு தேர்ச்சி பெற்ற திறமையான மாணவர்கள் பள்ளியை விட்டு நிற்காமல் இருக்க உதவுகிறது. மாநில அளவிலான தேர்வு மூலம் தேர்வு; தொடர்ந்து தேர்ச்சி பெற்றால் ஆண்டுதோறும் தொகை கிடைக்கும்.'),
 [eq('occ','student',STUDENT), eq('stage','school',SCHOOL), inc_lte(350000)],
 ['aadhaar','income','school','bank'], ['reg','form','inst','ver','trk','ren'], 'https://scholarships.gov.in')

add('yasasvi', ['s'],
 L('PM YASASVI Scholarship (OBC, EBC, DNT)','पीएम यशस्वी छात्रवृत्ति (ओबीसी, ईबीसी, डीएनटी)','பிஎம் யசஸ்வி உதவித்தொகை (OBC, EBC, DNT)'),
 L('Yearly scholarship for school students from OBC, EBC and DNT groups','ओबीसी, ईबीसी और डीएनटी वर्ग के स्कूली विद्यार्थियों को वार्षिक छात्रवृत्ति','OBC, EBC, DNT பிரிவு பள்ளி மாணவர்களுக்கு ஆண்டு உதவித்தொகை'),
 L('Helps students of Other Backward Classes, Economically Backward Classes and Denotified Tribes to continue school. Selection is through a national entrance test or on marks, depending on the class.',
   'अन्य पिछड़ा वर्ग, आर्थिक रूप से पिछड़े वर्ग और विमुक्त जनजातियों के विद्यार्थियों को स्कूली पढ़ाई जारी रखने में मदद। कक्षा के अनुसार चयन राष्ट्रीय प्रवेश परीक्षा या अंकों से होता है।',
   'பிற்படுத்தப்பட்டோர், பொருளாதார ரீதியில் பின்தங்கியோர், சீர்மரபினர் மாணவர்கள் பள்ளிப் படிப்பைத் தொடர உதவுகிறது. வகுப்பைப் பொறுத்து தேசிய நுழைவுத் தேர்வு அல்லது மதிப்பெண் அடிப்படையில் தேர்வு.'),
 [eq('occ','student',STUDENT), eq('cat','OBC',L('OBC / EBC / DNT category','ओबीसी / ईबीसी / डीएनटी वर्ग','OBC / EBC / DNT பிரிவு')), eq('stage','school',SCHOOL), inc_lte(250000)],
 ['aadhaar','caste','income','school','bank'], ['reg','form','inst','ver','trk','ren'], 'https://scholarships.gov.in')

add('prematric', ['s'],
 L('Pre-Matric Scholarship (SC / ST, Class 9 and 10)','प्री-मैट्रिक छात्रवृत्ति (एससी / एसटी, कक्षा 9 और 10)','பத்தாம் வகுப்புக்கு முந்தைய உதவித்தொகை (SC / ST, 9 மற்றும் 10)'),
 L('Monthly allowance and yearly grant for Class 9 and 10','कक्षा 9 और 10 के लिए मासिक भत्ता और वार्षिक अनुदान','9 மற்றும் 10 ஆம் வகுப்புக்கு மாதப் படியும் ஆண்டு மானியமும்'),
 L('Helps SC and ST children stay in school up to Class 10 with a monthly allowance and a yearly grant for books and other needs. Apply every year through your school.',
   'एससी और एसटी बच्चों को कक्षा 10 तक स्कूल में बनाए रखने के लिए मासिक भत्ता और किताबों आदि के लिए वार्षिक अनुदान। हर साल अपने स्कूल के माध्यम से आवेदन करें।',
   'SC, ST குழந்தைகள் 10 ஆம் வகுப்பு வரை பள்ளியில் தொடர மாதப் படியும் புத்தகம் போன்றவற்றுக்கு ஆண்டு மானியமும் வழங்குகிறது. ஒவ்வொரு ஆண்டும் பள்ளி மூலம் விண்ணப்பியுங்கள்.'),
 [eq('occ','student',STUDENT), inn('cat',['SC','ST'],L('SC or ST category','एससी या एसटी वर्ग','SC அல்லது ST பிரிவு')), eq('stage','school',SCHOOL), inc_lte(250000)],
 ['aadhaar','caste','income','school','bank'], ['reg','form','inst','ver','trk','ren'], 'https://scholarships.gov.in')

add('nos', ['s'],
 L('National Overseas Scholarship (SC)','राष्ट्रीय विदेश छात्रवृत्ति (एससी)','தேசிய வெளிநாட்டு உதவித்தொகை (SC)'),
 L('Help with fees, living costs and air fare for a master\'s or PhD abroad','विदेश में मास्टर्स या पीएचडी के लिए फीस, रहने का खर्च और हवाई किराये में मदद','வெளிநாட்டில் முதுகலை அல்லது முனைவர் படிப்புக்குக் கட்டணம், வாழ்க்கைச் செலவு, விமானக் கட்டண உதவி'),
 L('Helps students from Scheduled Caste families study a master\'s degree or PhD at a good university abroad. It covers tuition, living allowance and air fare for selected students.',
   'अनुसूचित जाति के परिवारों के विद्यार्थियों को विदेश के अच्छे विश्वविद्यालय में मास्टर्स या पीएचडी करने में मदद। चुने गए विद्यार्थियों की ट्यूशन फीस, रहने का भत्ता और हवाई किराया शामिल है।',
   'பட்டியல் இனக் குடும்ப மாணவர்கள் வெளிநாட்டு நல்ல பல்கலைக்கழகத்தில் முதுகலை அல்லது முனைவர் படிப்பு படிக்க உதவுகிறது. தேர்வான மாணவர்களுக்குக் கல்விக் கட்டணம், வாழ்க்கைப் படி, விமானக் கட்டணம் அடங்கும்.'),
 [eq('occ','student',STUDENT), eq('cat','SC',L('SC category','एससी वर्ग','SC பிரிவு')), eq('stage','pg',L('Postgraduate or research study','स्नातकोत्तर या शोध अध्ययन','முதுகலை அல்லது ஆராய்ச்சிப் படிப்பு')), inc_lte(800000)],
 ['aadhaar','caste','income','school','bank'], ['reg','form','iv','ver','trk'], 'https://nosmsje.gov.in')

add('topclass', ['s'],
 L('Top Class Education for SC Students','एससी विद्यार्थियों के लिए शीर्ष श्रेणी शिक्षा','SC மாணவர்களுக்கான உயர்தரக் கல்வி'),
 L('Full tuition, living allowance and books at top institutes','शीर्ष संस्थानों में पूरी ट्यूशन फीस, रहने का भत्ता और किताबें','முன்னணி கல்வி நிறுவனங்களில் முழுக் கட்டணம், வாழ்க்கைப் படி, புத்தகங்கள்'),
 L('For SC students admitted to a list of top colleges and universities in India. The government pays the full fee and gives an allowance for books and living costs.',
   'भारत के शीर्ष कॉलेजों और विश्वविद्यालयों की सूची में प्रवेश पाने वाले एससी विद्यार्थियों के लिए। सरकार पूरी फीस देती है और किताबों व रहने के खर्च के लिए भत्ता देती है।',
   'இந்தியாவின் முன்னணிக் கல்லூரிகள், பல்கலைக்கழகங்களின் பட்டியலில் சேரும் SC மாணவர்களுக்கு. அரசு முழுக் கட்டணத்தைச் செலுத்தி, புத்தகம் மற்றும் வாழ்க்கைச் செலவுக்குப் படி வழங்கும்.'),
 [eq('occ','student',STUDENT), eq('cat','SC',L('SC category','एससी वर्ग','SC பிரிவு')), inn('stage',['ug','pg'],L('Studying at college or university','कॉलेज या विश्वविद्यालय में पढ़ रहे हैं','கல்லூரி அல்லது பல்கலைக்கழகத்தில் படிக்கிறீர்கள்')), inc_lte(800000)],
 ['aadhaar','caste','income','fee','bank'], ['reg','form','inst','ver','trk','ren'], 'https://scholarships.gov.in')

# =====================  ENTREPRENEURS  =====================
RUNS = L('Runs a small business, trade or craft','छोटा व्यवसाय, व्यापार या शिल्प चलाते हैं','சிறு தொழில், வணிகம் அல்லது கைவினை நடத்துகிறீர்கள்')
PLANS = L('Runs or plans a micro or small business','सूक्ष्म या लघु व्यवसाय चलाते या शुरू करना चाहते हैं','நுண் அல்லது சிறு தொழில் நடத்துகிறீர்கள் அல்லது தொடங்கத் திட்டமிடுகிறீர்கள்')
add('udyam', ['e'],
 L('Udyam Registration (MSME)','उद्यम पंजीकरण (एमएसएमई)','உத்யம் பதிவு (MSME)'),
 L('Free online MSME certificate that opens doors to loans and subsidies','निःशुल्क ऑनलाइन एमएसएमई प्रमाणपत्र, जिससे ऋण और सब्सिडी के रास्ते खुलते हैं','கடன்கள், மானியங்களுக்கு வழிவகுக்கும் இலவச இணைய MSME சான்றிதழ்'),
 L('A free, paperless registration for micro, small and medium enterprises using your Aadhaar and PAN. The Udyam certificate helps you get priority-sector loans, subsidies, lower interest and government tenders.',
   'आधार और पैन से सूक्ष्म, लघु और मध्यम उद्यमों के लिए निःशुल्क, कागज़-रहित पंजीकरण। उद्यम प्रमाणपत्र से प्राथमिकता क्षेत्र ऋण, सब्सिडी, कम ब्याज और सरकारी निविदाओं में मदद मिलती है।',
   'ஆதார் மற்றும் PAN மூலம் நுண், சிறு, நடுத்தர நிறுவனங்களுக்கான இலவச, காகிதமற்ற பதிவு. உத்யம் சான்றிதழ் முன்னுரிமைத் துறைக் கடன், மானியம், குறைந்த வட்டி, அரசு ஒப்பந்தங்களுக்கு உதவும்.'),
 [inn('occ',['business','vendor','artisan'],RUNS)], ['aadhaar','pan','bank','trade'], ['reg','form','collect'], 'https://udyamregistration.gov.in')

add('cgtmse', ['e'],
 L('CGTMSE (loan without collateral)','सीजीटीएमएसई (बिना गारंटी ऋण)','CGTMSE (பிணையமில்லாக் கடன்)'),
 L('Bank loans for micro and small units without collateral or third-party guarantee','सूक्ष्म और लघु इकाइयों को बिना गिरवी या तीसरे पक्ष की गारंटी के बैंक ऋण','பிணையம் அல்லது மூன்றாம் நபர் உத்தரவாதம் இல்லாமல் நுண், சிறு தொழில்களுக்கு வங்கிக் கடன்'),
 L('The Credit Guarantee Fund Trust guarantees loans given by banks to micro and small businesses, so the bank can lend without asking for property as security. You apply to your bank, not to the Trust.',
   'क्रेडिट गारंटी फंड ट्रस्ट सूक्ष्म और लघु व्यवसायों को बैंकों के दिए ऋण की गारंटी लेता है, इसलिए बैंक संपत्ति गिरवी माँगे बिना ऋण दे सकता है। आप ट्रस्ट को नहीं, अपने बैंक को आवेदन करते हैं।',
   'கடன் உத்தரவாத நிதி அறக்கட்டளை நுண், சிறு தொழில்களுக்கு வங்கிகள் தரும் கடனுக்கு உத்தரவாதம் அளிக்கிறது; அதனால் சொத்தை அடமானம் கேட்காமல் வங்கி கடன் தரலாம். அறக்கட்டளைக்கு அல்ல, உங்கள் வங்கிக்கு விண்ணப்பியுங்கள்.'),
 [inn('occ',['business','vendor','artisan','unemp'],PLANS)], ['aadhaar','pan','bank','trade','plan'], ['plan','bankv','ver','loan'], 'https://www.cgtmse.in')

add('pmfme', ['e'],
 L('PM Formalisation of Micro Food Processing Enterprises','पीएम सूक्ष्म खाद्य प्रसंस्करण उद्यम औपचारिकीकरण योजना','பிஎம் நுண் உணவுப் பதப்படுத்தும் நிறுவன முறைப்படுத்தல் திட்டம்'),
 L('35% subsidy on project cost, up to ₹10 lakh','परियोजना लागत पर 35% सब्सिडी, ₹10 लाख तक','திட்டச் செலவில் 35% மானியம், ₹10 லட்சம் வரை'),
 L('For small food-processing units such as pickles, millets, bakery, dairy or spices. You get a subsidy linked to a bank loan, plus training, branding and marketing support.',
   'अचार, मोटे अनाज, बेकरी, डेयरी या मसालों जैसी छोटी खाद्य प्रसंस्करण इकाइयों के लिए। बैंक ऋण से जुड़ी सब्सिडी के साथ प्रशिक्षण, ब्रांडिंग और विपणन सहायता मिलती है।',
   'ஊறுகாய், சிறுதானியம், பேக்கரி, பால், மசாலா போன்ற சிறு உணவுப் பதப்படுத்தும் அலகுகளுக்கு. வங்கிக் கடனுடன் இணைந்த மானியம், பயிற்சி, பிராண்டிங், சந்தைப்படுத்தல் உதவி கிடைக்கும்.'),
 [inn('occ',['business','artisan','unemp'],L('Runs or plans a small food-processing unit','छोटी खाद्य प्रसंस्करण इकाई चलाते या शुरू करना चाहते हैं','சிறு உணவுப் பதப்படுத்தும் அலகு நடத்துகிறீர்கள் அல்லது தொடங்கத் திட்டமிடுகிறீர்கள்'))],
 ['aadhaar','pan','bank','plan','trade'], ['plan','reg','form','loan'], 'https://pmfme.mofpi.gov.in')

# =====================  WIDOWS  =====================
add('ignwps', ['w'],
 L('Indira Gandhi National Widow Pension Scheme','इंदिरा गांधी राष्ट्रीय विधवा पेंशन योजना','இந்திரா காந்தி தேசிய விதவை ஓய்வூதியத் திட்டம்'),
 L('Monthly pension (Centre ₹300; ₹500 at age 80+). Many states add more','मासिक पेंशन (केंद्र ₹300; 80+ पर ₹500)। कई राज्य और जोड़ते हैं','மாத ஓய்வூதியம் (மத்திய அரசு ₹300; 80+ வயதில் ₹500). பல மாநிலங்கள் கூடுதலாகத் தருகின்றன'),
 L('A monthly pension for widows from poor (BPL) families. The Centre pays a fixed part and most states add to it, so the total depends on your state. The money goes to your bank or post office account.',
   'गरीब (बीपीएल) परिवारों की विधवाओं के लिए मासिक पेंशन। केंद्र एक तय हिस्सा देता है और अधिकतर राज्य उसमें जोड़ते हैं, इसलिए कुल राशि राज्य पर निर्भर है। पैसा आपके बैंक या डाकघर खाते में आता है।',
   'ஏழை (BPL) குடும்பங்களின் விதவைகளுக்கான மாத ஓய்வூதியம். மத்திய அரசு ஒரு நிலையான பகுதியைத் தரும்; பெரும்பாலான மாநிலங்கள் கூடுதலாகச் சேர்க்கும், எனவே மொத்தத் தொகை மாநிலத்தைப் பொறுத்தது. பணம் உங்கள் வங்கி அல்லது அஞ்சலகக் கணக்கில் வரும்.'),
 [age_gte(40), eq('bpl','yes',BPL)], ['aadhaar','bank','bplc','deathc','ageproof','photo'], ['panch','form','ver','trk'], 'https://nsap.nic.in', cash=3600)

add('nfbs', ['w'],
 L('National Family Benefit Scheme','राष्ट्रीय पारिवारिक लाभ योजना','தேசிய குடும்ப நலத் திட்டம்'),
 L('One-time ₹20,000 when the main earner of a poor family dies','गरीब परिवार के मुख्य कमाने वाले की मृत्यु पर एकमुश्त ₹20,000','ஏழைக் குடும்பத்தின் முக்கிய வருமானம் ஈட்டுபவர் இறந்தால் ஒரே முறை ₹20,000'),
 L('If the main earning member (aged 18 to 59) of a below-poverty-line family dies, the family gets a one-time payment. Apply within the time limit your state allows after the death.',
   'बीपीएल परिवार के मुख्य कमाने वाले सदस्य (18 से 59 वर्ष) की मृत्यु होने पर परिवार को एकमुश्त राशि मिलती है। मृत्यु के बाद अपने राज्य की समय सीमा के भीतर आवेदन करें।',
   'வறுமைக் கோட்டிற்குக் கீழுள்ள குடும்பத்தின் முக்கிய வருமானம் ஈட்டும் உறுப்பினர் (18 முதல் 59 வயது) இறந்தால் குடும்பத்துக்கு ஒரே முறை தொகை கிடைக்கும். இறப்புக்குப் பிறகு உங்கள் மாநிலம் அனுமதிக்கும் காலத்துக்குள் விண்ணப்பியுங்கள்.'),
 [eq('bpl','yes',L('Poor (BPL) family whose main earner (aged 18 to 59) has died','गरीब (बीपीएल) परिवार जिसके मुख्य कमाने वाले (18 से 59 वर्ष) की मृत्यु हो गई है','ஏழை (BPL) குடும்பம்; முக்கிய வருமானம் ஈட்டுபவர் (18 முதல் 59 வயது) இறந்துவிட்டார்'))],
 ['aadhaar','bank','bplc','deathc'], ['panch','form','ver','trk'], 'https://nsap.nic.in')

add('ujjwala', ['w','f','e','y','d','o','s'],
 L('PM Ujjwala Yojana','पीएम उज्ज्वला योजना','பிஎம் உஜ்வாலா திட்டம்'),
 L('Free LPG connection for women from poor households','गरीब परिवारों की महिलाओं को निःशुल्क एलपीजी कनेक्शन','ஏழைக் குடும்பப் பெண்களுக்கு இலவச எல்பிஜி இணைப்பு'),
 L('Gives an adult woman of a poor household a free LPG gas connection so the family can stop cooking on wood or coal. A subsidy on refills is also available for eligible households.',
   'गरीब परिवार की वयस्क महिला को निःशुल्क एलपीजी गैस कनेक्शन मिलता है ताकि परिवार लकड़ी या कोयले पर खाना पकाना बंद कर सके। पात्र परिवारों को रिफिल पर सब्सिडी भी मिलती है।',
   'ஏழைக் குடும்பத்தின் வயது வந்த பெண்ணுக்கு இலவச எல்பிஜி எரிவாயு இணைப்பு வழங்கப்படும்; விறகு அல்லது நிலக்கரியில் சமைப்பதை நிறுத்தலாம். தகுதியான குடும்பங்களுக்கு மறுநிரப்பலுக்கு மானியமும் உண்டு.'),
 [eq('gender','female',FEMALE), age_gte(18), eq('bpl','yes',BPL)], ['aadhaar','bank','bplc','photo'], ['form','csc','ver'], 'https://www.pmuy.gov.in')

add('swadhar', ['w'],
 L('Swadhar Greh (shelter for women in distress)','स्वाधार गृह (संकटग्रस्त महिलाओं के लिए आश्रय)','ஸ்வாதார் கிரஹ் (துன்பத்தில் உள்ள பெண்களுக்கான தங்குமிடம்)'),
 L('Shelter, food, clothing, counselling and training','आश्रय, भोजन, कपड़े, परामर्श और प्रशिक्षण','தங்குமிடம், உணவு, உடை, ஆலோசனை, பயிற்சி'),
 L('Homes for women left without family support, including widows and women facing hardship. Run by NGOs and state governments with central funds, they give shelter, counselling, legal help and skill training.',
   'परिवार का सहारा खो चुकी महिलाओं, जिनमें विधवाएँ भी हैं, के लिए गृह। एनजीओ और राज्य सरकारें केंद्र के धन से इन्हें चलाती हैं; आश्रय, परामर्श, कानूनी मदद और कौशल प्रशिक्षण मिलता है।',
   'குடும்ப ஆதரவு இல்லாத பெண்களுக்கான இல்லங்கள்; விதவைகளும் இதில் அடங்குவர். மத்திய நிதியுடன் தொண்டு நிறுவனங்களும் மாநில அரசுகளும் நடத்துகின்றன; தங்குமிடம், ஆலோசனை, சட்ட உதவி, திறன் பயிற்சி கிடைக்கும்.'),
 [age_gte(18)], ['aadhaar','photo','address'], ['dsw','iv'], 'https://wcd.gov.in')

add('nrlm', ['w','f','e','y','d','o'],
 L('DAY-NRLM Women Self-Help Groups (Lakhpati Didi)','डे-एनआरएलएम महिला स्वयं सहायता समूह (लखपति दीदी)','DAY-NRLM மகளிர் சுய உதவிக் குழுக்கள் (லக்பதி தீதி)'),
 L('Group loans at low interest, training and market support for women','महिलाओं के लिए कम ब्याज पर समूह ऋण, प्रशिक्षण और बाज़ार सहायता','பெண்களுக்கு குறைந்த வட்டிக் குழுக் கடன், பயிற்சி, சந்தை உதவி'),
 L('Rural women join a self-help group, save together and get bank loans at low interest to start or grow a small business. The mission also trains members and helps them sell their products.',
   'ग्रामीण महिलाएँ स्वयं सहायता समूह से जुड़कर साथ बचत करती हैं और छोटा व्यवसाय शुरू या बढ़ाने के लिए कम ब्याज पर बैंक ऋण पाती हैं। मिशन सदस्यों को प्रशिक्षण और उत्पाद बेचने में मदद भी देता है।',
   'கிராமப்புறப் பெண்கள் சுய உதவிக் குழுவில் சேர்ந்து சேர்ந்து சேமித்து, சிறு தொழில் தொடங்க அல்லது விரிவாக்க குறைந்த வட்டியில் வங்கிக் கடன் பெறுகிறார்கள். உறுப்பினர்களுக்குப் பயிற்சியும் பொருட்களை விற்க உதவியும் கிடைக்கும்.'),
 [eq('gender','female',FEMALE), age_gte(18)], ['aadhaar','bank','bplc','photo'], ['shg','bankv','loan'], 'https://aajeevika.gov.in')

# =====================  UNEMPLOYED YOUTH  =====================
add('pmkvy', ['y','w','t','d','x'],
 L('PM Kaushal Vikas Yojana (Skill India)','पीएम कौशल विकास योजना (स्किल इंडिया)','பிஎம் கௌசல் விகாஸ் திட்டம் (ஸ்கில் இந்தியா)'),
 L('Free skill training with certificate and job help','प्रमाण पत्र और रोज़गार सहायता के साथ निःशुल्क कौशल प्रशिक्षण','சான்றிதழ் மற்றும் வேலை உதவியுடன் இலவசத் திறன் பயிற்சி'),
 L('Short-term training in hundreds of job roles. Training is free, an assessment gives you a government-recognised certificate, and training centres help with placement. Open to school or college dropouts and unemployed youth.',
   'सैकड़ों रोज़गार भूमिकाओं में अल्पकालिक प्रशिक्षण। प्रशिक्षण निःशुल्क है, मूल्यांकन के बाद सरकार से मान्य प्रमाण पत्र मिलता है और प्रशिक्षण केंद्र नौकरी दिलाने में मदद करते हैं। स्कूल या कॉलेज छोड़ने वालों और बेरोज़गार युवाओं के लिए।',
   'நூற்றுக்கணக்கான வேலைப் பணிகளில் குறுகியகாலப் பயிற்சி. பயிற்சி இலவசம்; மதிப்பீட்டுக்குப் பிறகு அரசு அங்கீகரித்த சான்றிதழ் கிடைக்கும்; பயிற்சி மையங்கள் வேலை பெற உதவும். பள்ளி அல்லது கல்லூரியை இடைநிறுத்தியோர், வேலையில்லா இளைஞர்களுக்கு.'),
 [age_between(15,45)], ['aadhaar','bank','educ','photo'], ['emp','trn'], 'https://www.skillindiadigital.gov.in')

add('pminternship', ['y'],
 L('PM Internship Scheme','पीएम इंटर्नशिप योजना','பிஎம் இன்டர்ன்ஷிப் திட்டம்'),
 L('₹5,000 a month for 12 months plus ₹6,000 one-time grant','12 महीने तक ₹5,000 प्रति माह और ₹6,000 एकमुश्त सहायता','12 மாதங்களுக்கு மாதம் ₹5,000 மற்றும் ஒரே முறை ₹6,000 உதவி'),
 L('Real work experience for 12 months in top companies. You get a monthly stipend (₹4,500 from the government and ₹500 from the company) and a one-time grant. For young people who are not in full-time study or a full-time job.',
   'शीर्ष कंपनियों में 12 महीने का वास्तविक कार्य अनुभव। मासिक वजीफा (सरकार से ₹4,500 और कंपनी से ₹500) और एकमुश्त सहायता मिलती है। उन युवाओं के लिए जो पूर्णकालिक पढ़ाई या नौकरी में नहीं हैं।',
   'முன்னணி நிறுவனங்களில் 12 மாத உண்மையான வேலை அனுபவம். மாத உதவித்தொகை (அரசிடமிருந்து ₹4,500, நிறுவனத்திடமிருந்து ₹500) மற்றும் ஒரே முறை உதவி கிடைக்கும். முழுநேரப் படிப்பு அல்லது முழுநேர வேலையில் இல்லாத இளைஞர்களுக்கு.'),
 [age_between(21,24), inn('edu',['10th','12th','grad','pg'],L('Passed Class 10 or higher','10वीं या उससे ऊपर पास','10 ஆம் வகுப்பு அல்லது அதற்கு மேல் தேர்ச்சி')), inc_lte(800000)],
 ['aadhaar','bank','educ','photo'], ['reg','form','ver','trk'], 'https://pminternship.mca.gov.in', cash=6000, once=True)

add('ddugky', ['y'],
 L('DDU-GKY (rural youth skills and jobs)','डीडीयू-जीकेवाई (ग्रामीण युवा कौशल और रोज़गार)','டிடியு-ஜிகேவை (கிராமப்புற இளைஞர் திறன் மற்றும் வேலை)'),
 L('Free training with food, stay and placement for poor rural youth','गरीब ग्रामीण युवाओं के लिए भोजन, आवास और नौकरी सहित निःशुल्क प्रशिक्षण','ஏழைக் கிராமப்புற இளைஞர்களுக்கு உணவு, தங்குமிடம், வேலை வாய்ப்புடன் இலவசப் பயிற்சி'),
 L('Residential and non-residential job training for young people from poor rural families, followed by a placement in a company. Training, food, stay and travel are usually free.',
   'गरीब ग्रामीण परिवारों के युवाओं के लिए आवासीय और गैर-आवासीय रोज़गार प्रशिक्षण, उसके बाद कंपनी में नौकरी। प्रशिक्षण, भोजन, आवास और यात्रा आमतौर पर निःशुल्क होते हैं।',
   'ஏழைக் கிராமப்புறக் குடும்ப இளைஞர்களுக்கு தங்கும் மற்றும் தங்காத வேலைப் பயிற்சி; அதன்பின் நிறுவனத்தில் வேலை. பயிற்சி, உணவு, தங்குமிடம், பயணம் பொதுவாக இலவசம்.'),
 [age_between(15,35), inc_lte(250000)], ['aadhaar','bplc','educ','photo','bank'], ['emp','trn'], 'https://ddugky.gov.in')

add('naps', ['y','w','t','d'],
 L('National Apprenticeship Promotion Scheme','राष्ट्रीय प्रशिक्षुता प्रोत्साहन योजना','தேசிய பயிற்சிப் பணி ஊக்குவிப்புத் திட்டம்'),
 L('Paid on-the-job apprenticeship; the government shares the stipend','वेतन सहित कार्यस्थल प्रशिक्षुता; सरकार वजीफे में हिस्सा देती है','ஊதியத்துடன் பணியிடப் பயிற்சி; உதவித்தொகையில் அரசு பங்களிக்கும்'),
 L('Learn on the job in a company and earn a monthly stipend. The government reimburses part of the stipend to the employer. Open to school pass-outs, ITI and diploma holders and graduates.',
   'कंपनी में काम सीखते हुए मासिक वजीफा पाएँ। सरकार नियोक्ता को वजीफे का एक हिस्सा लौटाती है। स्कूल पास, आईटीआई, डिप्लोमा और स्नातक सभी के लिए।',
   'நிறுவனத்தில் வேலை செய்து கற்றுக்கொண்டு மாத உதவித்தொகை பெறுங்கள். உதவித்தொகையின் ஒரு பகுதியை அரசு முதலாளிக்குத் திருப்பித் தரும். பள்ளி முடித்தவர்கள், ITI, டிப்ளமோ, பட்டதாரிகள் அனைவருக்கும்.'),
 [age_gte(14)], ['aadhaar','bank','educ','photo'], ['reg','form','iv','trn'], 'https://www.apprenticeshipindia.gov.in')

add('eli', ['y','t','d','w','x','s'],
 L('Employment Linked Incentive (PM Viksit Bharat Rozgar Yojana)','रोज़गार से जुड़ी प्रोत्साहन योजना (पीएम विकसित भारत रोज़गार योजना)','வேலையுடன் இணைந்த ஊக்கத்தொகை (பிஎம் விக்சித் பாரத் ரோஜ்கார் திட்டம்)'),
 L('Up to ₹15,000 for your first job in the formal sector','औपचारिक क्षेत्र में पहली नौकरी पर ₹15,000 तक','முறையான துறையில் முதல் வேலைக்கு ₹15,000 வரை'),
 L('If you join your first job in the formal sector and are registered with EPFO, the government pays a one-time incentive in two instalments, subject to salary limits. Your employer registers you; you need an Aadhaar-linked UAN and bank account.',
   'यदि आप औपचारिक क्षेत्र में पहली नौकरी शुरू करते हैं और ईपीएफओ में पंजीकृत हैं, तो सरकार वेतन सीमा के अनुसार दो किस्तों में एकमुश्त प्रोत्साहन देती है। आपका नियोक्ता पंजीकरण करता है; आपको आधार से जुड़ा यूएएन और बैंक खाता चाहिए।',
   'முறையான துறையில் முதல் வேலையில் சேர்ந்து EPFO-வில் பதிவு பெற்றால், ஊதிய வரம்புக்கு உட்பட்டு இரண்டு தவணைகளில் ஒரே முறை ஊக்கத்தொகையை அரசு வழங்கும். உங்கள் முதலாளி பதிவு செய்வார்; ஆதாருடன் இணைந்த UAN மற்றும் வங்கிக் கணக்கு தேவை.'),
 [age_gte(18)], ['aadhaar','bank'], ['kyc','ver','trk'], 'https://www.epfindia.gov.in')

add('ncs', ['y','s','w','t','d','x','p'],
 L('National Career Service (free job portal)','राष्ट्रीय कैरियर सेवा (निःशुल्क जॉब पोर्टल)','தேசிய வேலைவாய்ப்புச் சேவை (இலவச வேலை இணையதளம்)'),
 L('Free job matching, career counselling and job fairs','निःशुल्क नौकरी मिलान, करियर परामर्श और रोज़गार मेले','இலவச வேலைப் பொருத்தம், தொழில் ஆலோசனை, வேலைவாய்ப்பு முகாம்கள்'),
 L('A government job portal where you create a profile, get matched to private and government vacancies, attend job fairs and get career counselling. Registration and use are free.',
   'सरकारी जॉब पोर्टल जहाँ आप प्रोफ़ाइल बनाते हैं, निजी और सरकारी रिक्तियों से मिलान पाते हैं, रोज़गार मेलों में जाते हैं और करियर परामर्श लेते हैं। पंजीकरण और उपयोग निःशुल्क है।',
   'சுயவிவரம் உருவாக்கி, தனியார் மற்றும் அரசு காலியிடங்களுடன் பொருத்தம் பெற்று, வேலைவாய்ப்பு முகாம்களில் பங்கேற்று, தொழில் ஆலோசனை பெறக்கூடிய அரசு வேலை இணையதளம். பதிவும் பயன்பாடும் இலவசம்.'),
 [age_gte(14)], ['aadhaar','educ','photo'], ['reg','emp'], 'https://www.ncs.gov.in')

add('pmdaksh', ['y','t','w'],
 L('PM-DAKSH (skill training for SC, OBC and other groups)','पीएम-दक्ष (एससी, ओबीसी व अन्य वर्गों के लिए कौशल प्रशिक्षण)','பிஎம்-தக்ஷ் (SC, OBC மற்றும் பிற பிரிவினருக்கான திறன் பயிற்சி)'),
 L('Free skill, upskilling and entrepreneurship training with stipend','वजीफे के साथ निःशुल्क कौशल, उन्नयन और उद्यमिता प्रशिक्षण','உதவித்தொகையுடன் இலவசத் திறன், மேம்பாடு, தொழில்முனைவுப் பயிற்சி'),
 L('Training for young people from SC, OBC and similar groups in in-demand skills, with a stipend and help to find work or start a business.',
   'एससी, ओबीसी और ऐसे वर्गों के युवाओं के लिए माँग वाले कौशल का प्रशिक्षण, वजीफे के साथ और काम खोजने या व्यवसाय शुरू करने में मदद।',
   'SC, OBC போன்ற பிரிவு இளைஞர்களுக்கு தேவையுள்ள திறன்களில் பயிற்சி; உதவித்தொகையும் வேலை தேட அல்லது தொழில் தொடங்க உதவியும் கிடைக்கும்.'),
 [inn('cat',['SC','OBC'],L('SC or OBC category','एससी या ओबीसी वर्ग','SC அல்லது OBC பிரிவு')), age_between(18,45)],
 ['aadhaar','caste','income','bank','photo'], ['reg','form','trn'], 'https://pmdaksh.dosje.gov.in')

# =====================  TRANSGENDER PERSONS  =====================
TGL = L('Transgender person','ट्रांसजेंडर व्यक्ति','திருநங்கை / மூன்றாம் பாலினத்தவர்')
add('tgcert', ['t'],
 L('Transgender Certificate of Identity and ID Card','ट्रांसजेंडर पहचान प्रमाण पत्र और परिचय पत्र','திருநங்கை அடையாளச் சான்றிதழ் மற்றும் அடையாள அட்டை'),
 L('Free legal recognition of your identity, needed for most benefits','आपकी पहचान की निःशुल्क कानूनी मान्यता, अधिकतर लाभों के लिए ज़रूरी','உங்கள் அடையாளத்துக்கான இலவச சட்ட அங்கீகாரம்; பெரும்பாலான நலன்களுக்குத் தேவை'),
 L('Under the Transgender Persons (Protection of Rights) Act, 2019 you apply on the national portal and the District Magistrate issues a certificate of identity, followed by a national ID card. Most welfare schemes for transgender persons ask for this certificate.',
   'ट्रांसजेंडर व्यक्ति (अधिकारों का संरक्षण) अधिनियम, 2019 के तहत आप राष्ट्रीय पोर्टल पर आवेदन करते हैं और जिला मजिस्ट्रेट पहचान प्रमाण पत्र जारी करते हैं, फिर राष्ट्रीय परिचय पत्र मिलता है। ट्रांसजेंडर व्यक्तियों की अधिकतर कल्याण योजनाओं में यह प्रमाण पत्र माँगा जाता है।',
   'திருநங்கையர் (உரிமைகள் பாதுகாப்பு) சட்டம், 2019-ன் கீழ் தேசிய இணையதளத்தில் விண்ணப்பித்தால் மாவட்ட ஆட்சியர் அடையாளச் சான்றிதழ் வழங்குவார்; பிறகு தேசிய அடையாள அட்டை கிடைக்கும். திருநங்கையருக்கான பெரும்பாலான நலத் திட்டங்கள் இந்தச் சான்றிதழைக் கேட்கும்.'),
 [eq('track','t',TGL)], ['aadhaar','photo','address','ageproof'], ['tgp','ver','collect'], 'https://transgender.dosje.gov.in')

add('smile', ['t'],
 L('SMILE Scheme (livelihood and enterprise)','स्माइल योजना (आजीविका और उद्यम)','ஸ்மைல் திட்டம் (வாழ்வாதாரம் மற்றும் தொழில்)'),
 L('Skill training with stipend, and support to start a business','वजीफे के साथ कौशल प्रशिक्षण और व्यवसाय शुरू करने में सहायता','உதவித்தொகையுடன் திறன் பயிற்சி மற்றும் தொழில் தொடங்க உதவி'),
 L('SMILE stands for Support for Marginalised Individuals for Livelihood and Enterprise. It gives transgender persons skill training, a stipend and help to set up a business or self-employment, along with health and shelter support.',
   'स्माइल का अर्थ है आजीविका और उद्यम के लिए हाशिए पर खड़े व्यक्तियों को सहायता। यह ट्रांसजेंडर व्यक्तियों को कौशल प्रशिक्षण, वजीफा और व्यवसाय या स्वरोज़गार शुरू करने में मदद देती है, साथ में स्वास्थ्य और आश्रय सहायता भी।',
   'ஸ்மைல் என்பது வாழ்வாதாரம் மற்றும் தொழிலுக்கான விளிம்புநிலை நபர்களுக்கு ஆதரவு. திருநங்கையருக்குத் திறன் பயிற்சி, உதவித்தொகை, தொழில் அல்லது சுயவேலை தொடங்க உதவி, அத்துடன் சுகாதாரம் மற்றும் தங்குமிட ஆதரவு வழங்குகிறது.'),
 [eq('tgid','yes',L('Has a transgender certificate / ID card','ट्रांसजेंडर प्रमाण पत्र / परिचय पत्र है','திருநங்கை சான்றிதழ் / அடையாள அட்டை உள்ளது')), age_gte(18)],
 ['aadhaar','tgc','bank','photo'], ['tgp','ver','trn'], 'https://transgender.dosje.gov.in')

add('garima', ['t'],
 L('Garima Greh (shelter homes)','गरिमा गृह (आश्रय गृह)','கரிமா இல்லங்கள் (தங்குமிடங்கள்)'),
 L('Safe shelter, food, medical care and skill training','सुरक्षित आश्रय, भोजन, चिकित्सा और कौशल प्रशिक्षण','பாதுகாப்பான தங்குமிடம், உணவு, மருத்துவம், திறன் பயிற்சி'),
 L('Shelter homes run by community organisations for transgender persons who have no safe place to live. They give food, medical care, counselling, legal help and training.',
   'ट्रांसजेंडर व्यक्तियों के लिए समुदाय संगठनों द्वारा चलाए जाने वाले आश्रय गृह, जिनके पास रहने की सुरक्षित जगह नहीं है। भोजन, चिकित्सा, परामर्श, कानूनी मदद और प्रशिक्षण मिलता है।',
   'பாதுகாப்பாகத் தங்க இடமில்லாத திருநங்கையருக்கு சமூக அமைப்புகள் நடத்தும் தங்குமிடங்கள். உணவு, மருத்துவம், ஆலோசனை, சட்ட உதவி, பயிற்சி கிடைக்கும்.'),
 [eq('track','t',TGL)], ['aadhaar','photo','address'], ['tgp','iv'], 'https://transgender.dosje.gov.in')

add('tgscholar', ['t'],
 L('Scholarship for Transgender Students','ट्रांसजेंडर विद्यार्थियों के लिए छात्रवृत्ति','திருநங்கை மாணவர்களுக்கான உதவித்தொகை'),
 L('Scholarship from Class 9 up to postgraduate level','कक्षा 9 से स्नातकोत्तर स्तर तक छात्रवृत्ति','9 ஆம் வகுப்பு முதல் முதுகலை வரை உதவித்தொகை'),
 L('Helps transgender students continue school and college with a scholarship covering fees and study costs, from Class 9 to postgraduate level.',
   'ट्रांसजेंडर विद्यार्थियों को कक्षा 9 से स्नातकोत्तर तक फीस और पढ़ाई के खर्च के लिए छात्रवृत्ति देकर स्कूल और कॉलेज की पढ़ाई जारी रखने में मदद करती है।',
   'திருநங்கை மாணவர்கள் 9 ஆம் வகுப்பு முதல் முதுகலை வரை கட்டணம் மற்றும் படிப்புச் செலவுக்கான உதவித்தொகை மூலம் பள்ளி, கல்லூரியில் தொடர உதவுகிறது.'),
 [inn('edu',['below10','10th','12th','grad'],L('Studying from Class 9 up to postgraduate level','कक्षा 9 से स्नातकोत्तर स्तर तक पढ़ाई कर रहे हैं','9 ஆம் வகுப்பு முதல் முதுகலை வரை படிக்கிறீர்கள்'))],
 ['aadhaar','tgc','fee','school','bank'], ['tgp','inst','ver','trk'], 'https://transgender.dosje.gov.in')

add('tgayush', ['t'],
 L('Ayushman Bharat TG Plus Health Card','आयुष्मान भारत टीजी प्लस स्वास्थ्य कार्ड','ஆயுஷ்மான் பாரத் TG பிளஸ் சுகாதார அட்டை'),
 L('Free treatment up to ₹5 lakh a year, including gender-affirming care','प्रति वर्ष ₹5 लाख तक निःशुल्क इलाज, लिंग-पुष्टि देखभाल सहित','ஆண்டுக்கு ₹5 லட்சம் வரை இலவச சிகிச்சை; பாலின உறுதிப்படுத்தும் சிகிச்சை உட்பட'),
 L('A health card for transgender persons that covers hospital treatment and a package of transgender-specific medical care at listed hospitals, without paying from your pocket.',
   'ट्रांसजेंडर व्यक्तियों के लिए स्वास्थ्य कार्ड, जो सूचीबद्ध अस्पतालों में इलाज और ट्रांसजेंडर-विशेष चिकित्सा पैकेज की सुविधा बिना जेब से खर्च किए देता है।',
   'திருநங்கையருக்கான சுகாதார அட்டை; பட்டியலிடப்பட்ட மருத்துவமனைகளில் சிகிச்சையையும் திருநங்கையர் சார்ந்த மருத்துவத் தொகுப்பையும் கையிலிருந்து செலவிடாமல் வழங்குகிறது.'),
 [eq('tgid','yes',L('Has a transgender certificate / ID card','ट्रांसजेंडर प्रमाण पत्र / परिचय पत्र है','திருநங்கை சான்றிதழ் / அடையாள அட்டை உள்ளது'))],
 ['aadhaar','tgc','bank'], ['tgp','kyc','hosp'], 'https://pmjay.gov.in')

# =====================  EX-SERVICEMEN  =====================
add('echs', ['x'],
 L('ECHS (health care for ex-servicemen)','ईसीएचएस (पूर्व सैनिकों की स्वास्थ्य सेवा)','ECHS (முன்னாள் படைவீரர் மருத்துவத் திட்டம்)'),
 L('Cashless treatment for you and your family','आपके और परिवार के लिए कैशलेस इलाज','உங்களுக்கும் குடும்பத்துக்கும் பணமில்லா சிகிச்சை'),
 L('The Ex-servicemen Contributory Health Scheme gives cashless care at ECHS polyclinics and listed hospitals to pensioners and their dependants. You pay a one-time contribution based on your rank and get a smart card.',
   'पूर्व सैनिक अंशदायी स्वास्थ्य योजना पेंशनभोगियों और उनके आश्रितों को ईसीएचएस पॉलीक्लिनिक और सूचीबद्ध अस्पतालों में कैशलेस इलाज देती है। आप अपने रैंक के अनुसार एकमुश्त अंशदान देते हैं और स्मार्ट कार्ड पाते हैं।',
   'முன்னாள் படைவீரர் பங்களிப்பு மருத்துவத் திட்டம் ஓய்வூதியதாரர்களுக்கும் அவர்கள் சார்ந்தோருக்கும் ECHS மருந்தகங்கள் மற்றும் பட்டியலிடப்பட்ட மருத்துவமனைகளில் பணமில்லா சிகிச்சை வழங்குகிறது. உங்கள் பதவிக்கேற்ப ஒருமுறை பங்களிப்பு செலுத்தி ஸ்மார்ட் கார்டு பெறுவீர்கள்.'),
 [eq('pension','yes',L('Retired from service with a pension','पेंशन के साथ सेवानिवृत्त','ஓய்வூதியத்துடன் பணி ஓய்வு பெற்றவர்'))],
 ['aadhaar','esm','ppo','photo','bank'], ['zsb','echs','hosp'], 'https://echs.gov.in')

add('pmss', ['x'],
 L("Prime Minister's Scholarship Scheme (wards of ex-servicemen)",'प्रधानमंत्री छात्रवृत्ति योजना (पूर्व सैनिकों के बच्चे)','பிரதமர் உதவித்தொகைத் திட்டம் (முன்னாள் படைவீரர் பிள்ளைகள்)'),
 L('₹2,500 a month for boys and ₹3,000 for girls','लड़कों को ₹2,500 और लड़कियों को ₹3,000 प्रति माह','மாதம் மகன்களுக்கு ₹2,500, மகள்களுக்கு ₹3,000'),
 L('For the children and widows of ex-servicemen who start professional degree courses such as engineering, medicine or MBA. Selection is based on the marks in the qualifying exam.',
   'पूर्व सैनिकों के बच्चों और विधवाओं के लिए जो इंजीनियरिंग, मेडिकल या एमबीए जैसे व्यावसायिक डिग्री पाठ्यक्रम शुरू करते हैं। चयन योग्यता परीक्षा के अंकों से होता है।',
   'பொறியியல், மருத்துவம், MBA போன்ற தொழில்முறைப் பட்டப்படிப்பைத் தொடங்கும் முன்னாள் படைவீரர்களின் பிள்ளைகள் மற்றும் விதவைகளுக்கு. தகுதித் தேர்வு மதிப்பெண் அடிப்படையில் தேர்வு.'),
 [eq('ward','yes',L('Child or widow studying (or about to study) a professional degree','बच्चा या विधवा व्यावसायिक डिग्री पढ़ रहे (या पढ़ने वाले) हैं','பிள்ளை அல்லது விதவை தொழில்முறைப் பட்டப்படிப்பு படிக்கிறார் (அல்லது படிக்க உள்ளார்)'))],
 ['aadhaar','esm','school','fee','bank'], ['reg','form','inst','ver','trk'], 'https://ksb.gov.in')

add('ksbgrant', ['x'],
 L('Kendriya Sainik Board welfare grants','केंद्रीय सैनिक बोर्ड कल्याण अनुदान','கேந்திரிய சைனிக் வாரிய நலத் தொகைகள்'),
 L("Grants for education, daughters' marriage, medical and distress",'शिक्षा, बेटियों की शादी, इलाज और संकट के लिए अनुदान','கல்வி, மகள் திருமணம், மருத்துவம், இக்கட்டுக்கான நிதி உதவி'),
 L('The Armed Forces Flag Day Fund helps ex-servicemen, widows and dependants, mainly from JCO and other ranks, with education grants, marriage grants, medical aid and help in distress. Apply through your Zila Sainik Board.',
   'सशस्त्र सेना ध्वज दिवस कोष पूर्व सैनिकों, विधवाओं और आश्रितों, मुख्यतः जेसीओ और अन्य रैंक, को शिक्षा अनुदान, विवाह अनुदान, चिकित्सा सहायता और संकट में मदद देता है। अपने जिला सैनिक बोर्ड से आवेदन करें।',
   'ஆயுதப் படைகள் கொடி நாள் நிதி, முன்னாள் படைவீரர்கள், விதவைகள், சார்ந்தோருக்கு (முக்கியமாக JCO மற்றும் பிற நிலைகள்) கல்வி, திருமணம், மருத்துவம், இக்கட்டு உதவிகளை வழங்குகிறது. உங்கள் மாவட்ட சைனிக் வாரியம் மூலம் விண்ணப்பியுங்கள்.'),
 [eq('svc','jco',L('Retired from JCO / other ranks (most grants)','जेसीओ / अन्य रैंक से सेवानिवृत्त (अधिकतर अनुदान)','JCO / மற்ற நிலைகளில் ஓய்வு (பெரும்பாலான நிதிகள்)'))],
 ['aadhaar','esm','ppo','bank','wardproof'], ['zsb','form','ver','trk'], 'https://ksb.gov.in')

add('dgr', ['x'],
 L('DGR resettlement: training and re-employment','डीजीआर पुनर्वास: प्रशिक्षण और पुनः रोज़गार','DGR மறுவாழ்வு: பயிற்சி மற்றும் மறுவேலை'),
 L('Free resettlement courses and job placement help','निःशुल्क पुनर्वास पाठ्यक्रम और नौकरी दिलाने में सहायता','இலவச மறுவாழ்வுப் படிப்புகள் மற்றும் வேலை வாய்ப்பு உதவி'),
 L('The Directorate General Resettlement runs skill and management courses for soldiers who are about to retire or have retired, lists job openings, and helps with self-employment, security agency and franchise opportunities.',
   'पुनर्वास महानिदेशालय सेवानिवृत्त होने वाले या हो चुके सैनिकों के लिए कौशल और प्रबंधन पाठ्यक्रम चलाता है, रिक्तियाँ बताता है और स्वरोज़गार, सुरक्षा एजेंसी और फ्रैंचाइज़ी के अवसरों में मदद करता है।',
   'புனர்வாழ்வு இயக்குநரகம் ஓய்வு பெறவிருக்கும் அல்லது ஓய்வு பெற்ற வீரர்களுக்குத் திறன் மற்றும் மேலாண்மைப் படிப்புகளை நடத்தி, வேலை வாய்ப்புகளைப் பட்டியலிட்டு, சுயதொழில், பாதுகாப்பு நிறுவனம், உரிமம் பெற்ற தொழில் வாய்ப்புகளில் உதவுகிறது.'),
 [eq('track','x',L('Ex-serviceman or about to retire','पूर्व सैनिक या सेवानिवृत्त होने वाले','முன்னாள் படைவீரர் அல்லது ஓய்வு பெறவிருப்பவர்')) ],
 ['aadhaar','esm','ppo','educ','photo'], ['reg','emp','trn'], 'https://dgrindia.gov.in')

add('sparsh', ['x'],
 L('SPARSH (defence pension system)','स्पर्श (रक्षा पेंशन प्रणाली)','ஸ்பர்ஷ் (பாதுகாப்பு ஓய்வூதிய அமைப்பு)'),
 L('Pension paid straight to your bank, with online grievance help','पेंशन सीधे बैंक में, ऑनलाइन शिकायत सुविधा के साथ','ஓய்வூதியம் நேரடியாக வங்கிக்கு; இணையவழிக் குறை தீர்வு'),
 L('The defence pension system pays pension directly into your account and lets you see your pension details, update your records and raise grievances online, without visiting an office.',
   'रक्षा पेंशन प्रणाली पेंशन सीधे आपके खाते में भेजती है और आपको पेंशन का विवरण देखने, रिकॉर्ड अपडेट करने और ऑनलाइन शिकायत करने देती है, बिना दफ़्तर गए।',
   'பாதுகாப்பு ஓய்வூதிய அமைப்பு ஓய்வூதியத்தை நேரடியாக உங்கள் கணக்கில் செலுத்தி, அலுவலகம் செல்லாமல் ஓய்வூதிய விவரங்களைப் பார்க்கவும், பதிவுகளைப் புதுப்பிக்கவும், குறைகளைப் பதிவு செய்யவும் அனுமதிக்கிறது.'),
 [eq('pension','yes',L('Retired from service with a pension','पेंशन के साथ सेवानिवृत्त','ஓய்வூதியத்துடன் பணி ஓய்வு பெற்றவர்'))],
 ['aadhaar','esm','ppo','bank'], ['reg','kyc','trk'], 'https://sparsh.defencepension.gov.in')

# =====================  SPORTS PERSONS  =====================
add('kias', ['p'],
 L('Khelo India Athlete Scholarship','खेलो इंडिया एथलीट छात्रवृत्ति','கேலோ இந்தியா தடகள உதவித்தொகை'),
 L('Up to ₹10 lakh a year for training, kit and expenses','प्रशिक्षण, किट और खर्च के लिए प्रति वर्ष ₹10 लाख तक','பயிற்சி, உபகரணம், செலவுகளுக்கு ஆண்டுக்கு ₹10 லட்சம் வரை'),
 L('For talented young athletes picked through Khelo India Games and talent identification. The scholarship pays for coaching, equipment, diet, medical care and a monthly out-of-pocket allowance.',
   'खेलो इंडिया गेम्स और प्रतिभा पहचान से चुने गए प्रतिभाशाली युवा एथलीटों के लिए। छात्रवृत्ति कोचिंग, उपकरण, आहार, चिकित्सा और मासिक जेब-खर्च भत्ते का खर्च उठाती है।',
   'கேலோ இந்தியா விளையாட்டுகள் மற்றும் திறன் கண்டறிதல் மூலம் தேர்ந்தெடுக்கப்பட்ட திறமையான இளம் வீரர்களுக்கு. பயிற்சி, உபகரணம், உணவு, மருத்துவம், மாதக் கைச்செலவுப் படி ஆகியவற்றை உதவித்தொகை ஏற்கும்.'),
 [inn('level',['state','nat','intl'],L('Has played at state level or higher','राज्य स्तर या उससे ऊपर खेल चुके हैं','மாநில அளவு அல்லது அதற்கு மேல் விளையாடியுள்ளீர்கள்'))],
 ['aadhaar','sportc','school','bank','photo'], ['sai','ver','trk'], 'https://kheloindia.gov.in')

add('tops', ['p'],
 L('Target Olympic Podium Scheme (TOPS)','टारगेट ओलंपिक पोडियम योजना (टॉप्स)','இலக்கு ஒலிம்பிக் மேடைத் திட்டம் (TOPS)'),
 L('Full training funding plus ₹50,000 a month allowance','पूरा प्रशिक्षण खर्च और ₹50,000 मासिक भत्ता','முழுப் பயிற்சி நிதி மற்றும் மாதம் ₹50,000 படி'),
 L('For elite athletes who are medal prospects at the Olympics and Paralympics. Selected athletes get funding for coaching, foreign training, equipment, support staff and a monthly allowance.',
   'ओलंपिक और पैरालंपिक में पदक की संभावना वाले श्रेष्ठ एथलीटों के लिए। चुने गए एथलीटों को कोचिंग, विदेश प्रशिक्षण, उपकरण, सहायक स्टाफ और मासिक भत्ते के लिए धन मिलता है।',
   'ஒலிம்பிக் மற்றும் பாராலிம்பிக்கில் பதக்க வாய்ப்புள்ள சிறந்த வீரர்களுக்கு. தேர்வான வீரர்களுக்குப் பயிற்சி, வெளிநாட்டுப் பயிற்சி, உபகரணம், உதவிப் பணியாளர், மாதப் படிக்கான நிதி கிடைக்கும்.'),
 [eq('level','intl',L('Has played at international level','अंतरराष्ट्रीय स्तर पर खेल चुके हैं','சர்வதேச அளவில் விளையாடியுள்ளீர்கள்'))],
 ['aadhaar','sportc','bank','photo'], ['sai','ver','trk'], 'https://sportsauthorityofindia.nic.in')

add('sportpension', ['p'],
 L('Pension to Meritorious Sportspersons','मेधावी खिलाड़ियों को पेंशन','சிறந்த விளையாட்டு வீரர்களுக்கு ஓய்வூதியம்'),
 L('Monthly pension for international medal winners (up to ₹20,000)','अंतरराष्ट्रीय पदक विजेताओं को मासिक पेंशन (₹20,000 तक)','சர்வதேசப் பதக்க வெற்றியாளர்களுக்கு மாத ஓய்வூதியம் (₹20,000 வரை)'),
 L('For sportspersons who won medals at the Olympics, Paralympics, Asian Games, Commonwealth Games or world championships and have retired from active sport. The amount depends on the medal won.',
   'ओलंपिक, पैरालंपिक, एशियाई खेल, राष्ट्रमंडल खेल या विश्व चैंपियनशिप में पदक जीतने वाले और सक्रिय खेल से संन्यास ले चुके खिलाड़ियों के लिए। राशि जीते गए पदक पर निर्भर है।',
   'ஒலிம்பிக், பாராலிம்பிக், ஆசியப் போட்டிகள், காமன்வெல்த், உலக சாம்பியன்ஷிப்பில் பதக்கம் வென்று தீவிர விளையாட்டிலிருந்து ஓய்வு பெற்ற வீரர்களுக்கு. தொகை வென்ற பதக்கத்தைப் பொறுத்தது.'),
 [eq('medal','yes',L('Won an international medal','अंतरराष्ट्रीय पदक जीता है','சர்வதேசப் பதக்கம் வென்றுள்ளீர்கள்')), age_gte(30)],
 ['aadhaar','sportc','bank','photo'], ['sai','form','ver','trk'], 'https://yas.nic.in')

add('nswf', ['p'],
 L('National Welfare Fund for Sportspersons','राष्ट्रीय खिलाड़ी कल्याण कोष','தேசிய விளையாட்டு வீரர் நலநிதி'),
 L('Financial help for past medal winners in need','ज़रूरतमंद पूर्व पदक विजेताओं को आर्थिक सहायता','தேவையிலுள்ள முன்னாள் பதக்க வெற்றியாளர்களுக்கு நிதி உதவி'),
 L('Helps sportspersons who earned international honours and are now in financial difficulty, for example because of illness or hardship, and supports the families of those who died.',
   'अंतरराष्ट्रीय सम्मान जीतने वाले और अब आर्थिक कठिनाई में, जैसे बीमारी या संकट के कारण, खिलाड़ियों की मदद करता है और दिवंगत खिलाड़ियों के परिवारों को सहारा देता है।',
   'சர்வதேச சாதனை படைத்து, நோய் அல்லது இக்கட்டு காரணமாக இப்போது நிதி நெருக்கடியில் உள்ள வீரர்களுக்கு உதவுகிறது; இறந்த வீரர்களின் குடும்பங்களுக்கும் ஆதரவளிக்கிறது.'),
 [eq('medal','yes',L('Won a medal at a major international event','बड़े अंतरराष्ट्रीय आयोजन में पदक जीता है','பெரிய சர்வதேசப் போட்டியில் பதக்கம் வென்றுள்ளீர்கள்'))],
 ['aadhaar','sportc','income','bank'], ['sai','form','ver','trk'], 'https://yas.nic.in')

add('nstss', ['p'],
 L('National Sports Talent Search Scheme','राष्ट्रीय खेल प्रतिभा खोज योजना','தேசிய விளையாட்டுத் திறன் தேடல் திட்டம்'),
 L('Monthly scholarship and coaching for talented children','प्रतिभाशाली बच्चों के लिए मासिक छात्रवृत्ति और कोचिंग','திறமையான குழந்தைகளுக்கு மாத உதவித்தொகை மற்றும் பயிற்சி'),
 L('Finds talented children aged 8 to 14 through school-level tests and trains them at SAI centres and sports schools with a monthly scholarship.',
   '8 से 14 वर्ष के प्रतिभाशाली बच्चों को स्कूल स्तर की परीक्षाओं से खोजकर साई केंद्रों और खेल स्कूलों में मासिक छात्रवृत्ति के साथ प्रशिक्षण देती है।',
   '8 முதல் 14 வயதுள்ள திறமையான குழந்தைகளைப் பள்ளி அளவிலான தேர்வுகள் மூலம் கண்டறிந்து, SAI மையங்கள் மற்றும் விளையாட்டுப் பள்ளிகளில் மாத உதவித்தொகையுடன் பயிற்சி அளிக்கிறது.'),
 [age_between(8,14)], ['aadhaar','school','photo','bank'], ['sai','iv','trk'], 'https://sportsauthorityofindia.nic.in')

add('sportsquota', ['p'],
 L('Sports quota in jobs and admissions','नौकरी और प्रवेश में खेल कोटा','வேலை மற்றும் சேர்க்கையில் விளையாட்டு ஒதுக்கீடு'),
 L('Reserved posts and seats for national and international players','राष्ट्रीय और अंतरराष्ट्रीय खिलाड़ियों के लिए आरक्षित पद और सीटें','தேசிய மற்றும் சர்வதேச வீரர்களுக்கு ஒதுக்கப்பட்ட பணியிடங்கள் மற்றும் இடங்கள்'),
 L('Many central and state departments, railways, banks, police forces and colleges keep posts or seats for sportspersons with national or international achievements. Watch for recruitment notices that mention the sports quota.',
   'कई केंद्रीय और राज्य विभाग, रेलवे, बैंक, पुलिस बल और कॉलेज राष्ट्रीय या अंतरराष्ट्रीय उपलब्धि वाले खिलाड़ियों के लिए पद या सीटें रखते हैं। खेल कोटे का उल्लेख करने वाली भर्ती सूचनाओं पर नज़र रखें।',
   'பல மத்திய, மாநிலத் துறைகள், ரயில்வே, வங்கிகள், காவல் படைகள், கல்லூரிகள் தேசிய அல்லது சர்வதேச சாதனை படைத்த வீரர்களுக்குப் பணியிடங்கள் அல்லது இடங்களை ஒதுக்குகின்றன. விளையாட்டு ஒதுக்கீடு குறிப்பிடும் ஆட்சேர்ப்பு அறிவிப்புகளைக் கவனியுங்கள்.'),
 [inn('level',['nat','intl'],L('Has played at national level or higher','राष्ट्रीय स्तर या उससे ऊपर खेल चुके हैं','தேசிய அளவு அல்லது அதற்கு மேல் விளையாடியுள்ளீர்கள்'))],
 ['aadhaar','sportc','educ','photo'], ['emp','form','iv','ver'], 'https://yas.nic.in')

# =====================  PERSONS WITH DISABILITIES  =====================
PWD = dis_gte(40)
add('udid', ['d'],
 L('UDID card (Swavlamban card)','यूडीआईडी कार्ड (स्वावलंबन कार्ड)','UDID அட்டை (சுவாவலம்பன் அட்டை)'),
 L('One national ID that proves your disability for all benefits','सभी लाभों के लिए दिव्यांगता का एक राष्ट्रीय पहचान पत्र','அனைத்து நலன்களுக்கும் உங்கள் மாற்றுத்திறனை நிரூபிக்கும் ஒரே தேசிய அட்டை'),
 L('The Unique Disability ID is a single card accepted across India as proof of disability. Once you have it you do not need separate certificates for each scheme, railway concession or job reservation.',
   'यूनिक डिसेबिलिटी आईडी एक कार्ड है जो पूरे भारत में दिव्यांगता के प्रमाण के रूप में मान्य है। इसके बाद हर योजना, रेल रियायत या नौकरी आरक्षण के लिए अलग प्रमाण पत्र की ज़रूरत नहीं पड़ती।',
   'தனித்துவ மாற்றுத்திறன் அடையாள அட்டை இந்தியா முழுவதும் மாற்றுத்திறனுக்கான சான்றாக ஏற்கப்படும் ஒரே அட்டை. இது இருந்தால் ஒவ்வொரு திட்டம், ரயில் சலுகை, வேலை ஒதுக்கீட்டுக்கும் தனிச் சான்றிதழ் தேவையில்லை.'),
 [PWD], ['aadhaar','photo','medical'], ['reg','form','iv','collect'], 'https://www.swavlambancard.gov.in')

add('igndps', ['d'],
 L('Indira Gandhi National Disability Pension Scheme','इंदिरा गांधी राष्ट्रीय दिव्यांगता पेंशन योजना','இந்திரா காந்தி தேசிய மாற்றுத்திறன் ஓய்வூதியத் திட்டம்'),
 L('Monthly pension for severely disabled adults (Centre ₹300; states add more)','गंभीर दिव्यांग वयस्कों को मासिक पेंशन (केंद्र ₹300; राज्य और जोड़ते हैं)','கடும் மாற்றுத்திறன் கொண்ட பெரியவர்களுக்கு மாத ஓய்வூதியம் (மத்திய அரசு ₹300; மாநிலங்கள் கூடுதல்)'),
 L('A monthly pension for adults with severe (80% or more) or multiple disabilities from poor families. The Centre pays a fixed part and most states add to it.',
   'गरीब परिवारों के गंभीर (80% या अधिक) या बहु-दिव्यांगता वाले वयस्कों के लिए मासिक पेंशन। केंद्र एक तय हिस्सा देता है और अधिकतर राज्य उसमें जोड़ते हैं।',
   'ஏழைக் குடும்பங்களின் கடும் (80% அல்லது அதற்கு மேல்) அல்லது பல மாற்றுத்திறன் கொண்ட பெரியவர்களுக்கான மாத ஓய்வூதியம். மத்திய அரசு ஒரு நிலையான பகுதியைத் தரும்; பெரும்பாலான மாநிலங்கள் கூடுதலாகச் சேர்க்கும்.'),
 [dis_gte(80), age_between(18,79), eq('bpl','yes',BPL)], ['aadhaar','udidc','bplc','bank','photo'], ['panch','form','ver','trk'], 'https://nsap.nic.in', cash=3600)

add('adip', ['d'],
 L('ADIP Scheme (free aids and appliances)','एडीआईपी योजना (निःशुल्क सहायक उपकरण)','ADIP திட்டம் (இலவச உதவி உபகரணங்கள்)'),
 L('Free wheelchairs, hearing aids, artificial limbs and more','निःशुल्क व्हीलचेयर, श्रवण यंत्र, कृत्रिम अंग और अन्य','இலவச சக்கர நாற்காலி, செவிப்புலன் கருவி, செயற்கை உறுப்புகள் மற்றும் பல'),
 L('Gives good-quality aids to persons with 40% or more disability. Aids are free if monthly family income is up to ₹15,000, and half-price up to ₹20,000. Aids are given at camps run by ALIMCO and local bodies.',
   '40% या अधिक दिव्यांगता वाले व्यक्तियों को अच्छी गुणवत्ता के उपकरण देती है। मासिक पारिवारिक आय ₹15,000 तक हो तो उपकरण निःशुल्क और ₹20,000 तक हो तो आधी कीमत पर। उपकरण एलिम्को और स्थानीय निकायों के शिविरों में दिए जाते हैं।',
   '40% அல்லது அதற்கு மேல் மாற்றுத்திறன் உள்ளவர்களுக்குத் தரமான உபகரணங்களை வழங்குகிறது. மாதக் குடும்ப வருமானம் ₹15,000 வரை இருந்தால் இலவசம்; ₹20,000 வரை பாதி விலை. ALIMCO மற்றும் உள்ளாட்சி அமைப்புகள் நடத்தும் முகாம்களில் வழங்கப்படும்.'),
 [PWD, {"field":"income","op":"lte","value":180000,"label":L('Family income up to ₹15,000 a month (₹1.8 lakh a year)','परिवार की आय ₹15,000 प्रति माह (₹1.8 लाख सालाना) तक','குடும்ப வருமானம் மாதம் ₹15,000 (ஆண்டுக்கு ₹1.8 லட்சம்) வரை')}],
 ['aadhaar','udidc','income','photo'], ['udidf','form','camp'], 'https://disabilityaffairs.gov.in')

add('pmspwd', ['d'],
 L('Post-Matric Scholarship for Students with Disabilities','दिव्यांग विद्यार्थियों के लिए पोस्ट-मैट्रिक छात्रवृत्ति','மாற்றுத்திறன் மாணவர்களுக்கான மேற்படிப்பு உதவித்தொகை'),
 L('Fees and monthly allowance from Class 11 to PhD','कक्षा 11 से पीएचडी तक फीस और मासिक भत्ता','11 ஆம் வகுப்பு முதல் முனைவர் படிப்பு வரை கட்டணமும் மாதப் படியும்'),
 L('Helps students with 40% or more disability study after Class 10 with a maintenance allowance, fee reimbursement and a disability allowance. Apply every year on the National Scholarship Portal.',
   '40% या अधिक दिव्यांगता वाले विद्यार्थियों को कक्षा 10 के बाद की पढ़ाई के लिए निर्वाह भत्ता, फीस की प्रतिपूर्ति और दिव्यांगता भत्ता देती है। हर साल राष्ट्रीय छात्रवृत्ति पोर्टल पर आवेदन करें।',
   '40% அல்லது அதற்கு மேல் மாற்றுத்திறன் உள்ள மாணவர்கள் 10 ஆம் வகுப்புக்குப் பிறகு படிக்க பராமரிப்புப் படி, கட்டணத் திருப்பிச் செலுத்தல், மாற்றுத்திறன் படி வழங்குகிறது. ஆண்டுதோறும் தேசிய உதவித்தொகை இணையதளத்தில் விண்ணப்பியுங்கள்.'),
 [PWD, inc_lte(250000), inn('edu',['10th','12th','grad'],L('Passed Class 10 or higher and still studying','10वीं या उससे ऊपर पास और अभी पढ़ रहे हैं','10 ஆம் வகுப்பு அல்லது அதற்கு மேல் தேர்ச்சி; தொடர்ந்து படிக்கிறீர்கள்'))],
 ['aadhaar','udidc','income','fee','school','bank'], ['reg','form','inst','ver','trk','ren'], 'https://scholarships.gov.in')

add('prematricpwd', ['d'],
 L('Pre-Matric Scholarship for Students with Disabilities','दिव्यांग विद्यार्थियों के लिए प्री-मैट्रिक छात्रवृत्ति','மாற்றுத்திறன் மாணவர்களுக்கான பள்ளி உதவித்தொகை'),
 L('Allowance and fee support for Class 9 and 10','कक्षा 9 और 10 के लिए भत्ता और फीस सहायता','9 மற்றும் 10 ஆம் வகுப்புக்குப் படியும் கட்டண உதவியும்'),
 L('Helps school students with 40% or more disability in Class 9 and 10 with a monthly allowance, book grant and escort or reader allowance where needed.',
   '40% या अधिक दिव्यांगता वाले कक्षा 9 और 10 के स्कूली विद्यार्थियों को मासिक भत्ता, किताबों का अनुदान और ज़रूरत पड़ने पर सहायक या रीडर भत्ता देती है।',
   '40% அல்லது அதற்கு மேல் மாற்றுத்திறன் உள்ள 9, 10 ஆம் வகுப்பு மாணவர்களுக்கு மாதப் படி, புத்தக மானியம், தேவைப்பட்டால் துணையாளர் அல்லது வாசகர் படி வழங்குகிறது.'),
 [PWD, inc_lte(250000), age_lte(18)],
 ['aadhaar','udidc','income','school','bank'], ['reg','form','inst','ver','trk','ren'], 'https://scholarships.gov.in')

add('ndfdc', ['d'],
 L('NDFDC concessional loans','एनडीएफडीसी रियायती ऋण','NDFDC சலுகைக் கடன்கள்'),
 L('Low-interest loans for business, vehicle, education and farming','व्यवसाय, वाहन, शिक्षा और खेती के लिए कम ब्याज पर ऋण','தொழில், வாகனம், கல்வி, விவசாயத்துக்குக் குறைந்த வட்டிக் கடன்'),
 L('The National Divyangjan Finance and Development Corporation lends at concessional rates to persons with 40% or more disability, through state channelising agencies and banks.',
   'राष्ट्रीय दिव्यांगजन वित्त एवं विकास निगम 40% या अधिक दिव्यांगता वाले व्यक्तियों को राज्य चैनलाइज़िंग एजेंसियों और बैंकों के माध्यम से रियायती दर पर ऋण देता है।',
   'தேசிய மாற்றுத்திறனாளிகள் நிதி மற்றும் மேம்பாட்டுக் கழகம் 40% அல்லது அதற்கு மேல் மாற்றுத்திறன் உள்ளவர்களுக்கு மாநில வழிப்படுத்தும் முகமைகள் மற்றும் வங்கிகள் மூலம் சலுகை வட்டியில் கடன் வழங்குகிறது.'),
 [PWD, age_gte(18)], ['aadhaar','udidc','pan','bank','plan'], ['plan','bankv','ver','loan'], 'https://ndfdc.nic.in')

add('nfpwd', ['d'],
 L('National Fellowship for Persons with Disabilities','दिव्यांगजनों के लिए राष्ट्रीय फेलोशिप','மாற்றுத்திறனாளிகளுக்கான தேசிய ஆய்வு உதவித்தொகை'),
 L('Monthly fellowship for M.Phil and PhD research','एम.फिल और पीएचडी शोध के लिए मासिक फेलोशिप','எம்.ஃபில் மற்றும் முனைவர் ஆராய்ச்சிக்கு மாத உதவித்தொகை'),
 L('Supports students with 40% or more disability who go on to M.Phil or PhD research, with a monthly fellowship and a yearly contingency grant.',
   '40% या अधिक दिव्यांगता वाले जो विद्यार्थी एम.फिल या पीएचडी शोध करते हैं, उन्हें मासिक फेलोशिप और वार्षिक आकस्मिक अनुदान मिलता है।',
   '40% அல்லது அதற்கு மேல் மாற்றுத்திறன் உள்ள மாணவர்கள் எம்.ஃபில் அல்லது முனைவர் ஆராய்ச்சி செய்ய மாத உதவித்தொகையும் ஆண்டு தற்செயல் மானியமும் வழங்கி ஆதரிக்கிறது.'),
 [PWD, eq('edu','pg',L('Postgraduate degree completed','स्नातकोत्तर पूरा किया है','முதுகலை முடித்துள்ளீர்கள்'))],
 ['aadhaar','udidc','educ','bank'], ['reg','form','inst','ver','trk'], 'https://scholarships.gov.in')

add('railconc', ['d'],
 L('Railway fare concession for persons with disabilities','दिव्यांगजनों के लिए रेल किराये में रियायत','மாற்றுத்திறனாளிகளுக்கு ரயில் கட்டணச் சலுகை'),
 L('Concession on train fares (varies by disability), also for an escort','ट्रेन किराये में रियायत (दिव्यांगता के अनुसार), सहायक के लिए भी','ரயில் கட்டணத்தில் சலுகை (மாற்றுத்திறன் வகைக்கேற்ப), துணையாளருக்கும்'),
 L('Indian Railways gives a fare concession to persons with disabilities and, for some types of disability, to one escort. You need a valid disability certificate or UDID card and a concession certificate or smart ID.',
   'भारतीय रेल दिव्यांगजनों को और कुछ दिव्यांगताओं में एक सहायक को भी किराये में रियायत देती है। इसके लिए मान्य दिव्यांगता प्रमाण पत्र या यूडीआईडी कार्ड और रियायत प्रमाण पत्र या स्मार्ट आईडी चाहिए।',
   'இந்திய ரயில்வே மாற்றுத்திறனாளிகளுக்கும், சில வகை மாற்றுத்திறனுக்கு ஒரு துணையாளருக்கும் கட்டணச் சலுகை வழங்குகிறது. செல்லுபடியாகும் மாற்றுத்திறன் சான்றிதழ் அல்லது UDID அட்டை மற்றும் சலுகைச் சான்றிதழ் அல்லது ஸ்மார்ட் அடையாள அட்டை தேவை.'),
 [PWD], ['aadhaar','udidc','photo'], ['reg','form','collect'], 'https://indianrailways.gov.in')

add('pwdjobs', ['d'],
 L('4% job reservation for persons with disabilities','दिव्यांगजनों के लिए 4% सरकारी नौकरी आरक्षण','மாற்றுத்திறனாளிகளுக்கு 4% அரசு வேலை இடஒதுக்கீடு'),
 L('4% of government posts and 5% of college seats are reserved','सरकारी पदों में 4% और कॉलेज सीटों में 5% आरक्षण','அரசுப் பணிகளில் 4% மற்றும் கல்லூரி இடங்களில் 5% ஒதுக்கீடு'),
 L('Under the Rights of Persons with Disabilities Act, 2016, 4% of posts in government jobs and 5% of seats in higher education are reserved for persons with benchmark disabilities (40% or more). You also get age relaxation and exam help.',
   'दिव्यांगजन अधिकार अधिनियम, 2016 के तहत सरकारी नौकरियों के 4% पद और उच्च शिक्षा की 5% सीटें बेंचमार्क दिव्यांगता (40% या अधिक) वाले व्यक्तियों के लिए आरक्षित हैं। आयु में छूट और परीक्षा में सहायता भी मिलती है।',
   'மாற்றுத்திறனாளிகள் உரிமைகள் சட்டம், 2016-ன் கீழ் அரசு வேலைகளில் 4% பணியிடங்களும் உயர்கல்வியில் 5% இடங்களும் அளவுகோல் மாற்றுத்திறன் (40% அல்லது அதற்கு மேல்) கொண்டவர்களுக்கு ஒதுக்கப்பட்டுள்ளன. வயது தளர்வும் தேர்வு உதவியும் கிடைக்கும்.'),
 [PWD], ['aadhaar','udidc','educ','photo'], ['emp','form','iv'], 'https://disabilityaffairs.gov.in')

# =====================  SENIOR CITIZENS  =====================
add('ignoaps', ['o'],
 L('Indira Gandhi National Old Age Pension Scheme','इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना','இந்திரா காந்தி தேசிய முதியோர் ஓய்வூதியத் திட்டம்'),
 L('Monthly pension (Centre ₹200 at 60+, ₹500 at 80+). States add more','मासिक पेंशन (केंद्र: 60+ पर ₹200, 80+ पर ₹500)। राज्य और जोड़ते हैं','மாத ஓய்வூதியம் (மத்திய அரசு: 60+ வயதில் ₹200, 80+ வயதில் ₹500). மாநிலங்கள் கூடுதல்'),
 L('A monthly pension for senior citizens from poor (BPL) families. The Centre pays a fixed part and most states add to it, so what you receive depends on your state.',
   'गरीब (बीपीएल) परिवारों के वरिष्ठ नागरिकों के लिए मासिक पेंशन। केंद्र एक तय हिस्सा देता है और अधिकतर राज्य उसमें जोड़ते हैं, इसलिए आपको मिलने वाली राशि राज्य पर निर्भर है।',
   'ஏழை (BPL) குடும்பங்களின் மூத்த குடிமக்களுக்கான மாத ஓய்வூதியம். மத்திய அரசு ஒரு நிலையான பகுதியைத் தரும்; பெரும்பாலான மாநிலங்கள் கூடுதலாகச் சேர்க்கும்; எனவே நீங்கள் பெறும் தொகை மாநிலத்தைப் பொறுத்தது.'),
 [age_gte(60), eq('bpl','yes',BPL)], ['aadhaar','bank','bplc','ageproof','photo'], ['panch','form','ver','trk'], 'https://nsap.nic.in', cash=2400)

add('vayvandana', ['o'],
 L('Ayushman Vay Vandana Card (age 70+)','आयुष्मान वय वंदना कार्ड (70+ वर्ष)','ஆயுஷ்மான் வய வந்தனா அட்டை (70+ வயது)'),
 L('Free treatment up to ₹5 lakh a year, with no income limit','प्रति वर्ष ₹5 लाख तक निःशुल्क इलाज, आय की कोई सीमा नहीं','ஆண்டுக்கு ₹5 லட்சம் வரை இலவச சிகிச்சை; வருமான வரம்பு இல்லை'),
 L('Every citizen aged 70 or above can get health cover for hospital care, whatever their income. If your family is already covered by Ayushman Bharat, senior members get an extra top-up cover.',
   '70 वर्ष या उससे अधिक उम्र का हर नागरिक आय की परवाह किए बिना अस्पताल के इलाज के लिए स्वास्थ्य कवर पा सकता है। यदि आपका परिवार पहले से आयुष्मान भारत में है तो वरिष्ठ सदस्यों को अतिरिक्त टॉप-अप कवर मिलता है।',
   '70 வயது அல்லது அதற்கு மேற்பட்ட ஒவ்வொரு குடிமகனும் வருமானம் எதுவாக இருந்தாலும் மருத்துவமனைச் சிகிச்சைக்கான சுகாதாரக் காப்பீடு பெறலாம். உங்கள் குடும்பம் ஏற்கெனவே ஆயுஷ்மான் பாரத்தில் இருந்தால் மூத்த உறுப்பினர்களுக்குக் கூடுதல் காப்பீடு கிடைக்கும்.'),
 [age_gte(70)], ['aadhaar','address'], ['reg','kyc','hosp'], 'https://pmjay.gov.in')

add('annapurna', ['o'],
 L('Annapurna Scheme (free grain)','अन्नपूर्णा योजना (निःशुल्क अनाज)','அன்னபூர்ணா திட்டம் (இலவச தானியம்)'),
 L('10 kg of free food grain every month','हर महीने 10 किलो निःशुल्क अनाज','ஒவ்வொரு மாதமும் 10 கிலோ இலவச தானியம்'),
 L('For senior citizens aged 65 or above who qualify for an old-age pension but are not receiving it. The grain is given free through the ration shop.',
   '65 वर्ष या अधिक उम्र के वरिष्ठ नागरिकों के लिए जो वृद्धावस्था पेंशन के पात्र हैं पर पेंशन नहीं पा रहे। अनाज राशन दुकान से निःशुल्क मिलता है।',
   '65 வயது அல்லது அதற்கு மேற்பட்ட, முதியோர் ஓய்வூதியத்துக்குத் தகுதி இருந்தும் அதைப் பெறாத மூத்த குடிமக்களுக்கு. தானியம் நியாய விலைக் கடை மூலம் இலவசமாக வழங்கப்படும்.'),
 [age_gte(65), eq('bpl','yes',BPL)], ['aadhaar','bplc','ageproof','photo'], ['panch','form','ver'], 'https://nsap.nic.in')

add('vayoshri', ['o'],
 L('Rashtriya Vayoshri Yojana (free aids for seniors)','राष्ट्रीय वयोश्री योजना (वरिष्ठों के लिए निःशुल्क उपकरण)','ராஷ்ட்ரிய வயோஸ்ரீ திட்டம் (முதியோருக்கு இலவச உபகரணங்கள்)'),
 L('Free walking sticks, hearing aids, spectacles, wheelchairs and dentures','निःशुल्क छड़ी, श्रवण यंत्र, चश्मा, व्हीलचेयर और नकली दाँत','இலவச ஊன்றுகோல், செவிப்புலன் கருவி, கண்ணாடி, சக்கர நாற்காலி, செயற்கைப் பல்'),
 L('Gives free physical aids to senior citizens from poor families who have age-related problems such as low vision, hearing loss, weak legs or lost teeth. Aids are given at camps.',
   'गरीब परिवारों के वरिष्ठ नागरिकों को, जिन्हें कम दिखना, सुनने में कमी, कमज़ोर पैर या दाँत गिरने जैसी उम्र संबंधी समस्याएँ हैं, निःशुल्क उपकरण देती है। उपकरण शिविरों में दिए जाते हैं।',
   'குறைந்த பார்வை, செவித்திறன் குறைவு, பலவீனமான கால்கள், பல் இழப்பு போன்ற வயது தொடர்பான பிரச்சினைகள் உள்ள ஏழைக் குடும்ப மூத்த குடிமக்களுக்கு இலவச உபகரணங்களை வழங்குகிறது. உபகரணங்கள் முகாம்களில் வழங்கப்படும்.'),
 [age_gte(60), eq('bpl','yes',BPL)], ['aadhaar','bplc','ageproof','photo','medical'], ['form','camp'], 'https://alimco.in')

add('scss', ['o'],
 L('Senior Citizens Savings Scheme','वरिष्ठ नागरिक बचत योजना','மூத்த குடிமக்கள் சேமிப்புத் திட்டம்'),
 L('Safe savings with high government-set interest paid every quarter','हर तिमाही सरकार द्वारा तय ऊँचे ब्याज के साथ सुरक्षित बचत','ஒவ்வொரு காலாண்டும் அரசு நிர்ணயித்த உயர் வட்டியுடன் பாதுகாப்பான சேமிப்பு'),
 L('A 5-year deposit scheme for people aged 60 or above (55 for some retirees). You can deposit up to ₹30 lakh at a post office or bank, and interest is paid every quarter. The rate is set by the government.',
   '60 वर्ष या अधिक (कुछ सेवानिवृत्तों के लिए 55) उम्र के लोगों के लिए 5 साल की जमा योजना। डाकघर या बैंक में ₹30 लाख तक जमा कर सकते हैं और ब्याज हर तिमाही मिलता है। दर सरकार तय करती है।',
   '60 வயது அல்லது அதற்கு மேற்பட்டவர்களுக்கான (சில ஓய்வு பெற்றோருக்கு 55) 5 ஆண்டு வைப்புத் திட்டம். அஞ்சலகம் அல்லது வங்கியில் ₹30 லட்சம் வரை வைப்பு செய்யலாம்; வட்டி ஒவ்வொரு காலாண்டும் கிடைக்கும். வட்டி விகிதத்தை அரசு நிர்ணயிக்கும்.'),
 [age_gte(60)], ['aadhaar','pan','ageproof','photo','bank'], ['post'], 'https://www.indiapost.gov.in')

add('elderline', ['o'],
 L('Elderline 14567 (helpline for senior citizens)','एल्डरलाइन 14567 (वरिष्ठ नागरिक हेल्पलाइन)','எல்டர்லைன் 14567 (மூத்த குடிமக்கள் உதவி எண்)'),
 L('Free helpline for information, guidance and rescue help','जानकारी, मार्गदर्शन और बचाव सहायता के लिए निःशुल्क हेल्पलाइन','தகவல், வழிகாட்டல், மீட்பு உதவிக்கான இலவச உதவி எண்'),
 L('A national toll-free number for senior citizens. It gives information about schemes, pension and legal rights, and connects you to help in case of abuse or an emergency.',
   'वरिष्ठ नागरिकों के लिए राष्ट्रीय टोल-फ्री नंबर। यह योजनाओं, पेंशन और कानूनी अधिकारों की जानकारी देता है और दुर्व्यवहार या आपात स्थिति में मदद से जोड़ता है।',
   'மூத்த குடிமக்களுக்கான தேசிய இலவச அழைப்பு எண். திட்டங்கள், ஓய்வூதியம், சட்ட உரிமைகள் பற்றிய தகவல் அளித்து, துன்புறுத்தல் அல்லது அவசரத்தில் உதவியுடன் இணைக்கிறது.'),
 [age_gte(60)], ['aadhaar'], ['help'], 'https://socialjustice.gov.in')

# =====================  FOR EVERYONE (cross-category)  =====================
add('pmjdy', ALL,
 L('PM Jan Dhan Yojana (zero-balance bank account)','पीएम जन धन योजना (शून्य बैलेंस खाता)','பிஎம் ஜன் தன் திட்டம் (பூஜ்ய இருப்பு வங்கிக் கணக்கு)'),
 L('Free bank account with RuPay card and ₹2 lakh accident cover','रूपे कार्ड और ₹2 लाख दुर्घटना बीमा के साथ निःशुल्क बैंक खाता','ரூபே அட்டை மற்றும் ₹2 லட்சம் விபத்துக் காப்பீடுடன் இலவச வங்கிக் கணக்கு'),
 L('A basic bank account with no minimum balance. Most schemes pay money straight into a bank account, so this is the first step. The RuPay card comes with accident insurance.',
   'बिना न्यूनतम बैलेंस वाला बुनियादी बैंक खाता। अधिकतर योजनाएँ पैसा सीधे बैंक खाते में भेजती हैं, इसलिए यह पहला कदम है। रूपे कार्ड के साथ दुर्घटना बीमा भी मिलता है।',
   'குறைந்தபட்ச இருப்பு தேவையில்லாத அடிப்படை வங்கிக் கணக்கு. பெரும்பாலான திட்டங்கள் பணத்தை நேரடியாக வங்கிக் கணக்கில் செலுத்துவதால் இதுவே முதல் படி. ரூபே அட்டையுடன் விபத்துக் காப்பீடும் கிடைக்கும்.'),
 [age_gte(10)], ['aadhaar','photo','address'], ['bankv','kyc'], 'https://pmjdy.gov.in')

add('pmjjby', ALL,
 L('PM Jeevan Jyoti Bima Yojana','पीएम जीवन ज्योति बीमा योजना','பிஎம் ஜீவன் ஜோதி காப்பீட்டுத் திட்டம்'),
 L('₹2 lakh life cover for ₹436 a year','₹436 सालाना में ₹2 लाख का जीवन बीमा','ஆண்டுக்கு ₹436 செலுத்தி ₹2 லட்சம் ஆயுள் காப்பீடு'),
 L('A yearly renewable life insurance. If the insured person dies from any cause, the family gets ₹2 lakh. The premium is deducted automatically from your bank account every year.',
   'हर साल नवीनीकरण होने वाला जीवन बीमा। किसी भी कारण से बीमित की मृत्यु होने पर परिवार को ₹2 लाख मिलते हैं। प्रीमियम हर साल आपके बैंक खाते से अपने आप कट जाता है।',
   'ஆண்டுதோறும் புதுப்பிக்கப்படும் ஆயுள் காப்பீடு. காப்பீடு பெற்றவர் எந்தக் காரணத்தாலும் இறந்தால் குடும்பத்துக்கு ₹2 லட்சம் கிடைக்கும். பிரீமியம் ஆண்டுதோறும் வங்கிக் கணக்கிலிருந்து தானாகப் பிடிக்கப்படும்.'),
 [age_between(18,50)], ['aadhaar','bank'], ['bankv','kyc','ren'], 'https://jansuraksha.gov.in')

add('pmsby', ALL,
 L('PM Suraksha Bima Yojana','पीएम सुरक्षा बीमा योजना','பிஎம் சுரக்ஷா காப்பீட்டுத் திட்டம்'),
 L('₹2 lakh accident cover for just ₹20 a year','सिर्फ़ ₹20 सालाना में ₹2 लाख का दुर्घटना बीमा','ஆண்டுக்கு வெறும் ₹20-க்கு ₹2 லட்சம் விபத்துக் காப்பீடு'),
 L('Accident insurance that pays ₹2 lakh on accidental death or full disability and ₹1 lakh on partial disability. The small premium is deducted from your bank account once a year.',
   'दुर्घटना बीमा जो दुर्घटना में मृत्यु या पूर्ण विकलांगता पर ₹2 लाख और आंशिक विकलांगता पर ₹1 लाख देता है। छोटा प्रीमियम साल में एक बार आपके बैंक खाते से कटता है।',
   'விபத்து மரணம் அல்லது முழு மாற்றுத்திறனுக்கு ₹2 லட்சமும் பகுதி மாற்றுத்திறனுக்கு ₹1 லட்சமும் வழங்கும் விபத்துக் காப்பீடு. சிறிய பிரீமியம் ஆண்டுக்கு ஒருமுறை வங்கிக் கணக்கிலிருந்து பிடிக்கப்படும்.'),
 [age_between(18,70)], ['aadhaar','bank'], ['bankv','kyc','ren'], 'https://jansuraksha.gov.in')

add('apy', ALL,
 L('Atal Pension Yojana','अटल पेंशन योजना','அடல் ஓய்வூதியத் திட்டம்'),
 L('Fixed pension of ₹1,000 to ₹5,000 a month from age 60','60 वर्ष से ₹1,000 से ₹5,000 तक तय मासिक पेंशन','60 வயதிலிருந்து மாதம் ₹1,000 முதல் ₹5,000 வரை உறுதியான ஓய்வூதியம்'),
 L('A pension for workers in the unorganised sector. You save a small fixed amount every month (depending on your age and the pension you choose) and get the pension for life from age 60.',
   'असंगठित क्षेत्र के कामगारों के लिए पेंशन। आप उम्र और चुनी हुई पेंशन के अनुसार हर महीने थोड़ी तय राशि बचाते हैं और 60 वर्ष से जीवन भर पेंशन पाते हैं।',
   'அமைப்புசாராத் துறைத் தொழிலாளர்களுக்கான ஓய்வூதியம். உங்கள் வயது மற்றும் தேர்ந்தெடுத்த ஓய்வூதியத்துக்கேற்ப மாதம் சிறிய நிலையான தொகையைச் சேமித்தால் 60 வயதிலிருந்து வாழ்நாள் முழுவதும் ஓய்வூதியம் கிடைக்கும்.'),
 [age_between(18,40)], ['aadhaar','bank'], ['bankv','kyc','ren'], 'https://jansuraksha.gov.in')

add('pmjay', ALL,
 L('Ayushman Bharat PM-JAY','आयुष्मान भारत पीएम-जय','ஆயுஷ்மான் பாரத் பிஎம்-ஜே'),
 L('Free hospital treatment up to ₹5 lakh per family a year','प्रति परिवार प्रति वर्ष ₹5 लाख तक अस्पताल में निःशुल्क इलाज','குடும்பத்துக்கு ஆண்டுக்கு ₹5 லட்சம் வரை இலவச மருத்துவமனைச் சிகிச்சை'),
 L('Covers hospital treatment, surgery and medicines at government and listed private hospitals. Families are included based on deprivation and occupation criteria, so check your name on the portal or at a CSC.',
   'सरकारी और सूचीबद्ध निजी अस्पतालों में इलाज, सर्जरी और दवाइयों का खर्च उठाती है। परिवार अभाव और व्यवसाय के मापदंडों के आधार पर शामिल होते हैं, इसलिए पोर्टल या सीएससी पर अपना नाम जाँचें।',
   'அரசு மற்றும் பட்டியலிடப்பட்ட தனியார் மருத்துவமனைகளில் சிகிச்சை, அறுவை சிகிச்சை, மருந்துகளுக்கான செலவை ஏற்கும். குடும்பங்கள் வறுமை மற்றும் தொழில் அளவுகோல்களின்படி சேர்க்கப்படுவதால் இணையதளம் அல்லது CSC-யில் உங்கள் பெயரைச் சரிபாருங்கள்.'),
 [eq('bpl','yes',L('Poor or deprived family (listed under Ayushman Bharat)','गरीब या वंचित परिवार (आयुष्मान भारत में सूचीबद्ध)','ஏழை அல்லது வறிய குடும்பம் (ஆயுஷ்மான் பாரத் பட்டியலில்)'))],
 ['aadhaar','bplc'], ['csc','kyc','hosp'], 'https://pmjay.gov.in')

add('pmayg', ['f','w','t','d','o'],
 L('PM Awas Yojana (housing)','पीएम आवास योजना','பிஎம் ஆவாஸ் திட்டம்'),
 L('Money to build or buy a pucca house (₹1.2 lakh in plains rural areas)','पक्का घर बनाने या खरीदने के लिए सहायता (मैदानी ग्रामीण क्षेत्र में ₹1.2 लाख)','பக்கா வீடு கட்ட அல்லது வாங்க உதவி (சமவெளி கிராமப்புறத்தில் ₹1.2 லட்சம்)'),
 L('Rural (Gramin) and urban versions help homeless families and those living in kutcha or one-room houses. Rural beneficiaries are listed by the Gram Sabha; urban applicants apply online or through the municipality, and some get an interest subsidy on a home loan.',
   'ग्रामीण और शहरी रूप बेघर परिवारों और कच्चे या एक कमरे के घरों में रहने वालों की मदद करते हैं। ग्रामीण लाभार्थियों की सूची ग्राम सभा बनाती है; शहरी आवेदक ऑनलाइन या नगर निकाय से आवेदन करते हैं और कुछ को गृह ऋण पर ब्याज सब्सिडी मिलती है।',
   'கிராமப்புற (கிராமின்) மற்றும் நகர்ப்புற வடிவங்கள் வீடற்ற குடும்பங்களுக்கும் குடிசை அல்லது ஒரு அறை வீட்டில் வசிப்போருக்கும் உதவுகின்றன. கிராமப்புறப் பயனாளிகளைக் கிராம சபை பட்டியலிடும்; நகர்ப்புற விண்ணப்பதாரர்கள் இணையத்தில் அல்லது நகராட்சி மூலம் விண்ணப்பிப்பர்; சிலருக்கு வீட்டுக் கடனில் வட்டி மானியம் கிடைக்கும்.'),
 [eq('home','no',L('Does not own a pucca house','पक्का घर नहीं है','பக்கா வீடு இல்லை'))],
 ['aadhaar','bank','bplc','address','photo'], ['panch','form','ver','trk'], 'https://pmayg.nic.in')

add('nfsa', ['f','w','y','t','d','o','x'],
 L('Ration card (free food grain under NFSA)','राशन कार्ड (एनएफएसए के तहत निःशुल्क अनाज)','குடும்ப அட்டை (NFSA கீழ் இலவச தானியம்)'),
 L('5 kg free grain per person every month (35 kg per family for the poorest)','हर माह प्रति व्यक्ति 5 किलो निःशुल्क अनाज (सबसे गरीब परिवारों को 35 किलो)','மாதம் ஒருவருக்கு 5 கிலோ இலவச தானியம் (மிக ஏழைக் குடும்பத்துக்கு 35 கிலோ)'),
 L('Under the National Food Security Act, priority and Antyodaya households get rice or wheat free through the ration shop. Apply for a ration card at your state food department, Panchayat or CSC.',
   'राष्ट्रीय खाद्य सुरक्षा अधिनियम के तहत प्राथमिकता और अंत्योदय परिवारों को राशन दुकान से चावल या गेहूँ निःशुल्क मिलता है। अपने राज्य के खाद्य विभाग, पंचायत या सीएससी में राशन कार्ड के लिए आवेदन करें।',
   'தேசிய உணவுப் பாதுகாப்புச் சட்டத்தின் கீழ் முன்னுரிமை மற்றும் அந்த்யோதயா குடும்பங்களுக்கு நியாய விலைக் கடை மூலம் அரிசி அல்லது கோதுமை இலவசமாகக் கிடைக்கும். உங்கள் மாநில உணவுத் துறை, ஊராட்சி அல்லது CSC-யில் குடும்ப அட்டைக்கு விண்ணப்பியுங்கள்.'),
 [eq('bpl','yes',BPL)], ['aadhaar','bplc','photo','address'], ['form','ver','collect'], 'https://nfsa.gov.in')

# ---------- write ----------
json.dump(schemes, open(os.path.join(ROOT,'data/schemes.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(vocab, open(os.path.join(ROOT,'data/vocab.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('schemes:', len(schemes))
from collections import Counter
c = Counter()
for s in schemes:
    for t in s.get('tracks', [s['track']]): c[t] += 1
print(dict(c))
