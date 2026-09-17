import sys

file_path = r'e:\Brainstrom\Religions\Islam\rag_engine.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_modules_code = """
# ----------------- Phase 2 Expansion: In-Memory Data Modules -----------------

# Module 1: Prophetic Medicine & Modern Bioethics (PROPHETIC_MEDICINE_DATA)
PROPHETIC_MEDICINE_DATA = [
    {
        "id": 1,
        "name_ar": "حبة البركة",
        "name_th": "ฮับบะตุสเสาดาอ์ (Nigella sativa / Black Seed)",
        "name_en": "Black Seed",
        "category": "herb",
        "prophetic_reference": "ท่านนบีกล่าวว่า 'ในฮับบะตุสเสาดาอ์นั้น มีการเยียวยาสำหรับทุกโรค ยกเว้นความตาย'",
        "hadith_source": "Sahih al-Bukhari 5688",
        "modern_evidence": "งานวิจัยพบสาร Thymoquinone มีฤทธิ์ต้านอนุมูลอิสระ ต้านการอักเสบ และเสริมภูมิคุ้มกัน",
        "evidence_level": "strong_evidence",
        "health_benefits": "บรรเทาอาการหอบหืด ภูมิแพ้ ลดความดันโลหิต และช่วยควบคุมน้ำตาลในเลือด",
        "cautions": "สตรีมีครรภ์ควรระวังการใช้ในปริมาณที่มากเกินไป",
        "bioethics_note": ""
    },
    {
        "id": 2,
        "name_ar": "عسل",
        "name_th": "น้ำผึ้ง (Honey)",
        "name_en": "Honey",
        "category": "food",
        "prophetic_reference": "และมีเครื่องดื่มที่มีสีสันแตกต่างกันออกมาจากท้องของมัน ซึ่งในนั้นมีการบำบัดโรคสำหรับมนุษย์ (อัลกุรอาน 16:69)",
        "hadith_source": "Quran 16:69, Sahih al-Bukhari",
        "modern_evidence": "มีฤทธิ์ต้านเชื้อแบคทีเรีย ช่วยสมานแผล และบรรเทาอาการไอ",
        "evidence_level": "strong_evidence",
        "health_benefits": "ช่วยบำรุงกำลัง แก้อาการเจ็บคอ และใช้ทาแผลไฟไหม้",
        "cautions": "ห้ามให้เด็กทารกอายุต่ำกว่า 1 ปีบริโภค เนื่องจากเสี่ยงต่อโรคโบทูลิซึม",
        "bioethics_note": ""
    },
    {
        "id": 3,
        "name_ar": "حجامة",
        "name_th": "ฮิญามะฮ์ (Hijama / Cupping)",
        "name_en": "Cupping Therapy",
        "category": "practice",
        "prophetic_reference": "การเยียวยาที่ดีที่สุดที่พวกท่านใช้คือ ฮิญามะฮ์",
        "hadith_source": "Sahih al-Bukhari 5696",
        "modern_evidence": "ช่วยลดอาการปวดกล้ามเนื้อเรื้อรัง และกระตุ้นการไหลเวียนของโลหิตเฉพาะจุด",
        "evidence_level": "moderate_evidence",
        "health_benefits": "บรรเทาอาการปวดหลัง คอ บ่า ไหล่ และปวดศีรษะไมเกรน",
        "cautions": "ผู้ที่มีภาวะเลือดออกง่าย โลหิตจาง หรือหญิงตั้งครรภ์ควรหลีกเลี่ยง",
        "bioethics_note": ""
    },
    {
        "id": 4,
        "name_ar": "عجوة",
        "name_th": "อินทผลัม (Dates / Ajwa)",
        "name_en": "Ajwa Dates",
        "category": "food",
        "prophetic_reference": "ผู้ใดรับประทานอินทผลัมอัจวะฮ์ 7 เม็ดในตอนเช้า ในวันนั้นเขาจะปลอดภัยจากพิษและไสยศาสตร์",
        "hadith_source": "Sahih al-Bukhari 5445",
        "modern_evidence": "อุดมไปด้วยสารต้านอนุมูลอิสระ ไฟเบอร์ โพแทสเซียม และแมกนีเซียม",
        "evidence_level": "moderate_evidence",
        "health_benefits": "ให้พลังงานทันที ช่วยระบบขับถ่าย และบำรุงครรภ์",
        "cautions": "ผู้ป่วยเบาหวานควรควบคุมปริมาณการบริโภค",
        "bioethics_note": ""
    },
    {
        "id": 5,
        "name_ar": "أطفال الأنابيب",
        "name_th": "IVF เด็กหลอดแก้ว",
        "name_en": "In Vitro Fertilization (IVF)",
        "category": "bioethics",
        "prophetic_reference": "-",
        "hadith_source": "Islamic Fiqh Council",
        "modern_evidence": "เทคโนโลยีช่วยการเจริญพันธุ์สำหรับผู้มีบุตรยาก",
        "evidence_level": "bioethical_debate",
        "health_benefits": "ช่วยให้คู่สมรสที่มีบุตรยากสามารถตั้งครรภ์ได้",
        "cautions": "ต้องเป็นอสุจิและไข่ของสามีภรรยาที่ถูกต้องตามหลักศาสนาเท่านั้น",
        "bioethics_note": "อนุญาตให้ทำได้หากใช้เซลล์สืบพันธุ์ของสามีภรรยาที่สมรสถูกต้อง ห้ามการอุ้มบุญ หรือการบริจาคอสุจิ/ไข่จากบุคคลที่สาม"
    },
    {
        "id": 6,
        "name_ar": "القتل الرحيم",
        "name_th": "การุณยฆาต (Euthanasia)",
        "name_en": "Euthanasia",
        "category": "bioethics",
        "prophetic_reference": "ชีวิตเป็นกรรมสิทธิ์ของอัลลอฮ์",
        "hadith_source": "General Islamic Consensus",
        "modern_evidence": "ประเด็นข้อถกเถียงทางการแพทย์และจริยธรรมในผู้ป่วยระยะสุดท้าย",
        "evidence_level": "bioethical_debate",
        "health_benefits": "-",
        "cautions": "ผู้ประเมินต้องเป็นแพทย์ผู้เชี่ยวชาญหลายท่าน",
        "bioethics_note": "ไม่อนุญาตให้ทำการุณยฆาตแบบ Active (ฉีดยาให้เสียชีวิต) โดยเด็ดขาด ถือเป็นบาปใหญ่ แต่ในกรณีสมองตายหรือไม่มีความหวังในการรักษา อนุญาตให้ถอดเครื่องช่วยหายใจได้ (Passive) ปล่อยให้เสียชีวิตตามธรรมชาติ"
    }
]

def search_prophetic_medicine(query, category_filter=None):
    results = []
    q = query.lower()
    for item in PROPHETIC_MEDICINE_DATA:
        if category_filter and item["category"] != category_filter:
            continue
        if q in item["name_ar"].lower() or q in item["name_th"].lower() or q in item["name_en"].lower() or q in item["health_benefits"].lower():
            results.append(item)
    return results

def get_prophetic_medicine(medicine_id):
    for item in PROPHETIC_MEDICINE_DATA:
        if item["id"] == medicine_id:
            return item
    return None

