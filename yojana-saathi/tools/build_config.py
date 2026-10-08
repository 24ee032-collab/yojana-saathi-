# Builds data/fields.json and data/categories.json (run: python3 tools/build_config.py)
import json

YN = [["yes","Yes","हाँ","ஆம்"],["no","No","नहीं","இல்லை"]]
fields = {
 "age":    {"type":"num","max":110},
 "income": {"type":"num"},
 "land":   {"type":"num"},
 "dis":    {"type":"num","max":100},
 "gender": {"type":"choice","options":[
    ["female","Female","महिला","பெண்"],["male","Male","पुरुष","ஆண்"],["other","Other","अन्य","மற்றவர்"]]},
 "cat": {"type":"choice","options":[
    ["General","General","सामान्य","பொது"],
    ["OBC","OBC (incl. BC / MBC)","ओबीसी","பிற்படுத்தப்பட்டோர் (OBC / BC / MBC)"],
    ["SC","SC","अनुसूचित जाति","பட்டியல் இனத்தவர் (SC)"],
    ["ST","ST","अनुसूचित जनजाति","பழங்குடியினர் (ST)"]]},
 "occ": {"type":"choice","pick":["vendor","artisan","business","unemp"],"options":[
    ["vendor","Street vendor","रेहड़ी-पटरी वाला","தெருவோர வியாபாரி"],
    ["artisan","Artisan / craftsperson","कारीगर","கைவினைஞர்"],
    ["business","Business owner / startup founder","व्यवसायी / स्टार्टअप संस्थापक","தொழில் உரிமையாளர் / ஸ்டார்ட்அப் நிறுவனர்"],
    ["unemp","Want to start a business","व्यवसाय शुरू करना चाहते हैं","தொழில் தொடங்க விரும்புகிறேன்"],
    ["farmer","Farmer","किसान","விவசாயி"],["student","Student","विद्यार्थी","மாணவர்"],
    ["labour","Daily wage worker","मज़दूर","தினக்கூலித் தொழிலாளி"],
    ["salaried","Salaried job","नौकरी","சம்பளப் பணி"],["other","Other","अन्य","மற்றவை"]]},
 "course": {"type":"choice","when":{"field":"stage","ne":"school"},"options":[
    ["tech","Technical (engineering, diploma, pharmacy)","तकनीकी (इंजीनियरिंग, डिप्लोमा, फार्मेसी)","தொழில்நுட்பம் (பொறியியல், டிப்ளமோ, மருந்தியல்)"],
    ["other","Other (BA, BSc, BCom, etc.)","अन्य (बीए, बीएससी, बीकॉम आदि)","மற்றவை (பி.ஏ., பி.எஸ்சி., பி.காம். போன்றவை)"]]},
 "stage": {"type":"choice","options":[
    ["school","School (Class 9 to 12)","स्कूल (कक्षा 9 से 12)","பள்ளி (9 முதல் 12 ஆம் வகுப்பு)"],
    ["ug","College: degree or diploma","कॉलेज: डिग्री या डिप्लोमा","கல்லூரி: பட்டம் அல்லது டிப்ளமோ"],
    ["pg","Postgraduate or research","स्नातकोत्तर या शोध","முதுகலை அல்லது ஆராய்ச்சி"]]},
 "edu": {"type":"choice","options":[
    ["below10","Below Class 10","10वीं से कम","10 ஆம் வகுப்புக்குக் கீழ்"],
    ["10th","Class 10 passed","10वीं पास","10 ஆம் வகுப்பு தேர்ச்சி"],
    ["12th","Class 12 passed","12वीं पास","12 ஆம் வகுப்பு தேர்ச்சி"],
    ["grad","Graduate or diploma","स्नातक या डिप्लोमा","பட்டதாரி அல்லது டிப்ளமோ"],
    ["pg","Postgraduate","स्नातकोत्तर","முதுகலை"]]},
 "bpl": {"type":"choice","options":YN},
 "home":{"type":"choice","options":YN},
 "tgid":{"type":"choice","options":YN},
 "pension":{"type":"choice","options":YN},
 "ward":{"type":"choice","options":YN},
 "medal":{"type":"choice","options":YN},
 "udid":{"type":"choice","options":YN},
 "svc": {"type":"choice","options":[
    ["jco","JCO / other ranks (soldier, sailor, airman)","जेसीओ / अन्य रैंक (सिपाही, नाविक, वायुसैनिक)","ஜேசிஓ / மற்ற நிலைகள் (சிப்பாய், மாலுமி, விமானப்படை வீரர்)"],
    ["off","Commissioned officer","कमीशन प्राप्त अधिकारी","ஆணையிடப்பட்ட அதிகாரி"]]},
 "level": {"type":"choice","options":[
    ["dist","District, school or university","जिला, स्कूल या विश्वविद्यालय","மாவட்டம், பள்ளி அல்லது பல்கலைக்கழகம்"],
    ["state","State level","राज्य स्तर","மாநில அளவு"],
    ["nat","National level","राष्ट्रीय स्तर","தேசிய அளவு"],
    ["intl","International level","अंतरराष्ट्रीय स्तर","சர்வதேச அளவு"]]}
}
# track is the category itself
cats = [
 {"id":"f","icon":"farmer","color":"#2F7D32","fields":["age","gender","cat","income","land"],
  "name":["Farmer","किसान","விவசாயி"],
  "desc":["Income support, crop insurance, loans and irrigation","आय सहायता, फसल बीमा, ऋण और सिंचाई","வருமான ஆதரவு, பயிர்க் காப்பீடு, கடன், நீர்ப்பாசனம்"]},
 {"id":"s","icon":"student","color":"#26307B","fields":["age","gender","cat","income","stage","course"],
  "name":["Students","विद्यार्थी","மாணவர்கள்"],
  "desc":["Scholarships, fee support and education loans","छात्रवृत्ति, फीस सहायता और शिक्षा ऋण","உதவித்தொகை, கட்டண உதவி, கல்விக் கடன்"]},
 {"id":"w","icon":"widow","color":"#8E3B7A","fields":["age","cat","income","bpl","home"],
  "name":["Widows","विधवाएँ","விதவைகள்"],
  "desc":["Widow pension, family benefit, housing and livelihood","विधवा पेंशन, पारिवारिक लाभ, आवास और आजीविका","விதவை ஓய்வூதியம், குடும்ப நலன், வீடு, வாழ்வாதாரம்"]},
 {"id":"y","icon":"youth","color":"#C2571A","fields":["age","gender","cat","income","edu"],
  "name":["Unemployed youth","बेरोज़गार युवा","வேலையில்லா இளைஞர்கள்"],
  "desc":["Skill training, internships, apprenticeships and job incentives","कौशल प्रशिक्षण, इंटर्नशिप, अप्रेंटिसशिप और रोज़गार प्रोत्साहन","திறன் பயிற்சி, பயிற்சிப் பணி, வேலை ஊக்கத்தொகை"]},
 {"id":"t","icon":"trans","color":"#1B8A9A","fields":["age","edu","cat","income","tgid","bpl","home"],
  "name":["Transgender persons","ट्रांसजेंडर व्यक्ति","திருநங்கையர் / மூன்றாம் பாலினத்தவர்"],
  "desc":["Identity certificate, shelter, scholarship, health and livelihood","पहचान प्रमाणपत्र, आश्रय, छात्रवृत्ति, स्वास्थ्य और आजीविका","அடையாளச் சான்று, தங்குமிடம், உதவித்தொகை, சுகாதாரம், வாழ்வாதாரம்"]},
 {"id":"e","icon":"business","color":"#B8860B","fields":["occ","age","gender","cat","income"],
  "name":["Entrepreneurs","उद्यमी","தொழில்முனைவோர்"],
  "desc":["Business loans, subsidies, registration and startup funds","व्यवसाय ऋण, सब्सिडी, पंजीकरण और स्टार्टअप फंड","தொழில் கடன், மானியம், பதிவு, ஸ்டார்ட்அப் நிதி"]},
 {"id":"x","icon":"soldier","color":"#4B5320","fields":["age","svc","pension","income","ward"],
  "name":["Ex-servicemen","पूर्व सैनिक","முன்னாள் படைவீரர்கள்"],
  "desc":["Health care, pension help, resettlement and wards' scholarships","स्वास्थ्य सेवा, पेंशन सहायता, पुनर्वास और बच्चों की छात्रवृत्ति","மருத்துவம், ஓய்வூதிய உதவி, மறுவாழ்வு, பிள்ளைகளின் உதவித்தொகை"]},
 {"id":"p","icon":"sport","color":"#D2402B","fields":["age","gender","cat","income","level","medal"],
  "name":["Sports persons","खिलाड़ी","விளையாட்டு வீரர்கள்"],
  "desc":["Scholarships, elite funding, pension and sports quota","छात्रवृत्ति, उत्कृष्ट खिलाड़ी निधि, पेंशन और खेल कोटा","உதவித்தொகை, சிறந்த வீரர் நிதி, ஓய்வூதியம், விளையாட்டு ஒதுக்கீடு"]},
 {"id":"d","icon":"access","color":"#0B6E99","fields":["age","gender","cat","income","edu","dis","udid","bpl"],
  "name":["Persons with disabilities","दिव्यांगजन","மாற்றுத்திறனாளிகள்"],
  "desc":["UDID card, pension, free aids, scholarships and loans","यूडीआईडी कार्ड, पेंशन, निःशुल्क उपकरण, छात्रवृत्ति और ऋण","UDID அட்டை, ஓய்வூதியம், இலவச உபகரணங்கள், உதவித்தொகை, கடன்"]},
 {"id":"o","icon":"senior","color":"#6D4C41","fields":["age","gender","cat","income","bpl","home"],
  "name":["Senior citizens","वरिष्ठ नागरिक","மூத்த குடிமக்கள்"],
  "desc":["Old-age pension, free health cover, savings and aids","वृद्धावस्था पेंशन, निःशुल्क स्वास्थ्य बीमा, बचत और उपकरण","முதியோர் ஓய்வூதியம், இலவச மருத்துவக் காப்பீடு, சேமிப்பு, உபகரணங்கள்"]},
]
json.dump(fields, open('data/fields.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(cats, open('data/categories.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', len(fields), len(cats))
