"""
Quran & Hadith Big Corpus Compiler (Super-Upgrade Edition)
Compiles full Quran (6,236 Ayahs) + Complete Six Canonical Books (Kutub al-Sittah: 34,600+ Hadiths)
+ Contemporary Fatwas and Fiqh Rulings into SQLite FTS5 for sub-millisecond local RAG searches.
"""

import os
import sys
import json
import sqlite3
import urllib.request

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "quran_hadith_corpus.db")

SURAH_NAMES_TH = {
    1: "อัล-ฟาติฮะฮ์ (การเปิด)", 2: "อัล-บะเกาะเราะฮ์ (วัวตัวเมีย)", 3: "อาลิ อิมรอน (วงศ์วานอิมรอน)",
    4: "อัน-นิซาอ์ (สตรี)", 5: "อัล-มาอิดะฮ์ (โต๊ะอาหาร)", 6: "อัล-อันอาม (ปศุสัตว์)",
    7: "อัล-อะอ์รอฟ (ที่สูง)", 8: "อัล-อันฟาล (ของเชลย)", 9: "อัต-เตาบะฮ์ (การสำนึกผิด)",
    10: "ยูนุส", 11: "ฮูด", 12: "ยูซุฟ", 13: "อัร-เราะอ์ด (ฟ้าร้อง)", 14: "อิบรอฮีม",
    15: "อัล-ฮิจญร์", 16: "อัน-นะห์ล (ผึ้ง)", 17: "อัล-อิสรออ์ (การเดินทางยามค่ำ)",
    18: "อัล-กะฮ์ฟ (ถ้ำ)", 19: "มัรยัม", 20: "ฏอฮา", 21: "อัล-อันบิยาอ์ (บรรดานบี)",
    22: "อัล-ฮัจญ์", 23: "อัล-มุอ์มินูน (บรรดาผู้ศรัทธา)", 24: "อัน-นูร (แสงสว่าง)",
    25: "อัล-ฟุรกอน (การจำแนก)", 26: "อัช-ชุอะรออ์ (บรรดากวี)", 27: "อัน-นัมล (มด)",
    28: "อัล-เกาะศ็อศ (เรื่องราว)", 29: "อัล-อันกะบูต (แมงมุม)", 30: "อัร-รูม (ชาวโรมัน)",
    31: "ลุกมาน", 32: "อัซ-ซัจญ์ดะฮ์ (การกราบ)", 33: "อัล-อะห์ซาบ (ฝ่ายพันธมิตร)",
    34: "สะบาอ์", 35: "ฟาฏิร (ผู้ทรงสร้าง)", 36: "ยาซีน", 37: "อัศ-ศ็อฟฟาต (ผู้เรียงแถว)",
    38: "ศอด", 39: "อัซ-ซุมัร (หมู่ชน)", 40: "ฆอฟิร (ผู้ทรงอภัย)", 41: "ฟุศศิลัต (อธิบายกระจ่าง)",
    42: "อัช-ชูรอ (การปรึกษาหารือ)", 43: "อัซ-ซุครุฟ (เครื่องประดับทอง)", 44: "อัด-ดุคอน (ควัน)",
    45: "อัล-ญาษิยะฮ์ (ผู้คุกเข่า)", 46: "อัล-อะห์กอฟ (เนินทราย)", 47: "มุฮัมมัด",
    48: "อัล-ฟัตห์ (ชัยชนะ)", 49: "อัล-ฮุญุรอต (ห้องหับ)", 50: "กอฟ",
    51: "อัซ-ซาริยาต (ลมพัดกระจาย)", 52: "อัฏ-ฏูร (ภูเขาฏูร)", 53: "อัน-นัจญ์ม (ดวงดาว)",
    54: "อัล-เกาะมัร (ดวงจันทร์)", 55: "อัร-เราะห์มาน (ผู้ทรงกรุณาปราณี)", 56: "อัล-วากิอะฮ์ (เหตุการณ์จริง)",
    57: "อัล-ฮะดีด (เหล็ก)", 58: "อัล-มุญาดะละฮ์ (การโต้แย้ง)", 59: "อัล-ฮัชร์ (การเนรเทศ/ชุมนุม)",
    60: "อัล-มุมตะหะนะฮ์ (หญิงผู้ถูกทดสอบ)", 61: "อัศ-ศ็อฟ (แถวทหาร)", 62: "อัล-ญุมุอะฮ์ (วันศุกร์)",
    63: "อัล-มุนาฟิกูน (พวกกลับกลอก)", 64: "อัต-ตะฆอบุน (การขาดทุน)", 65: "อัฏ-เฏาะลาก (การหย่า)",
    66: "อัต-ตะห์รีม (การห้าม)", 67: "อัล-มุลก์ (อำนาจการปกครอง)", 68: "อัล-เกาะลัม (ปากกา)",
    69: "อัล-ฮากเกาะฮ์ (ความจริงอันเที่ยงแท้)", 70: "อัล-มะอาริจญ์ (หนทางขึ้นสู่เบื้องบน)",
    71: "นูห์", 72: "อัล-ญิน (พวกญิน)", 73: "อัล-มุซซัมมิล (ผู้ห่มกาย)",
    74: "อัล-มุดดัษษิร (ผู้คลุมกาย)", 75: "อัล-กิยามะฮ์ (วันฟื้นคืนชีพ)", 76: "อัล-อินซาน (มนุษย์)",
    77: "อัล-มุรสะลาต (สายลมที่ถูกส่งมา)", 78: "อัน-นะบะอ์ (ข่าวใหญ่)", 79: "อัน-นาซิอาต (ผู้กระชาก)",
    80: "อะบะสะ (เขาหน้านิ่ว)", 81: "อัต-ตักวีร (การม้วนดับ)", 82: "อัล-อินฟิฏอร (การแยกออก)",
    83: "อัล-มุฏ็อฟฟิฟีน (พวกโกงตาชั่ง)", 84: "อัล-อินชิกอก (การแตกสลาย)", 85: "อัล-บุรูจญ์ (กลุ่มดาวจักรราศี)",
    86: "อัฏ-ฏอริก (ดาวประกายพรึก)", 87: "อัล-อะอ์ลา (ผู้ทรงสูงสุด)", 88: "อัล-ฆอชิยะฮ์ (ความหายนะที่ครอบคลุม)",
    89: "อัล-ฟัจญ์ร (แสงอรุณ)", 90: "อัล-บะลัด (บ้านเมือง)", 91: "อัช-ชัมส์ (ดวงอาทิตย์)",
    92: "อัล-ลัยล์ (กลางคืน)", 93: "อัฎ-ฎุฮา (ยามสาย)", 94: "อัช-ชัรห์ (การเปิดอก)",
    95: "อัต-ตีน (มะเดื่อ)", 96: "อัล-อะลัก (ก้อนเนื้อ/หยดเลือด)", 97: "อัล-ก็อดร์ (ค่ำคืนแห่งเกียรติยศ)",
    98: "อัล-บัยยินะฮ์ (หลักฐานอันชัดแจ้ง)", 99: "อัซ-ซัลซะละฮ์ (แผ่นดินไหวสะเทือน)",
    100: "อัล-อาดิยาต (ม้าศึกวิ่งหอบ)", 101: "อัล-กอริอะฮ์ (วันวิบัติเคาะประตู)",
    102: "อัต-ตะกาษุร (การสะสมหลงใหล)", 103: "อัล-อัศร์ (กาลเวลา)", 104: "อัล-ฮุมะซะฮ์ (พวกชอบนินทา)",
    105: "อัล-ฟีล (ช้าง)", 106: "กุรอยช์ (เผ่ากุเรช)", 107: "อัล-มาอูน (สิ่งของเครื่องใช้)",
    108: "อัล-เกาษัร (แม่น้ำแห่งความอุดมสมบูรณ์)", 109: "อัล-กาฟิรูน (บรรดาผู้ปฏิเสธ)",
    110: "อัน-นัศร์ (การช่วยเหลือ)", 111: "อัล-มะสัด (เชือกใยอินทผลัม)",
    112: "อัล-อิคลาศ (ความบริสุทธิ์ใจ/เอกภาพ)", 113: "อัล-ฟะลัก (รุ่งอรุณ)", 114: "อัน-นาส (มนุษยชาติ)"
}

def fetch_json(url):
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=60) as res:
        data = res.read().decode("utf-8")
        return json.loads(data)