# Module 2: Daily Adhkar (DAILY_ADHKAR_DATA)
DAILY_ADHKAR_DATA = [
    {
        "id": 1,
        "category": "morning",
        "title_th": "อัซการ์เช้า: สุบฮานัลลอฮิวะบิฮัมดิฮี",
        "arabic_text": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ",
        "transliteration": "Subhanallahi wa bihamdihi",
        "meaning_th": "มหาบริสุทธิ์ยิ่งแด่อัลลอฮ์ และการสรรเสริญเป็นของพระองค์",
        "source": "Sahih Muslim",
        "virtue": "ความผิดของเขาจะถูกลบล้าง แม้จะมากมายดั่งฟองน้ำในทะเล",
        "repeat_count": 100
    },
    {
        "id": 2,
        "category": "morning",
        "title_th": "อัซการ์เช้า: อายะตุลกุรซี",
        "arabic_text": "اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...",
        "transliteration": "Allahu la ilaha illa Huwa, Al-Haiyul-Qaiyum...",
        "meaning_th": "อัลลอฮ์นั้นคือไม่มีพระเจ้าอื่นใดนอกจากพระองค์ ผู้ทรงมีชีวิต ผู้ทรงบริหารกิจการทั้งหลาย...",
        "source": "Al-Baqarah 2:255, An-Nasa'i",
        "virtue": "จะได้รับการคุ้มครองจากอัลลอฮ์ และชัยฏอนจะไม่เข้าใกล้จนถึงเย็น",
        "repeat_count": 1
    },
    {
        "id": 3,
        "category": "evening",
        "title_th": "อัซการ์เย็น: ซัยยิดุลอิสติฆฟาร",
        "arabic_text": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ...",
        "transliteration": "Allahumma anta Rabbi la ilaha illa anta...",
        "meaning_th": "โอ้อัลลอฮ์ พระองค์คือพระเจ้าของข้าพระองค์ ไม่มีพระเจ้าอื่นใดนอกจากพระองค์...",
        "source": "Sahih al-Bukhari",
        "virtue": "สุดยอดของการขออภัยโทษ ผู้ใดอ่านด้วยความเชื่อมั่นแล้วเสียชีวิต เขาจะได้เข้าสวรรค์",
        "repeat_count": 1
    },
    {
        "id": 4,
        "category": "after_prayer",
        "title_th": "หลังละหมาด: สุบฮานัลลอฮ์ อัลฮัมดุลิลลาฮ์ อัลลอฮุอักบัร",
        "arabic_text": "سُبْحَانَ اللَّهِ، وَالْحَمْدُ لِلَّهِ، وَاللَّهُ أَكْبَرُ",
        "transliteration": "Subhanallah, Alhamdulillah, Allahu Akbar",
        "meaning_th": "มหาบริสุทธิ์ยิ่งแด่อัลลอฮ์, มวลการสรรเสริญเป็นของอัลลอฮ์, อัลลอฮ์ผู้ทรงยิ่งใหญ่",
        "source": "Sahih Muslim",
        "virtue": "บาปของเขาจะถูกอภัย แม้จะมากมายดั่งฟองน้ำในทะเล (เมื่ออ่านครบและปิดท้ายด้วยลาอิลาฮะฯ)",
        "repeat_count": 33
    },
    {
        "id": 5,
        "category": "sleep",
        "title_th": "ก่อนนอน: อายะตุลกุรซี",
        "arabic_text": "اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...",
        "transliteration": "Allahu la ilaha illa Huwa, Al-Haiyul-Qaiyum...",
        "meaning_th": "อัลลอฮ์นั้นคือไม่มีพระเจ้าอื่นใดนอกจากพระองค์...",
        "source": "Sahih al-Bukhari",
        "virtue": "จะมีมะลักมาคุ้มครอง และชัยฏอนจะไม่เข้าใกล้จนถึงเช้า",
        "repeat_count": 1
    },
    {
        "id": 6,
        "category": "distress",
        "title_th": "เมื่อเครียด: ดุอาอ์ขจัดความกังวล",
        "arabic_text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
        "transliteration": "Allahumma inni a'udhu bika minal-hammi wal-hazan",
        "meaning_th": "โอ้อัลลอฮ์ ข้าพระองค์ขอความคุ้มครองต่อพระองค์ให้พ้นจากความเครียดและความเศร้าหมอง",
        "source": "Sahih al-Bukhari",
        "virtue": "ช่วยให้จิตใจสงบและขจัดความกังวล",
        "repeat_count": 1
    },
    {
        "id": 7,
        "category": "distress",
        "title_th": "เมื่อเครียด: ลาเฮาละวะลากูวะตะ อิลลาบิลลาฮ์",
        "arabic_text": "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ",
        "transliteration": "La hawla wa la quwwata illa billah",
        "meaning_th": "ไม่มีอำนาจและพลังใดๆ เว้นแต่ด้วยความช่วยเหลือของอัลลอฮ์",
        "source": "Sahih al-Bukhari",
        "virtue": "เป็นหนึ่งในขุมทรัพย์แห่งสรวงสวรรค์ ช่วยให้ขจัดความยากลำบาก",
        "repeat_count": 1
    },
    {
        "id": 8,
        "category": "misc",
        "title_th": "ทั่วไป: ดุอาอ์อิสติคอเราะฮ์",
        "arabic_text": "اللَّهُمَّ إِنِّي أَسْتَخِيرُكَ بِعِلْمِكَ...",
        "transliteration": "Allahumma inni astakhiruka bi'ilmika...",
        "meaning_th": "โอ้อัลลอฮ์ ข้าพระองค์ขอการเลือกที่ดีจากพระองค์ด้วยความรู้ของพระองค์...",
        "source": "Sahih al-Bukhari",
        "virtue": "เพื่อขอการชี้นำจากอัลลอฮ์เมื่อต้องตัดสินใจในเรื่องสำคัญ",
        "repeat_count": 1
    }
]

def get_daily_adhkar(category=None):
    if category:
        return [item for item in DAILY_ADHKAR_DATA if item["category"] == category]
    return DAILY_ADHKAR_DATA

def search_daily_adhkar(query):
    results = []
    q = query.lower()
    for item in DAILY_ADHKAR_DATA:
        if q in item["title_th"].lower() or q in item["arabic_text"].lower() or q in item["transliteration"].lower() or q in item["meaning_th"].lower():
            results.append(item)
    return results

# Module 3: Quran Chronology (QURAN_CHRONOLOGY_DATA)
QURAN_CHRONOLOGY_DATA = [
    {
        "surah_number": 96,
        "name_ar": "العلق",
        "name_th": "อัล-อะลัก (ก้อนเลือด)",
        "name_en": "Al-Alaq",
        "revelation_order": 1,
        "revelation_type": "Makki",
        "period": "Makki Phase 1 (Early)",
        "ayah_count": 19,
        "key_theme": "การประทานวะฮีย์ครั้งแรก คำสั่งให้ 'อ่าน' และความสำคัญของความรู้"
    },
    {
        "surah_number": 68,
        "name_ar": "القلم",
        "name_th": "อัล-เกาะลัม (ปากกา)",
        "name_en": "Al-Qalam",
        "revelation_order": 2,
        "revelation_type": "Makki",
        "period": "Makki Phase 1 (Early)",
        "ayah_count": 52,
        "key_theme": "การปกป้องนบีมุฮัมมัดจากข้อกล่าวหา และชะตากรรมของผู้ปฏิเสธ"
    },
    {
        "surah_number": 73,
        "name_ar": "المزمل",
        "name_th": "อัล-มุซซัมมิล (ผู้ห่มกาย)",
        "name_en": "Al-Muzzammil",
        "revelation_order": 3,
        "revelation_type": "Makki",
        "period": "Makki Phase 1 (Early)",
        "ayah_count": 20,
        "key_theme": "การเตรียมตัวของนบีในการรับภาระหนักผ่านการละหมาดกิยามุลลัยล์"
    },
    {
        "surah_number": 1,
        "name_ar": "الفاتحة",
        "name_th": "อัล-ฟาติฮะฮ์ (ปฐมบท)",
        "name_en": "Al-Fatihah",
        "revelation_order": 5,
        "revelation_type": "Makki",
        "period": "Makki Phase 1 (Early)",
        "ayah_count": 7,
        "key_theme": "แก่นแท้ของคัมภีร์ การสรรเสริญอัลลอฮ์ และการขอทางนำที่เที่ยงตรง"
    },
    {
        "surah_number": 36,
        "name_ar": "يس",
        "name_th": "ยาซีน",
        "name_en": "Ya-Sin",
        "revelation_order": 41,
        "revelation_type": "Makki",
        "period": "Makki Phase 2 (Middle)",
        "ayah_count": 83,
        "key_theme": "หัวใจของอัลกุรอาน เน้นย้ำเรื่องเตาฮีด ศาสนทูต และการฟื้นคืนชีพ"
    },
    {
        "surah_number": 18,
        "name_ar": "الكهف",
        "name_th": "อัล-กะฮ์ฟิ (ถ้ำ)",
        "name_en": "Al-Kahf",
        "revelation_order": 69,
        "revelation_type": "Makki",
        "period": "Makki Phase 3 (Late)",
        "ayah_count": 110,
        "key_theme": "เรื่องราวชาวถ้ำ นบีมูซาและคิฎิร ซุลก็อรนัยน์ เพื่อเตรียมพร้อมรับมือกับฟิตนะฮ์"
    },
    {
        "surah_number": 2,
        "name_ar": "البقرة",
        "name_th": "อัล-บะเกาะเราะฮ์ (วัวตัวเมีย)",
        "name_en": "Al-Baqarah",
        "revelation_order": 87,
        "revelation_type": "Madani",
        "period": "Madani",
        "ayah_count": 286,
        "key_theme": "การวางรากฐานของสังคมมุสลิม กฎหมาย ครอบครัว และเศรษฐศาสตร์"
    },
    {
        "surah_number": 4,
        "name_ar": "النساء",
        "name_th": "อัน-นิซาอ์ (สตรี)",
        "name_en": "An-Nisa",
        "revelation_order": 92,
        "revelation_type": "Madani",
        "period": "Madani",
        "ayah_count": 176,
        "key_theme": "สิทธิสตรี กฎหมายครอบครัว มรดก และการดูแลเด็กกำพร้า"
    },
    {
        "surah_number": 5,
        "name_ar": "المائدة",
        "name_th": "อัล-มาอิดะฮ์ (สำรับอาหาร)",
        "name_en": "Al-Ma'idah",
        "revelation_order": 112,
        "revelation_type": "Madani",
        "period": "Madani",
        "ayah_count": 120,
        "key_theme": "กฎหมายอาหารฮาลาล การปกครอง ความสมบูรณ์ของศาสนา"
    },
    {
        "surah_number": 110,
        "name_ar": "النصر",
        "name_th": "อัน-นัศร์ (ความช่วยเหลือ)",
        "name_en": "An-Nasr",
        "revelation_order": 114,
        "revelation_type": "Madani",
        "period": "Madani",
        "ayah_count": 3,
        "key_theme": "ชัยชนะในการพิชิตมักกะฮ์ และสัญญาณแห่งวาระสุดท้ายของนบี"
    }
]

def get_quran_chronology():
    return sorted(QURAN_CHRONOLOGY_DATA, key=lambda x: x["revelation_order"])

def get_surah_chronology(surah_number):
    for item in QURAN_CHRONOLOGY_DATA:
        if item["surah_number"] == surah_number:
            return item
    return None

# Module 4: Tajweed Rules (TAJWEED_RULES_DATA)
TAJWEED_RULES_DATA = [
    {
        "id": 1,
        "rule_ar": "إدغام",
        "rule_th": "อิดฆอม (การผนวก)",
        "rule_en": "Idgham",
        "category": "noon_sakinah",
        "description_th": "เมื่อนูนตายหรือตันวีนพบกับอักษร 6 ตัว (ยามีลูน - ي ر م ل و ن) ให้อ่านผนวกเสียง แบ่งเป็นแบบมีหน่วงเสียง (บิฆุนนะฮ์) และไม่มีหน่วงเสียง (บิลาฆุนนะฮ์)",
        "arabic_example": "مَن يَقُولُ",
        "example_ref": "Al-Baqarah 2:8",
        "phonetic_guide": "อ่านว่า 'มัย-ยะกูลุ' (หน่วงเสียง 2 ฮะเราะกะฮ์)"
    },
    {
        "id": 2,
        "rule_ar": "إخفاء",
        "rule_th": "อิิค์ฟาอ์ (การซ่อนเสียง)",
        "rule_en": "Ikhfa",
        "category": "noon_sakinah",
        "description_th": "เมื่อนูนตายหรือตันวีนพบกับอักษร 15 ตัว ให้อ่านซ่อนเสียงนูน โดยหน่วงเสียง 2 ฮะเราะกะฮ์",
        "arabic_example": "مِن شَرِّ",
        "example_ref": "Al-Falaq 113:2",
        "phonetic_guide": "อ่านว่า 'มิง-ชัร-ริ' (ซ่อนเสียงนูนเป็นเสียงงอ-งูหรือคล้ายๆ กัน พร้อมหน่วงเสียง)"
    },
    {
        "id": 3,
        "rule_ar": "إقلاب",
        "rule_th": "อิกลาบ (การเปลี่ยนเสียง)",
        "rule_en": "Iqlab",
        "category": "noon_sakinah",
        "description_th": "เมื่อนูนตายหรือตันวีนพบกับตัว บาอ์ (ب) ให้เปลี่ยนเสียงนูนเป็นเสียงมีม (م) และหน่วงเสียง",
        "arabic_example": "مِن بَعْدِ",
        "example_ref": "Al-Baqarah 2:253",
        "phonetic_guide": "อ่านว่า 'มิม-บะอ์ดิ' (หน่วงเสียง 2 ฮะเราะกะฮ์)"
    },
    {
        "id": 4,
        "rule_ar": "إظهار",
        "rule_th": "อิซฮาร (การอ่านชัดเจน)",
        "rule_en": "Izhar",
        "category": "noon_sakinah",
        "description_th": "เมื่อนูนตายหรือตันวีนพบกับอักษรคอ 6 ตัว (ء ه ع ح غ خ) ให้อ่านออกเสียงนูนชัดเจน ไม่ต้องหน่วงเสียง",
        "arabic_example": "مِنْ خَوْفٍ",
        "example_ref": "Quraish 106:4",
        "phonetic_guide": "อ่านว่า 'มิน-เคาฟฺ' (ชัดเจน ไม่หน่วงเสียง)"
    },
    {
        "id": 5,
        "rule_ar": "قلقلة",
        "rule_th": "ก็อลเกาะละฮ์ (การสะท้อนเสียง)",
        "rule_en": "Qalqalah",
        "category": "qalqalah",
        "description_th": "เมื่ออักษร 5 ตัว (กุฏบุญจัด - ق ط ب ج د) มีสระสุกูน (ตาย) ให้อ่านสะท้อนเสียง",
        "arabic_example": "أَحَدٌ",
        "example_ref": "Al-Ikhlas 112:1",
        "phonetic_guide": "อ่านว่า 'อะฮัด-ดฺ' (สะท้อนเสียงตัวดาลตอนท้าย)"
    },
    {
        "id": 6,
        "rule_ar": "مد لازم",
        "rule_th": "มัดลาซิม (การลากเสียงยาวบังคับ)",
        "rule_en": "Madd Lazim",
        "category": "madd",
        "description_th": "เมื่ออักษรมัด (ا و ي) พบกับสุกูนแท้หรือชัดดะฮ์ (สระทับซ้อน) ในคำเดียวกัน บังคับให้อ่านยาว 6 ฮะเราะกะฮ์",
        "arabic_example": "الضَّالِّينَ",
        "example_ref": "Al-Fatihah 1:7",
        "phonetic_guide": "อ่านว่า 'อัฎ-ฎ้ออออออล-ลีน' (ลากเสียงยาว 6 ฮะเราะกะฮ์)"
    }
]