def init_db(conn):
    cursor = conn.cursor()
    
    # Core Quran tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS surahs (
        number INTEGER PRIMARY KEY,
        name_ar TEXT NOT NULL,
        name_en TEXT NOT NULL,
        name_th TEXT NOT NULL,
        revelation_type TEXT NOT NULL,
        total_ayahs INTEGER NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quran (
        id INTEGER PRIMARY KEY,
        surah_number INTEGER NOT NULL,
        ayah_number INTEGER NOT NULL,
        arabic_text TEXT NOT NULL,
        thai_text TEXT NOT NULL,
        FOREIGN KEY (surah_number) REFERENCES surahs(number)
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS quran_fts USING fts5(
        surah_number UNINDEXED,
        ayah_number UNINDEXED,
        surah_name,
        arabic_text,
        thai_text
    );
    """)

    # Upgraded Hadith Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hadiths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection TEXT NOT NULL,
        collection_title TEXT NOT NULL,
        hadith_number INTEGER NOT NULL,
        book_number INTEGER,
        chapter_title TEXT,
        arabic_text TEXT,
        english_text TEXT,
        grade TEXT
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS hadiths_fts USING fts5(
        collection,
        collection_title,
        hadith_number UNINDEXED,
        chapter_title,
        arabic_text,
        english_text
    );
    """)

    # Contemporary Fatwa & Rulings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contemporary_fatwas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title_th TEXT NOT NULL,
        ruling_summary TEXT NOT NULL,
        detailed_explanation TEXT NOT NULL,
        authorities TEXT NOT NULL,
        primary_evidences TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS contemporary_fatwas_fts USING fts5(
        category,
        title_th,
        ruling_summary,
        detailed_explanation,
        authorities,
        primary_evidences
    );
    """)

    # Primary Texts of Sects and Theological Schools Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sect_texts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tradition TEXT NOT NULL,          -- 'shia', 'salafi', 'ibadi', 'sufi'
        tradition_title_th TEXT NOT NULL,
        book_title TEXT NOT NULL,
        author TEXT NOT NULL,
        chapter_title TEXT NOT NULL,
        arabic_text TEXT,
        thai_text TEXT NOT NULL,
        english_text TEXT,
        doctrinal_theme TEXT NOT NULL,
        notes TEXT
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS sect_texts_fts USING fts5(
        tradition,
        tradition_title_th,
        book_title,
        author,
        chapter_title,
        arabic_text,
        thai_text,
        english_text,
        doctrinal_theme
    );
    """)

    # Halal E-Number Food Additives Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS halal_enumbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        e_number TEXT UNIQUE NOT NULL,    -- 'E120', 'E471', etc.
        name_th TEXT NOT NULL,
        name_en TEXT NOT NULL,
        category TEXT NOT NULL,           -- 'สีผสมอาหาร', 'สารทำให้คงตัว', etc.
        halal_status TEXT NOT NULL,       -- 'halal', 'haram', 'shubhah'
        source_origin TEXT NOT NULL,      -- 'พืช', 'แมลง', 'ไขมันสัตว์', 'เคมีสังเคราะห์'
        explanation TEXT NOT NULL,
        authority_fatwa TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS halal_enumbers_fts USING fts5(
        e_number,
        name_th,
        name_en,
        category,
        halal_status,
        source_origin,
        explanation,
        authority_fatwa
    );
    """)

    # Quranic Root Words & Morphology Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quran_roots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        root_ar TEXT UNIQUE NOT NULL,     -- e.g. 'س ل م'
        root_lat TEXT NOT NULL,           -- e.g. 'S-L-M'
        meaning_th TEXT NOT NULL,
        frequency_in_quran INTEGER NOT NULL,
        derived_words TEXT NOT NULL,      -- JSON list of derivatives
        sample_ayah TEXT NOT NULL,
        theological_significance TEXT NOT NULL
    );
    """)

    conn.commit()