def get_tajweed_rules(category=None):
    if category:
        return [item for item in TAJWEED_RULES_DATA if item["category"] == category]
    return TAJWEED_RULES_DATA

def search_tajweed(query):
    results = []
    q = query.lower()
    for item in TAJWEED_RULES_DATA:
        if q in item["rule_ar"].lower() or q in item["rule_th"].lower() or q in item["rule_en"].lower() or q in item["description_th"].lower():
            results.append(item)
    return results

# Module 5: Islamic Contracts (ISLAMIC_CONTRACTS_DATA)
ISLAMIC_CONTRACTS_DATA = [
    {
        "id": 1,
        "name_ar": "مرابحة",
        "name_th": "มุรอบะฮะฮ์ (Murabahah)",
        "name_en": "Cost-Plus Financing",
        "contract_type": "sale",
        "mechanism_th": "สถาบันการเงินซื้อสินทรัพย์ตามที่ลูกค้าต้องการ แล้วนำมาขายต่อให้ลูกค้าโดยบวกกำไรที่ตกลงกันไว้ล่วงหน้า ลูกค้าผ่อนชำระเป็นงวดๆ",
        "sharia_basis": "อัลลอฮ์ทรงอนุมัติการค้าขาย แต่ทรงห้ามดอกเบี้ย (อัล-บะเกาะเราะฮ์ 2:275)",
        "conventional_equivalent": "สินเชื่อส่วนบุคคล/สินเชื่อรถยนต์ แบบคิดดอกเบี้ย",
        "key_difference": "ไม่ใช่การให้กู้เงิน แต่เป็นการซื้อมาขายไป (Sale Contract) กำไรคงที่และไม่มีการคิดดอกเบี้ยปรับเพิ่มเมื่อจ่ายล่าช้า",
        "risk_sharing": "ธนาคารรับความเสี่ยงในตัวทรัพย์สินก่อนที่จะขายและส่งมอบให้ลูกค้า",
        "example_th": "ธนาคารซื้อรถราคา 1 ล้านบาท และขายต่อให้ลูกค้าในราคา 1.2 ล้านบาท โดยให้ลูกค้าผ่อนชำระ 5 ปี"
    },
    {
        "id": 2,
        "name_ar": "مضاربة",
        "name_th": "มุฎอรอบะฮ์ (Mudarabah)",
        "name_en": "Profit-Sharing Partnership",
        "contract_type": "partnership",
        "mechanism_th": "ฝ่ายหนึ่งลงทุน (ร็อบบุลมาล) อีกฝ่ายหนึ่งลงแรง/บริหารจัดการ (มุฎอริบ) กำไรแบ่งตามสัดส่วนที่ตกลงกัน ขาดทุนทางการเงินผู้ลงทุนรับผิดชอบ",
        "sharia_basis": "ซุนนะฮ์ท่านนบีในการค้าขายให้กับท่านหญิงคอดีญะฮ์",
        "conventional_equivalent": "เงินฝากประจำ/กองทุนรวม",
        "key_difference": "ผลตอบแทนไม่คงที่ ขึ้นอยู่กับผลกำไรจริง หากขาดทุน ผู้ฝากเงินจะสูญเสียเงินต้น (ยกเว้นผู้บริหารประมาทเลินเล่อ)",
        "risk_sharing": "ผู้ลงทุนรับความเสี่ยงทางการเงิน ผู้บริหารรับความเสี่ยงด้านแรงงานและเวลาที่เสียไป",
        "example_th": "ลูกค้าฝากเงินกับธนาคาร ธนาคารนำไปลงทุนทางธุรกิจ กำไรแบ่งกัน 60:40 หากขาดทุนลูกค้าเสียเงินต้น"
    },
    {
        "id": 3,
        "name_ar": "مشاركة",
        "name_th": "มุชาเราะกะฮ์ (Musharakah)",
        "name_en": "Joint Venture",
        "contract_type": "partnership",
        "mechanism_th": "หุ้นส่วนตั้งแต่สองฝ่ายขึ้นไปนำทุนมารวมกันเพื่อทำธุรกิจ กำไรแบ่งตามสัดส่วนที่ตกลงกัน ขาดทุนแบ่งตามสัดส่วนของทุน",
        "sharia_basis": "การกระทำของบรรดาซอฮาบะฮ์ในการร่วมทุน",
        "conventional_equivalent": "สินเชื่อธุรกิจ/สินเชื่อบ้านแบบลดต้นลดดอก",
        "key_difference": "เป็นการร่วมลงทุน ธนาคารและลูกค้าเป็นหุ้นส่วนกัน ในกรณีสินเชื่อบ้าน (Diminishing Musharakah) ลูกค้าค่อยๆ ซื้อหุ้นของธนาคารจนครบ",
        "risk_sharing": "ทุกฝ่ายรับความเสี่ยงทางการเงินร่วมกันตามสัดส่วนทุน",
        "example_th": "ธนาคารและลูกค้าร่วมทุนซื้อบ้าน (ธนาคาร 80% ลูกค้า 20%) ลูกค้าจ่ายค่าเช่าในส่วนของธนาคารและทยอยซื้อหุ้นคืนจนครบ 100%"
    },
    {
        "id": 4,
        "name_ar": "إجارة",
        "name_th": "อิญาเราะฮ์ (Ijarah)",
        "name_en": "Leasing",
        "contract_type": "lease",
        "mechanism_th": "การให้เช่าทรัพย์สิน โดยโอนสิทธิการใช้ประโยชน์ในทรัพย์สินตามระยะเวลาที่กำหนด แลกกับค่าเช่า",
        "sharia_basis": "อัลกุรอาน 28:26 เรื่องการจ้างงาน",
        "conventional_equivalent": "Financial Lease / เช่าซื้อ",
        "key_difference": "กรรมสิทธิ์ในทรัพย์สินยังคงเป็นของผู้ให้เช่า ผู้ให้เช่าต้องรับผิดชอบความเสียหายหลักที่ไม่ได้เกิดจากความประมาทของผู้เช่า",
        "risk_sharing": "ผู้ให้เช่ารับความเสี่ยงต่อทรัพย์สิน",
        "example_th": "สัญญาเช่าซื้อเครื่องจักร ธนาคารซื้อเครื่องจักรและให้ลูกค้าเช่าใช้ โดยอาจมีข้อตกลงโอนกรรมสิทธิ์เมื่อสิ้นสุดสัญญา (Ijarah Muntahia Bittamleek)"
    },
    {
        "id": 5,
        "name_ar": "صكوك",
        "name_th": "ศุกูก (Sukuk)",
        "name_en": "Islamic Bonds",
        "contract_type": "investment",
        "mechanism_th": "เอกสารรับรองความเป็นเจ้าของในสัดส่วนที่เท่ากันในทรัพย์สินอ้างอิง ผลตอบแทนมาจากรายได้หรือค่าเช่าของทรัพย์สินนั้น",
        "sharia_basis": "หลักการของสัญญาต่างๆ เช่น อิญาเราะฮ์, มุชาเราะกะฮ์",
        "conventional_equivalent": "พันธบัตรรัฐบาล/หุ้นกู้บริษัท",
        "key_difference": "ไม่ใช่ตราสารหนี้ แต่เป็นตราสารทุนที่อิงกับสินทรัพย์ที่มีอยู่จริง (Asset-backed/Asset-based) ห้ามรับประกันเงินต้น",
        "risk_sharing": "ผู้ถือศุกูกรับความเสี่ยงของสินทรัพย์อ้างอิง",
        "example_th": "รัฐบาลออกศุกูกเพื่อสร้างโรงไฟฟ้า ผู้ซื้อศุกูกเป็นเจ้าของร่วมในโรงไฟฟ้า และได้รับผลตอบแทนจากรายได้ของโรงไฟฟ้า"
    },
    {
        "id": 6,
        "name_ar": "تكافل",
        "name_th": "ตะกาฟุล (Takaful)",
        "name_en": "Islamic Insurance",
        "contract_type": "insurance",
        "mechanism_th": "การประกันภัยร่วมกัน สมาชิกบริจาคเงิน (Tabarru) เข้ากองทุนส่วนกลาง เพื่อช่วยเหลือสมาชิกที่ประสบภัย",
        "sharia_basis": "หลักการร่วมมือกันและความช่วยเหลือเกื้อกูล (อัล-มาอิดะฮ์ 5:2)",
        "conventional_equivalent": "ประกันชีวิต/ประกันวินาศภัยแบบทั่วไป",
        "key_difference": "ไม่มีการพนัน (Maysir) ไม่มีความไม่แน่นอน (Gharar) และไม่มีดอกเบี้ย (Riba) เงินกองทุนถูกนำไปลงทุนในธุรกิจฮาลาล",
        "risk_sharing": "สมาชิกทุกคนรับความเสี่ยงร่วมกัน (Risk Sharing) ไม่ใช่การโอนความเสี่ยงไปยังบริษัทประกัน",
        "example_th": "ลูกค้าจ่ายเงินสมทบเข้ากองทุนตะกาฟุลรถยนต์ หากมีอุบัติเหตุ เงินจากกองทุนกลางจะถูกนำมาจ่ายค่าสินไหมทดแทน เงินที่เหลือตอนสิ้นปีจะนำมาแบ่งคืนสมาชิก"
    }
]

def get_islamic_contracts(contract_type=None):
    if contract_type:
        return [item for item in ISLAMIC_CONTRACTS_DATA if item["contract_type"] == contract_type]
    return ISLAMIC_CONTRACTS_DATA

def calculate_murabahah(principal, profit_rate, tenure_months):
    total_profit = principal * profit_rate
    total_price = principal + total_profit
    monthly_payment = total_price / tenure_months
    
    # Conventional comparison
    r = profit_rate / 12
    if r > 0:
        conv_monthly = principal * (r * (1 + r)**tenure_months) / ((1 + r)**tenure_months - 1)
    else:
        conv_monthly = principal / tenure_months
    conv_total = conv_monthly * tenure_months
    
    return {
        "principal": principal,
        "profit_rate": profit_rate,
        "tenure_months": tenure_months,
        "total_profit": total_profit,
        "total_price": total_price,
        "monthly_payment": monthly_payment,
        "conventional_comparison": {
            "total_interest": conv_total - principal,
            "total_price": conv_total,
            "monthly_payment": conv_monthly
        }
    }

# Module 6: History Timeline (HISTORY_TIMELINE_DATA)
HISTORY_TIMELINE_DATA = [
    {
        "id": 1,
        "era_name_th": "ยุคท่านนบี (Prophetic Era)",
        "era_name_en": "Prophetic Era",
        "era_name_ar": "العصر النبوي",
        "start_year_ce": 610,
        "end_year_ce": 632,
        "key_events": [
            {"year_ce": 610, "event_th": "รับวะฮีย์ครั้งแรกที่ถ้ำฮิรออ์", "event_en": "First Revelation at Cave Hira"},
            {"year_ce": 622, "event_th": "ฮิจเราะฮ์ (อพยพ) สู่นครมะดีนะฮ์", "event_en": "Hijrah to Madinah"},
            {"year_ce": 630, "event_th": "พิชิตมักกะฮ์", "event_en": "Conquest of Makkah"}
        ],
        "significance_th": "จุดเริ่มต้นของศาสนาอิสลาม การประทานอัลกุรอาน และการสร้างรัฐอิสลามแห่งแรก",
        "notable_figures": ["นบีมุฮัมมัด (ศ็อลฯ)", "ท่านหญิงคอดีญะฮ์", "อบูบักรฺ อัศศิดดีก"]
    },
    {
        "id": 2,
        "era_name_th": "คอลีฟะฮ์ราชิดูน (Rashidun)",
        "era_name_en": "Rashidun Caliphate",
        "era_name_ar": "الخلافة الراشدة",
        "start_year_ce": 632,
        "end_year_ce": 661,
        "key_events": [
            {"year_ce": 632, "event_th": "อบูบักรฺขึ้นเป็นคอลีฟะฮ์ท่านแรก", "event_en": "Abu Bakr becomes first Caliph"},
            {"year_ce": 637, "event_th": "พิชิตเยรูซาเล็มในสมัยอุมัร", "event_en": "Conquest of Jerusalem"},
            {"year_ce": 653, "event_th": "รวบรวมคัมภีร์อัลกุรอานฉบับมาตรฐานในสมัยอุษมาน", "event_en": "Standardization of Quran by Uthman"}
        ],
        "significance_th": "ยุคของผู้นำที่ทรงธรรมทั้ง 4 การขยายอาณาเขตอย่างรวดเร็ว และการรวบรวมอัลกุรอานเป็นรูปเล่ม",
        "notable_figures": ["อบูบักรฺ", "อุมัร", "อุษมาน", "อะลี"]
    },
    {
        "id": 3,
        "era_name_th": "ราชวงศ์อุมัยยะฮ์ (Umayyad)",
        "era_name_en": "Umayyad Caliphate",
        "era_name_ar": "الدولة الأموية",
        "start_year_ce": 661,
        "end_year_ce": 750,
        "key_events": [
            {"year_ce": 661, "event_th": "สถาปนาราชวงศ์โดยมุอาวิยะฮ์", "event_en": "Establishment by Mu'awiyah"},
            {"year_ce": 711, "event_th": "ตอริก บิน ซิยาด พิชิตสเปน", "event_en": "Conquest of Hispania by Tariq bin Ziyad"}
        ],
        "significance_th": "อาณาจักรอิสลามที่ใหญ่ที่สุดในประวัติศาสตร์ ครอบคลุมตั้งแต่สเปนถึงอินเดีย มีดามัสกัสเป็นเมืองหลวง",
        "notable_figures": ["มุอาวิยะฮ์", "อับดุลมาลิก บิน มัรวาน", "อุมัร บิน อับดุลอะซีซ", "ตอริก บิน ซิยาด"]
    },
    {
        "id": 4,
        "era_name_th": "ราชวงศ์อับบาสียะฮ์ (Abbasid Golden Age)",
        "era_name_en": "Abbasid Caliphate",
        "era_name_ar": "الدولة العباسية",
        "start_year_ce": 750,
        "end_year_ce": 1258,
        "key_events": [
            {"year_ce": 762, "event_th": "สร้างกรุงแบกแดดเป็นเมืองหลวง", "event_en": "Foundation of Baghdad"},
            {"year_ce": 832, "event_th": "ก่อตั้ง 'บัยตุลฮิกมะฮ์' (House of Wisdom)", "event_en": "Establishment of House of Wisdom"},
            {"year_ce": 1258, "event_th": "มองโกลทำลายกรุงแบกแดด", "event_en": "Mongol sack of Baghdad"}
        ],
        "significance_th": "ยุคทองของอารยธรรมอิสลาม ความรุ่งเรืองทางวิทยาศาสตร์ ปรัชญา คณิตศาสตร์ และการแพทย์",
        "notable_figures": ["ฮารูน อัร-เราะชีด", "อัล-คอวาริซมี (นักคณิตศาสตร์)", "อิบนุ ซีนา (Avicenna)"]
    },
    {
        "id": 5,
        "era_name_th": "อันดาลุส (Al-Andalus)",
        "era_name_en": "Al-Andalus",
        "era_name_ar": "الأندلس",
        "start_year_ce": 711,
        "end_year_ce": 1492,
        "key_events": [
            {"year_ce": 756, "event_th": "ก่อตั้งเอมิเรตคอร์โดบา", "event_en": "Emirate of Cordoba established"},
            {"year_ce": 1492, "event_th": "กรานาดาแตก สิ้นสุดการปกครองของมุสลิมในสเปน", "event_en": "Fall of Granada"}
        ],
        "significance_th": "ศูนย์กลางการเรียนรู้ในยุโรป การอยู่ร่วมกันของชาวมุสลิม คริสเตียน และยิว นำแสงสว่างสู่ยุโรปยุคมืด",
        "notable_figures": ["อับดุรเราะฮ์มานที่ 3", "อิบนุ รุชด์ (Averroes)", "อิบนุ ฮัซมฺ"]
    },
    {
        "id": 6,
        "era_name_th": "สุลต่านมัมลูก (Mamluk)",
        "era_name_en": "Mamluk Sultanate",
        "era_name_ar": "سلطنة المماليك",
        "start_year_ce": 1250,
        "end_year_ce": 1517,
        "key_events": [
            {"year_ce": 1260, "event_th": "สงคราม อัยน์ ญาลูต หยุดยั้งทัพมองโกล", "event_en": "Battle of Ain Jalut"},
            {"year_ce": 1291, "event_th": "ขับไล่ครูเสดออกจากตะวันออกกลาง", "event_en": "End of Crusader states"}
        ],
        "significance_th": "ผู้ปกป้องโลกอิสลามจากมองโกลและครูเสด มีอียิปต์เป็นศูนย์กลางแห่งใหม่ของโลกอิสลาม",
        "notable_figures": ["สุลต่านซัยฟุดดีน กุตุซ", "บัยบาร์ส", "อิบนุ ตัยมียะฮ์"]
    },
    {
        "id": 7,
        "era_name_th": "จักรวรรดิออตโตมัน (Ottoman)",
        "era_name_en": "Ottoman Empire",
        "era_name_ar": "الدولة العثمانية",
        "start_year_ce": 1299,
        "end_year_ce": 1924,
        "key_events": [
            {"year_ce": 1453, "event_th": "มุฮัมมัดที่ 2 พิชิตคอนสแตนติโนเปิล", "event_en": "Conquest of Constantinople"},
            {"year_ce": 1924, "event_th": "มุสตาฟา เคมาล ยกเลิกระบบคอลีฟะฮ์", "event_en": "Abolition of the Caliphate"}
        ],
        "significance_th": "อาณาจักรที่ยาวนานที่สุดของอิสลาม เป็นมหาอำนาจระดับโลก ควบคุมเส้นทางเชื่อมยุโรปและเอเชีย",
        "notable_figures": ["มุฮัมมัด อัล-ฟาติฮ์", "สุลัยมานผู้เกรียงไกร", "ซินาน (สถาปนิก)"]
    },
    {
        "id": 8,
        "era_name_th": "ราชวงศ์มุฆัล (Mughal India)",
        "era_name_en": "Mughal Empire",
        "era_name_ar": "سلطنة المغول",
        "start_year_ce": 1526,
        "end_year_ce": 1857,
        "key_events": [
            {"year_ce": 1526, "event_th": "บาบูร์ชนะสงครามปณิปัต สถาปนาราชวงศ์", "event_en": "First Battle of Panipat"},
            {"year_ce": 1632, "event_th": "ชาห์ชะฮัน เริ่มสร้างทัชมาฮาล", "event_en": "Construction of Taj Mahal begins"}
        ],
        "significance_th": "ความเจริญรุ่งเรืองทางศิลปะและสถาปัตยกรรม การเผยแผ่อิสลามในอนุทวีปอินเดีย",
        "notable_figures": ["บาบูร์", "อักบาร์", "เอารังเซบ"]
    },
    {
        "id": 9,
        "era_name_th": "ยุคอาณานิคมและตื่นตัว (Colonial & Nahda)",
        "era_name_en": "Colonialism & Islamic Revival",
        "era_name_ar": "عصر الاستعمار والنهضة",
        "start_year_ce": 1800,
        "end_year_ce": 1945,
        "key_events": [
            {"year_ce": 1798, "event_th": "นโปเลียนบุกอียิปต์", "event_en": "Napoleon's campaign in Egypt"},
            {"year_ce": 1916, "event_th": "ข้อตกลงไซก์ส-ปิโกต์ แบ่งแยกตะวันออกกลาง", "event_en": "Sykes-Picot Agreement"}
        ],
        "significance_th": "การล่มสลายของรัฐอิสลามดั้งเดิม การตกเป็นอาณานิคมของชาติตะวันตก และการเกิดขบวนการปฏิรูป (Nahda)",
        "notable_figures": ["ญะมาลุดดีน อัล-อัฟฆอนี", "มุฮัมมัด อับดุฮ์", "อิกบาล"]
    },
    {
        "id": 10,
        "era_name_th": "ยุคสมัยใหม่ (Modern Era)",
        "era_name_en": "Modern Era",
        "era_name_ar": "العصر الحديث",
        "start_year_ce": 1945,
        "end_year_ce": 2024,
        "key_events": [
            {"year_ce": 1948, "event_th": "การก่อตั้งรัฐอิสราเอลและสงครามอาหรับ-อิสราเอลครั้งแรก", "event_en": "Creation of Israel"},
            {"year_ce": 1979, "event_th": "การปฏิวัติอิสลามในอิหร่าน", "event_en": "Iranian Revolution"}
        ],
        "significance_th": "การก่อตั้งรัฐชาติสมัยใหม่ในโลกมุสลิม ความท้าทายจากกระแสโลกาภิวัตน์ เศรษฐกิจน้ำมัน และความขัดแย้งภูมิรัฐศาสตร์",
        "notable_figures": ["ผู้ก่อตั้ง OIC", "นักวิชาการร่วมสมัย"]
    }
]