def populate_surahs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM surahs")
    if cursor.fetchone()[0] == 114:
        print("[1/4] Surahs metadata already populated (114 surahs). Skipping download.")
        return

    print("\n[1/4] Populating Surah metadata...")
    surahs_data = fetch_json("http://api.alquran.cloud/v1/surah")["data"]
    for s in surahs_data:
        num = s["number"]
        name_th = SURAH_NAMES_TH.get(num, s["englishName"])
        cursor.execute("""
        INSERT OR REPLACE INTO surahs (number, name_ar, name_en, name_th, revelation_type, total_ayahs)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (num, s["name"], s["englishName"], name_th, s["revelationType"], s["numberOfAyahs"]))
    conn.commit()
    print(f"Saved {len(surahs_data)} surahs.")

def populate_quran(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM quran")
    if cursor.fetchone()[0] == 6236:
        print("[2/4] Quran verses already populated (6,236 Ayahs). Checking FTS...")
        cursor.execute("SELECT count(*) FROM quran_fts")
        if cursor.fetchone()[0] == 6236:
            print("Quran FTS5 index intact. Skipping download.")
            return

    print("\n[2/4] Downloading and compiling Quran verses (Arabic & Thai)...")
    thai_data = fetch_json("https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/tha-kingfahadquranc.min.json")["quran"]
    arabic_data = fetch_json("https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/ara-quransimple.min.json")["quran"]

    ar_map = {(v["chapter"], v["verse"]): v["text"] for v in arabic_data}

    cursor.execute("DELETE FROM quran;")
    cursor.execute("DELETE FROM quran_fts;")

    verse_id = 1
    for item in thai_data:
        ch = item["chapter"]
        v_num = item["verse"]
        th_text = item["text"]
        ar_text = ar_map.get((ch, v_num), "")
        surah_th = SURAH_NAMES_TH.get(ch, f"ซูเราะฮ์ที่ {ch}")

        cursor.execute("""
        INSERT INTO quran (id, surah_number, ayah_number, arabic_text, thai_text)
        VALUES (?, ?, ?, ?, ?)
        """, (verse_id, ch, v_num, ar_text, th_text))

        cursor.execute("""
        INSERT INTO quran_fts (surah_number, ayah_number, surah_name, arabic_text, thai_text)
        VALUES (?, ?, ?, ?, ?)
        """, (ch, v_num, surah_th, ar_text, th_text))

        verse_id += 1

    conn.commit()
    print(f"Compiled {verse_id - 1} Quran verses into SQLite FTS5.")

def populate_all_hadiths(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM hadiths")
    cur_count = cursor.fetchone()[0]
    if cur_count >= 34600:
        print(f"[3/4] Hadith corpus already populated ({cur_count} hadiths). Skipping download.")
        return

    print("\n[3/4] Downloading and compiling 34,600+ Hadiths (Complete Kutub al-Sittah + Nawawi + Qudsi)...")

    collections = [
        ("nawawi", "An-Nawawi 40 (40 ฮะดีษอัน-นะวะวีย์)", "ara-nawawi", "eng-nawawi"),
        ("qudsi", "Hadith Qudsi (40 ฮะดีษกุดซีย์)", "ara-qudsi", "eng-qudsi"),
        ("bukhari", "Sahih al-Bukhari (เศาะฮีฮ์ อัล-บุคอรี)", "ara-bukhari1", "eng-bukhari"),
        ("muslim", "Sahih Muslim (เศาะฮีฮ์ มุสลิม)", "ara-muslim1", "eng-muslim"),
        ("abudawud", "Sunan Abi Dawud (สุนัน อบูดาวูด)", "ara-abudawud", "eng-abudawud"),
        ("tirmidhi", "Jami' at-Tirmidhi (ญามิอ์ อัต-ติรมีซี)", "ara-tirmidhi", "eng-tirmidhi"),
        ("nasai", "Sunan an-Nasa'i (สุนัน อัน-นะซาอี)", "ara-nasai", "eng-nasai"),
        ("ibnmajah", "Sunan Ibn Majah (สุนัน อิบนุ มาญะฮ์)", "ara-ibnmajah", "eng-ibnmajah"),
    ]

    total_hadiths_saved = 0

    for col_key, col_title, ara_key, eng_key in collections:
        print(f"\nProcessing collection: {col_title}...")
        ara_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{ara_key}.min.json"
        eng_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{eng_key}.min.json"

        eng_data = fetch_json(eng_url)
        ara_data = fetch_json(ara_url)

        sections = eng_data.get("metadata", {}).get("sections", {})
        ara_map = {h["hadithnumber"]: h["text"] for h in ara_data.get("hadiths", [])}

        count = 0
        for h in eng_data.get("hadiths", []):
            h_num = h["hadithnumber"]
            eng_txt = h.get("text", "")
            ara_txt = ara_map.get(h_num, "")
            ref = h.get("reference", {})
            book_num = ref.get("book", 0) if isinstance(ref, dict) else 0
            chapter_title = sections.get(str(book_num), "")

            # Determine grade
            grade_str = "Sahih" if col_key in ["bukhari", "muslim", "nawawi", "qudsi"] else "Documented"
            grades = h.get("grades", [])
            if grades and isinstance(grades, list):
                # Prefer Al-Albani or Ahmad Shakir if present
                for g in grades:
                    if "Albani" in g.get("name", ""):
                        grade_str = g.get("grade", grade_str)
                        break
                if grade_str == "Documented" and len(grades) > 0:
                    grade_str = grades[0].get("grade", "Documented")

            cursor.execute("""
            INSERT INTO hadiths (collection, collection_title, hadith_number, book_number, chapter_title, arabic_text, english_text, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (col_key, col_title, h_num, book_num, chapter_title, ara_txt, eng_txt, grade_str))

            cursor.execute("""
            INSERT INTO hadiths_fts (collection, collection_title, hadith_number, chapter_title, arabic_text, english_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (col_key, col_title, h_num, chapter_title, ara_txt, eng_txt))

            count += 1

        conn.commit()
        total_hadiths_saved += count
        print(f"-> Saved {count} hadiths for {col_key} ({col_title}).")

    print(f"\nSuccessfully indexed {total_hadiths_saved} total Hadiths across complete Kutub al-Sittah into SQLite FTS5!")

def populate_contemporary_fatwas(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM contemporary_fatwas")
    if cursor.fetchone()[0] == 9:
        print("[4/4] Contemporary Fatwas already populated (9 fatwas). Skipping.")
        return

    print("\n[4/4] Ingesting Contemporary Fatwas and Fiqh Rulings...")
    cursor.execute("DELETE FROM contemporary_fatwas;")
    cursor.execute("DELETE FROM contemporary_fatwas_fts;")

    fatwas = [
        (
            "การเงินและตลาดทุน (Finance & Stocks)",
            "เกณฑ์การคัดกรองหุ้นฮาลาลตามมาตรฐานสากล (AAOIFI Standard 21)",
            "หุ้นฮาลาลต้องผ่านเกณฑ์ 3 ข้อ: 1) ธุรกิจหลักต้องฮาลาล 2) หนี้สินมีดอกเบี้ยต้องไม่เกิน 33% ของมูลค่าตลาด 3) รายได้ที่ไม่ฮาลาลต้องไม่เกิน 5%",
            "การลงทุนในหุ้นสามัญเป็นที่อนุมัติตามมติสภาฟิกฮ์อิสลามนานาชาติ (OIC) ภายใต้เงื่อนไข AAOIFI: 1. Core Business: ห้ามประกอบกิจการธนาคารดอกเบี้ย สุรา สุกร การพนัน บันเทิงลามก หรืออาวุธผิดกฎหมาย 2. Financial Ratio: หนี้สินมีดอกเบี้ย / Market Cap < 33%, เงินฝากที่ได้ดอกเบี้ย / Market Cap < 33% 3. Non-Halal Income: รายได้ดอกเบี้ยหรือกิจกรรมต้องห้ามปนเปื้อน < 5% ของรายได้รวม และต้องทำ 'การชำระล้าง (Purification/Tathir)' โดยบริจาคส่วน 5% นั้นทิ้งเพื่อการกุศลโดยไม่หวังผลบุญ",
            "Accounting and Auditing Organization for Islamic Financial Institutions (AAOIFI Standard No. 21), สภาฟิกฮ์อิสลามนานาชาติ (OIC-IFA)",
            "ซูเราะฮ์อัล-บะเกาะเราะฮ์ 2:275 (อัลลอฮ์ทรงอนุมัติการค้าและห้ามดอกเบี้ย), ฮะดีษบุคอรี 52 (หลีกเลี่ยงสิ่งคลุมเครือ ชุบฮาต)"
        ),
        (
            "ครอบครัวและนะฟะเกาะฮ์ (Family & Maintenance)",
            "ลำดับขั้นและเกณฑ์การจ่ายนะฟะเกาะฮ์ให้ครอบครัวและพ่อแม่",
            "ลำดับการจ่ายนะฟะเกาะฮ์: 1) ตัวเอง 2) ภรรยา (สัญญาวาญิบ) 3) ลูกเล็ก 4) พ่อแม่ (เฉพาะเมื่อท่านขัดสนและลูกมีเงินเหลือ) ห้ามอดตายเพื่อเอาเงินไปให้พ่อแม่",
            "นะฟะเกาะฮ์ภรรยาและลูกเล็กถือเป็นหน้าที่ผูกพันตามสัญญา (ฟัรดูอัยน์) หากสามีไม่จ่ายถือเป็นบาปใหญ่ ส่วนนะฟะเกาะฮ์พ่อแม่เป็นข้อบังคับเมื่อ 1. พ่อแม่ยากจนขัดสน 2. ลูกมีเงินส่วนเกิน (ฟัฎล์) หลังจากหักค่ากินอยู่ของตัวเองและลูกเมียแล้ว หากลูกตกอยู่ในภาวะขัดสน (มุอ์ซิร) หน้าที่การจ่ายเงินสดให้พ่อแม่ตกไปทันที และพ่อแม่ไม่มีสิทธิ์ข่มขู่หรือไถเงินจนลูกเมียต้องอดอยาก",
            "มติของ 4 มัซฮับ (ฮะนะฟี, มาลิกี, ชาฟิอี, ฮันบะลี), คณะกรรมการฟัตวาถาวรแห่งซาอุดีอาระเบีย (อัล-ลัจญ์นะฮ์ อัด-ดาอิมะฮ์)",
            "ซูเราะฮ์อัต-เฏาะลาก 65:7, ฮะดีษอบูดาวูด (บาปมหันต์ที่ละเลยคนที่มีหน้าที่ต้องป้อนข้าว), ฮะดีษมุสลิม (จงเริ่มที่ตัวเองก่อน แล้วจึงครอบครัว)"
        ),
        (
            "สิ่งเสพติดและสุขภาพ (Substances & Health)",
            "ฮุก่มพืชกระท่อม, น้ำท่อมต้ม 4x100 และกัญชา",
            "น้ำท่อมต้มเพื่อการมึนเมา/เสพติด และ 4x100 เป็นสิ่งฮะรอม (ต้องห้ามเด็ดขาด 100%) ทั้งผู้ต้ม ผู้ขาย และผู้ดื่ม มีสถานะเทียบเท่าสิ่งมึนเมาและยาเสพติด",
            "สำนักจุฬาราชมนตรีและคณะกรรมการอิสลามประจำจังหวัดฟันธงว่า น้ำกระท่อมต้มผสมยาแก้ไอ ยาแก้แพ้ หรือน้ำอัดลม (4x100) มีฤทธิ์กดประสาท กล่อมประสาท ทำให้เคลิบเคลิ้ม และทำให้เสพติด เข้าข่าย 'มุฟัตติร (สิ่งที่ทำให้ประสาทมึนชา)' และ 'มุสกีร (สิ่งมึนเมา)' ตามฮะดีษที่ท่านนบีสั่งห้ามทุกสิ่งที่ทำให้เมาและมึนชา การอ้างว่าเป็นพืชธรรมชาติไม่ทำให้ฮาลาล เพราะอิสลามตัดสินที่ฤทธิ์ต่อจิตประสาทและผลเสียต่อร่างกาย",
            "สำนักจุฬาราชมนตรี (คำวินิจฉัยฟัตวาเรื่องพืชกระท่อมและกัญชา), มติสภาฟิกฮ์แห่งชาติมาเลเซีย",
            "ฮะดีษสุนัน อบูดาวูด 3686 (ห้ามมุสกีรและมุฟัตติร), 40 ฮะดีษนะวะวีย์ บทที่ 32 (ห้ามสร้างความเสียหายต่อตนเองและผู้อื่น)"
        ),
        (
            "อาหารและโภชนาการ (Food & Dining)",
            "ฮุก่มการรับประทานอาหารญี่ปุ่นที่มีมิริน และการปนเปื้อนข้าม (Cross-Contamination)",
            "มิรินแท้ (Hon-Mirin) มีแอลกอฮอล์ 14% เป็นสิ่งฮะรอม แม้ใส่ในอาหารเล็กน้อยจนไม่เมาก็ยังฮะรอม ร้านที่ไม่มีตรารับรองและมีเมนูหมูปนเปื้อนควรหลีกเลี่ยง",
            "มิรินจัดเป็นค็อมร์ (สุราหมัก) เพราะมีแอลกอฮอล์ 14% เทียบเท่าไวน์ ตามกฎ 'สิ่งใดที่กินมากแล้วเมา สิ่งนั้นแม้เพียงเล็กน้อยก็ฮะรอม' ข้าวซูชิหรือซอสที่ผสมมิรินจึงไม่ฮาลาล นอกจากนี้ ร้านซูชิสายพานทั่วไปที่ไม่มีการรับรองฮาลาล (เช่น Sushiro) มีความเสี่ยงสูงจากการปนเปื้อนข้าม (Cross-contamination) จากเนื้อหมู มีด เขียง น้ำมันทอดรวม และเจลาตินหมูในขนมหวาน มุสลิมควรหลีกเลี่ยงตามหลักการระวังสิ่งคลุมเครือ (ชุบฮาต)",
            "คณะกรรมการกลางอิสลามแห่งประเทศไทย (กอท.), สถาบันมาตรฐานอาหารฮาลาล",
            "ฮะดีษสุนันอบูดาวูด 3681 (สิ่งที่มากแล้วเมา เล็กน้อยก็ฮะรอม), ฮะดีษบุคอรี 52 (ชุบฮาต), ฮะดีษมุสลิม 5219 (ทุกสิ่งมึนเมาคือค็อมร์)"
        ),
        (
            "เทคโนโลยีและความบันเทิง (Entertainment & Gaming)",
            "ฮุก่มการเล่นวิดีโอเกม (Video Games & E-Sports)",
            "การเล่นเกมโดยพื้นฐานเป็นที่อนุมัติ (มุบาฮ์) เพื่อการพักผ่อน แต่จะกลายเป็นฮะรอมหากมีชิริก ภาพโป๊ การพนันกาชา หรือทำให้ละเลยการละหมาด",
            "เกมเป็นสิ่งบันเทิงที่อนุญาตได้ตามหลัก 'สิ่งทางโลกเดิมทีอนุมัติ' แต่ต้องปลอดจาก 5 องค์ประกอบต้องห้าม: 1. ไม่มีเนื้อหาตั้งภาคี (ชิริก) เช่น กราบไหว้รูปปั้น บูชาซาตาน หรือจำลองตนเองเป็นพระเจ้า 2. ไม่มีภาพลามกอนาจารหรือเปิดเผยเอาเราะฮ์ 3. ไม่มีการพนันสุ่มเกลือด้วยเงินจริง (Gacha/Loot Box) 4. ต้องไม่ทำให้ละเลยเวลาละหมาดและหน้าที่ต่อครอบครัว 5. ไม่สร้างความก้าวร้าว Toxic สาปแช่งบุพการี",
            "สภาฟัตวาแห่งประเทศอียิปต์ (ดารุลอิฟตาอ์ อัลมิศรียะฮ์), มติคณะกรรมการฟัตวาถาวรซาอุดีอาระเบีย",
            "ฮะดีษมุสลิม 6966 (ชีวิตมีเวลาสำหรับศาสนาและเวลาสำหรับการพักผ่อน), ซูเราะฮ์อัล-มาอูน 107:4-5 (เตือนผู้ละเลยละหมาด)"
        ),
        (
            "ดนตรีและเครื่องดนตรี (Music & Instruments)",
            "ฮุก่มเสียงดนตรี เครื่องดนตรี และการขับลำนำ (นะชีด)",
            "มติ 4 มัซฮับระบุว่าเครื่องดนตรีทั่วไป (เครื่องสาย เครื่องเป่า) เป็นสิ่งฮะรอม ยกเว้น 'กลองดุฟฟ์ (รำมะนา)' ในวันอีดและงานแต่งงาน ส่วนการร้องเพลงปากเปล่าเนื้อหาดีอนุญาตได้",
            "ปราชญ์ส่วนใหญ่ (ญุมฮูร ทั้ง 4 มัซฮับ) ถือว่าเครื่องดนตรี (มะอาซิฟ) เป็นสิ่งต้องห้าม โดยอิงจากฮะดีษเศาะฮีฮ์ที่เตือนเรื่องการทำให้เครื่องดนตรีเป็นเรื่องฮาลาลคู่กับสุราและผิดประเวณี ส่วนข้อยกเว้นคือการตีกลองหน้าเดียว (ดุฟฟ์) สำหรับสตรีหรือเด็กในวันเฉลิมฉลอง (วันอีด) และงานนิกาฮ์เพื่อประกาศการแต่งงาน สำหรับการขับร้องปากเปล่า (นะชีด/บทกวี) หากเนื้อหาสรรเสริญความดี เตือนสติ และไม่มีเสียงดนตรี ถือว่าอนุญาตได้ตามแบบฉบับท่านฮัสซาน บิน ษาบิต",
            "มติของทั้ง 4 มัซฮับ (ฮะนะฟี, มาลิกี, ชาฟิอี, ฮันบะลี), ตัฟซีร อิบนุ กะษีร",
            "ซูเราะฮ์ลุกมาน 31:6 (ละฮ์วัลฮะดีษ), ฮะดีษบุคอรี 5590 (เครื่องดนตรีจะถูกทำให้ฮาลาล), ฮะดีษบุคอรี 3931 (กลองดุฟฟ์ในวันอีด)"
        ),
        (
            "ดาราศาสตร์และจักรวาลวิทยา (Astronomy & Aliens)",
            "มุมมองอิสลามต่ออวกาศและสิ่งมีชีวิตทรงภูมิปัญญานอกโลก (Extraterrestrial Life)",
            "อัลกุรอานเปิดกว้างและระบุชัดเจนว่ามี 'สิ่งมีชีวิตทางกายภาพ (ดาบบะฮ์)' กระจายอยู่ในห้วงอวกาศและชั้นฟ้า ไม่ขัดต่อหลักการศาสนาหากมีการค้นพบเอเลี่ยน",
            "ซูเราะฮ์อัช-ชูรอ 42:29 ระบุถึงการสร้างชั้นฟ้าและแผ่นดิน และการแพร่กระจายของ 'สิ่งมีชีวิต (ดาบบะฮ์)' ในทั้งสองสิ่งนั้น ซึ่งคำว่าดาบบะฮ์หมายถึงสิ่งมีชีวิตทางกายภาพที่เคลื่อนไหวได้ ไม่ใช่แค่มลาอิกะฮ์ และท่านอิบนุ อับบาส ปราชญ์อรรถาธิบายกุรอานอันดับหนึ่ง ได้ระบุถึงการมีอยู่ของดาวเคราะห์โลกอื่นๆ ที่มีนบีและสิ่งมีชีวิตทรงภูมิปัญญา นอกจากนี้ ซูเราะฮ์ 51:47 ยังระบุถึงการขยายตัวของเอกภพ (Expanding Universe) อย่างชัดเจนตั้งแต่ 1,400 ปีก่อน",
            "ตัฟซีร อัร-รอซี (มุฟาตีฮุล ฆ็อยบ์), ตัฟซีร อัฏ-เฏาะบะรี, มุสตัดร็อก อัล-ฮากิม",
            "ซูเราะฮ์อัช-ชูรอ 42:29, ซูเราะฮ์อัน-นะห์ล 16:49, ซูเราะฮ์อัฏ-เฏาะลาก 65:12, ซูเราะฮ์อัซ-ซาริยาต 51:47"
        ),
        (
            "การแพทย์และจริยธรรมชีวภาพ (Medical Ethics)",
            "ฮุก่มการบริจาคอวัยวะ และการถอดเครื่องพยุงชีพ",
            "การบริจาคอวัยวะเพื่อช่วยชีวิตผู้อื่นเป็นสิ่งที่อนุมัติและได้บุญมหาศาล ภายใต้เงื่อนไขว่าต้องได้รับความยินยอมและห้ามซื้อขาย ส่วนการถอดเครื่องพยุงชีพในภาวะสมองตายทำได้",
            "สภาฟิกฮ์อิสลามนานาชาติ (OIC) มีมติว่า การบริจาคอวัยวะหลังเสียชีวิต หรือบริจาคไต 1 ข้างขณะมีชีวิตเพื่อช่วยชีวิตผู้ป่วย ถือเป็นการเสียสละและทานอันยิ่งใหญ่ตามเจตนารมณ์ 'การรักษาชีวิตมนุษย์' แต่ห้ามมีการซื้อขายเชิงพาณิชย์เด็ดขาด สำหรับผู้ป่วยที่สมองตายโดยสิ้นเชิง (Brain Death) ตามการยืนยันของแพทย์ผู้เชี่ยวชาญ 3 ท่าน อนุญาตให้ถอดเครื่องช่วยหายใจได้ ไม่ถือเป็นการฆาตกรรม",
            "สภาฟิกฮ์อิสลามนานาชาติ (OIC-IFA Resolution No. 26), สำนักจุฬาราชมนตรี",
            "ซูเราะฮ์อัล-มาอิดะฮ์ 5:32 (ผู้ใดช่วยชีวิตคนหนึ่ง เสมือนเขาได้ช่วยชีวิตมนุษยชาติทั้งมวล)"
        ),
        (
            "ความมั่นคงและการป้องกันตัว (Defense & Weapons)",
            "ฮุก่มการค้าอาวุธ และการใช้อาวุธในยุคปัจจุบัน",
            "การค้าอาวุธถูกกฎหมายเพื่อป้องกันตัวและป้องกันประเทศเป็นสิ่งฮาลาล แต่ห้ามค้าอาวุธเถื่อน และห้ามใช้อาวุธทำลายล้างสูงเข่นฆ่าผู้หญิง เด็ก และพลเรือน",
            "การจัดหายุทโธปกรณ์เพื่อป้องกันรัฐเป็นภาระหน้าที่ (ฟัรดู กิฟายะฮ์) ตามซูเราะฮ์อัล-อันฟาล 8:60 การเปิดร้านค้าอาวุธที่ถูกต้องตามกฎหมายเพื่อความมั่นคงถือเป็นสิ่งที่อนุมัติ แต่การค้าอาวุธเถื่อนหรือขายอาวุธให้แก่ศัตรู/ผู้ก่อการร้ายเป็นสิ่งฮะรอมเด็ดขาด ในการทำศึกสงคราม ท่านนบีสั่งห้ามสังหารเด็ก ผู้หญิง และคนชราอย่างเด็ดขาด (เศาะฮีฮ์ อัล-บุคอรี 3015)",
            "มติสภาฟิกฮ์อิสลามนานาชาติ, สำนักจุฬาราชมนตรี",
            "ซูเราะฮ์อัล-อันฟาล 8:60, ซูเราะฮ์อัล-มาอิดะฮ์ 5:2, ฮะดีษบุคอรี 3015"
        )
    ]

    for cat, title, summary, detail, auth, ev in fatwas:
        cursor.execute("""
        INSERT INTO contemporary_fatwas (category, title_th, ruling_summary, detailed_explanation, authorities, primary_evidences)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (cat, title, summary, detail, auth, ev))

        cursor.execute("""
        INSERT INTO contemporary_fatwas_fts (category, title_th, ruling_summary, detailed_explanation, authorities, primary_evidences)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (cat, title, summary, detail, auth, ev))

    conn.commit()
    print(f"Successfully indexed {len(fatwas)} contemporary fatwas and rulings into SQLite FTS5!")

def populate_sect_texts(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM sect_texts")
    if cursor.fetchone()[0] >= 7:
        print("[4/6] Sect & Theological Schools primary texts already populated. Skipping.")
        return

    print("\n[4/6] Populating Sects & Theological Schools Primary Texts (Shia, Salafi, Ibadi, Sufi)...")
    cursor.execute("DELETE FROM sect_texts;")
    cursor.execute("DELETE FROM sect_texts_fts;")

    sect_data = [
        # Shia Tradition
        (
            "shia", "ชีอะฮ์ (Shia / Twelver)",
            "Nahj al-Balagha (นะฮ์ญุล บะลาเฆาะฮ์)",
            "อะลี อิบน์ อบีฏอลิบ (รวบรวมโดย อัช-ชะรีฟ อัร-เราะฎี)",
            "จดหมายฉบับที่ 53: ธรรมนูญการปกครองส่งถึงมาลิก อัล-อัชตัร",
            "وأشعر قلبك الرحمة للرعية، والمحبة لهم، واللطف بهم، ولا تكونن عليهم سبعاً ضارياً تغتنم أكلهم، فإنهم صنفان: إما أخ لك في الدين، وإما نظير لك في الخلق",
            "จงปลูกฝังหัวใจของเจ้าให้เปี่ยมด้วยความเมตตาต่อประชาราษฎร์ ความรัก และความอ่อนโยนต่อพวกเขา อย่าทำตนเยี่ยงสัตว์ร้ายที่จ้องกัดกินพวกเขา เพราะแท้จริงมนุษย์มีอยู่สองจำพวก: ไม่เป็นพี่น้องร่วมศาสนาของเจ้า ก็เป็นเพื่อนร่วมเผ่าพันธุ์มนุษย์ที่เสมอภาคกับเจ้าในการถูกสร้าง",
            "Habituate your heart to mercy for the subjects and to affection and kindness for them. Do not stand over them like a greedy beast, for they are of two kinds: either your brother in religion or your equal in creation.",
            "จริยธรรมการปกครอง ความยุติธรรม และสิทธิมนุษยชนสากล",
            "สหประชาชาติ (UN 2002) ยกย่องพระราชสาส์นฉบับนี้เป็นเอกสารต้นแบบธรรมาภิบาลแห่งประวัติศาสตร์โลก"
        ),
        (
            "shia", "ชีอะฮ์ (Shia / Twelver)",
            "Al-Kafi (กิตาบ อัล-กาฟี)",
            "อัล-กุลัยนี (Abu Ja'far Muhammad ibn Ya'qub al-Kulayni)",
            "คัมภีร์แห่งสติปัญญาและความเขลา (Kitab al-Aql wal-Jahl) วจนะที่ 1",
            "إن الله خلق العقل فقال له: أقبل فأقبل، ثم قال له: أدبر فأدبر، فقال: وعزتي وجلالي ما خلقت خلقاً أحب إلي منك",
            "แท้จริงอัลลอฮ์ได้ทรงสร้างสติปัญญาขึ้นมา แล้วตรัสแก่มันว่า 'จงก้าวเข้ามา' มันจึงก้าวเข้ามา แล้วตรัสว่า 'จงถอยออกไป' มันจึงถอยออกไป แล้วพระองค์ตรัสว่า: 'ขอสาบานด้วยเกียรติยศและความยิ่งใหญ่ของข้า ข้ามิได้สร้างสิ่งใดที่จะเป็นที่รักยิ่งแก่ข้ามากกว่าเจ้า'",
            "Indeed Allah created the intellect and said to it: 'Come forward,' and it came forward. Then He said: 'Turn back,' and it turned back. Then He said: 'By My Honor and Majesty, I have not created any creation more beloved to Me than you.'",
            "ญาณวิทยาและสถานะสูงสุดของสติปัญญาและตรรกะในเทววิทยา",
            "ฮะดีษบทแรกในคัมภีร์อัล-กาฟี ตอกย้ำว่าสติปัญญาคือรากฐานในการเข้าถึงความศรัทธา"
        ),
        (
            "shia", "ชีอะฮ์ (Shia / Twelver)",
            "Al-Kafi (กิตาบ อัล-กาฟี)",
            "อัล-กุลัยนี (Al-Kulayni)",
            "คัมภีร์แห่งหลักฐานชี้ขาดและการแต่งตั้งอิหม่าม (Kitab al-Hujjah)",
            "إن الأرض لا تخلو من حجة، ولولا الحجة لساخت الأرض بأهلها",
            "แท้จริงผืนแผ่นดินนี้จะไม่ว่างเว้นจากหลักฐานชี้ขาด (ฮุจญะฮ์/อิหม่าม) และหากปราศจากฮุจญะฮ์แล้ว แผ่นดินย่อมถล่มกลืนผู้อาศัยอยู่บนนั้นอย่างแน่นอน",
            "Indeed the earth is never devoid of a Divine Proof (Hujjah), and were it not for the Proof, the earth would swallow its inhabitants.",
            "สถาบันอิหม่ามและการชี้นำนิรันดร์ (Doctrine of Imamate)",
            "รากฐานความเชื่อสายอิษนาอะชะรียะฮ์ (สิบสองอิหม่าม) ว่าต้องมีอิหม่ามผู้ไร้มลทินคอยคุ้มครองสัจธรรม"
        ),
        # Salafi / Wahhabi Tradition
        (
            "salafi", "สะละฟีย์ / อะษะรีย์ (Salafi / Athari)",
            "Kitab al-Tawhid (กิตาบ อัต-เตาฮีด)",
            "มุฮัมมัด บิน อับดุลวะฮ์ฮาบ (Muhammad ibn Abd al-Wahhab)",
            "บทที่ 1: ความจำเป็นแห่งเตาฮีดและสิทธิของอัลลอฮ์เหนือปวงบ่าว",
            "حق الله على العباد أن يعبدوه ولا يشركوا به شيئاً، وحق العباد على الله أن لا يعذب من لا يشرك به شيئاً",
            "สิทธิของอัลลอฮ์เหนือปวงบ่าวคือ พวกเขาจะต้องเคารพภักดีต่อพระองค์เพียงผู้เดียว และต้องไม่ตั้งภาคี (ชิริก) ใดๆ กับพระองค์ และสิทธิของบ่าวเหนืออัลลอฮ์คือ พระองค์จะไม่ทรงลงทัณฑ์ผู้ที่มิได้ตั้งภาคีใดๆ ต่อพระองค์",
            "The right of Allah upon His servants is that they worship Him alone and associate nothing with Him, and the right of the servants upon Allah is that He does not punish those who associate nothing with Him.",
            "เตาฮีด อัล-อุลูฮียะฮ์ และการขจัดชิริกทุกรูปแบบ",
            "ตำราแม่บทของขบวนการฟื้นฟูนัจญ์ดีย์ มุ่งเน้นการปฏิบัติตนตามเตาฮีดบริสุทธิ์และการละทิ้งบิดอะฮ์"
        ),
        (
            "salafi", "สะละฟีย์ / อะษะรีย์ (Salafi / Athari)",
            "Al-Aqidah al-Wasitiyyah (อัล-อากีดะฮ์ อัล-วาสิฏียะฮ์)",
            "ชัยคุลอิสลาม อิบนุ ตัยมียะฮ์ (Ibn Taymiyyah)",
            "หมวดการยืนยันพระนามและคุณลักษณะของพระเจ้า (อัสมาอ์ วัศ-ศิฟาต)",
            "من الإيمان بالله: الإيمان بما وصف به نفسه في كتابه، وبما وصفه به رسوله من غير تحريف ولا تعطيل، ومن غير تكييف ولا تمثيل",
            "หนึ่งในการศรัทธาต่ออัลลอฮ์ คือ การศรัทธาต่อสิ่งซึ่งพระองค์ทรงพรรณนาถึงพระองค์เองไว้ในคัมภีร์ และสิ่งที่ศาสนทูตพรรณนาถึงพระองค์ โดยปราศจากการบิดเบือนความหมาย (ตะห์รีฟ), ปราศจากการปฏิเสธคุณลักษณะ (ตะอ์ฏีล), ปราศจากการจินตนาการสภาพ (ตักยีฟ), และปราศจากการเปรียบเหมือนสิ่งถูกสร้าง (ตัมษีล)",
            "Part of faith in Allah is to believe in how He described Himself in His Book and how His Messenger described Him, without distortion, without denial, without asking how, and without comparison to creation.",
            "ระเบียบวิธีอะษะรีย์ในการยืนยันคุณลักษณะพระเจ้า (Bila Kayf)",
            "หลักเกณฑ์ทางศาสนศาสตร์อันเป็นเสาหลักของฝ่ายสะละฟีย์ในการตีความตัวบทตามความหมายดั้งเดิม"
        ),
        # Ibadi Tradition
        (
            "ibadi", "อิบาดี (Ibadi)",
            "Musnad al-Rabi' ibn Habib (ตัรตีบ อัล-มุสนัด)",
            "อัร-รอบีอ์ บิน ฮะบีบ อัล-ฟะรอฮีดี (Al-Rabi' ibn Habib)",
            "หมวดความยุติธรรมและภาวะผู้นำ (อัล-อัดล์ วัล-อิมามะฮ์)",
            "لا فضل لعربي على عجمي ولا لأبيض على أسود إلا بالتقوى، والإمامة لمن قام بالعدل وحكم بالكتاب",
            "ไม่มีความประเสริฐใดๆ สำหรับชาวอาหรับเหนือผู้มิใช่ชาวอาหรับ และไม่มีความประเสริฐใดสำหรับคนผิวขาวเหนือคนผิวดำ เว้นแต่ด้วยความยำเกรง (ตักวา) และตำแหน่งผู้นำ (อิมามะฮ์) ย่อมเป็นของผู้ที่ยืนหยัดในความยุติธรรมและตัดสินด้วยคัมภีร์ของพระเจ้า",
            "There is no superiority for an Arab over a non-Arab, nor a white person over a black person, except through piety. Leadership belongs to whoever establishes justice and judges by the Book.",
            "ความเสมอภาคทางเชื้อชาติและภาวะผู้นำที่วัดด้วยคุณธรรม (Meritocratic Leadership)",
            "คัมภีร์ฮะดีษมาตรฐานสูงสุดของนิกายอิบาดี ปฏิเสธการผูกขาดอำนาจผู้นำตามสายตระกูลกุเรช"
        ),
        # Sufi Tradition
        (
            "sufi", "ซูฟี / ตะศ็อฟวุฟ (Sufism / Tasawwuf)",
            "Ihya Ulum al-Din (การฟื้นฟูวิทยาการศาสนา)",
            "ฮุจญะตุลอิสลาม อบู ฮามิด อัล-ฆอซาลี (Al-Ghazali)",
            "คัมภีร์แห่งความอดทนและการขอบคุณ (Kitab al-Sabr wal-Shukr)",
            "الإيمان نصفان: نصف صبر ونصف شكر، والصبر حبس النفس عن الجزع واللسان عن الشكوى",
            "การศรัทธานั้นแบ่งออกเป็นสองซีก: ซีกหนึ่งคือความอดทน (ศ็อบร์) และอีกซีกหนึ่งคือการกตัญญูขอบคุณ (ชุกร์) และความอดทนที่แท้จริงคือการยับยั้งจิตใจมิให้ทุรนทุราย และยับยั้งลิ้นมิให้พร่ำบ่นตัดพ้อต่อพระเจ้า",
            "Faith is in two halves: one half is patience (sabr) and the other half is gratitude (shukr). Patience is restraining the soul from despair and restraining the tongue from complaint.",
            "การขัดเกลาจิตใจ (ตัซกียะตุลนัฟส์) และความสมถะทางจิตวิญญาณ",
            "งานชิ้นเอกที่สังเคราะห์นิติศาสตร์ชะรีอะฮ์เข้ากับจิตวิญญาณซูฟีอย่างลงตัว"
        ),
        (
            "sufi", "ซูฟี / ตะศ็อฟวุฟ (Sufism / Tasawwuf)",
            "Masnavi-e Ma'navi (บทกวีมัษนะวี)",
            "มะวะลานา ญะลาลุดดีน รูมี (Jalal al-Din Rumi)",
            "บทนำ: บทเพลงคร่ำครวญแห่งต้นอ้อ (Ney-nameh)",
            "بشنو اين نی چون حكايت مى‌كند، از جدايى‌ها شكايت مى‌كند؛ كز نيستان تا مرا ببريده‌اند، در نفيرم مرد و زن ناليده‌اند",
            "จงสดับฟังเสียงปี่อ้อที่กำลังบอกเล่าเรื่องราว มันกำลังตัดพ้อคร่ำครวญถึงความพลัดพราก: นับแต่ที่ข้าถูกตัดขาดจากกออ้อดั้งเดิม เสียงร่ำไห้ของข้าทำให้ผู้คนทั้งหญิงชายต้องหลั่งน้ำตา (นัยถึงจิตวิญญาณมนุษย์ที่โหยหาการกลับคืนสู่พระผู้สร้าง)",
            "Listen to the reed how it tells a tale, complaining of separations: Ever since they tore me from the reedbed, my lament has caused men and women to weep.",
            "ความรักอันบริสุทธิ์ต่อพระเจ้าและการเดินทางของจิตวิญญาณ (Divine Love)",
            "มหากาพย์กวีนิพนธ์จิตวิญญาณอิสลามที่ทรงอิทธิพลระดับโลก"
        )
    ]

    for item in sect_data:
        cursor.execute("""
        INSERT INTO sect_texts (tradition, tradition_title_th, book_title, author, chapter_title, arabic_text, thai_text, english_text, doctrinal_theme, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)
        cursor.execute("""
        INSERT INTO sect_texts_fts (tradition, tradition_title_th, book_title, author, chapter_title, arabic_text, thai_text, english_text, doctrinal_theme)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item[:9])

    conn.commit()
    print(f"Successfully indexed {len(sect_data)} Sect & Theological primary texts into SQLite FTS5!")

def populate_halal_enumbers(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM halal_enumbers")
    if cursor.fetchone()[0] >= 15:
        print("[5/6] Halal E-Numbers database already populated. Skipping.")
        return

    print("\n[5/6] Populating Halal E-Number Food Additives Database...")
    cursor.execute("DELETE FROM halal_enumbers;")
    cursor.execute("DELETE FROM halal_enumbers_fts;")

    enumbers_data = [
        ("E100", "เคอร์คูมิน (Curcumin)", "Curcumin", "สีผสมอาหารสีเหลือง", "halal", "พืช (ขมิ้นชัน)", "สกัดจากเหง้าขมิ้นชันธรรมชาติ 100% ปลอดภัย ไร้สารเจือปนจากสัตว์", "มติสภาฟิกฮ์ฮาลาลสากล: ฮาลาลบริสุทธิ์ 100%"),
        ("E120", "คาร์มีน / กรดคาร์มินิก (Carmine)", "Cochineal / Carmine", "สีผสมอาหารสีแดงสด", "shubhah", "แมลง (Cochineal)", "สกัดจากแมลงโคชินีลเพศเมียบดแห้ง มักใส่ในโยเกิร์ต นมสตรอว์เบอร์รี ลิปสติก และน้ำผลไม้", "สำนักจุฬาราชมนตรีและ OIC ถือเป็นชุบฮาต/ฮะรอมเนื่องจากเป็นแมลงบกที่ไม่มีการเชือด ยกเว้นมัซฮับมาลิกีที่อนุมัติหากไม่มีพิษ"),
        ("E150a", "คาราเมลธรรมดา (Plain Caramel)", "Caramel I", "สีผสมอาหารสีน้ำตาล", "halal", "พืช/น้ำตาล", "ได้จากการให้ความร้อนแก่น้ำตาลและคาร์โบไฮเดรตบริสุทธิ์", "ฮาลาล 100%"),
        ("E160a", "เบตาแคโรทีน (Beta-Carotene)", "Carotenes", "สีผสมอาหารสีส้ม", "halal", "พืช (แครอท/ปาล์ม)", "สกัดจากพืชหรือสังเคราะห์ทางเคมี ปลอดภัย", "ฮาลาล 100%"),
        ("E200", "กรดซอร์บิก (Sorbic Acid)", "Sorbic Acid", "วัตถุกันเสีย", "halal", "เคมีสังเคราะห์", "สารกันเสียยับยั้งเชื้อรา ปลอดภัยต่อการบริโภค", "ฮาลาล 100%"),
        ("E211", "โซเดียมเบนโซเอต (Sodium Benzoate)", "Sodium Benzoate", "วัตถุกันเสีย", "halal", "เคมีสังเคราะห์", "สารกันบูดในน้ำอัดลมและอาหารแปรรูป สังเคราะห์จากสารเคมี", "ฮาลาล 100%"),
        ("E322", "เลซิติน (Lecithin)", "Lecithins", "สารทำให้เกิดอิมัลชัน", "shubhah", "พืช (ถั่วเหลือง) หรือสัตว์", "หากสกัดจากถั่วเหลือง (Soy Lecithin) = ฮาลาล 100% หากไม่ระบุแหล่งที่มาอาจสกัดจากไขมันสัตว์ ซึ่งต้องตรวจว่าเชือดถูกต้องหรือไม่", "แนะนำให้มองหาคำว่า 'Soy Lecithin' หรือตรารับรองฮาลาล"),
        ("E407", "คาราจีแนน (Carrageenan)", "Carrageenan", "สารก่อเจลและข้นหนืด", "halal", "พืช (สาหร่ายทะเลสีแดง)", "สกัดจากสาหร่ายทะเล ใช้ทดแทนเจลาตินในเยลลี่และไอศกรีม", "ฮาลาล 100% เป็นทางเลือกมุสลิมยอดนิยม"),
        ("E412", "กัวร์กัม (Guar Gum)", "Guar Gum", "สารให้ความคงตัว", "halal", "พืช (เมล็ดกัวร์)", "สารสกัดจากพืชตระกูลถั่วในอินเดียและปากีสถาน", "ฮาลาล 100%"),
        ("E415", "แซนแทนกัม (Xanthan Gum)", "Xanthan Gum", "สารให้ความหนืด", "halal", "การหมักจุลินทรีย์", "ได้จากการหมักน้ำตาลด้วยแบคทีเรีย Xanthomonas campestris", "ฮาลาล 100%"),
        ("E422", "กลีเซอรอล / กลีเซอรีน (Glycerol)", "Glycerol", "สารกักเก็บความชื้น", "shubhah", "พืชหรือไขมันสัตว์", "หากเป็น Vegetable Glycerin = ฮาลาล หากผลิตจากไขมันสัตว์อาจมาจากสุกรหรือสัตว์ไม่เชือด", "หากไม่มีตรารับรองฮาลาลให้หลีกเลี่ยง"),
        ("E441", "เจลาติน (Gelatin)", "Gelatin", "สารก่อเจลในเยลลี่และแคปซูล", "shubhah", "หนังสัตว์ กระดูกสัตว์ (สุกร/วัว)", "หากทำจากสุกร = ฮะรอมเด็ดขาด หากทำจากวัวเชือดฮาลาล หรือปลา = ฮาลาล", "ต้องตรวจสอบตรารับรองฮาลาลบนบรรจุภัณฑ์เสมอ ห้ามรับประทานโดยไม่ตรวจสอบ"),
        ("E471", "โมโนและไดกลีเซอไรด์ (Mono- and di-glycerides)", "Mono- and di-glycerides", "สารประสานไขมันในเบเกอรี่", "shubhah", "ไขมันพืช (ปาล์ม) หรือไขมันสัตว์", "นิยมใส่ในขนมปัง เค้ก เนยเทียม ไอศกรีม หากสกัดจากน้ำมันปาล์มถือเป็นฮาลาล หากสกัดจากไขมันสัตว์หมูถือเป็นฮะรอม", "มติสภาฟิกฮ์: ต้องตรวจสอบระบุ 'Plant-origin' หรือมีตรารับรองฮาลาล"),
        ("E621", "โมโนโซเดียมกลูตาเมต (ผงชูรส MSG)", "Monosodium Glutamate", "วัตถุปรุงแต่งรสอาหาร", "halal", "การหมักกากน้ำตาลและแป้ง", "ผลิตจากการหมักทางชีวภาพของแป้งมันสำปะหลังหรือกากน้ำตาลอ้อย", "ฮาลาล 100% (สำนักงานคณะกรรมการกลางอิสลามฯ รับรอง)"),
        ("E904", "เชลแล็ก (Shellac)", "Shellac", "สารเคลือบผิวเงา", "halal", "สารคัดหลั่งจากแมลงครั่ง", "สารเคลือบเงาเม็ดยา ช็อกโกแลต และผลไม้ สกัดจากเรซินที่แมลงครั่งขับออกมา ไม่ใช่ตัวแมลง", "มติ OIC-IFA และสภาฟิกฮ์ส่วนใหญ่: สะอาด (ฏอฮิร) และอนุมัติให้บริโภคได้"),
        ("E920", "แอล-ซิสเตอีน (L-cysteine)", "L-cysteine hydrochloride", "สารปรับปรุงคุณภาพแป้ง", "shubhah", "เส้นผมมนุษย์ หรือขนเป็ดไก่", "หากสกัดจากเส้นผมมนุษย์ถือเป็น ฮะรอมเด็ดขาด (ห้ามละเมิดเกียรติมนุษย์) หากสกัดจากขนเป็ดไก่ที่เชือดถูกต้องหรือสังเคราะห์ทางเคมีถือเป็น ฮาลาล", "สภาฟิกฮ์นานาชาติสั่งห้ามใช้ L-cysteine จากเส้นผมมนุษย์ 100%")
    ]

    for item in enumbers_data:
        cursor.execute("""
        INSERT INTO halal_enumbers (e_number, name_th, name_en, category, halal_status, source_origin, explanation, authority_fatwa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, item)
        cursor.execute("""
        INSERT INTO halal_enumbers_fts (e_number, name_th, name_en, category, halal_status, source_origin, explanation, authority_fatwa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    print(f"Successfully indexed {len(enumbers_data)} Halal E-Number additives into SQLite FTS5!")

def populate_quran_roots(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM quran_roots")
    if cursor.fetchone()[0] >= 8:
        print("[6/6] Quranic Root Words database already populated. Skipping.")
        return

    print("\n[6/6] Populating Quranic Tri-Literal Root Words & Morphology Database...")
    cursor.execute("DELETE FROM quran_roots;")

    roots_data = [
        (
            "س ل م", "S-L-M", "สันติภาพ, ความปลอดภัย, การยอมจำนนนอบน้อม", 140,
            json.dumps(["إسلام (อิสลาม)", "مسلم (มุสลิม)", "سلام (สันติสุข)", "سليم (หัวใจบริสุทธิ์)", "تسليم (การยอมจำนน)", "سلم (สันติภาพ)"], ensure_ascii=False),
            "อัล-บะเกาะเราะฮ์ 2:208 'โอ้บรรดาผู้ศรัทธาเอ๋ย จงเข้าสู่อิสลาม (ความสันติ) โดยดุษณีทั้งมวล'",
            "รากศัพท์แห่งชื่อศาสนา 'อิสลาม' และ 'มุสลิม' สะท้อนความหมายแฝงคู่ขนาน: การยอมจำนนต่อพระผู้สร้างนำมาซึ่งสันติสุขที่แท้จริง"
        ),
        (
            "ر ح م", "R-H-M", "ความรักความเมตตากรุณา, มดลูก/ครรภ์มารดา", 339,
            json.dumps(["رحمن (ผู้ทรงกรุณาปราณี)", "رحيم (ผู้ทรงเมตตาเสมอ)", "رحمة (ความเมตตา)", "أرحام (สายสัมพันธ์เครือญาติ)", "مرحمة (การเกื้อกูล)"], ensure_ascii=False),
            "อัล-อันบิยาอ์ 21:107 'และเรามิได้ส่งเจ้ามาเพื่ออื่นใด เว้นแต่เพื่อเป็นความเมตตาแก่สากลจักรวาล'",
            "พระคุณลักษณะเด่นที่สุดของอัลลอฮ์ ปรากฏในบิสมิลลาฮ์ต้นทุกซูเราะฮ์ ความเมตตาของพระองค์มีชัยเหนือความกริ้วโกรธ"
        ),
        (
            "ع ل م", "'-L-M", "ความรู้, ปัญญา, เครื่องหมาย, สากลจักรวาล", 854,
            json.dumps(["علم (ความรู้)", "عالم (ผู้รู้/นักปราชญ์)", "عالمين (สากลโลก)", "معلم (ครูผู้สอน)", "علام (ผู้ทรงรอบรู้อย่างยิ่ง)"], ensure_ascii=False),
            "อัล-อะลัก 96:4-5 'ผู้ทรงสอนด้วยปากกา ผู้ทรงสอนมนุษย์ในสิ่งที่เขาไม่รู้มาก่อน'",
            "อิสลามเป็นศาสนาแห่งปัญญาและวิทยาการ คำสั่งแรกที่ประทานลงมาคือ 'จงอ่าน' และรากศัพท์นี้ปรากฏบ่อยเป็นอันดับต้นๆ ในคัมภีร์"
        ),
        (
            "ك ت ب", "K-T-B", "การขีดเขียน, การบันทึกคัมภีร์, การกำหนดกฎหมาย", 319,
            json.dumps(["كتاب (คัมภีร์/หนังสือ)", "كتب (เขียน/บัญญัติ)", "كاتب (ผู้บันทึก/เสมียน)", "مكتوب (สิ่งที่ถูกลิขิตไว้)", "كتابة (การเขียน)"], ensure_ascii=False),
            "อัล-บะเกาะเราะฮ์ 2:2 'นั่นคือคัมภีร์ที่ไม่มีข้อเคลือบแคลงสงสัย เป็นทางนำแก่บรรดาผู้ยำเกรง'",
            "ตอกย้ำว่าวิวรณ์แห่งพระเจ้าถูกธำรงไว้ในรูปแบบลายลักษณ์อักษรที่เที่ยงตรง ไม่สูญสลาย และกฎหมายมีสถานะเป็นพันธสัญญาที่แน่นอน"
        ),
        (
            "ع ب د", "'-B-D", "การเคารพบูชา, ความเป็นบ่าว, การนอบน้อมถ่อมตน", 275,
            json.dumps(["عبادة (การเคารพบูชา/อิบาดะฮ์)", "عبد (บ่าว/ผู้รับใช้)", "عباد (ปวงบ่าว)", "معبود (ผู้ได้รับการกราบไหว้)"], ensure_ascii=False),
            "อัซ-ซาริยาต 51:56 'และข้ามิได้สร้างญินและมนุษย์มาเพื่ออื่นใด เว้นแต่เพื่อให้พวกเขาเคารพภักดีต่อข้า'",
            "จุดประสงค์สูงสุดแห่งการมีอยู่ของมนุษยชาติ ความเป็น 'อับดุลลอฮ์' (บ่าวของพระเจ้า) คือเกียรติยศสูงสุดที่ปลดแอกมนุษย์จากการเป็นทาสของวัตถุ"
        ),
        (
            "ح ك م", "H-K-M", "การตัดสิน, กฎเกณฑ์, วิทยปัญญา, การควบคุม", 210,
            json.dumps(["حكم (ฮุก่ม/คำพิพากษา)", "حكمة (วิทยปัญญา/ฮิกมะฮ์)", "حاكم (ผู้ปกครอง/ผู้พิพากษา)", "محكم (ข้อความกระจ่างชัด)"], ensure_ascii=False),
            "อัล-บะเกาะเราะฮ์ 2:269 'ผู้ใดที่ได้รับวิทยปัญญา แน่นอนเขาได้รับความดีงามอันล้นพ้น'",
            "รากฐานของนิติศาสตร์ชะรีอะฮ์ กฎเกณฑ์ทุกข้อที่พระเจ้ากำหนดขึ้นล้วนแฝงไว้ด้วย 'ฮิกมะฮ์' (วิทยปัญญาอันลึกซึ้ง) เพื่อพิทักษ์มนุษย์"
        ),
        (
            "ن ف س", "N-F-S", "จิตวิญญาณ, ตัวตน, ชีวิต, การหายใจ", 298,
            json.dumps(["نفس (จิตใจ/ตัวตน/นัฟส์)", "أنفس (จิตใจทั้งหลาย)", "نفيس (สิ่งล้ำค่า)", "تنفس (การหายใจ)"], ensure_ascii=False),
            "อัช-ชัมส์ 91:7-9 'ขอสาบานด้วยจิตวิญญาณและผู้ทรงปรับแต่งมัน... แท้จริงผู้ที่ขัดเกลามันย่อมประสบความสำเร็จ'",
            "หัวใจของศาสตร์จิตวิทยาอิสลามและการขัดเกลาจิตใจ (ตัซกียะฮ์) จิตใจมนุษย์มีทั้งระดับใฝ่ต่ำ (อัมมาระฮ์) ตักเตือน (ลัววามะฮ์) และสงบสุข (มุฏมะอินนะฮ์)"
        ),
        (
            "ق د ر", "Q-D-R", "สัดส่วน, อำนาจความสามารถ, กำหนดสภาวการณ์, เกียรติยศ", 132,
            json.dumps(["قدر (ลิขิตสภาวะ/กอดัร)", "تقدير (การกำหนดสัดส่วน)", "قدير (ผู้ทรงอานุภาพ)", "مقدار (ปริมาณ/มาตรวัด)", "ليلة القدر (ค่ำคืนอัล-ก็อดร์)"], ensure_ascii=False),
            "อัล-ก็อมัร 54:49 'แท้จริงทุกๆ สิ่งนั้น เราได้สร้างมันขึ้นมาตามสัดส่วนที่ถูกกำหนดไว้อย่างแม่นยำ (กอดัร)'",
            "เสาหลักข้อที่ 6 แห่งความศรัทธา: ทุกสรรพสิ่งในจักรวาลมีสัดส่วน กฎเกณฑ์ และการวัดที่ประณีตสมบูรณ์แบบ"
        )
    ]

    for item in roots_data:
        cursor.execute("""
        INSERT INTO quran_roots (root_ar, root_lat, meaning_th, frequency_in_quran, derived_words, sample_ayah, theological_significance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    print(f"Successfully indexed {len(roots_data)} Quranic tri-literal root words into SQLite!")

def main():
    print("==================================================================")
    print("  Islamic Big Corpus Compiler (Grand Upgrade Edition)")
    print("  Quran + Kutub al-Sittah + Fatwas + Sect Texts + E-Numbers + Roots")
    print(f"  Target DB: {DB_PATH}")
    print("==================================================================")

    conn = sqlite3.connect(DB_PATH)
    try:
        init_db(conn)
        populate_surahs(conn)
        populate_quran(conn)
        populate_all_hadiths(conn)
        populate_contemporary_fatwas(conn)
        populate_sect_texts(conn)
        populate_halal_enumbers(conn)
        populate_quran_roots(conn)
        print("\nAll database population tasks completed successfully!")
        print(f"Database final size: {os.path.getsize(DB_PATH) / (1024 * 1024):.2f} MB")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