def get_history_timeline(era_id=None):
    if era_id:
        return [item for item in HISTORY_TIMELINE_DATA if item["id"] == int(era_id)]
    return HISTORY_TIMELINE_DATA

def search_history_timeline(query):
    results = []
    q = query.lower()
    for item in HISTORY_TIMELINE_DATA:
        if q in item["era_name_th"].lower() or q in item["era_name_en"].lower():
            results.append(item)
            continue
        for ev in item["key_events"]:
            if q in ev["event_th"].lower() or q in ev["event_en"].lower():
                results.append(item)
                break
    return results

# Module 7: Omni-Search
def omni_search(query, limit=5):
    q = query.lower()
    results = []

    def calc_relevance(item, fields):
        score = 0
        for f in fields:
            val = str(item.get(f, "")).lower()
            if q in val:
                score += 1
        return score

    med_res = []
    for item in PROPHETIC_MEDICINE_DATA:
        score = calc_relevance(item, ["name_ar", "name_th", "name_en", "health_benefits"])
        if score > 0:
            med_res.append({"module": "Prophetic Medicine & Bioethics", "title": item["name_th"], "summary": item["health_benefits"], "relevance": score})
    results.extend(sorted(med_res, key=lambda x: x["relevance"], reverse=True)[:limit])

    adhkar_res = []
    for item in DAILY_ADHKAR_DATA:
        score = calc_relevance(item, ["title_th", "arabic_text", "transliteration", "meaning_th"])
        if score > 0:
            adhkar_res.append({"module": "Daily Adhkar", "title": item["title_th"], "summary": item["meaning_th"], "relevance": score})
    results.extend(sorted(adhkar_res, key=lambda x: x["relevance"], reverse=True)[:limit])

    quran_res = []
    for item in QURAN_CHRONOLOGY_DATA:
        score = calc_relevance(item, ["name_ar", "name_th", "name_en", "key_theme"])
        if score > 0:
            quran_res.append({"module": "Quran Chronology", "title": f"Surah {item['surah_number']} {item['name_th']}", "summary": item["key_theme"], "relevance": score})
    results.extend(sorted(quran_res, key=lambda x: x["relevance"], reverse=True)[:limit])

    tajweed_res = []
    for item in TAJWEED_RULES_DATA:
        score = calc_relevance(item, ["rule_ar", "rule_th", "rule_en", "description_th"])
        if score > 0:
            tajweed_res.append({"module": "Tajweed Rules", "title": item["rule_th"], "summary": item["description_th"], "relevance": score})
    results.extend(sorted(tajweed_res, key=lambda x: x["relevance"], reverse=True)[:limit])

    contract_res = []
    for item in ISLAMIC_CONTRACTS_DATA:
        score = calc_relevance(item, ["name_ar", "name_th", "name_en", "mechanism_th"])
        if score > 0:
            contract_res.append({"module": "Islamic Contracts", "title": item["name_th"], "summary": item["mechanism_th"], "relevance": score})
    results.extend(sorted(contract_res, key=lambda x: x["relevance"], reverse=True)[:limit])

    history_res = []
    for item in HISTORY_TIMELINE_DATA:
        score = calc_relevance(item, ["era_name_th", "era_name_en", "significance_th"])
        if score == 0:
            for ev in item["key_events"]:
                if q in ev["event_th"].lower() or q in ev["event_en"].lower():
                    score += 1
        if score > 0:
            history_res.append({"module": "History Timeline", "title": item["era_name_th"], "summary": item["significance_th"], "relevance": score})
    results.extend(sorted(history_res, key=lambda x: x["relevance"], reverse=True)[:limit])

    try:
        cross_res = []
        for item in CROSS_SECT_MATRIX:
            score = calc_relevance(item, ["issue_th", "issue_en", "category"])
            if score > 0:
                cross_res.append({"module": "Cross-Sect Matrix", "title": item["issue_th"], "summary": f"Category: {item['category']}", "relevance": score})
        results.extend(sorted(cross_res, key=lambda x: x["relevance"], reverse=True)[:limit])

        fiqh_res = []
        for item in COMPARATIVE_FIQH_DATA:
            score = calc_relevance(item, ["issue_th", "issue_en"])
            if score > 0:
                fiqh_res.append({"module": "Comparative Fiqh", "title": item["issue_th"], "summary": "Comparative rulings from Madhahib", "relevance": score})
        results.extend(sorted(fiqh_res, key=lambda x: x["relevance"], reverse=True)[:limit])

        qawaid_res = []
        for item in QAWAID_DATA:
            score = calc_relevance(item, ["rule_ar", "rule_th", "rule_en", "explanation_th"])
            if score > 0:
                qawaid_res.append({"module": "Qawaid Fiqhiyyah", "title": item["rule_th"], "summary": item["explanation_th"], "relevance": score})
        results.extend(sorted(qawaid_res, key=lambda x: x["relevance"], reverse=True)[:limit])
    except NameError:
        pass

    return sorted(results, key=lambda x: x["relevance"], reverse=True)

"""

new_cli_args_code = """
    # Phase 2 Expansion:
    parser.add_argument("--medicine", type=str, nargs="?", const="all", help="Search Prophetic Medicine & Bioethics")
    parser.add_argument("--adhkar", type=str, nargs="?", const="all", help="Daily Adhkar & Du'a (morning/evening/after_prayer/sleep/distress)")
    parser.add_argument("--chronology", action="store_true", help="Quranic Chronological Revelation Order")
    parser.add_argument("--tajweed", type=str, nargs="?", const="all", help="Tajweed Rules (idgham/ikhfa/iqlab/izhar/qalqalah/madd)")
    parser.add_argument("--contract", type=str, nargs="?", const="all", help="Islamic Financing Contracts (murabahah/mudarabah/musharakah/ijarah/sukuk/takaful)")
    parser.add_argument("--calc-murabahah", action="store_true", dest="calc_murabahah", help="Calculate Murabahah vs Interest (requires --principal, --profit-rate, --tenure)")
    parser.add_argument("--principal", type=float, default=0.0, help="Asset price for Murabahah calculation")
    parser.add_argument("--profit-rate", type=float, default=0.0, dest="profit_rate", help="Profit rate (e.g. 0.05 for 5%)")
    parser.add_argument("--tenure", type=int, default=60, help="Tenure in months for Murabahah")
    parser.add_argument("--timeline", type=str, nargs="?", const="all", help="1,300-Year Islamic History Timeline")
    parser.add_argument("--omni", type=str, help="Universal Omni-Search across all modules")
"""

new_cli_handlers_code = """
    # Phase 2 Expansion Handlers
    if args.omni is not None:
        res = omni_search(args.omni)
        print(f"### 🌐 ผลการค้นหาครอบจักรวาล (Omni-Search for: '{args.omni}')")
        if not res:
            print("ไม่พบข้อมูลที่ตรงกับการค้นหา")
        else:
            for item in res:
                print(f"  * **[{item['module']}]** {item['title']}")
                print(f"    - {item['summary']}")
        return

    if args.medicine is not None:
        if args.medicine == "all":
            res = PROPHETIC_MEDICINE_DATA
        else:
            res = search_prophetic_medicine(args.medicine)
        print(f"### 🌿 การแพทย์ตามซุนนะฮ์และชีวจริยธรรม (Prophetic Medicine & Bioethics)")
        for item in res:
            print(f"  * **{item['name_th']}** ({item['name_en']} / {item['name_ar']})")
            print(f"    - หมวดหมู่: {item['category']} | ระดับหลักฐาน: {item['evidence_level']}")
            if item.get("prophetic_reference"):
                print(f"    - 📖 อ้างอิง: {item['prophetic_reference']} ({item['hadith_source']})")
            if item.get("modern_evidence"):
                print(f"    - 🔬 วิทยาศาสตร์/การแพทย์สมัยใหม่: {item['modern_evidence']}")
            if item.get("health_benefits"):
                print(f"    - ✅ สรรพคุณ: {item['health_benefits']}")
            if item.get("cautions"):
                print(f"    - ⚠️ ข้อควรระวัง: {item['cautions']}")
            if item.get("bioethics_note"):
                print(f"    - ⚖️ มุมมองชีวจริยธรรมอิสลาม: {item['bioethics_note']}")
            print()
        return

    if args.adhkar is not None:
        if args.adhkar == "all":
            res = get_daily_adhkar()
        else:
            res = search_daily_adhkar(args.adhkar)
        print(f"### 🤲 อัซการ์และการรำลึกถึงอัลลอฮ์ (Daily Adhkar)")
        for item in res:
            print(f"  * **{item['title_th']}**")
            print(f"    - 📜 อาหรับ: {item['arabic_text']}")
            print(f"    - 🗣️ คำอ่าน: {item['transliteration']}")
            print(f"    - 🇹🇭 ความหมาย: {item['meaning_th']}")
            print(f"    - 💡 ความประเสริฐ: {item['virtue']}")
            print(f"    - 🔢 จำนวนที่อ่าน: {item['repeat_count']} ครั้ง | แหล่งที่มา: {item['source']}")
            print()
        return

    if args.chronology:
        res = get_quran_chronology()
        print(f"### 📜 ลำดับการประทานอัลกุรอานตามประวัติศาสตร์ (Chronological Order)")
        for item in res:
            print(f"  * ลำดับประทาน: **{item['revelation_order']}** | ซูเราะฮ์ที่: {item['surah_number']} {item['name_th']} ({item['name_ar']})")
            print(f"    - ยุค: {item['period']} | {item['ayah_count']} อายะฮ์")
            print(f"    - แก่นทรรศนะ: {item['key_theme']}")
        return

    if args.tajweed is not None:
        if args.tajweed == "all":
            res = get_tajweed_rules()
        else:
            res = search_tajweed(args.tajweed)
        print(f"### 📖 กฎตัจญ์วีดสำหรับการอ่านอัลกุรอาน (Tajweed Rules)")
        for item in res:
            print(f"  * **{item['rule_th']}** ({item['rule_ar']})")
            print(f"    - กฎ: {item['description_th']}")
            print(f"    - ตัวอย่าง: {item['arabic_example']} ({item['example_ref']}) -> {item['phonetic_guide']}")
        return

    if args.contract is not None:
        if args.contract == "all":
            res = get_islamic_contracts()
        else:
            res = get_islamic_contracts(args.contract)
        print(f"### 💰 ธุรกรรมและการเงินอิสลาม (Islamic Contracts)")
        for item in res:
            print(f"  * **{item['name_th']}** ({item['name_en']})")
            print(f"    - ⚙️ กลไก: {item['mechanism_th']}")
            print(f"    - 📖 หลักการศาสนา: {item['sharia_basis']}")
            print(f"    - ⚖️ เทียบกับระบบทั่วไป: {item['conventional_equivalent']}")
            print(f"    - ❗ ข้อแตกต่างสำคัญ: {item['key_difference']}")
            print(f"    - 🛡️ การรับความเสี่ยง: {item['risk_sharing']}")
            print(f"    - 📝 ตัวอย่าง: {item['example_th']}")
            print()
        return

    if args.calc_murabahah:
        res = calculate_murabahah(args.principal, args.profit_rate, args.tenure)
        print(f"### 🧮 คำนวณสินเชื่อตามหลักมุรอบะฮะฮ์ (Murabahah Calculation)")
        print(f"  * ต้นทุนทรัพย์สิน: {res['principal']:,.2f}")
        print(f"  * อัตรากำไร: {res['profit_rate']*100:.2f}%")
        print(f"  * ระยะเวลาผ่อนชำระ: {res['tenure_months']} เดือน")
        print(f"  * กำไรทั้งหมดของสถาบันการเงิน: {res['total_profit']:,.2f}")
        print(f"  * ราคาขายรวม: {res['total_price']:,.2f}")
        print(f"  * ยอดผ่อนชำระต่อเดือน (คงที่): **{res['monthly_payment']:,.2f}**")
        print(f"  \n  **เปรียบเทียบกับระบบดอกเบี้ยทบต้น (ประมาณการ):**")
        print(f"    - ดอกเบี้ยรวม: {res['conventional_comparison']['total_interest']:,.2f}")
        print(f"    - ยอดชำระรวม: {res['conventional_comparison']['total_price']:,.2f}")
        print(f"    - ยอดผ่อนชำระต่อเดือน: {res['conventional_comparison']['monthly_payment']:,.2f}")
        return

    if args.timeline is not None:
        if args.timeline == "all":
            res = get_history_timeline()
        else:
            res = search_history_timeline(args.timeline)
        print(f"### ⏳ ลำดับเวลาประวัติศาสตร์อิสลาม (Islamic History Timeline)")
        for item in res:
            print(f"  * **{item['era_name_th']}** ({item['start_year_ce']} - {item['end_year_ce']} CE)")
            print(f"    - นัยยะสำคัญ: {item['significance_th']}")
            print(f"    - บุคคลสำคัญ: {', '.join(item['notable_figures'])}")
            print(f"    - เหตุการณ์สำคัญ:")
            for ev in item['key_events']:
                print(f"      • {ev['year_ce']} CE: {ev['event_th']}")
            print()
        return
"""

out_lines = []
for i, line in enumerate(lines):
    if i == 1570:
        out_lines.append(line)
        out_lines.append(new_modules_code + "\n")
    elif i == 1681:
        out_lines.append(line)
        out_lines.append(new_cli_args_code + "\n")
    elif i == 1839:
        out_lines.append(new_cli_handlers_code + "\n")
        out_lines.append(line)
    else:
        out_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print('Success')
