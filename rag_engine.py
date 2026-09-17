#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Islamic Big Corpus RAG Engine (Quran 6,236 Ayahs + Hadith 34,614+ Passages + Contemporary Fatwas)
Complete Kutub al-Sittah: Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah + Nawawi + Qudsi.
Sub-millisecond retrieval with SQLite FTS5, BM25 ranking, and Bilingual Semantic Keyword Mapping.
"""

import os
import sys
import json
import sqlite3
import argparse
import math
import datetime
from fractions import Fraction

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "quran_hadith_corpus.db")

# Auto-extract database if only the compressed zip archive is present
if not os.path.exists(DB_PATH):
    _zip_db_path = DB_PATH + ".zip"
    if os.path.exists(_zip_db_path):
        import zipfile
        try:
            with zipfile.ZipFile(_zip_db_path, "r") as _zf:
                _zf.extractall(os.path.join(os.path.dirname(__file__), "data"))
        except Exception:
            pass


# Bilingual Thai -> English Keyword Dictionary for Hadith Search
THAI_TO_ENG_KEYWORDS = {
    "เจตนา": ["intention", "intentions", "deeds", "niyyah"],
    "เหนียต": ["intention", "intentions", "niyyah"],
    "ละหมาด": ["prayer", "prayers", "salat", "prostration", "mosque", "imam", "worship"],
    "การละหมาด": ["prayer", "prayers", "salat", "prostration"],
    "ศีลอด": ["fasting", "fast", "ramadan", "sawm", "iftar"],
    "การถือศีลอด": ["fasting", "fast", "ramadan", "sawm"],
    "ซะกาต": ["zakat", "charity", "alms", "poor", "sadaqah", "wealth"],
    "ทาน": ["charity", "alms", "sadaqah", "giving"],
    "ฮัจญ์": ["hajj", "pilgrimage", "kaaba", "makkah", "tawaf", "arafat"],
    "การทำฮัจญ์": ["hajj", "pilgrimage", "makkah"],
    "ความอดทน": ["patience", "patient", "sabr", "affliction", "calamity", "grief"],
    "อดทน": ["patience", "patient", "sabr"],
    "ดอกเบี้ย": ["usury", "riba", "interest"],
    "การค้า": ["trade", "sale", "selling", "merchant", "business", "transaction", "buyer", "seller"],
    "ค้าขาย": ["trade", "sale", "selling", "merchant", "business"],
    "อาวุธ": ["weapon", "weapons", "sword", "swords", "arms", "iron", "armor", "fighting", "battle", "war"],
    "ขายอาวุธ": ["weapon", "weapons", "sword", "arms", "sale", "trade"],
    "ส้วม": ["toilet", "privy", "relieve", "relieving", "lavatory", "bathroom", "wudu", "filth", "impurity"],
    "ห้องน้ำ": ["toilet", "privy", "relieve", "relieving", "bathroom", "wudu"],
    "กรรไกร": ["scissors", "shears", "cut"],
    "กระท่อม": ["intoxicant", "intoxicants", "khamr", "drug", "narcotic", "poison", "harm"],
    "น้ำท่อม": ["intoxicant", "intoxicants", "khamr", "drug", "narcotic"],
    "หุ้น": ["wealth", "money", "usury", "riba", "trade", "investment", "partnership", "debt", "share"],
    "การเงิน": ["wealth", "money", "usury", "riba", "trade", "investment", "debt", "gold", "silver"],
    "ดนตรี": ["music", "musical", "instruments", "singing", "flute", "drum", "duff"],
    "เพลง": ["singing", "song", "musical", "instruments", "music"],
    "หมู": ["swine", "pork", "pig"],
    "หมา": ["dog", "dogs", "hunting dog", "saliva"],
    "สุนัข": ["dog", "dogs", "hunting dog", "saliva"],
    "แมว": ["cat", "cats"],
    "อวกาศ": ["heavens", "earth", "creation", "stars", "creatures"],
    "เอเลี่ยน": ["creation", "heavens", "earth", "creatures", "created"],
    "ชุบฮาต": ["doubt", "doubtful", "suspicious", "shubuhat"],
    "คลุมเครือ": ["doubt", "doubtful", "suspicious", "unclear"],
    "อิคติลาฟ": ["difference", "disagreement", "opinion", "dispute", "consensus"],
    "ความเห็นต่าง": ["difference", "disagreement", "opinion", "dispute"],
    "นาฟะเกาะฮ์": ["maintenance", "spending", "family", "wife", "dependents", "nafaqah"],
    "ค่าเลี้ยงดู": ["maintenance", "spending", "family", "wife", "children", "dependents"],
    "เจลาติน": ["carrion", "pork", "swine", "lawful", "unlawful"],
    "มิริน": ["alcohol", "wine", "khamr", "intoxicant", "intoxicants"],
    "พ่อแม่": ["parents", "mother", "father", "dutiful", "undutiful"],
    "บิดามารดา": ["parents", "mother", "father", "kindness to parents"],
    "มารยาท": ["manner", "manners", "etiquette", "character", "conduct", "akhlaq"],
    "ความซื่อสัตย์": ["honesty", "truthful", "truth", "sincere", "trustworthy"],
    "สัจจะ": ["truth", "truthfulness", "honest"],
    "ความรู้": ["knowledge", "scholar", "learn", "teach", "seeking knowledge"],
    "การศึกษา": ["knowledge", "scholar", "seeking knowledge"],
    "การให้อภัย": ["forgiveness", "pardon", "mercy", "forgive", "merciful"],
    "อภัย": ["forgiveness", "pardon", "mercy", "forgive"],
    "เพื่อนบ้าน": ["neighbor", "neighbour", "neighbors"],
    "ความโกรธ": ["anger", "angry", "wrath", "rage"],
    "โกรธ": ["anger", "angry"],
    "สวรรค์": ["paradise", "jannah", "gardens", "dwellers of paradise"],
    "นรก": ["hell", "fire", "punishment", "jahannam", "dwellers of the fire"],
    "ความยุติธรรม": ["justice", "fairness", "oppression", "unjust", "oppressor"],
    "ความสะอาด": ["ablution", "wudu", "purification", "cleanliness", "ghusl"],
    "น้ำละหมาด": ["ablution", "wudu", "purification"],
    "ศรัทธา": ["faith", "belief", "iman", "believer", "believers"],
    "ความศรัทธา": ["faith", "belief", "iman"],
    "ความดี": ["good deeds", "righteous", "virtue", "piety"],
    "ความชั่ว": ["evil", "sin", "transgression", "wicked"],
    "การขอดุอาอ์": ["supplication", "dua", "invoke", "invoking"],
    "ดุอาอ์": ["supplication", "dua", "prayer"],
    "ความตาย": ["death", "dying", "grave", "funeral"],
    "หลุมศพ": ["grave", "graves", "punishment in the grave"],
    "พี่น้อง": ["brother", "brotherhood", "muslims are brothers"],
    "การนินทา": ["backbiting", "slander", "calumny"],
    "การแต่งงาน": ["marriage", "marry", "nikah", "wedding", "wife", "husband"],
    "การหย่า": ["divorce", "talaq"],
    "ลูกสาว": ["daughter", "daughters", "girls"],
    "สตรี": ["women", "woman", "female", "wife"],
    "อาหาร": ["food", "eating", "drink", "lawful", "unlawful"],
}

def get_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Corpus database not found at: {DB_PATH}. Run compile_corpus.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- Quran Operations -----------------

def get_exact_ayah(surah_number, ayah_number):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT q.surah_number, q.ayah_number, s.name_th, s.name_ar, s.name_en, s.revelation_type,
               q.arabic_text, q.thai_text
        FROM quran q
        JOIN surahs s ON q.surah_number = s.number
        WHERE q.surah_number = ? AND q.ayah_number = ?
        """, (surah_number, ayah_number))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def search_quran(query_text, limit=5, surah_filter=None):
    conn = get_connection()
    results = []
    try:
        cursor = conn.cursor()
        clean_q = query_text.strip().replace('"', '""')

        # 1. Try FTS5 MATCH
        try:
            if surah_filter:
                fts_sql = """
                SELECT q.surah_number, q.ayah_number, q.surah_name, q.arabic_text, q.thai_text,
                       bm25(quran_fts) as rank
                FROM quran_fts q
                WHERE quran_fts MATCH ? AND q.surah_number = ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(fts_sql, (f'"{clean_q}"*', surah_filter, limit))
            else:
                fts_sql = """
                SELECT q.surah_number, q.ayah_number, q.surah_name, q.arabic_text, q.thai_text,
                       bm25(quran_fts) as rank
                FROM quran_fts q
                WHERE quran_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(fts_sql, (f'"{clean_q}"*', limit))
            for r in cursor.fetchall():
                results.append(dict(r))
        except Exception:
            pass

        # 2. Fallback to SQL LIKE for Thai substrings
        if len(results) < limit:
            existing_keys = {(r["surah_number"], r["ayah_number"]) for r in results}
            remaining = limit - len(results)
            like_pattern = f"%{clean_q}%"
            if surah_filter:
                like_sql = """
                SELECT q.surah_number, q.ayah_number, s.name_th as surah_name, q.arabic_text, q.thai_text, 999.0 as rank
                FROM quran q
                JOIN surahs s ON q.surah_number = s.number
                WHERE q.surah_number = ? AND (q.thai_text LIKE ? OR q.arabic_text LIKE ?)
                LIMIT ?
                """
                cursor.execute(like_sql, (surah_filter, like_pattern, like_pattern, remaining + 10))
            else:
                like_sql = """
                SELECT q.surah_number, q.ayah_number, s.name_th as surah_name, q.arabic_text, q.thai_text, 999.0 as rank
                FROM quran q
                JOIN surahs s ON q.surah_number = s.number
                WHERE q.thai_text LIKE ? OR q.arabic_text LIKE ?
                LIMIT ?
                """
                cursor.execute(like_sql, (like_pattern, like_pattern, remaining + 10))
                
            for r in cursor.fetchall():
                key = (r["surah_number"], r["ayah_number"])
                if key not in existing_keys:
                    results.append(dict(r))
                    existing_keys.add(key)
                if len(results) >= limit:
                    break

        return results
    finally:
        conn.close()

# ----------------- Hadith Operations -----------------

def get_exact_hadith(collection, hadith_number):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        col_key = collection.lower().strip()
        cursor.execute("""
        SELECT collection, collection_title, hadith_number, book_number, chapter_title,
               arabic_text, english_text, grade
        FROM hadiths
        WHERE (collection = ? OR collection_title LIKE ?) AND hadith_number = ?
        """, (col_key, f"%{col_key}%", hadith_number))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def search_hadith(query_text, limit=5, collection_filter=None):
    """
    Searches 34,600+ hadiths (Complete Kutub al-Sittah + Nawawi + Qudsi) using bilingual mapping + FTS5 BM25.
    """
    conn = get_connection()
    results = []
    try:
        cursor = conn.cursor()
        clean_q = query_text.strip()

        # Check for Thai keyword expansions
        search_terms = [clean_q]
        for th_key, eng_list in THAI_TO_ENG_KEYWORDS.items():
            if th_key in clean_q:
                search_terms.extend(eng_list)

        existing_ids = set()

        # Query FTS5 for each term
        for term in search_terms:
            if len(results) >= limit:
                break
            safe_term = term.replace('"', '""')
            try:
                if collection_filter:
                    sql = """
                    WITH top_fts AS (
                        SELECT collection, collection_title, hadith_number, chapter_title, arabic_text, english_text,
                               bm25(hadiths_fts) as rank
                        FROM hadiths_fts
                        WHERE hadiths_fts MATCH ? AND collection = ?
                        ORDER BY rank
                        LIMIT ?
                    )
                    SELECT t.*, coalesce(h.grade, 'Sahih') as grade
                    FROM top_fts t
                    LEFT JOIN hadiths h ON t.collection = h.collection AND t.hadith_number = h.hadith_number
                    """
                    cursor.execute(sql, (f'"{safe_term}"*', collection_filter.lower(), limit - len(results)))
                else:
                    sql = """
                    WITH top_fts AS (
                        SELECT collection, collection_title, hadith_number, chapter_title, arabic_text, english_text,
                               bm25(hadiths_fts) as rank
                        FROM hadiths_fts
                        WHERE hadiths_fts MATCH ?
                        ORDER BY rank
                        LIMIT ?
                    )
                    SELECT t.*, coalesce(h.grade, 'Sahih') as grade
                    FROM top_fts t
                    LEFT JOIN hadiths h ON t.collection = h.collection AND t.hadith_number = h.hadith_number
                    """
                    cursor.execute(sql, (f'"{safe_term}"*', limit - len(results)))

                for r in cursor.fetchall():
                    item = dict(r)
                    key = (item["collection"], item["hadith_number"])
                    if key not in existing_ids:
                        results.append(item)
                        existing_ids.add(key)
            except Exception:
                # Fallback to LIKE
                like_pat = f"%{term}%"
                if collection_filter:
                    like_sql = """
                    SELECT collection, collection_title, hadith_number, chapter_title, arabic_text, english_text, grade, 999.0 as rank
                    FROM hadiths
                    WHERE collection = ? AND (english_text LIKE ? OR arabic_text LIKE ? OR chapter_title LIKE ?)
                    LIMIT ?
                    """
                    cursor.execute(like_sql, (collection_filter.lower(), like_pat, like_pat, like_pat, limit - len(results)))
                else:
                    like_sql = """
                    SELECT collection, collection_title, hadith_number, chapter_title, arabic_text, english_text, grade, 999.0 as rank
                    FROM hadiths
                    WHERE english_text LIKE ? OR arabic_text LIKE ? OR chapter_title LIKE ?
                    LIMIT ?
                    """
                    cursor.execute(like_sql, (like_pat, like_pat, like_pat, limit - len(results)))

                for r in cursor.fetchall():
                    item = dict(r)
                    key = (item["collection"], item["hadith_number"])
                    if key not in existing_ids:
                        results.append(item)
                        existing_ids.add(key)

        return results[:limit]
    finally:
        conn.close()

# ----------------- Contemporary Fatwa Operations -----------------

def get_fatwa(query_id_or_title):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if str(query_id_or_title).isdigit():
            cursor.execute("""
            SELECT id, category, title_th, ruling_summary, detailed_explanation,
                   authorities, primary_evidences
            FROM contemporary_fatwas
            WHERE id = ?
            """, (int(query_id_or_title),))
        else:
            cursor.execute("""
            SELECT id, category, title_th, ruling_summary, detailed_explanation,
                   authorities, primary_evidences
            FROM contemporary_fatwas
            WHERE title_th LIKE ? OR category LIKE ?
            LIMIT 1
            """, (f"%{query_id_or_title}%", f"%{query_id_or_title}%"))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def search_fatwas(query_text, limit=5, category_filter=None):
    """
    Searches contemporary fatwas using FTS5 and LIKE fallback.
    """
    conn = get_connection()
    results = []
    try:
        cursor = conn.cursor()
        clean_q = query_text.strip().replace('"', '""')

        # 1. FTS5 MATCH
        try:
            if category_filter:
                sql = """
                SELECT rowid as id, category, title_th, ruling_summary, detailed_explanation,
                       authorities, primary_evidences,
                       bm25(contemporary_fatwas_fts) as rank
                FROM contemporary_fatwas_fts
                WHERE contemporary_fatwas_fts MATCH ? AND category = ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(sql, (f'"{clean_q}"*', category_filter, limit))
            else:
                sql = """
                SELECT rowid as id, category, title_th, ruling_summary, detailed_explanation,
                       authorities, primary_evidences,
                       bm25(contemporary_fatwas_fts) as rank
                FROM contemporary_fatwas_fts
                WHERE contemporary_fatwas_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(sql, (f'"{clean_q}"*', limit))
            for r in cursor.fetchall():
                results.append(dict(r))
        except Exception:
            pass

        # 2. LIKE fallback
        if len(results) < limit:
            existing_ids = {r["id"] for r in results}
            like_pat = f"%{query_text.strip()}%"
            if category_filter:
                like_sql = """
                SELECT id, category, title_th, ruling_summary, detailed_explanation,
                       authorities, primary_evidences, 999.0 as rank
                FROM contemporary_fatwas
                WHERE category = ? AND (title_th LIKE ? OR ruling_summary LIKE ? OR detailed_explanation LIKE ?)
                LIMIT ?
                """
                cursor.execute(like_sql, (category_filter, like_pat, like_pat, like_pat, limit - len(results)))
            else:
                like_sql = """
                SELECT id, category, title_th, ruling_summary, detailed_explanation,
                       authorities, primary_evidences, 999.0 as rank
                FROM contemporary_fatwas
                WHERE title_th LIKE ? OR ruling_summary LIKE ? OR detailed_explanation LIKE ? OR category LIKE ?
                LIMIT ?
                """
                cursor.execute(like_sql, (like_pat, like_pat, like_pat, like_pat, limit - len(results)))
            for r in cursor.fetchall():
                if r["id"] not in existing_ids:
                    results.append(dict(r))
                    existing_ids.add(r["id"])

        return results[:limit]
    finally:
        conn.close()

# ----------------- Islamic Inheritance (Mirath / Ilm al-Fara'id) Engine -----------------

def calculate_mirath(net_estate=0.0, heirs=None, debts=0.0, funeral=0.0, washiyyah=0.0, estate=None, wills=None):
    """
    Calculates Islamic inheritance according to Surah An-Nisa (4:11, 12, 176) and Sunnah.
    Handles debts, funeral expenses, washiyyah (will capped at 1/3), Ashab al-Furud,
    Asabah, Hajb (blocking), Awl (deficit), and Radd (surplus).
    """
    if heirs is None:
        heirs = {}
    if estate is not None:
        net_estate = estate
    if wills is not None:
        washiyyah = wills

    estate = max(0.0, float(net_estate))
    debts = max(0.0, float(debts))
    funeral = max(0.0, float(funeral))
    requested_wills = max(0.0, float(washiyyah))


    # Priority 1 & 2: Funeral & Debts
    after_deductions = max(0.0, estate - debts - funeral)

    # Priority 3: Washiyyah (Will capped at max 1/3 of net remaining)
    max_wills_allowed = after_deductions / 3.0
    actual_wills = min(requested_wills, max_wills_allowed)
    distributable_estate = max(0.0, after_deductions - actual_wills)

    # Extract heirs
    husband = bool(heirs.get("husband", False))
    wives_count = max(0, int(heirs.get("wives", heirs.get("wife", 0))))
    sons_count = max(0, int(heirs.get("sons", heirs.get("son", 0))))
    daughters_count = max(0, int(heirs.get("daughters", heirs.get("daughter", 0))))
    father = bool(heirs.get("father", False))
    mother = bool(heirs.get("mother", False))
    brothers_count = max(0, int(heirs.get("brothers", heirs.get("brother", 0))))
    sisters_count = max(0, int(heirs.get("sisters", heirs.get("sister", 0))))

    has_children = (sons_count > 0 or daughters_count > 0)
    has_male_descendant = (sons_count > 0)
    total_siblings = brothers_count + sisters_count

    hajb_notes = []
    # Hajb al-Hirman (Full Exclusion Rules)
    if sons_count > 0:
        if brothers_count > 0 or sisters_count > 0:
            hajb_notes.append("บุตรชายกีดกันพี่น้องทั้งหมดจากการรับมรดก (Al-Hajb al-Hirman)")
            brothers_count = 0
            sisters_count = 0
    if father:
        if brothers_count > 0 or sisters_count > 0:
            hajb_notes.append("บิดากีดกันพี่น้องทั้งหมดจากการรับมรดก (Al-Hajb al-Hirman)")
            brothers_count = 0
            sisters_count = 0

    fixed_shares = {}

    # 1. Spouses (Ashab al-Furud)
    if husband:
        fixed_shares["สามี (Husband)"] = Fraction(1, 4) if has_children else Fraction(1, 2)
    elif wives_count > 0:
        total_wife_share = Fraction(1, 8) if has_children else Fraction(1, 4)
        fixed_shares[f"ภรรยา ({wives_count} ท่าน)"] = total_wife_share

    # 2. Mother
    if mother:
        if has_children or total_siblings >= 2:
            fixed_shares["มารดา (Mother)"] = Fraction(1, 6)
        else:
            fixed_shares["มารดา (Mother)"] = Fraction(1, 3)

    # 3. Father
    if father:
        if has_male_descendant:
            fixed_shares["บิดา (Father - ฟัรฎ์ 1/6)"] = Fraction(1, 6)
        elif daughters_count > 0:
            fixed_shares["บิดา (Father - ฟัรฎ์ 1/6 + อะเศาะบะฮ์)"] = Fraction(1, 6)
        else:
            # Father is purely Asabah if no children
            pass

    # 4. Daughters (without sons)
    if daughters_count > 0 and sons_count == 0:
        if daughters_count == 1:
            fixed_shares["บุตรสาว (1 คน)"] = Fraction(1, 2)
        else:
            fixed_shares[f"บุตรสาว ({daughters_count} คน)"] = Fraction(2, 3)

    # 5. Sisters (without children, father, brothers)
    if sisters_count > 0 and not has_children and not father and brothers_count == 0:
        if sisters_count == 1:
            fixed_shares["พี่สาว/น้องสาว (1 คน)"] = Fraction(1, 2)
        else:
            fixed_shares[f"พี่สาว/น้องสาว ({sisters_count} คน)"] = Fraction(2, 3)

    sum_fixed = sum(fixed_shares.values())
    adjustment_type = "None"
    final_shares = {}

    # Check for Al-Awl (Deficit) first: If sum of fixed shares exceeds 1, no Asabah remainder exists
    if sum_fixed > 1:
        adjustment_type = "Al-Awl (อัล-เอาล์ - ทอนสัดส่วนลงตามฐานรวมเศษส่วน)"
        for k, frac in fixed_shares.items():
            final_shares[k] = frac / sum_fixed
    # Check for Asabah heirs when sum_fixed <= 1
    elif sons_count > 0:
        # Residuary with sons and daughters
        remainder = max(Fraction(0, 1), Fraction(1, 1) - sum_fixed)
        final_shares = dict(fixed_shares)
        total_parts = 2 * sons_count + daughters_count
        if total_parts > 0 and remainder > 0:
            final_shares[f"บุตรชาย ({sons_count} คน) [อะเศาะบะฮ์]"] = remainder * Fraction(2 * sons_count, total_parts)
            if daughters_count > 0:
                final_shares[f"บุตรสาว ({daughters_count} คน) [อะเศาะบะฮ์ร่วม]"] = remainder * Fraction(daughters_count, total_parts)
        adjustment_type = "Asabah Distribution (จัดสรรส่วนเหลือแก่อะเศาะบะฮ์ ชายได้ 2 เท่าของหญิง)"
    elif father and daughters_count > 0:
        remainder = max(Fraction(0, 1), Fraction(1, 1) - sum_fixed)
        final_shares = dict(fixed_shares)
        father_key = "บิดา (Father - ฟัรฎ์ 1/6 + อะเศาะบะฮ์)"
        final_shares[father_key] = fixed_shares[father_key] + remainder
        adjustment_type = "Father Fard + Asabah (บิดารับฟัรฎ์ 1/6 และรับส่วนเหลือทั้งหมด)"
    elif father and not has_children:
        remainder = max(Fraction(0, 1), Fraction(1, 1) - sum_fixed)
        final_shares = dict(fixed_shares)
        final_shares["บิดา (Father) [อะเศาะบะฮ์]"] = remainder
        adjustment_type = "Father Asabah (บิดารับส่วนเหลือทั้งหมด)"
    elif not has_children and not father and brothers_count > 0:
        remainder = max(Fraction(0, 1), Fraction(1, 1) - sum_fixed)
        final_shares = dict(fixed_shares)
        total_parts = 2 * brothers_count + sisters_count
        if total_parts > 0 and remainder > 0:
            final_shares[f"พี่/น้องชาย ({brothers_count} คน) [อะเศาะบะฮ์]"] = remainder * Fraction(2 * brothers_count, total_parts)
            if sisters_count > 0:
                final_shares[f"พี่/น้องสาว ({sisters_count} คน) [อะเศาะบะฮ์ร่วม]"] = remainder * Fraction(sisters_count, total_parts)
        adjustment_type = "Siblings Asabah (พี่น้องรับส่วนเหลือ)"

    elif sum_fixed == 1:
        adjustment_type = "Exact Match (สัดส่วนลงตัวพอดี 100%)"
        final_shares = dict(fixed_shares)
    elif sum_fixed > 0:
        # Al-Radd (Surplus) - Return to non-spouse Ashab al-Furud proportionally
        non_spouse = {k: v for k, v in fixed_shares.items() if "สามี" not in k and "ภรรยา" not in k}
        spouse = {k: v for k, v in fixed_shares.items() if "สามี" in k or "ภรรยา" in k}
        if non_spouse:
            adjustment_type = "Al-Radd (อัร-ร็อดด์ - ปันส่วนเหลือคืนแก่ทายาทสายโลหิต)"
            for k, v in spouse.items():
                final_shares[k] = v
            non_spouse_distributable = Fraction(1, 1) - sum(spouse.values())
            non_spouse_sum = sum(non_spouse.values())
            for k, v in non_spouse.items():
                final_shares[k] = (v / non_spouse_sum) * non_spouse_distributable
        else:
            final_shares = dict(fixed_shares)
            adjustment_type = "Surplus to Public Treasury (บัยตุลมาล) / คู่สมรส"
    else:
        adjustment_type = "No Heirs (ไม่มีทายาท - ตกเป็นของกองทุนสาธารณะประโยชน์ บัยตุลมาล)"

    results_breakdown = []
    for k, frac in final_shares.items():
        pct = float(frac) * 100.0
        amt = float(frac) * distributable_estate
        results_breakdown.append({
            "heir": k,
            "fraction_str": str(frac),
            "percentage": round(pct, 4),
            "amount": round(amt, 2)
        })

    return {
        "estate_gross": estate,
        "debts": debts,
        "funeral": funeral,
        "wills_requested": requested_wills,
        "wills_allowed": round(actual_wills, 2),
        "distributable_estate": round(distributable_estate, 2),
        "adjustment_type": adjustment_type,
        "hajb_notes": hajb_notes,
        "breakdown": results_breakdown
    }

# ----------------- 5 Legal Maxims (Al-Qawa'id al-Fiqhiyyah) -----------------

QAWAID_DATA = [
    {
        "id": 1,
        "title_ar": "الأمور بمقاصدها",
        "transliteration": "Al-Umuru bi-Maqasidiha",
        "title_th": "กิจการทั้งหลายขึ้นอยู่กับเจตนา",
        "meaning": "สถานะทางศาสนา ผลลัพธ์ และความชอบธรรมของการกระทำและธุรกรรม ขึ้นอยู่กับเจตนาและความมุ่งหมายของผู้กระทำ",
        "primary_evidence": "เศาะฮีฮ์ อัล-บุคอรี บทที่ 1: 'แท้จริงการงานทั้งหลายขึ้นอยู่กับเจตนา และทุกคนจะได้รับตามที่เขาได้ตั้งเจตนาไว้'",
        "contemporary_applications": [
            "สัญญาอัจฉริยะ (Smart Contracts) และธุรกรรมดิจิทัล: ให้ดูที่เจตนาของคู่สัญญา มิใช่เพียงรูปแบบคำหรือโค้ดโปรแกรม",
            "การลงทุนในหุ้นและตราสารทางการเงิน: ซื้อเพื่อรับเงินปันผลและการเติบโต (ฮาลาล) vs เก็งกำไรแบบปั่นหุ้นไร้เจตนาถือครอง (ฮะรอม)",
            "การพัฒนาปัญญาประดิษฐ์ (AI Development): จุดประสงค์การใช้งานเป็นตัวกำหนดฮุก่ม"
        ]
    },
    {
        "id": 2,
        "title_ar": "اليقين لا يزول بالشك",
        "transliteration": "Al-Yaqinu la Yazulu bi-Shakk",
        "title_th": "ความแน่นอนไม่อาจถูกลบล้างด้วยความสงสัย",
        "meaning": "สถานะเดิมหรือข้อเท็จจริงที่ประจักษ์ชัดและมีหลักฐานแน่นอน จะไม่ถูกยกเลิกหรือเปลี่ยนแปลงด้วยเพียงความลังเลสงสัยที่ไม่มีหลักฐาน",
        "primary_evidence": "เศาะฮีฮ์ มุสลิม: หากผู้ใดสงสัยว่าเสียน้ำละหมาดหรือไม่ในละหมาด อย่าได้ออกจนกว่าจะได้ยินเสียงหรือได้กลิ่น",
        "contemporary_applications": [
            "ความบริสุทธิ์ของอาหารและวัตถุดิบ: อาหารเดิมถือว่าสะอาดและฮาลาล จนกว่าจะปรากฏสิ่งนะยิสหรือสิ่งต้องห้ามที่มีหลักฐานชัด",
            "สถานะการชำระหนี้และภาระผูกพัน: หนี้สินที่เกิดขึ้นอย่างแน่นอนแล้ว ย่อมคงอยู่จนกว่าจะมีหลักฐานการชำระหนี้",
            "การถือศีลอดและการเห็นจันทร์เสี้ยว: ยึดการนับวันครบ 30 วันเป็นหลักแน่นอนหากมีเมฆบดบัง"
        ]
    },
    {
        "id": 3,
        "title_ar": "المشقة تجلب التيسير",
        "transliteration": "Al-Mashaqqatu Tajlibu al-Taysir",
        "title_th": "ความยากลำบากนำมาซึ่งความผ่อนปรน",
        "meaning": "เมื่อเกิดความยากลำบาก อุปสรรค หรือภัยจำเป็นเกินกว่าวิสัยปกติ ชะรีอะฮ์ได้บัญญัติการผ่อนผัน (รุกเศาะฮ์) เพื่อความสะดวก",
        "primary_evidence": "ซูเราะฮ์อัล-บะเกาะเราะฮ์ 2:185: 'อัลลอฮ์ทรงประสงค์ความสะดวกง่ายดายแก่พวกเจ้า และไม่ทรงประสงค์ความยากลำบากแก่พวกเจ้า'",
        "contemporary_applications": [
            "การละหมาดและการกำหนดทิศกิบลัตในสภาวะพิเศษ (เช่น บนเครื่องบิน ยานอวกาศ หรือในหอผู้ป่วยวิกฤต ICU)",
            "การรักษาทางการแพทย์: การใช้ยารักษาโรคที่มีสารสังเคราะห์ต้องห้าม เมื่อไม่มีทางเลือกอื่นและชีวิตตกอยู่ในภาวะอันตราย (ฎะรูเราะฮ์)",
            "การผ่อนปรนธุรกรรมในช่วงภัยพิบัติ วิกฤตการณ์เศรษฐกิจ หรือการล็อกดาวน์"
        ]
    },
    {
        "id": 4,
        "title_ar": "الضرر يزال",
        "transliteration": "Al-Dhararu Yuzal",
        "title_th": "อันตรายและความเสียหายต้องได้รับการขจัด",
        "meaning": "การสร้างอันตรายหรือความเสียหายต่อตนเองและผู้อื่นเป็นสิ่งต้องห้าม และเมื่อเกิดความเสียหายขึ้น จำเป็นต้องระงับและเยียวยาแก้ไข",
        "primary_evidence": "40 ฮะดีษอัน-นะวะวีย์ บทที่ 32: 'ต้องไม่สร้างความเสียหายแก่ตนเอง และต้องไม่สร้างความเสียหายแก่ผู้อื่น (ลา เฎาะร็อร วะลา ฎิรอร)'",
        "contemporary_applications": [
            "กฎหมายสิ่งแวดล้อมและมลพิษ: การปล่อยมลพิษ โรงงานอุตสาหกรรม หรือขยะพิษที่กระทบชุมชนถือเป็นบาปและต้องถูกสั่งระงับ",
            "การห้ามสารเสพติด สารพิษ และน้ำท่อม 4x100: ขจัดอันตรายต่อสมอง ระบบประสาท และความสงบสุขของสังคม",
            "ความปลอดภัยทางไซเบอร์และการหลอกลวงทางการเงิน: การแบนแชร์ลูกโซ่ ฟิชชิ่ง มัลแวร์ และการละเมิดข้อมูลส่วนบุคคล"
        ]
    },
    {
        "id": 5,
        "title_ar": "العادة محكمة",
        "transliteration": "Al-'Adatu Muhakkamah",
        "title_th": "จารีตประเพณีเป็นข้อยุติในการพิจารณา",
        "meaning": "ขนบธรรมเนียมและจารีตประเพณีที่ดีงามที่ผู้คนยึดถือปฏิบัติทั่วไป สามารถนำมาเป็นเกณฑ์วินิจฉัยทางกฎหมายได้ ตราบใดที่ไม่ขัดต่อบทบัญญัติศาสนาที่ชัดเจน",
        "primary_evidence": "ซูเราะฮ์อัล-อะอ์รอฟ 7:199: 'เจ้าจงยึดถือการให้อภัย และจงสั่งสอนสิ่งที่ดีงาม (อัล-อุรฟ์ / จารีตที่ดี)'",
        "contemporary_applications": [
            "ธรรมเนียมการค้าปลีกและการรับประกันสินค้า: นโยบายการคืนเงิน คืนสินค้า หรือการเคลมประกันตามมาตรฐานอุตสาหกรรม",
            "การกำหนดสินสอด (มะฮัร มิศล์) และค่าเลี้ยงดู: อ้างอิงตามฐานะและธรรมเนียมปฏิบัติของท้องถิ่นในยุคสมัยนั้นๆ",
            "สัญญาจ้างงานและเวลาทำงาน: นิยามของ 'วันทำงานปกติ' และ 'ล่วงเวลา (OT)' ตามกฎหมายแรงงานและจารีตธุรกิจ"
        ]
    }
]

def get_qawaid(rule_id_or_keyword=None, rule_id=None):
    if rule_id is not None:
        rule_id_or_keyword = rule_id
    if not rule_id_or_keyword:
        return QAWAID_DATA

    q = str(rule_id_or_keyword).strip().lower()
    if q.isdigit():
        rid = int(q)
        for r in QAWAID_DATA:
            if r["id"] == rid:
                return r
        return None
    for r in QAWAID_DATA:
        if q in r["title_th"].lower() or q in r["transliteration"].lower() or q in r["title_ar"]:
            return r
    return None

def search_qawaid(query):
    q = query.strip().lower()
    results = []
    for r in QAWAID_DATA:
        text_corpus = f"{r['title_th']} {r['transliteration']} {r['meaning']} {' '.join(r['contemporary_applications'])}".lower()
        if q in text_corpus:
            results.append(r)
    return results

# ----------------- Comparative Fiqh Matrix (4 Sunni Madhhabs) -----------------

COMPARATIVE_FIQH_DATA = [
    {
        "id": 1,
        "topic_th": "การสัมผัสผิวหนังสตรีต่างเพศ (การเสียน้ำละหมาด)",
        "issue_description": "เมื่อผิวหนังของผู้ชายสัมผัสกับผิวหนังของผู้หญิงที่ไม่ใช่มะฮ์ร็อม (แต่งงานกันได้) โดยไม่มีผ้ากั้น",
        "hanafi": {
            "ruling": "ไม่เสียน้ำละหมาด (ไม่ขาด)",
            "detail": "การสัมผัสผิวหนังธรรมดาไม่ทำให้เสียน้ำละหมาดเด็ดขาด ยกเว้นกรณีมีการร่วมประเวณี หรือเกิดอารมณ์ใคร่อย่างรุนแรงจนเกิดสารคัดหลั่ง",
            "evidence": "ฮะดีษท่านหญิงอาอิชะฮ์: ท่านนบีเคยจูบภรรยาบางท่านแล้วออกไปละหมาดโดยไม่ได้อาบน้ำละหมาดใหม่ (อบูดาวูด, ติรมีซี)"
        },
        "maliki": {
            "ruling": "เสียเฉพาะเมื่อมีเจตนาใคร่หรือเกิดอารมณ์",
            "detail": "หากสัมผัสโดยมีเจตนาหาความสุขสำราญ (ลัซซะฮ์) หรือเกิดความรู้สึกใคร่ขณะสัมผัส น้ำละหมาดเสีย แต่หากสัมผัสโดยบังเอิญหรือไร้เจตนา ไม่เสีย",
            "evidence": "ตีความคำว่า 'ลามัสตุม' ในกุรอาน 4:43 ว่าหมายถึงการสัมผัสที่มีอารมณ์ใคร่เจือปน"
        },
        "shafii": {
            "ruling": "เสียน้ำละหมาดเสมอ (ขาดเด็ดขาด)",
            "detail": "น้ำละหมาดเสียทันทีเมื่อผิวหนังสัมผัสผิวหนัง ไม่ว่าจะเจตนาหรือไม่ มีอารมณ์ใคร่หรือไม่ก็ตาม ตราบใดที่เป็นหญิงต่างเพศที่แต่งงานกันได้",
            "evidence": "ยึดความหมายตรงตัวของอายะฮ์ 'เอา ลามัสตุมุน-นิซาอ์' (หรือเมื่อพวกเจ้าสัมผัสสตรี) ตามทัศนะของท่านอิบนุ มัสอูด และอิบนุ อุมัร"
        },
        "hanbali": {
            "ruling": "เสียเฉพาะเมื่อสัมผัสด้วยความกำหนัด (ชะฮ์วะฮ์)",
            "detail": "หากสัมผัสโดยมีความรู้สึกใคร่กำหนัด น้ำละหมาดเสีย แต่หากสัมผัสโดยปราศจากความรู้สึกใคร่ (เช่น สัมผัสธรรมดาในการส่งของหรือเบียดเสียด) ไม่เสีย",
            "evidence": "สอดคล้องกับหลักการรวมหลักฐานระหว่างอายะฮ์กุรอานและฮะดีษการจูบของท่านนบี"
        },
        "practical_advice": "ในสถานการณ์ที่คนแออัดมาก เช่น ขณะเฏาะวาฟรอบกะอ์บะฮ์ที่มักกะฮ์ นักวิชาการมัซฮับชาฟิอีอนุญาตให้ยึดตามทัศนะของฮะนะฟีหรือฮันบะลีเพื่อความสะดวก (ตักลีด)"
    },
    {
        "id": 2,
        "topic_th": "การอ่านซูเราะฮ์อัล-ฟาติฮะฮ์ตามอิหม่ามในการละหมาดเสียงดัง",
        "issue_description": "มะอ์มูม (ผู้ตาม) จำเป็นต้องอ่านฟาติฮะฮ์ในละหมาดที่อิหม่ามนำอ่านเสียงดัง (เช่น มัฆริบ, อิชาอ์, ศุบห์) หรือไม่",
        "hanafi": {
            "ruling": "ไม่อนุญาตให้อ่าน (มักรูฮ์ตะห์รีม / ฮะรอม)",
            "detail": "มะอ์มูมไม่ต้องอ่านทั้งในละหมาดเสียงดังและเสียงค่อย การอ่านของอิหม่ามถือเป็นการอ่านของผู้ตามอย่างสมบูรณ์แล้ว",
            "evidence": "อัลกุรอาน 7:204 ('เมื่อกุรอานถูกอ่าน จงสดับฟังและสงบนิ่ง') และฮะดีษ 'ผู้ใดมีอิหม่าม การอ่านของอิหม่ามคือการอ่านของเขา'"
        },
        "maliki": {
            "ruling": "มักรูฮ์ (ไม่ควรอ่าน) ในละหมาดเสียงดัง แต่สุนัตให้อ่านในละหมาดเสียงค่อย",
            "detail": "ในละหมาดเสียงดังให้ตั้งใจฟังอิหม่าม ห้ามอ่านแทรก ส่วนละหมาดเสียงค่อยควรอ่าน",
            "evidence": "การสดับฟังในละหมาดเสียงดังเป็นคำสั่งที่ต้องให้ความสำคัญสูงสุด"
        },
        "shafii": {
            "ruling": "วาญิบ (จำเป็นต้องอ่านทุกคน ทุกร็อกอะฮ์)",
            "detail": "การอ่านฟาติฮะฮ์เป็นรุก่น (เสาหลัก) ของทุกคน ทั้งอิหม่าม มะอ์มูม ผู้ละหมาดเดี่ยว ทั้งในละหมาดเสียงดังและเสียงค่อย",
            "evidence": "ฮะดีษเศาะฮีฮ์ อัล-บุคอรี: 'ไม่มีการละหมาดสำหรับผู้ที่ไม่อ่านฟาติฮะฮ์แห่งคัมภีร์'"
        },
        "hanbali": {
            "ruling": "สุนัตให้อ่านตอนอิหม่ามหยุดพักเสียง (สกุต)",
            "detail": "หากอิหม่ามหยุดพักหายใจ ให้มะอ์มูมรีบอ่าน หากอิหม่ามไม่อ่านหยุดพัก ให้ยืนฟัง และการฟังนั้นเพียงพอแล้ว",
            "evidence": "ผสานระหว่างตัวบทการสดับฟังกุรอานกับตัวบทความสำคัญของฟาติฮะฮ์"
        },
        "practical_advice": "หากละหมาดตามอิหม่ามที่อ่านเร็ว ให้มะอ์มูมสายชาฟิอีอ่านฟาติฮะฮ์ให้ทัน หรือหากตามอิหม่ามต่างมัซฮับในต่างประเทศสามารถปฏิบัติตามทัศนะญุมฮูรเพื่อความสมานฉันท์"
    },
    {
        "id": 3,
        "topic_th": "ระยะทางของการเดินทางที่อนุญาตให้ละหมาดย่อ-รวม (มุซาฟิร)",
        "issue_description": "เกณฑ์ระยะทางขั้นต่ำในการเดินทาง (สะฟัร) ที่อนุญาตให้ละหมาดก็อศร์ (ย่อจาก 4 เหลือ 2) และญัมอ์ (รวมเวลา)",
        "hanafi": {
            "ruling": "การเดินทาง 3 วัน 3 คืน (~81-88 กม.) และไม่อนุญาตให้รวมเวลา ยกเว้นที่ฮัจญ์",
            "detail": "ระยะทางต้องเทียบเท่าการเดินเท้าหรือขี่อูฐ 3 วัน (~81 กม. ขึ้นไป) และมัซฮับฮะนะฟีไม่อนุญาตให้รวมเวลาละหมาด (ญัมอ์) ในการเดินทางทั่วไป ยกเว้นในพิธีฮัจญ์ที่ทุ่งอะเราะฟะฮ์และมุซดะลิฟะฮ์เท่านั้น",
            "evidence": "ฮะดีษห้ามสตรีเดินทาง 3 วันโดยไม่มีมะฮ์ร็อม"
        },
        "maliki": {
            "ruling": "4 บุรุด (~80-88 กม.) อนุญาตทั้งย่อและรวมเมื่อเดินทางจริง",
            "detail": "ระยะทางประมาณ 80-88 กิโลเมตร อนุญาตให้ย่อละหมาด และอนุญาตให้รวมละหมาดได้เมื่ออยู่ในระหว่างการเดินทางขับขี่บนพาหนะ",
            "evidence": "ธรรมเนียมของชาวมะดีนะฮ์และการปฏิบัติของบรรดาเศาะฮาบะฮ์"
        },
        "shafii": {
            "ruling": "4 บุรุด (16 ฟัรซัค = ~81-89 กม.) อนุญาตทั้งย่อและรวม (ตักดีม/ตะอ์คีร)",
            "detail": "ระยะทาง 81-89 กิโลเมตร เป็นการเดินทางที่อนุญาต (ไม่ใช่เดินทางไปทำบาป) สามารถย่อละหมาด 4 ร็อกอะฮ์เหลือ 2 และรวมเวลามัฆริบ-อิชาอ์ หรือ ซุฮริ-อัศริ ได้ทั้งแบบล่วงหน้า (ตักดีม) หรือเลื่อนไปรวม (ตะอ์คีร)",
            "evidence": "การกำหนดระยะทางของท่านอิบนุ อับบาส และอิบนุ อุมัร จากมักกะฮ์ไปอุสฟาน"
        },
        "hanbali": {
            "ruling": "4 บุรุด (~80-88 กม.) และผ่อนปรนให้รวมเวลาได้กว้างขวางกว่า",
            "detail": "นอกจากระยะทางสะฟัรแล้ว มัซฮับฮันบะลียังอนุญาตให้รวมละหมาดได้ในเมืองกรณีมีฝนตกหนัก โคลนตม ความกลัว หรือความเจ็บป่วยรุนแรง",
            "evidence": "ฮะดีษท่านนบีรวมละหมาดในมะดีนะฮ์โดยไม่มีเหตุกลัวหรือฝนตก เพื่อไม่ให้เกิดความยากลำบากแก่อุมมะฮ์"
        },
        "practical_advice": "สำหรับการใช้ชีวิตในปัจจุบัน การเดินทางด้วยรถยนต์ข้ามจังหวัดเกิน 81-90 กิโลเมตร เข้าเกณฑ์มุซาฟิรตามมติของทั้ง 4 มัซฮับ"
    },
    {
        "id": 4,
        "topic_th": "การยกมือขณะตักบีรในการละหมาด (ร็อฟอุล ยะดัยน์)",
        "issue_description": "ตำแหน่งในการยกมือเสมอไหล่หรือติ่งหูขณะกล่าวตักบีรในละหมาด",
        "hanafi": {
            "ruling": "ยกเฉพาะตักบีรแรกเริ่มละหมาดเท่านั้น",
            "detail": "ยกมือเฉพาะตักบีเราะตุล อิฮ์รอม ส่วนการก้มรุกูอ์และเงยจากรุกูอ์ไม่ต้องยกมือ",
            "evidence": "ฮะดีษท่านอิบนุ มัสอูด ที่ละหมาดให้ดูโดยยกมือเพียงครั้งแรกครั้งเดียว (สุนัน อบูดาวูด)"
        },
        "maliki": {
            "ruling": "ยกเฉพาะตักบีรแรก (ทัศนะมัชฮูรในมุดาววะนะฮ์)",
            "detail": "ทัศนะที่แพร่หลายที่สุดในมัซฮับคือยกมือเฉพาะตักบีรแรก และปล่อยมือแนบลำตัว (สัดล์)",
            "evidence": "การปฏิบัติของชาวมะดีนะฮ์ (อะมัล อะฮ์ลิล มะดีนะฮ์)"
        },
        "shafii": {
            "ruling": "สุนัตให้ยกมือ 4 ตำแหน่งในละหมาด",
            "detail": "1. ตักบีรแรกเริ่ม, 2. ขณะลงรุกูอ์, 3. ขณะเงยขึ้นจากรุกูอ์ (สะมิอัลลอฮุ ลิมัน หะมิดะฮ์), 4. เมื่อลุกขึ้นจากตะชะฮ์ฮุดแรก",
            "evidence": "ฮะดีษเศาะฮีฮ์ อัล-บุคอรี และมุสลิม จากท่านอิบนุ อุมัร ยืนยันการกระทำของท่านนบีทั้ง 4 ตำแหน่ง"
        },
        "hanbali": {
            "ruling": "สุนัตให้ยกมือ 3 ตำแหน่งหลัก",
            "detail": "1. ตักบีรแรก, 2. ก่อนลงรุกูอ์, 3. ขณะเงยจากรุกูอ์ (บางสายรายงานอนุญาตจุดที่ 4 เมื่อลุกจากตะชะฮ์ฮุดแรก)",
            "evidence": "ฮะดีษเศาะฮีฮ์ของท่านอิบนุ อุมัร และวาอิล บิน ฮุจญ์ร"
        },
        "practical_advice": "ทุกรูปแบบมีสายรายงานฮะดีษที่ถูกต้องรองรับ การยกหรือไม่ยกมือไม่ทำให้ละหมาดใช้ไม่ได้ มุสลิมควรให้เกียรติความหลากหลาย"
    },
    {
        "id": 5,
        "topic_th": "การดุอาอ์กุนูตในการละหมาดศุบห์",
        "issue_description": "การยืนอ่านบทขอดุอาอ์กุนูตในร็อกอะฮ์สุดท้ายของการละหมาดยามรุ่งอรุณ (ศุบห์)",
        "hanafi": {
            "ruling": "ไม่เป็นสุนัตในละหมาดศุบห์ (ทำเฉพาะในละหมาดวิตร์)",
            "detail": "ถือว่าการกุนูตในศุบห์ถูกยกเลิกแล้ว (มันซูค) ยกเว้นเมื่อเกิดวิกฤติรุนแรงต่อส่วนรวม (กุนูต นาซิละฮ์)",
            "evidence": "ฮะดีษที่ระบุว่าท่านนบีกุนูตอยู่ 1 เดือนขอดุอาอ์ให้เผ่าหนึ่งแล้วท่านก็หยุดไป"
        },
        "maliki": {
            "ruling": "เป็นสุนัต (มุสตะฮับ) อ่านค่อยๆ ก่อนลงรุกูอ์",
            "detail": "ส่งเสริมให้อ่านกุนูตในศุบห์ โดยให้อ่านเบาๆ ก่อนที่จะก้มลงรุกูอ์",
            "evidence": "ฮะดีษท่านอนัส บิน มาลิก ว่าท่านนบียังคงกุนูตในศุบห์จนกระทั่งจากโลกนี้ไป"
        },
        "shafii": {
            "ruling": "เป็นสุนัตมุอั๊กกัด (สุนัตอับอ๊าด) หลังเงยจากรุกูอ์",
            "detail": "ให้อ่านหลังเงยขึ้นจากรุกูอ์ร็อกอะฮ์ที่สอง หากลืมอ่าน ส่งเสริมให้สุญูดซะฮ์วีชดเชย",
            "evidence": "ฮะดีษเศาะฮีฮ์ของท่านอนัส บิน มาลิก และการปฏิบัติของเคาะลีฟะฮ์ทั้งสี่"
        },
        "hanbali": {
            "ruling": "ไม่เป็นสุนัตในศุบห์ ยกเว้นเมื่อเกิดภัยพิบัติ (นาซิละฮ์)",
            "detail": "ในยามปกติไม่มีกุนูตในศุบห์ แต่หากมีสงครามหรือภัยพิบัติคุกคามมุสลิม ให้อิหม่ามนำกุนูตนาซิละฮ์ได้ทุกเวลา",
            "evidence": "ฮะดีษการหยุดกุนูตของท่านนบีหลังครบกำหนด 1 เดือน"
        },
        "practical_advice": "หากละหมาดตามอิหม่ามที่อ่านกุนูต ให้ยกมือขอดุอาอ์และกล่าวอามีนตาม เพื่อรักษาความเป็นเอกภาพของการละหมาดตามคำสอนของท่านอิหม่ามอะห์มัด บิน ฮันบัล"
    }
]

def get_comparative_fiqh(topic_id_or_keyword=None):
    if not topic_id_or_keyword:
        return COMPARATIVE_FIQH_DATA
    q = str(topic_id_or_keyword).strip().lower()
    if q.isdigit():
        tid = int(q)
        for t in COMPARATIVE_FIQH_DATA:
            if t["id"] == tid:
                return t
        return None
    for t in COMPARATIVE_FIQH_DATA:
        if q in t["topic_th"].lower() or q in t["issue_description"].lower():
            return t
    return None

# ----------------- Asbab al-Nuzul (Causes of Revelation) -----------------

ASBAB_DATA = [
    {
        "surah": 2,
        "ayah": 190,
        "surah_name": "อัล-บะเกาะเราะฮ์",
        "verse_text_th": "และพวกเจ้าจงต่อสู้ในทางของอัลลอฮ์ต่อบรรดาผู้ที่ต่อสู้พวกเจ้า และจงอย่ารุกราน แท้จริงอัลลอฮ์ไม่ทรงรักบรรดาผู้รุกราน",
        "authorities": "อัล-วาฮิดีย์ (Asbab al-Nuzul) และอัส-สุยูฏีย์ (Lubab al-Nuqul)",
        "context_th": "ประทานลงมา ณ ตำบลอัล-ฮุดัยบียะฮ์ เมื่อครั้งที่ท่านศาสดาและบรรดาเศาะฮาบะฮ์ถูกสกัดกั้นไม่ให้เข้าทำอุมเราะฮ์ บรรดามุสลิมเกรงว่าจะเกิดการสู้รบในเขตหวงห้าม อัลลอฮ์จึงทรงอนุญาตให้ต่อสู้เพื่อป้องกันตัวเท่านั้น และทรงสั่งห้ามอย่างเด็ดขาดไม่ให้รุกรานบุคคลที่ไม่ได้ร่วมรบ เช่น สตรี เด็ก นักบวช และคนชรา"
    },
    {
        "surah": 2,
        "ayah": 256,
        "surah_name": "อัล-บะเกาะเราะฮ์",
        "verse_text_th": "ไม่มีการบังคับใดๆ ในการยอมรับนับถือศาสนา แท้จริงความถูกต้องได้ประจักษ์ชัดจากความหลงผิดแล้ว",
        "authorities": "สุนัน อบูดาวูด (3582), อิบนุ ญะรีร อัฏ-เฏาะบะรี",
        "context_th": "ประทานลงมาเกี่ยวกับชายชาวอันศอร (ชาวมะดีนะฮ์) คนหนึ่งชื่อ อัล-ฮุศอยน์ ซึ่งมีบุตรชายสองคนหันไปนับถือศาสนาคริสต์ก่อนอิสลามจะมาถึง เมื่อบิดาเข้ารับอิสลามจึงพยายามจะบังคับลูกทั้งสองให้เข้ารับอิสลาม อัลลอฮ์จึงทรงประทานอายะฮ์นี้ลงมาเพื่อห้ามการบังคับขู่เข็ญในเรื่องศรัทธา"
    },
    {
        "surah": 4,
        "ayah": 11,
        "surah_name": "อัน-นิซาอ์",
        "verse_text_th": "อัลลอฮ์ทรงสั่งเสียพวกเจ้าในเรื่องลูกๆ ของพวกเจ้า สำหรับเพศชายจะได้รับส่วนแบ่งเท่ากับส่วนของเพศหญิงสองคน...",
        "authorities": "ญามิอ์ อัต-ติรมีซี (2092), สุนัน อบูดาวูด",
        "context_th": "สืบเนื่องจากการทำศึกอุฮุด ท่านสะอ์ด บิน อัร-รอบีอ์ ได้เสียชีวิตในสนามรบ ทิ้งภรรยาและบุตรสาวสองคนไว้ ลุงของเด็กได้ยึดทรัพย์สินทั้งหมดตามจารีตยุคญาฮิลียะฮ์ (ที่ให้เฉพาะชายที่จับอาวุธรบได้รับมรดก) ภรรยาจึงมาร้องเรียนต่อท่านนบี จนกระทั่งอายะฮ์นี้ถูกประทานลงมาเพื่อคุ้มครองและจัดสรรสัดส่วนแก่สตรีและเด็กเป็นครั้งแรกในประวัติศาสตร์อาหรับ"
    },
    {
        "surah": 5,
        "ayah": 90,
        "surah_name": "อัล-มาอิดะฮ์",
        "verse_text_th": "โอ้บรรดาผู้ศรัทธาเอ๋ย แท้จริงสุรา การพนัน แท่นหินบูชา และการเสี่ยงทาย ล้วนเป็นสิ่งโสโครกอันเกิดจากการงานของชัยฏอน จงหลีกเลี่ยงเสีย...",
        "authorities": "เศาะฮีฮ์ มุสลิม, อัส-สุยูฏีย์",
        "context_th": "เป็นขั้นตอนสุดท้ายของการสั่งห้ามสิ่งมึนเมาอย่างเด็ดขาด หลังจากที่มีการเตือนเรื่องประโยชน์และโทษ (2:219) และห้ามละหมาดขณะมึนเมา (4:43) เหตุการณ์เกิดขึ้นเมื่อเศาะฮาบะฮ์บางท่านดื่มสุราในงานเลี้ยงแล้วเกิดการทะเลาะวิวาท อายะฮ์นี้จึงถูกประทานลงมาสั่งห้าม (ฮะรอม) 100% โดยสิ้นเชิง"
    },
    {
        "surah": 108,
        "ayah": 1,
        "surah_name": "อัล-เกาษัร",
        "verse_text_th": "แท้จริงเราได้ประทานแม่น้ำอัล-เกาษัร (ความดีอันล้นพ้น) แก่เจ้าแล้ว",
        "authorities": "อิบนุ อับบาส, อัล-วาฮิดีย์",
        "context_th": "ประทานลงมาเพื่อปลอบประโลมท่านนบีมุฮัมมัด เมื่อบุตรชายของท่าน (อัล-กอสิม) เสียชีวิต บรรดาหัวหน้าชาวกุรอยช์ผู้ปฏิเสธ เช่น อัล-อ๊าศ บิน วาอิล ได้เยาะเย้ยท่านว่าเป็น 'อับตัร' (ผู้ถูกตัดขาด ไร้ทายาทสืบสกุล) อัลลอฮ์จึงทรงประทานซูเราะฮ์นี้เพื่อยืนยันว่าศัตรูของท่านต่างหากที่จะถูกตัดขาด และท่านได้รับเกียรติยศอันไพศาล"
    },
    {
        "surah": 112,
        "ayah": 1,
        "surah_name": "อัล-อิคลาศ",
        "verse_text_th": "จงกล่าวเถิดมุฮัมมัด พระองค์คืออัลลอฮ์ผู้ทรงเอกะ",
        "authorities": "มุสนัด อะห์มัด, อัต-ติรมีซี",
        "context_th": "ประทานลงมาเมื่อบรรดามุชริกีน (ผู้ตั้งภาคีชาวมักกะฮ์) และชาวยิวได้มาท้าทายถามท่านนบีว่า 'โอ้มุฮัมมัด จงบอกเชื้อสายและโคตรเหง้าของพระเจ้าของเจ้ามาสิ พระองค์ทำจากทองคำ เงิน หรือทับทิม?' อัลลอฮ์จึงทรงประทานซูเราะฮ์นี้เพื่อประกาศความบริสุทธิ์และเอกภาพอันสูงสุดของพระองค์"
    }
]

def get_asbab_al_nuzul(surah, ayah):
    for a in ASBAB_DATA:
        if a["surah"] == int(surah) and a["ayah"] == int(ayah):
            return a
    return None

def search_asbab_al_nuzul(query):
    q = query.strip().lower()
    results = []
    for a in ASBAB_DATA:
        text = f"{a['surah_name']} {a['verse_text_th']} {a['context_th']}".lower()
        if q in text:
            results.append(a)
    return results

# ----------------- Classical Tafsir (Ibn Kathir, Jalalayn, Sa'di) -----------------

TAFSIR_DATA = [
    {
        "surah": 1,
        "ayah": 1,
        "ibn_kathir": "บิสมิลลาฮ์ คือการเริ่มต้นทุกกิจการด้วยพระนามอันเป็นมงคล เพื่อขอความจำเริญและความช่วยเหลือจากอัลลอฮ์ผู้ทรงเมตตาเสมอ",
        "jalalayn": "เริ่มต้นด้วยพระนามของอัลลอฮ์ ผู้ทรงเปี่ยมด้วยความเมตตาแก่สิ่งถูกสร้างทั้งมวลในโลกนี้ และเมตตายิ่งเฉพาะผู้ศรัทธาในวันปรโลก",
        "sadi": "การกล่าวบิสมิลลาฮ์เป็นการมอบหมายการงานทั้งสิ้นแด่พระเจ้า และเป็นการยอมรับว่ามนุษย์ไม่อาจสำเร็จสิ่งใดได้หากปราศจากความช่วยเหลือของพระองค์"
    },
    {
        "surah": 2,
        "ayah": 255,
        "ibn_kathir": "อายะตุลกุรซีย์คืออายะฮ์ที่ยิ่งใหญ่ที่สุดในอัลกุรอาน ประกอบด้วย 10 วรรคทองที่ประกาศเตาฮีดอันบริสุทธิ์ พระองค์ทรงมีชีวิตนิรันดร์ ทรงอภิบาลสรรพสิ่ง ไม่ทรงง่วงนอนหรือหลับใหล พระที่นั่งของพระองค์กว้างใหญ่ไพศาลครอบคลุมฟากฟ้าและแผ่นดิน",
        "jalalayn": "อัลลอฮ์ไม่มีพระเจ้าอื่นใดนอกจากพระองค์ ทรงดำรงอยู่ด้วยพระองค์เอง ทรงบริหารจัดการสิ่งถูกสร้าง กุรซีย์ของพระองค์ครอบฟ้าดินโดยไม่ทรงเหน็ดเหนื่อยในการพิทักษ์รักษา",
        "sadi": "วรรคนี้รวมหลักอากีดะฮ์สูงสุด ยืนยันอำนาจเด็ดขาดและความสมบูรณ์แบบไร้ที่ติ ใครอ่านหลังละหมาดฟัรฎ์ทุกเวลา ไม่มีสิ่งใดกั้นเขาจากสวรรค์นอกจากความตาย"
    },
    {
        "surah": 2,
        "ayah": 275,
        "ibn_kathir": "อัลลอฮ์ทรงอนุมัติการค้าขายที่มีความเสี่ยงและการแลกเปลี่ยนที่เป็นธรรม แต่ทรงห้ามดอกเบี้ย (ริบา) ทุกชนิด ผู้กินดอกเบี้ยจะฟื้นคืนชีพในสภาพเหมือนผู้ถูกชัยฏอนเข้าสิง",
        "jalalayn": "การค้าขายต่างจากดอกเบี้ยโดยสิ้นเชิง เพราะการค้าตั้งอยู่บนกำไรจากการลงแรงและความเสี่ยง ส่วนดอกเบี้ยคือการเพิ่มพูนเงินบนความเดือดร้อนของลูกหนี้",
        "sadi": "ชะรีอะฮ์ปกป้องระบบเศรษฐกิจจากการเอารัดเอาเปรียบ ดอกเบี้ยก่อให้เกิดความอยุติธรรมและทำลายเสถียรภาพสังคม"
    },
    {
        "surah": 112,
        "ayah": 1,
        "ibn_kathir": "อัลลอฮ์ทรงเป็นหนึ่งเดียว ไร้ภาคี ไร้หุ้นส่วน ไร้บุตร และไม่ทรงถูกกำเนิด ซูเราะฮ์นี้มีคุณค่าเทียบเท่า 1 ใน 3 ของอัลกุรอาน เพราะเนื้อหากล่าวถึงพระลักษณะของพระเจ้าโดยเฉพาะ",
        "jalalayn": "พระองค์ทรงเป็นเอกะ ปราศจากสิ่งใดเสมอเหมือนในพระนามและคุณลักษณะ",
        "sadi": "ความหมายของ 'อัศ-เศาะมัด' คือศูนย์รวมแห่งความสมบูรณ์แบบที่สรรพสิ่งทั้งหลายต่างต้องพึ่งพาพระองค์ในทุกกิจการ"
    }
]

def get_tafsir(surah, ayah):
    for t in TAFSIR_DATA:
        if t["surah"] == int(surah) and t["ayah"] == int(ayah):
            return t
    return None

# ----------------- EveryAyah Audio Integration -----------------

def get_audio_url(surah, ayah, reciter="Alafasy_128kbps"):
    s = str(surah).zfill(3)
    a = str(ayah).zfill(3)
    return f"https://everyayah.com/data/{reciter}/{s}{a}.mp3"

def get_surah_audio_playlist(surah, reciter="Alafasy_128kbps"):
    """
    Returns complete continuous audio playlist URLs for all verses of a Surah.
    Enables continuous long playback (เล่นยาวต่อเนื่อง) across the entire chapter.
    """
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT total_ayahs, name_th, name_ar FROM surahs WHERE number = ?", (int(surah),))
        row = c.fetchone()
        if not row:
            return None
        total_ayahs, name_th, name_ar = row
        s3 = str(surah).zfill(3)
        playlist = []
        for a in range(1, total_ayahs + 1):

            a3 = str(a).zfill(3)
            url = f"https://everyayah.com/data/{reciter}/{s3}{a3}.mp3"
            playlist.append({
                "surah": int(surah),
                "ayah": a,
                "url": url
            })
        return {
            "surah": int(surah),
            "name_th": name_th,
            "name_ar": name_ar,
            "total_verses": total_ayahs,
            "total_ayahs": total_ayahs,
            "reciter": reciter,
            "playlist": playlist
        }

    finally:
        conn.close()

# ----------------- Sects & Traditions Primary Texts Operations -----------------

def search_sect_texts(query_text, limit=5, sect_filter=None):
    """
    Search primary texts from various Islamic sects & schools:
    Shia, Salafi/Wahhabi, Ibadi, and Sufi.
    Uses SQLite FTS5 with fallback to LIKE.
    """
    conn = get_connection()
    results = []
    try:
        cursor = conn.cursor()
        clean_q = query_text.strip().replace('"', '""')
        
        # 1. FTS5 MATCH
        try:
            if sect_filter:
                sql = """
                SELECT rowid as id, tradition, tradition_title_th, book_title, author, chapter_title, arabic_text, thai_text, english_text, doctrinal_theme,
                       bm25(sect_texts_fts) as rank
                FROM sect_texts_fts
                WHERE sect_texts_fts MATCH ? AND tradition = ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(sql, (f'"{clean_q}"*', sect_filter.lower(), limit))
            else:
                sql = """
                SELECT rowid as id, tradition, tradition_title_th, book_title, author, chapter_title, arabic_text, thai_text, english_text, doctrinal_theme,
                       bm25(sect_texts_fts) as rank
                FROM sect_texts_fts
                WHERE sect_texts_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(sql, (f'"{clean_q}"*', limit))
            for r in cursor.fetchall():
                d = dict(r)
                d["sect"] = d["tradition"]
                d["thai_translation"] = d["thai_text"]
                d["theological_context"] = d["doctrinal_theme"]
                d["passage_ref"] = d.get("chapter_title", "")
                results.append(d)
        except Exception:
            pass

        # 2. LIKE fallback
        if len(results) < limit:
            existing_ids = {r["id"] for r in results if "id" in r}
            like_pat = f"%{clean_q}%"
            if sect_filter:
                sql = """
                SELECT id, tradition, tradition_title_th, book_title, author, chapter_title, arabic_text, thai_text, english_text, doctrinal_theme, notes
                FROM sect_texts
                WHERE tradition = ? AND (book_title LIKE ? OR author LIKE ? OR thai_text LIKE ? OR doctrinal_theme LIKE ? OR arabic_text LIKE ? OR chapter_title LIKE ?)
                LIMIT ?
                """
                cursor.execute(sql, (sect_filter.lower(), like_pat, like_pat, like_pat, like_pat, like_pat, like_pat, limit))
            else:
                sql = """
                SELECT id, tradition, tradition_title_th, book_title, author, chapter_title, arabic_text, thai_text, english_text, doctrinal_theme, notes
                FROM sect_texts
                WHERE book_title LIKE ? OR author LIKE ? OR thai_text LIKE ? OR doctrinal_theme LIKE ? OR arabic_text LIKE ? OR tradition LIKE ? OR chapter_title LIKE ?
                LIMIT ?
                """
                cursor.execute(sql, (like_pat, like_pat, like_pat, like_pat, like_pat, like_pat, like_pat, limit))
            for r in cursor.fetchall():
                d = dict(r)
                d["sect"] = d["tradition"]
                d["thai_translation"] = d["thai_text"]
                d["theological_context"] = d["doctrinal_theme"]
                d["passage_ref"] = d.get("chapter_title", "")
                if d["id"] not in existing_ids:
                    results.append(d)
                    existing_ids.add(d["id"])
                if len(results) >= limit:
                    break
        return results
    finally:
        conn.close()

def get_sect_text(text_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sect_texts WHERE id = ?", (text_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["sect"] = d["tradition"]
        d["thai_translation"] = d["thai_text"]
        d["theological_context"] = d["doctrinal_theme"]
        d["passage_ref"] = d.get("chapter_title", "")
        return d
    finally:
        conn.close()

# ----------------- Cross-Sect Comparative Matrix (Sunni, Salafi, Shia, Ibadi) -----------------

CROSS_SECT_MATRIX = [
    {
        "id": 1,
        "topic_key": "combining_prayers",
        "topic_th": "การรวมเวลาละหมาด (Jam' al-Salat)",
        "topic_ar": "جمع الصلاتين",
        "issue_description": "การรวมละหมาดซุฮรีกับอัศรี หรือมัฆริบกับอิชาอ์ ในสถานการณ์ปกติและเมื่อมีอุปสรรค",
        "sunni": {
            "position": "อนุญาตเฉพาะกรณีจำเป็น",
            "detail": "อนุญาตเฉพาะกรณีเดินทาง (Safar), ฝนตกหนัก/พายุ, อาการเจ็บป่วยจำเป็น และในพิธีฮัจญ์ (อะเราะฟะฮ์และมุซดะลิฟะฮ์) ไม่อนุญาตให้รวมในเวลาปกติโดยไม่มีเหตุจำเป็นเด็ดขาด (ตามมติ 4 มัซฮับ)",
            "evidences": "กุรอาน 4:103 (إن الصلاة كانت على المؤمنين كتابا موقوتا), ซอฮีฮ์ บุคอรี 543"
        },
        "salafi": {
            "position": "ยึดตามซุนนะฮ์เคร่งครัดเรื่องอุปสรรค",
            "detail": "อนุญาตเมื่อเดินทางหรือมีอุปสรรคตามตัวบทเท่านั้น การรวมเป็นกิจวัตรในภาวะปกติถือเป็นสิ่งต้องห้ามและค้านกับเวลาละหมาดที่กำหนดไว้ในอัลกุรอาน",
            "evidences": "กุรอาน 4:103, ฟัตวา ชัยค์ บินบาซ และอุษัยมีน"
        },
        "shia": {
            "position": "อนุญาตให้รวมได้เป็นปกติทุกวัน",
            "detail": "อนุญาตให้รวมเวลาซุฮรี+อัศรี และมัฆริบ+อิชาอ์ ได้เป็นปกติทุกวันแม้ไม่มีการเดินทางหรืออุปสรรค โดยถือว่าอัลกุรอานระบุช่วงเวลาหลักไว้ 3 ช่วง (ดุลูกุชชัมส์ ถึง ฆะซะกิลลัยล์ และฟัจญ์ร)",
            "evidences": "กุรอาน 17:78, อัล-กาฟี เล่ม 3 หน้า 274, วะซาอิล อัช-ชีอะฮ์ เล่ม 4"
        },
        "ibadi": {
            "position": "อนุญาตเฉพาะเดินทางหรืออุปสรรคหนัก",
            "detail": "อนุญาตให้รวมเฉพาะเมื่อเดินทางหรือมีอุปสรรคหนักตามเงื่อนไขชะรีอะฮ์ ในยามปกติวาญิบต้องละหมาดแยกตาม 5 เวลาที่ชัดเจน",
            "evidences": "มุสนัด อัร-รอบีอ์ อิกน์ ฮะบีบ บาบ อัศ-เศาะลาฮ์"
        },
        "key_difference": "ชีอะฮ์อนุญาตให้รวมเป็นกิจวัตรปกติ ขณะที่ซุนนี สะลัฟ และอิบาดีเห็นพ้องว่าต้องละหมาดแยก 5 เวลา ยกเว้นมีเหตุเดินทางหรืออุปสรรค",
        "primary_sources": "กุรอาน 4:103, 17:78; ซอฮีฮ์ มุสลิม 705; อัล-กาฟี เล่ม 3; มุสนัด อัร-รอบีอ์"
    },
    {
        "id": 2,
        "topic_key": "prayer_postures",
        "topic_th": "ท่าทางในการยืนละหมาดและการสุญูด (Sadl vs Qabd & Turbah)",
        "topic_ar": "قبض اليدين والسجود على التربة",
        "issue_description": "การกอดอกหรือปล่อยมือแนบลำตัวขณะยืนละหมาด และวัตถุที่ใช้อนุญาตให้หน้าผากสัมผัสขณะสุญูด",
        "sunni": {
            "position": "กอดอกเป็นหลัก / ปล่อยมือในมาลิกี",
            "detail": "กอดอก (Qabd) มือขวาทับมือซ้ายเหนือสะดือหรือระดับอก (ชาฟิอี ฮันบะลี ฮะนะฟี) ขณะที่มัซฮับมาลิกียึดการปล่อยมือ (Sadl) สุญูดบนพื้น ผ้ารอง หรือพรมสะอาดได้ทั้งหมด",
            "evidences": "ซอฮีฮ์ บุคอรี 740, อัล-มุวัฏเฏาะอ์ ของอิมามมาลิก"
        },
        "salafi": {
            "position": "กอดอกระดับอกอย่างเคร่งครัด",
            "detail": "เน้นการกอดอก (Qabd) บนหน้าอกตามสายรายงานที่แข็งแรงที่สุด ปฏิเสธการปล่อยมือ และไม่อนุญาตให้เจาะจงนำดินก้อนพิเศษมาสุญูด",
            "evidences": "ซุนัน อบูดาวูด 759, ศิฟะตุ เศาะลาติน นบี (อัลบานีย์)"
        },
        "shia": {
            "position": "ปล่อยมือวาญิบ + สุญูดบนดินบริสุทธิ์ (Turbah)",
            "detail": "วาญิบปล่อยมือแนบลำตัว (Sadl/Irsal) การกอดอกถือเป็น 'ตักฟีร' ที่ทำให้ละหมาดเสีย และวาญิบสุญูดลงบนดินบริสุทธิ์หรือหินธรรมชาติที่ไม่ใช่อาหาร/เครื่องนุ่งห่ม จึงนิยมใช้แผ่นดินกัรบะลาอ์ (Turbah)",
            "evidences": "อัล-กาฟี เล่ม 3 หน้า 334, มัน ลา ยะห์ฎุรุฮุล ฟะกีฮ์"
        },
        "ibadi": {
            "position": "ปล่อยมือแนบลำตัว (Irsal) + สุญูดบนพื้นสะอาด",
            "detail": "ยืนละหมาดแบบปล่อยมือแนบลำตัว (Irsal / Sadl) เช่นเดียวกับมัซฮับมาลิกีและชีอะฮ์ สุญูดลงบนพื้นสะอาดทั่วไปได้โดยไม่ต้องใช้ดินก้อนเฉพาะ",
            "evidences": "มุสนัด อัร-รอบีอ์, กิตาบ อัล-อีดอฮ์"
        },
        "key_difference": "ซุนนีส่วนใหญ่กอดอก ชีอะฮ์และอิบาดี (รวมถึงมาลิกี) ปล่อยมือ; ชีอะฮ์กำหนดให้สุญูดบนดิน/หินธรรมชาติเท่านั้น",
        "primary_sources": "ซอฮีฮ์ บุคอรี 740; อัล-มุวัฏเฏาะอ์; มะซาอิล อะฮ์มัด; อัล-กาฟี เล่ม 3; มุสนัด อัร-รอบีอ์"
    },
    {
        "id": 3,
        "topic_key": "divine_attributes",
        "topic_th": "พระลักษณะของอัลลอฮ์และการตีความ (Sifat Allah & Ta'wil)",
        "topic_ar": "صفات الله وتأويلها",
        "issue_description": "การทำความเข้าใจข้อความเกี่ยวกับพระหัตถ์ พระพักตร์ การเสด็จลงมา และการสถิตเหนือบัลลังก์",
        "sunni": {
            "position": "ตัฟวีฎ (Tafwid) หรือ ตะอ์วีล (Ta'wil)",
            "detail": "อัชอะรีและมาตุรีดียึดแนวทางตัฟวีฎ (มอบหมายความหมายที่แท้จริงแด่อัลลอฮ์) หรือตะอ์วีล (ตีความเชิงภาษาเปรียบเทียบ) เพื่อไม่ให้เกิดการเปรียบเทียบกับสิ่งถูกสร้าง (Tanzih)",
            "evidences": "กุรอาน 42:11, ลุอะอ์ อัล-อะดิลละฮ์ (อิมาม อัล-ฮะเราะมัยน์ อัล-ญุวัยนีย์)"
        },
        "salafi": {
            "position": "ยืนยันตามตัวอักษรโดยไม่ถามว่าอย่างไร (Bila Kayf)",
            "detail": "ยึดแนวทางอะษะรี (Athari) ยืนยันพระลักษณะตามตัวบทอักษรโดยไม่ถามว่าอย่างไร (Bila Kayf) ไม่เปรียบเทียบ (Tashbih) และปฏิเสธการตีความเชิงเปรียบเทียบ (Ta'wil) โดยเด็ดขาด",
            "evidences": "อัล-อะกีดะฮ์ อัล-วาซิฏียะฮ์ (อิบนุ ตัยมียะฮ์), ชัรฮ์ อัส-สุนนะฮ์ (อัล-บัรบะฮารีย์)"
        },
        "shia": {
            "position": "ตันซีฮ์บริสุทธิ์ + ตีความเชิงนามธรรม (Ta'wil)",
            "detail": "ยึดหลักเตาฮีดขั้นบริสุทธิ์ (Tawhid al-Sifat) พระองค์ปราศจากอวัยวะและมิติทางกายภาพ ตีความ (Ta'wil) โองการเชิงรูปธรรมโดยอาศัยสติปัญญาและคำสอนของอะฮ์ลุลบัยต์",
            "evidences": "นะฮ์ญุล บะลาเฆาะฮ์ คุฏบะฮ์ที่ 1, อัล-เตาฮีด (ชัยค์ อัศ-ศอดูก)"
        },
        "ibadi": {
            "position": "ตันซีฮ์เด็ดขาด + ปฏิเสธการมองเห็นพระเจ้า (Nafi Ru'yah)",
            "detail": "ยึดแนวทางตันซีฮ์ (Tanzih) ขั้นสมบูรณ์ อัลลอฮ์ไม่มีสิ่งใดเหมือน ไม่สามารถมองเห็นได้ด้วยสายตาทั้งในโลกนี้และในสวรรค์ (Nafi Ru'yatullah) และปฏิเสธการมีอวัยวะอย่างสิ้นเชิง",
            "evidences": "กุรอาน 6:103 (لا تدركه الأبصار), มุสนัด อัร-รอบีอ์, ชัรฮ์ อัน-นีล"
        },
        "key_difference": "สะลัฟยืนยันพระลักษณะตามตัวอักษรแบบ Bila Kayf; ซุนนีอัชอะรีเปิดรับ Ta'wil เพื่อพิทักษ์ Tanzih; ชีอะฮ์และอิบาดีปฏิเสธมิติทางกายภาพและการมองเห็นพระองค์ด้วยสายตา",
        "primary_sources": "กุรอาน 42:11, 7:54; อัล-อะกีดะฮ์ อัล-วาซิฏียะฮ์; ลุอะอ์ อัล-อะดิลละฮ์; นะฮ์ญุล บะลาเฆาะฮ์"
    },
    {
        "id": 4,
        "topic_key": "mutah_marriage",
        "topic_th": "การสมรสชั่วคราว (Nikah al-Mut'ah)",
        "topic_ar": "نكاح المتعة",
        "issue_description": "การแต่งงานที่มีการระบุสินจ้างและกำหนดระยะเวลาสิ้นสุดไว้ล่วงหน้า",
        "sunni": {
            "position": "หะรอมเด็ดขาดและถูกยกเลิกถาวร (Mansukh)",
            "detail": "หะรอมเด็ดขาดและเป็นโมฆะ โดยท่านนบีสั่งห้ามในวันสงครามค็อยบัรและยืนยันในฮัจญ์อำลา ผู้กระทำมีโทษเช่นเดียวกับการทำซินา",
            "evidences": "ซอฮีฮ์ บุคอรี 5115, ซอฮีฮ์ มุสลิม 1407"
        },
        "salafi": {
            "position": "หะรอมเด็ดขาด ถือเป็นบาปใหญ่ (Zina)",
            "detail": "หะรอมเด็ดขาด ถือเป็นบาปใหญ่และเป็นโมฆะตามมติของเศาะฮาบะฮ์และซุนนะฮ์ที่ชัดเจน",
            "evidences": "ซอฮีฮ์ มุสลิม 1406, ฟัตวา อัล-ลัจญ์นะฮ์ อัด-ดาอิมะฮ์"
        },
        "shia": {
            "position": "อนุญาต (มุบาฮ์/มุสตะฮับ)",
            "detail": "อนุญาตโดยมีเงื่อนไขและสินสอดชัดเจน อ้างอิงกุรอาน 4:24 และถือว่าบทบัญญัตินี้ไม่เคยถูกยกเลิกโดยท่านนบี แต่ถูกห้ามโดยเคาะลีฟะฮ์อุมัร",
            "evidences": "กุรอาน 4:24, วะซาอิล อัช-ชีอะฮ์ กิตาบ อัน-นิกาฮ์, อัล-กาฟี เล่ม 5"
        },
        "ibadi": {
            "position": "หะรอมเด็ดขาดและเป็นโมฆะ",
            "detail": "หะรอมเด็ดขาดและเป็นโมฆะอย่างสิ้นเชิง ถือเป็นพฤติกรรมที่ขัดกับเจตนารมณ์ของการแต่งงานในอิสลาม",
            "evidences": "มุสนัด อัร-รอบีอ์, กิตาบ อัล-นีล"
        },
        "key_difference": "ชีอะฮ์ (อิษนาอะชะรียะฮ์) เป็นสำนักเดียวที่อนุญาต มัซฮับซุนนีทั้งหมด สะลัฟ และอิบาดี ถือเป็นหะรอมเด็ดขาดและสัญญาเป็นโมฆะ",
        "primary_sources": "กุรอาน 4:24; ซอฮีฮ์ บุคอรี 5115; ซอฮีฮ์ มุสลิม 1407; วะซาอิล อัช-ชีอะฮ์"
    },
    {
        "id": 5,
        "topic_key": "tawassul_ziyarah",
        "topic_th": "การทำตะวัสสุลและการเยือนกุโบร์ (Tawassul & Ziyarah)",
        "topic_ar": "التوسل والزيارة",
        "issue_description": "การขอความช่วยเหลือโดยอาศัยสื่อบุคคล หรือการเดินทางไปเยือนสุสานของนบีและวะลีย์",
        "sunni": {
            "position": "อนุญาตด้วยความดีและเกียรติของนบี",
            "detail": "อนุญาตให้ทำตะวัสสุลด้วยพระนามของอัลลอฮ์, การงานที่ดี และด้วยเกียรติของท่านนบี (ตามทัศนะญุมฮูรปราชญ์) แต่ห้ามการวิงวอนขอต่อผู้ตายโดยตรง การเยือนสุสานเพื่อระลึกถึงความตายเป็นสุนัต",
            "evidences": "กุรอาน 5:35, สุนัน อัต-ติรมีซี 3578 (ฮะดีษชายตาบอด)"
        },
        "salafi": {
            "position": "อนุญาตเฉพาะ 3 รูปแบบ / ห้ามขอผ่านคนตายเด็ดขาด",
            "detail": "ตะวัสสุลอนุญาตเพียง 3 รูปแบบ (พระนามอัลลอฮ์, การงานที่ดี, คนเป็นที่ยังมีชีวิตขอดุอาอ์ให้) การวิงวอนผ่านคนตายหรือขอให้คนตายช่วยเหลือถือเป็นชิริกใหญ่ การเดินทางเจาะจงเพื่อไปขอดุอาอ์ที่สุสานเป็นสิ่งต้องห้าม",
            "evidences": "กิตาบ อัต-เตาฮีด (มุฮัมมัด อิบน์ อับดิลวะฮ์ฮาบ), กุรอาน 39:3"
        },
        "shia": {
            "position": "หัวใจสำคัญของความศรัทธา + การเยือนศาลเจ้า (Ziyarah)",
            "detail": "การตะวัสสุลและขอชะฟาอัตผ่านท่านนบีและบรรดาอิมาม 12 ท่านเป็นหัวใจสำคัญของความศรัทธา การเยือนศาลเจ้าศักดิ์สิทธิ์ (Ziyarah) เป็นอิบาดะฮ์ที่มีภาคผลบุญสูงยิ่ง",
            "evidences": "กุรอาน 4:64, กามิล อัซ-ซิยารอต (อิบนุ เคาะละวัยฮ์), มะฟาตีห์ อัล-ญินาน"
        },
        "ibadi": {
            "position": "เฉพาะด้วยความดีและการเตาบะฮ์",
            "detail": "ตะวัสสุลทำได้เฉพาะด้วยความดีและการกลับตัว (Tawbah) ปฏิเสธการขอชะฟาอัตให้แก่ผู้กระทำบาปใหญ่ที่ไม่เตาบะฮ์ และไม่อนุญาตให้วิงวอนผ่านสื่อกลางใดๆ",
            "evidences": "กิตาบ อัล-อัดล์ วัล-อินศอฟ, ชัรฮ์ อัน-นีล"
        },
        "key_difference": "ชีอะฮ์เน้นการขอชะฟาอัตผ่านอิมาม; สะลัฟห้ามเด็ดขาดและมองว่าเป็นชิริก; ซุนนีอนุญาตตะวัสสุลด้วยเกียรตินบีแต่มิใช่วิงวอนคนตาย; อิบาดีปฏิเสธชะฟาอัตคนบาปใหญ่",
        "primary_sources": "กุรอาน 5:35; สุนัน ติรมีซี 3578; กิตาบ อัต-เตาฮีด; มะฟาตีห์ อัล-ญินาน"
    },
    {
        "id": 6,
        "topic_key": "imamate_leadership",
        "topic_th": "ตำแหน่งผู้นำสูงสุดและการสืบทอดอำนาจ (Caliphate vs Imamate)",
        "topic_ar": "الخلافة والإمامة",
        "issue_description": "ที่มาของความชอบธรรมในการนำประชาชาติอิสลามหลังการวะฟาตของท่านนบี",
        "sunni": {
            "position": "ชูรอ (Shura) และการสัตยาบัน (Bay'ah)",
            "detail": "ผู้นำ (เคาะลีฟะฮ์) มาจากการปรึกษาหารือ (Shura) และการให้สัตยาบัน (Bay'ah) ลำดับความประเสริฐของ 4 เคาะลีฟะฮ์ตรงตามลำดับการขึ้นครองอำนาจจริง (อบูบักร, อุมัร, อุษมาน, อะลี)",
            "evidences": "กุรอาน 42:38, ซอฮีฮ์ บุคอรี 3667"
        },
        "salafi": {
            "position": "ยึดมั่นตามมติเศาะฮาบะฮ์และคอลีฟะฮ์ทั้งสี่",
            "detail": "ยึดมั่นตามมติของเศาะฮาบะฮ์ ให้เกียรติและรับรองความชอบธรรมของเคาะลีฟะฮ์ทั้งสี่ ห้ามการก่นด่าหรือเคลือบแคลงสงสัยในเกียรติภูมิของบรรดาสาวก",
            "evidences": "สุนัน อบูดาวูด 4607, อะกีดะฮ์ ฏอฮาวียะฮ์"
        },
        "shia": {
            "position": "อิม่ามัตเป็นหลักศรัทธาที่พระเจ้าแต่งตั้ง (Nass)",
            "detail": "อิม่ามัต (Imamate) เป็นหลักศรัทธาข้อหนึ่ง (Usul al-Din) ที่ได้รับการแต่งตั้งโดยตรงจากอัลลอฮ์และท่านนบี (Nass) ณ ค็อดดีร คุม ท่านอะลีคือผู้สืบทอดโดยชอบธรรมท่านแรก และตามด้วยอิมามอีก 11 ท่านผู้ไร้มลทิน (Ma'sum)",
            "evidences": "กุรอาน 5:67 (Ayah al-Tabligh), ฮะดีษ ฆ่อดีร คุม, อัล-กาฟี กิตาบ อัล-ฮุจญะฮ์"
        },
        "ibadi": {
            "position": "เลือกตั้งตามคุณธรรม ไม่จำกัดชาติพันธุ์หรือสายเลือด",
            "detail": "ผู้นำสูงสุด (อิมาม) ต้องได้รับเลือกตั้งจากความยำเกรง ความยุติธรรม และความรู้ ไม่จำกัดชาติพันธุ์หรือสายเลือด ไม่จำเป็นต้องมาจากกุร็อยช์ และสามารถถอดถอนได้หากปฏิบัติไม่เป็นธรรม",
            "evidences": "มุสนัด อัร-รอบีอ์, กิตาบ อัศ-เศาะฮีฮะฮ์"
        },
        "key_difference": "ซุนนีมองเรื่องการเมือง/ชูรอ; ชีอะฮ์ถือเป็นหลักศรัทธาที่มีการแต่งตั้งจากพระเจ้า (Nass); อิบาดีเน้นความสามารถและความยุติธรรมโดยไม่ยึดติดวงศ์ตระกูล",
        "primary_sources": "กุรอาน 4:59, 42:38; ซอฮีฮ์ มุสลิม 1821; นะฮ์ญุล บะลาเฆาะฮ์; มุสนัด อัร-รอบีอ์"
    }
]

def get_cross_sect_matrix(topic_id=None):
    if topic_id is None:
        return CROSS_SECT_MATRIX
    for item in CROSS_SECT_MATRIX:
        if str(item["id"]) == str(topic_id) or item["topic_key"] == str(topic_id):
            return item
    return None

def search_cross_sect(query_text):
    clean = query_text.lower().strip()
    res = []
    for item in CROSS_SECT_MATRIX:
        txt = f"{item['topic_th']} {item['issue_description']} {item['sunni']['detail']} {item['salafi']['detail']} {item['shia']['detail']} {item['ibadi']['detail']} {item['key_difference']}".lower()
        if clean in txt:
            res.append(item)
    return res

# ----------------- Halal E-Number Database Operations -----------------

def search_enumbers(query_text, limit=10, status_filter=None):
    """
    Search Halal E-Number database (E100-E1500) with Sharia status.
    """
    conn = get_connection()
    results = []
    try:
        cursor = conn.cursor()
        clean_q = query_text.strip().replace('"', '""')

        # 1. FTS5
        try:
            if status_filter:
                sql = """
                SELECT rowid as id, e_number, name_th, name_en, category, halal_status, source_origin, explanation, authority_fatwa,
                       bm25(halal_enumbers_fts) as rank
                FROM halal_enumbers_fts
                WHERE halal_enumbers_fts MATCH ? AND halal_status = ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(sql, (f'"{clean_q}"*', status_filter.lower(), limit))
            else:
                sql = """
                SELECT rowid as id, e_number, name_th, name_en, category, halal_status, source_origin, explanation, authority_fatwa,
                       bm25(halal_enumbers_fts) as rank
                FROM halal_enumbers_fts
                WHERE halal_enumbers_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """
                cursor.execute(sql, (f'"{clean_q}"*', limit))
            for r in cursor.fetchall():
                d = dict(r)
                d["code"] = d["e_number"]
                d["status"] = d["halal_status"].capitalize()
                d["origin"] = d["source_origin"]
                d["description_th"] = d["explanation"]
                d["fatwa_sources"] = d["authority_fatwa"]
                results.append(d)
        except Exception:
            pass

        # 2. LIKE fallback
        if len(results) < limit:
            existing_codes = {r["e_number"] for r in results if "e_number" in r}
            like_pat = f"%{clean_q}%"
            if status_filter:
                sql = """
                SELECT id, e_number, name_th, name_en, category, halal_status, source_origin, explanation, authority_fatwa
                FROM halal_enumbers
                WHERE halal_status = ? AND (e_number LIKE ? OR name_th LIKE ? OR name_en LIKE ? OR category LIKE ? OR source_origin LIKE ? OR explanation LIKE ?)
                LIMIT ?
                """
                cursor.execute(sql, (status_filter.lower(), like_pat, like_pat, like_pat, like_pat, like_pat, like_pat, limit))
            else:
                sql = """
                SELECT id, e_number, name_th, name_en, category, halal_status, source_origin, explanation, authority_fatwa
                FROM halal_enumbers
                WHERE e_number LIKE ? OR name_th LIKE ? OR name_en LIKE ? OR category LIKE ? OR source_origin LIKE ? OR explanation LIKE ? OR halal_status LIKE ?
                LIMIT ?
                """
                cursor.execute(sql, (like_pat, like_pat, like_pat, like_pat, like_pat, like_pat, like_pat, limit))
            for r in cursor.fetchall():
                d = dict(r)
                d["code"] = d["e_number"]
                d["status"] = d["halal_status"].capitalize()
                d["origin"] = d["source_origin"]
                d["description_th"] = d["explanation"]
                d["fatwa_sources"] = d["authority_fatwa"]
                if d["e_number"] not in existing_codes:
                    results.append(d)
                    existing_codes.add(d["e_number"])
                if len(results) >= limit:
                    break
        return results
    finally:
        conn.close()

def get_enumber(code):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        clean = code.strip().upper()
        if not clean.startswith("E") and clean.isdigit():
            clean = f"E{clean}"
        cursor.execute("SELECT * FROM halal_enumbers WHERE UPPER(e_number) = ?", (clean,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["code"] = d["e_number"]
        d["status"] = d["halal_status"].capitalize()
        d["origin"] = d["source_origin"]
        d["description_th"] = d["explanation"]
        d["fatwa_sources"] = d["authority_fatwa"]
        return d
    finally:
        conn.close()

# ----------------- Offline Astronomical Prayer Times & Qibla Compass Engine -----------------

def get_julian_date(year, month, day):
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5

def calculate_prayer_times(lat, lon, date_str=None, tz_offset=7, asr_hanafi=False, fajr_angle=18.0, isha_angle=17.0):
    """
    Calculates 5 daily prayer times using astronomical solar position algorithms.
    lat: Latitude in decimal degrees (North positive)
    lon: Longitude in decimal degrees (East positive)
    date_str: 'YYYY-MM-DD' or None (defaults to today)
    tz_offset: UTC offset in hours (default +7 for Thailand)
    asr_hanafi: If True, uses shadow length factor 2 (Hanafi), else 1 (Standard/Shafi'i/Maliki/Hanbali)
    fajr_angle: Fajr solar depression angle in degrees (default 18.0 MWL)
    isha_angle: Isha solar depression angle in degrees (default 17.0 MWL)
    """
    if date_str:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        dt = datetime.date.today()

    jd = get_julian_date(dt.year, dt.month, dt.day)
    d = jd - 2451545.0
    g = (357.529 + 0.98560028 * d) % 360
    q = (280.459 + 0.98564736 * d) % 360
    l_ecl = (q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))) % 360
    eps = 23.439 - 0.00000036 * d

    ra = math.degrees(math.atan2(math.cos(math.radians(eps)) * math.sin(math.radians(l_ecl)), math.cos(math.radians(l_ecl)))) % 360
    eqt = (q / 15.0 - ra / 15.0) * 60.0
    while eqt > 20: eqt -= 1440
    while eqt < -20: eqt += 1440
    dec = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(l_ecl))))

    # Solar noon (Dhuhr)
    noon = 12.0 + tz_offset - (lon / 15.0) - (eqt / 60.0)

    def hour_angle(altitude):
        cos_h = (math.sin(math.radians(altitude)) - math.sin(math.radians(lat)) * math.sin(math.radians(dec))) / (math.cos(math.radians(lat)) * math.cos(math.radians(dec)))
        if cos_h > 1.0: return 0.0
        if cos_h < -1.0: return 180.0
        return math.degrees(math.acos(cos_h))

    # Sunrise & Sunset (center of sun 50 arcminutes = -0.833 deg below horizon)
    h_sun = hour_angle(-0.833) / 15.0
    sunrise = noon - h_sun
    sunset = noon + h_sun

    # Fajr (-fajr_angle)
    h_fajr = hour_angle(-fajr_angle) / 15.0
    fajr = noon - h_fajr

    # Isha (-isha_angle)
    h_isha = hour_angle(-isha_angle) / 15.0
    isha = noon + h_isha

    # Asr
    asr_factor = 2 if asr_hanafi else 1
    asr_alt = math.degrees(math.atan(1.0 / (asr_factor + math.tan(math.radians(abs(lat - dec))))))
    h_asr = hour_angle(asr_alt) / 15.0
    asr = noon + h_asr

    def to_time_str(h):
        h = h % 24
        hours = int(h)
        mins = int(round((h - hours) * 60))
        if mins >= 60:
            hours += 1
            mins = 0
        return f"{hours:02d}:{mins:02d}"

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "coordinates": {"latitude": lat, "longitude": lon},
        "timezone_offset": tz_offset,
        "asr_method": "Hanafi" if asr_hanafi else "Standard (Shafi'i/Maliki/Hanbali)",
        "angles": {"fajr": fajr_angle, "isha": isha_angle},
        "times": {
            "fajr": to_time_str(fajr),
            "sunrise": to_time_str(sunrise),
            "dhuhr": to_time_str(noon + (2.0 / 60.0)),
            "asr": to_time_str(asr),
            "maghrib": to_time_str(sunset + (2.0 / 60.0)),
            "isha": to_time_str(isha)
        }
    }

def calculate_qibla_bearing(lat, lon):
    """
    Calculates great-circle forward azimuth bearing to the Holy Kaaba in Makkah
    (Lat: 21.422487 N, Lon: 39.826206 E).
    Returns bearing in degrees (0-360), compass point, and distance in km.
    """
    k_lat = math.radians(21.422487)
    k_lon = math.radians(39.826206)
    p_lat = math.radians(lat)
    p_lon = math.radians(lon)

    d_lon = k_lon - p_lon
    y = math.sin(d_lon) * math.cos(k_lat)
    x = math.cos(p_lat) * math.sin(k_lat) - math.sin(p_lat) * math.cos(k_lat) * math.cos(d_lon)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360

    # Great-circle distance (Haversine formula)
    d_lat = k_lat - p_lat
    a = math.sin(d_lat / 2)**2 + math.cos(p_lat) * math.cos(k_lat) * math.sin(d_lon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    dist_km = 6371.0 * c

    points = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int(round(bearing / 22.5)) % 16
    compass_pt = points[idx]

    return {
        "latitude": lat,
        "longitude": lon,
        "kaaba_latitude": 21.422487,
        "kaaba_longitude": 39.826206,
        "bearing_degrees": round(bearing, 2),
        "compass_direction": compass_pt,
        "distance_km": round(dist_km, 1)
    }

# ----------------- Quranic Tri-Literal Root Words & Morphology -----------------

def search_quran_roots(query_text):
    """
    Search Quranic tri-literal root words by Arabic root, transliteration, or Thai meaning.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        clean = query_text.strip()
        like_pat = f"%{clean}%"
        clean_nospace = clean.replace(" ", "")
        sql = """
        SELECT id, root_ar, root_lat, meaning_th, frequency_in_quran, derived_words, sample_ayah, theological_significance
        FROM quran_roots
        WHERE root_ar LIKE ? OR root_lat LIKE ? OR meaning_th LIKE ? OR derived_words LIKE ?
           OR REPLACE(root_ar, ' ', '') = ?
        ORDER BY frequency_in_quran DESC
        """
        cursor.execute(sql, (like_pat, like_pat, like_pat, like_pat, clean_nospace))
        rows = cursor.fetchall()
        res = []
        for r in rows:
            d = dict(r)
            d["root_arabic"] = d["root_ar"]
            d["transliteration"] = d["root_lat"]
            d["occurrences_count"] = d["frequency_in_quran"]
            try:
                d["derivatives"] = json.loads(d["derived_words"])
            except Exception:
                d["derivatives"] = []
            d["sample_verses"] = [{"ref": "", "surah_name": "", "ayah_text": d["sample_ayah"]}]
            res.append(d)
        return res
    finally:
        conn.close()

def get_quran_root(root_arabic):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        clean = root_arabic.strip()
        clean_nospace = clean.replace(" ", "")
        cursor.execute("""
        SELECT id, root_ar, root_lat, meaning_th, frequency_in_quran, derived_words, sample_ayah, theological_significance
        FROM quran_roots
        WHERE root_ar = ? OR REPLACE(root_ar, ' ', '') = ? OR UPPER(root_lat) = UPPER(?)
        """, (clean, clean_nospace, clean))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["root_arabic"] = d["root_ar"]
        d["transliteration"] = d["root_lat"]
        d["occurrences_count"] = d["frequency_in_quran"]
        try:
            d["derivatives"] = json.loads(d["derived_words"])
        except Exception:
            d["derivatives"] = []
        d["sample_verses"] = [{"ref": "", "surah_name": "", "ayah_text": d["sample_ayah"]}]
        return d
    finally:
        conn.close()

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
    q = str(query).lower().strip()
    for item in PROPHETIC_MEDICINE_DATA:
        if category_filter and item["category"] != category_filter:
            continue
        if q.isdigit() and item["id"] == int(q):
            results.append(item)
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
    q = str(query).lower().strip()
    for item in DAILY_ADHKAR_DATA:
        if q.isdigit() and item["id"] == int(q):
            results.append(item)
            continue
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
    q = str(query).lower().strip()
    for item in TAJWEED_RULES_DATA:
        if q.isdigit() and item["id"] == int(q):
            results.append(item)
            continue
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
        c = str(contract_type).lower().strip()
        if c.isdigit():
            return [item for item in ISLAMIC_CONTRACTS_DATA if item["id"] == int(c)]
        return [item for item in ISLAMIC_CONTRACTS_DATA if item["contract_type"].lower() == c or c in item["name_en"].lower() or c in item["name_th"].lower()]
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
    q = str(query).lower().strip()
    for item in HISTORY_TIMELINE_DATA:
        if q.isdigit() and item["id"] == int(q):
            results.append(item)
            continue
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
    if not query or not str(query).strip():
        return []
    q = str(query).lower().strip()
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
            score = calc_relevance(item, ["topic_th", "topic_ar", "issue_description", "key_difference"])
            if score > 0:
                cross_res.append({"module": "Cross-Sect Matrix", "title": item.get("topic_th", ""), "summary": item.get("key_difference", ""), "relevance": score})
        results.extend(sorted(cross_res, key=lambda x: x["relevance"], reverse=True)[:limit])

        fiqh_res = []
        for item in COMPARATIVE_FIQH_DATA:
            score = calc_relevance(item, ["topic_th", "issue_description", "practical_advice"])
            if score > 0:
                fiqh_res.append({"module": "Comparative Fiqh", "title": item.get("topic_th", ""), "summary": item.get("practical_advice", ""), "relevance": score})
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


# ----------------- Formatter -----------------


def format_rag_context(query, quran_results=None, hadith_results=None, fatwa_results=None):
    lines = []
    lines.append(f"### 🔍 ผลการสืบค้นตัวบทปฐมภูมิ (RAG Retrieval for: '{query}')\n")

    if quran_results:
        lines.append(f"#### 📖 พระมหาคัมภีร์อัลกุรอาน ({len(quran_results)} อายะฮ์ที่เกี่ยวข้อง):")
        for i, res in enumerate(quran_results, 1):
            surah_num = res["surah_number"]
            ayah_num = res["ayah_number"]
            surah_name = res["surah_name"]
            ar_text = res["arabic_text"]
            th_text = res["thai_text"]

            lines.append(f"**[{i}] ซูเราะฮ์ {surah_name} (บทที่ {surah_num}:{ayah_num})**")
            lines.append(f"> ۞ **ภาษาอาหรับ:** {ar_text}")
            lines.append(f"> 💬 **คำแปลภาษาไทย:** \"{th_text}\"\n")
    elif quran_results is not None:
        lines.append("*(ไม่พบอายะฮ์อัลกุรอานที่มีคำค้นตรงกันโดยตรง)*\n")

    if hadith_results:
        lines.append(f"#### 📜 อัลฮะดีษ ({len(hadith_results)} บทที่เกี่ยวข้องจากคลัง 34,600+ บท):")
        for j, h in enumerate(hadith_results, 1):
            col_title = h.get("collection_title") or h.get("collection")
            h_num = h["hadith_number"]
            ch_title = h.get("chapter_title", "")
            eng_txt = h.get("english_text", "")
            ar_txt = h.get("arabic_text", "")
            grade = h.get("grade", "Sahih")

            lines.append(f"**[{j}] {col_title} (บทที่ {h_num})**" + (f" — *หมวด: {ch_title}*" if ch_title else "") + f" [สถานะ: {grade}]")
            if ar_txt:
                lines.append(f"> ۞ **ภาษาอาหรับ:** {ar_txt[:280]}...")
            if eng_txt:
                lines.append(f"> 💬 **ตัวบท:** \"{eng_txt[:350]}...\"\n")

    if fatwa_results:
        lines.append(f"#### ⚖️ คำวินิจฉัยและฟัตวาร่วมสมัย ({len(fatwa_results)} ประเด็นที่เกี่ยวข้อง):")
        for k, fatwa in enumerate(fatwa_results, 1):
            f_id = fatwa.get("id")
            cat = fatwa.get("category", "")
            title = fatwa.get("title_th", "")
            ruling = fatwa.get("ruling_summary", "")
            auth = fatwa.get("authorities", "")
            evid = fatwa.get("primary_evidences", "")
            detail = fatwa.get("detailed_explanation", "")

            lines.append(f"**[{k}] {title} (หมวด: {cat} | ID: {f_id})**")
            lines.append(f"> 📌 **คำวินิจฉัยสรุป:** {ruling}")
            if auth:
                lines.append(f"> 🏛️ **สภาชี้ขาด/นักวิชาการ:** {auth}")
            if evid:
                lines.append(f"> 📖 **ตัวบทและหลักฐานอ้างอิง:** {evid}")
            if detail:
                lines.append(f"> 💡 **คำอธิบาย:** {detail[:300]}...\n")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Islamic Big Corpus RAG Engine (Quran 6,236 + Hadith 34,614+ + Contemporary Fatwas + Fiqh Engines)")
    parser.add_argument("--query", "-q", type=str, help="Search query (Thai, Arabic, or English)")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Max results count (default: 5)")
    parser.add_argument("--surah", "-s", type=int, help="Filter by Surah number (1-114)")
    parser.add_argument("--ayah", "-a", type=int, help="Fetch exact Ayah number (requires --surah)")
    parser.add_argument("--hadith", action="store_true", help="Search Hadith collections")
    parser.add_argument("--book", "-b", type=str, help="Specify Hadith book: bukhari, muslim, abudawud, tirmidhi, nasai, ibnmajah, nawawi, qudsi")
    parser.add_argument("--number", "-n", type=int, help="Specify Hadith number (requires --book)")
    parser.add_argument("--fatwa", action="store_true", help="Search contemporary fatwas and modern fiqh issues")
    parser.add_argument("--topic", "-t", type=str, help="Fetch exact fatwa by ID or title keyword (e.g. 1, หุ้น, เลี้ยงดู)")
    parser.add_argument("--category", "-c", type=str, help="Filter fatwas by category (Finance, Family, Food, etc.)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Extensions: Mirath, Qawaid, Comparative Fiqh, Asbab, Tafsir, Audio
    parser.add_argument("--mirath", action="store_true", help="Calculate Islamic inheritance (Mirath / Fara'id)")
    parser.add_argument("--estate", type=float, default=0.0, help="Total gross estate in currency")
    parser.add_argument("--debts", type=float, default=0.0, help="Total debts of deceased")
    parser.add_argument("--funeral", type=float, default=0.0, help="Funeral expenses")
    parser.add_argument("--wills", type=float, default=0.0, help="Washiyyah (wills) requested")
    parser.add_argument("--husband", action="store_true", help="Husband survives")
    parser.add_argument("--wives", type=int, default=0, help="Number of surviving wives (1-4)")
    parser.add_argument("--sons", type=int, default=0, help="Number of surviving sons")
    parser.add_argument("--daughters", type=int, default=0, help="Number of surviving daughters")
    parser.add_argument("--father", action="store_true", help="Father survives")
    parser.add_argument("--mother", action="store_true", help="Mother survives")
    parser.add_argument("--brothers", type=int, default=0, help="Number of full brothers")
    parser.add_argument("--sisters", type=int, default=0, help="Number of full sisters")

    parser.add_argument("--qawaid", "--rule", dest="qawaid_query", nargs="?", const="all", help="Fetch 5 Legal Maxims (Al-Qawa'id al-Fiqhiyyah) by ID or keyword")
    parser.add_argument("--comparative", "--madhhab", dest="comparative_query", nargs="?", const="all", help="Fetch Comparative Fiqh (4 Madhhabs) by ID or keyword")
    parser.add_argument("--asbab", "--nuzul", action="store_true", help="Fetch Asbab al-Nuzul (requires --surah and --ayah, or --query)")
    parser.add_argument("--tafsir", action="store_true", help="Fetch Classical Tafsir (requires --surah and --ayah)")
    parser.add_argument("--audio", action="store_true", help="Get EveryAyah audio URL (requires --surah and --ayah)")
    parser.add_argument("--surah-audio", "--playlist", type=int, dest="surah_audio", help="Get continuous audio playlist for entire Surah")
    parser.add_argument("--reciter", type=str, default="Alafasy_128kbps", help="Reciter folder name for EveryAyah CDN")

    # Grand Upgrade additions:
    parser.add_argument("--sect", type=str, nargs="?", const="all", help="Search or list primary texts of Sects & Traditions (Shia, Salafi, Ibadi, Sufi)")
    parser.add_argument("--sect-name", type=str, help="Filter sect texts by sect name (shia, salafi, ibadi, sufi)")
    parser.add_argument("--cross-sect", "--cross", nargs="?", const="all", dest="cross_sect", help="Comparative Flashpoints Matrix across Sunni, Salafi, Shia, Ibadi (1-6 or all)")
    parser.add_argument("--enumber", "-e", type=str, help="Lookup Halal/Haram food additive E-Number or ingredient (e.g. E120, E441, เจลาติน)")
    parser.add_argument("--prayer", action="store_true", help="Calculate 5 daily prayer times using astronomical solar algorithms")
    parser.add_argument("--qibla", action="store_true", help="Calculate great-circle Qibla bearing and distance to Makkah")
    parser.add_argument("--lat", type=float, default=13.7563, help="Latitude for prayer/qibla (default: Bangkok 13.7563)")
    parser.add_argument("--lon", type=float, default=100.5018, help="Longitude for prayer/qibla (default: Bangkok 100.5018)")
    parser.add_argument("--tz", type=float, default=7.0, help="Timezone offset in hours (default: 7.0 for Thailand)")
    parser.add_argument("--date", type=str, help="Date for prayer times YYYY-MM-DD (default: today)")
    parser.add_argument("--asr-hanafi", action="store_true", help="Use Hanafi Asr calculation (shadow factor 2)")
    parser.add_argument("--root", type=str, help="Lookup Quranic tri-literal root and morphology (e.g. 'س ل م' or 'سلم')")
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


    args = parser.parse_args()

    # Grand Upgrade Handler: Cross-Sect Comparative Matrix
    if args.cross_sect is not None:
        if args.cross_sect == "all":
            res = get_cross_sect_matrix()
        else:
            res = get_cross_sect_matrix(args.cross_sect)
            if not res:
                res = search_cross_sect(args.cross_sect)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            if isinstance(res, list):
                print("### 🌐 เมทริกซ์เปรียบเทียบสำนักคิด (Cross-Sect Comparative Matrix: Sunni vs Salafi vs Shia vs Ibadi)\n")
                for item in res:
                    print(f"**ประเด็นที่ {item['id']}: {item['topic_th']} ({item['topic_ar']})**")
                    print(f"> 🔍 **ประเด็น:** {item['issue_description']}")
                    print(f"- 🟢 **ซุนนี (Sunni):** {item['sunni']['position']} — {item['sunni']['detail'][:110]}...")
                    print(f"- 🔵 **สะลัฟ (Salafi):** {item['salafi']['position']} — {item['salafi']['detail'][:110]}...")
                    print(f"- 🟣 **ชีอะฮ์ (Shia):** {item['shia']['position']} — {item['shia']['detail'][:110]}...")
                    print(f"- 🟠 **อิบาดี (Ibadi):** {item['ibadi']['position']} — {item['ibadi']['detail'][:110]}...")
                    print(f"📌 **จุดต่างสำคัญ:** {item['key_difference']}\n")
            elif res:
                print(f"### 🌐 {res['topic_th']} ({res['topic_ar']}) [หัวข้อที่ {res['id']}]")
                print(f"**ประเด็นพิจารณา:** {res['issue_description']}\n")
                print(f"**1. ซุนนี (Sunni - 4 Madhhabs / Ash'ari & Maturidi):** {res['sunni']['position']}")
                print(f"> 💡 {res['sunni']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['sunni']['evidences']}\n")
                print(f"**2. สะลัฟ / อะษะรี (Salafi / Athari):** {res['salafi']['position']}")
                print(f"> 💡 {res['salafi']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['salafi']['evidences']}\n")
                print(f"**3. ชีอะฮ์ อิษนาอะชะรียะฮ์ (Shia Twelver / Ja'fari):** {res['shia']['position']}")
                print(f"> 💡 {res['shia']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['shia']['evidences']}\n")
                print(f"**4. อิบาดี (Ibadi - Oman):** {res['ibadi']['position']}")
                print(f"> 💡 {res['ibadi']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['ibadi']['evidences']}\n")
                print(f"📌 **จุดต่างเชิงหลักการ:** {res['key_difference']}")
                print(f"🏛️ **คัมภีร์อ้างอิง:** {res['primary_sources']}")
            else:
                print(f"Error: Cross-sect topic '{args.cross_sect}' not found.")
                sys.exit(1)
        return

    # Grand Upgrade Handler: Sect Primary Texts
    if args.sect is not None:
        sect_q = "" if args.sect == "all" else args.sect
        if args.query:
            sect_q = args.query
        res = search_sect_texts(sect_q, limit=args.limit, sect_filter=args.sect_name)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"### 📚 ตำราและตัวบทปฐมภูมิสำนักคิดและแนวทางอิสลาม ({len(res)} รายการ)\n")
            for item in res:
                sect_badge = f"[{item['sect'].upper()}]"
                print(f"**{sect_badge} {item['book_title']} — โดย {item['author']}** ({item['passage_ref']})")
                if item.get('arabic_text'):
                    print(f"> ۞ **ตัวบทอาหรับ:** {item['arabic_text'][:250]}...")
                print(f"> 💬 **แปลไทย:** {item['thai_translation']}")
                print(f"> 💡 **บริบทเทววิทยา:** {item['theological_context']}\n")
        return

    # Grand Upgrade Handler: Halal E-Number Database
    if args.enumber:
        exact = get_enumber(args.enumber)
        if exact:
            res = [exact]
        else:
            res = search_enumbers(args.enumber, limit=args.limit)
        if args.json:
            print(json.dumps(res if len(res) > 1 else exact, ensure_ascii=False, indent=2))
        else:
            if not res:
                print(f"ไม่พบข้อมูลวัตถุเจือปนสำหรับ: '{args.enumber}'")
                sys.exit(1)
            print(f"### 🧪 ฐานข้อมูลสารเจือปนอาหารและสถานะชะรีอะฮ์ ({len(res)} รายการ)\n")
            for item in res:
                status_icon = "✅" if item['status'] == 'Halal' else ("❌" if item['status'] == 'Haram' else "⚠️")
                print(f"**{status_icon} [{item['code']}] {item['name_th']} ({item['name_en']})**")
                print(f"- **สถานะชะรีอะฮ์:** {item['status']} | **ประเภท:** {item['category']}")
                print(f"- **แหล่งที่มา/วัตถุดิบ:** {item['origin']}")
                print(f"> 💡 **คำอธิบาย:** {item['description_th']}")
                print(f"> 🏛️ **การวินิจฉัย/ฟัตวา:** {item['fatwa_sources']}\n")
        return

    # Grand Upgrade Handler: Astronomical Prayer Times
    if args.prayer:
        p_res = calculate_prayer_times(args.lat, args.lon, date_str=args.date, tz_offset=args.tz, asr_hanafi=args.asr_hanafi)
        if args.json:
            print(json.dumps(p_res, ensure_ascii=False, indent=2))
        else:
            print(f"### 🕌 ตารางเวลาละหมาดดาราศาสตร์ประจำวัน (Astronomical Prayer Times)")
            print(f"- **วันที่:** {p_res['date']} (UTC{args.tz:+.1f})")
            print(f"- **พิกัด:** ละติจูด {p_res['coordinates']['latitude']:.4f}°N, ลองจิจูด {p_res['coordinates']['longitude']:.4f}°E")
            print(f"- **วิธีคำนวณเวลาอัศรี:** {p_res['asr_method']}")
            print("\n| เวลาละหมาด (Salat) | เวลาท้องถิ่น | คำอธิบายดาราศาสตร์ |")
            print("| :--- | :---: | :--- |")
            print(f"| **ซุบฮี (Fajr)** | **{p_res['times']['fajr']}** | แสงอรุณจริง (ดวงอาทิตย์ต่ำกว่าขอบฟ้า 18°) |")
            print(f"| **ดวงอาทิตย์ขึ้น (Sunrise)** | {p_res['times']['sunrise']} | ขอบบนของดวงอาทิตย์พ้นขอบฟ้า |")
            print(f"| **ซุฮรี (Dhuhr)** | **{p_res['times']['dhuhr']}** | ดวงอาทิตย์คล้อยจากจุดกึ่งกลางท้องฟ้า (Zawal +2m) |")
            print(f"| **อัศรี (Asr)** | **{p_res['times']['asr']}** | เงาวัตถุยื่นยาวเท่ากับตัววัตถุ (หรือ 2 เท่าสำหรับฮะนะฟี) |")
            print(f"| **มัฆริบ (Maghrib)** | **{p_res['times']['maghrib']}** | ดวงอาทิตย์ตกลับขอบฟ้าอย่างสมบูรณ์ |")
            print(f"| **อิชาอ์ (Isha)** | **{p_res['times']['isha']}** | สิ้นสุดแสงสนธยาสีแดง (ดวงอาทิตย์ต่ำกว่าขอบฟ้า 17°) |")
        return

    # Grand Upgrade Handler: Qibla Compass Bearing
    if args.qibla:
        q_res = calculate_qibla_bearing(args.lat, args.lon)
        if args.json:
            print(json.dumps(q_res, ensure_ascii=False, indent=2))
        else:
            print(f"### 🧭 ทิศกิบลัตสู่มหาอัลกะอ์บะฮ์ มักกะฮ์ (Qibla Direction & Kaaba Bearing)")
            print(f"- **พิกัดผู้สังเกต:** ละติจูด {q_res['latitude']:.4f}°N, ลองจิจูด {q_res['longitude']:.4f}°E")
            print(f"- **พิกัดมหาอัลกะอ์บะฮ์:** ละติจูด 21.4225°N, ลองจิจูด 39.8262°E")
            print(f"- **มุมทิศกิบลัต (Forward Azimuth):** **{q_res['bearing_degrees']:.2f}°** จากทิศเหนือจริง (ทิศ {q_res['compass_direction']})")
            print(f"- **ระยะทางวงกลมใหญ่ (Great-Circle Distance):** **{q_res['distance_km']:,} กิโลเมตร**")
        return

    # Grand Upgrade Handler: Quranic Roots Explorer
    if args.root:
        exact_root = get_quran_root(args.root)
        if exact_root:
            r_list = [exact_root]
        else:
            r_list = search_quran_roots(args.root)
        if args.json:
            print(json.dumps(r_list if len(r_list) > 1 else exact_root, ensure_ascii=False, indent=2))
        else:
            if not r_list:
                print(f"ไม่พบข้อมูลรากศัพท์กุรอานสำหรับ: '{args.root}'")
                sys.exit(1)
            print(f"### 🌿 การสืบค้นรากศัพท์ภาษาอาหรับในอัลกุรอาน ({len(r_list)} รากศัพท์)\n")
            for item in r_list:
                print(f"**۞ รากศัพท์: {item['root_arabic']} ({item['transliteration']})** — ความหมาย: **{item['meaning_th']}**")
                print(f"- **ความถี่ในอัลกุรอาน:** ปรากฏ {item['occurrences_count']} ครั้ง")
                if item.get('derivatives'):
                    print(f"- **คำอนุพันธ์หลัก:**")
                    for d in item['derivatives']:
                        if isinstance(d, dict):
                            print(f"  * **{d.get('word', '')}** ({d.get('form', '')}): {d.get('meaning', '')}")
                        else:
                            print(f"  * {d}")
                if item.get('sample_verses'):
                    print(f"- **ตัวอย่างอายะฮ์และบริบท:**")
                    for v in item['sample_verses']:
                        if isinstance(v, dict):
                            ref_str = f"ซูเราะฮ์ {v.get('surah_name', '')} [{v.get('ref', '')}]: " if v.get('ref') else ""
                            print(f"  * {ref_str}\"{v.get('ayah_text', '')}\"")
                        else:
                            print(f"  * {v}")
                if item.get('theological_significance'):
                    print(f"> 💡 **นัยยะทางเทววิทยาและภาษาศาสตร์:** {item['theological_significance']}")
                print()
        return
    
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
            if item.get("prophetic_reference") and item["prophetic_reference"] != "-":
                print(f"    - 📖 อ้างอิง: {item['prophetic_reference']} ({item['hadith_source']})")
            if item.get("modern_evidence") and item["modern_evidence"] != "-":
                print(f"    - 🔬 วิทยาศาสตร์/การแพทย์สมัยใหม่: {item['modern_evidence']}")
            if item.get("health_benefits") and item["health_benefits"] != "-":
                print(f"    - ✅ สรรพคุณ: {item['health_benefits']}")
            if item.get("cautions") and item["cautions"] != "-":
                print(f"    - ⚠️ ข้อควรระวัง: {item['cautions']}")
            if item.get("bioethics_note") and item["bioethics_note"] != "-":
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

    # 1. Mirath Inheritance Calculation
    if args.mirath:
        heirs = {
            "husband": args.husband,
            "wives": args.wives,
            "sons": args.sons,
            "daughters": args.daughters,
            "father": args.father,
            "mother": args.mother,
            "brothers": args.brothers,
            "sisters": args.sisters
        }
        res = calculate_mirath(args.estate, heirs, debts=args.debts, funeral=args.funeral, washiyyah=args.wills)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print("### ⚖️ ผลการคำนวณมรดกตามหลักนิติศาสตร์อิสลาม (Islamic Inheritance Calculation)")
            print(f"- **ทรัพย์สินรวมก่อนหัก:** {res['estate_gross']:,.2f} บาท")
            print(f"- **หักหนี้สิน:** {res['debts']:,.2f} บาท | **ค่าจัดการศพ:** {res['funeral']:,.2f} บาท")
            print(f"- **หักพินัยกรรม (สูงสุดไม่เกิน 1/3):** {res['wills_allowed']:,.2f} บาท (ขอมา: {res['wills_requested']:,.2f} บาท)")
            print(f"- **กองมรดกสุทธิที่จะจัดสรร:** {res['distributable_estate']:,.2f} บาท")
            print(f"- **สถานะการจัดสรร:** {res['adjustment_type']}")
            if res['hajb_notes']:
                print("- **การกันสิทธิ์ (อัล-ฮัจญ์บ์):**")
                for note in res['hajb_notes']:
                    print(f"  * {note}")
            print("\n| ทายาทผู้มีสิทธิ์ | สัดส่วนเศษส่วน | ร้อยละ (%) | ยอดเงินที่ได้รับ (บาท) |")
            print("| :--- | :---: | :---: | :--- |")
            for b in res['breakdown']:
                print(f"| {b['heir']} | {b['fraction_str']} | {b['percentage']:.2f}% | {b['amount']:,.2f} บาท |")
        return

    # 2. Qawa'id Fiqhiyyah (5 Legal Maxims)
    if args.qawaid_query is not None:
        if args.qawaid_query == "all":
            res = get_qawaid()
        else:
            res = get_qawaid(args.qawaid_query)
            if not res:
                res = search_qawaid(args.qawaid_query)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            if isinstance(res, list):
                print("### 📜 5 กฎนิติศาสตร์แม่บท (Al-Qawa'id al-Fiqhiyyah al-Khamsah)\n")
                for r in res:
                    print(f"**กฎข้อที่ {r['id']}: {r['title_ar']} ({r['transliteration']})**")
                    print(f"> 📌 **ความหมาย:** {r['title_th']} — {r['meaning']}")
                    print(f"> 📖 **ตัวบทอ้างอิง:** {r['primary_evidence']}")
                    print(f"> 💡 **การนำไปประยุกต์:** {r['contemporary_applications'][0]}\n")
            elif res:
                print(f"### 📜 กฎข้อที่ {res['id']}: {res['title_ar']} ({res['transliteration']})")
                print(f"**ความหมายภาษาไทย:** {res['title_th']}")
                print(f"\n> 📌 **คำอธิบาย:** {res['meaning']}")
                print(f"\n> 📖 **ตัวบทหลักฐาน:** {res['primary_evidence']}")
                print("\n> 💡 **การประยุกต์ใช้ในยุคปัจจุบัน:**")
                for app in res['contemporary_applications']:
                    print(f"- {app}")
            else:
                print(f"Error: Rule '{args.qawaid_query}' not found.")
                sys.exit(1)
        return

    # 3. Comparative Fiqh (4 Sunni Madhhabs)
    if args.comparative_query is not None:
        if args.comparative_query == "all":
            res = get_comparative_fiqh()
        else:
            res = get_comparative_fiqh(args.comparative_query)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            if isinstance(res, list):
                print("### ⚖️ เมทริกซ์ 4 มัซฮับเปรียบเทียบ (Comparative Fiqh Matrix)\n")
                for t in res:
                    print(f"**หัวข้อที่ {t['id']}: {t['topic_th']}**")
                    print(f"> 🔍 **ประเด็น:** {t['issue_description']}")
                    print(f"- **ฮะนะฟี:** {t['hanafi']['ruling']} ({t['hanafi']['detail'][:90]}...)")
                    print(f"- **มาลิกี:** {t['maliki']['ruling']} ({t['maliki']['detail'][:90]}...)")
                    print(f"- **ชาฟิอี:** {t['shafii']['ruling']} ({t['shafii']['detail'][:90]}...)")
                    print(f"- **ฮันบะลี:** {t['hanbali']['ruling']} ({t['hanbali']['detail'][:90]}...)\n")
            elif res:
                print(f"### ⚖️ {res['topic_th']} [หัวข้อที่ {res['id']}]")
                print(f"**ประเด็นพิจารณา:** {res['issue_description']}\n")
                print(f"**1. มัซฮับฮะนะฟี (Hanafi):** {res['hanafi']['ruling']}")
                print(f"> 💡 {res['hanafi']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['hanafi']['evidence']}\n")
                print(f"**2. มัซฮับมาลิกี (Maliki):** {res['maliki']['ruling']}")
                print(f"> 💡 {res['maliki']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['maliki']['evidence']}\n")
                print(f"**3. มัซฮับชาฟิอี (Shafi'i):** {res['shafii']['ruling']}")
                print(f"> 💡 {res['shafii']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['shafii']['evidence']}\n")
                print(f"**4. มัซฮับฮันบะลี (Hanbali):** {res['hanbali']['ruling']}")
                print(f"> 💡 {res['hanbali']['detail']}")
                print(f"> 📖 *หลักฐาน:* {res['hanbali']['evidence']}\n")
                print(f"📌 **แนวทางปฏิบัติที่เป็นเลิศ:** {res['practical_advice']}")
            else:
                print(f"Error: Comparative topic '{args.comparative_query}' not found.")
                sys.exit(1)
        return

    # 4. Asbab al-Nuzul lookup
    if args.asbab:
        if args.surah and args.ayah:
            res = get_asbab_al_nuzul(args.surah, args.ayah)
        elif args.query:
            res = search_asbab_al_nuzul(args.query)
        else:
            res = ASBAB_DATA
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            if isinstance(res, list):
                print(f"### 📖 สาเหตุแห่งการประทานอายะฮ์ (Asbab al-Nuzul - {len(res)} รายการ)\n")
                for item in res:
                    print(f"**ซูเราะฮ์ {item['surah_name']} [{item['surah']}:{item['ayah']}]**")
                    print(f"> ۞ *ตัวบท:* \"{item['verse_text_th']}\"")
                    print(f"> 📜 *ปราชญ์อ้างอิง:* {item['authorities']}")
                    print(f"> 💡 *บริบทประวัติศาสตร์:* {item['context_th']}\n")
            elif res:
                print(f"### 📖 สาเหตุแห่งการประทาน: ซูเราะฮ์ {res['surah_name']} [{res['surah']}:{res['ayah']}]")
                print(f"> ۞ **ตัวบทอายะฮ์:** \"{res['verse_text_th']}\"")
                print(f"\n> 🏛️ **แหล่งอ้างอิง:** {res['authorities']}")
                print(f"\n> 💡 **บริบทและเหตุการณ์ประวัติศาสตร์:** {res['context_th']}")
            else:
                print(f"ไม่พบบันทึก Asbab al-Nuzul สำหรับ {args.surah}:{args.ayah}")
        return

    # 5. Classical Tafsir lookup
    if args.tafsir:
        if not (args.surah and args.ayah):
            print("Error: --tafsir requires --surah N --ayah N.")
            sys.exit(1)
        res = get_tafsir(args.surah, args.ayah)
        if not res:
            print(f"ไม่พบตัฟซีรคลาสสิกสำหรับ {args.surah}:{args.ayah}")
            sys.exit(1)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"### 📚 อรรถกถาตัฟซีรคลาสสิก (Classical Tafsir) [{args.surah}:{args.ayah}]")
            print(f"\n**1. Tafsir Ibn Kathir (ตัฟซีร อิบนุ กะษีร):**")
            print(f"> {res['ibn_kathir']}")
            print(f"\n**2. Tafsir al-Jalalayn (ตัฟซีร อัล-ญะลาลัยน์):**")
            print(f"> {res['jalalayn']}")
            print(f"\n**3. Tafsir al-Sa'di (ตัฟซีร อัส-สะอ์ดีย์):**")
            print(f"> {res['sadi']}")
        return

    # 6. EveryAyah Audio URL lookup
    if args.audio:
        if not (args.surah and args.ayah):
            print("Error: --audio requires --surah N --ayah N.")
            sys.exit(1)
        url = get_audio_url(args.surah, args.ayah, args.reciter)
        if args.json:
            print(json.dumps({"surah": args.surah, "ayah": args.ayah, "reciter": args.reciter, "audio_url": url}))
        else:
            print(f"### 🎧 EveryAyah Audio Stream [{args.surah}:{args.ayah}]")
            print(f"- **กอรี:** {args.reciter}")
            print(f"- **URL:** {url}")
        return

    # 6.2. EveryAyah Surah Continuous Audio Playlist lookup
    if args.surah_audio:
        res = get_surah_audio_playlist(args.surah_audio, args.reciter)
        if not res:
            print(f"Error: Surah #{args.surah_audio} not found.")
            sys.exit(1)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"### 🎧 EveryAyah Continuous Audio Playlist: ซูเราะฮ์ {res['name_th']} ({res['name_ar']}) [#{res['surah']}]")
            print(f"- **กอรี:** {res['reciter']}")
            print(f"- **จำนวนอายะฮ์ทั้งหมด:** {res['total_verses']} อายะฮ์ (เล่นยาวต่อเนื่อง)")
            print("\n**URL เสียงอ่านทีละอายะฮ์ (10 วรรคแรก):**")
            for item in res['playlist'][:10]:
                print(f"- อายะฮ์ {item['ayah']}: {item['url']}")
            if res['total_verses'] > 10:
                print(f"- ... และอีก {res['total_verses'] - 10} อายะฮ์")
        return


    # 7. Exact Fatwa lookup
    if args.topic:
        res = get_fatwa(args.topic)
        if not res:
            print(f"Error: Fatwa topic '{args.topic}' not found.")
            sys.exit(1)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"### ⚖️ {res['title_th']} [ID: {res['id']}]")
            print(f"**หมวด:** {res['category']} | **สภาชี้ขาด:** {res['authorities']}")
            print(f"\n> 📌 **คำวินิจฉัยสรุป:** {res['ruling_summary']}")
            print(f"\n> 📖 **ตัวบทอ้างอิง:** {res['primary_evidences']}")
            print(f"\n> 💡 **คำอธิบายละเอียด:** {res['detailed_explanation']}")
        return

    # 8. Exact Hadith lookup
    if args.book and args.number:
        res = get_exact_hadith(args.book, args.number)
        if not res:
            print(f"Error: Hadith {args.book} #{args.number} not found.")
            sys.exit(1)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"### 📜 {res['collection_title']} [บทที่ {res['hadith_number']}]")
            if res.get("chapter_title"):
                print(f"**หมวดหมู่:** {res['chapter_title']}")
            print(f"**สถานะความน่าเชื่อถือ:** {res.get('grade', 'Sahih')}")
            if res.get("arabic_text"):
                print(f"\n> **ภาษาอาหรับ:** {res['arabic_text']}")
            print(f"\n> **ตัวบท:** {res['english_text']}")
        return

    # 9. Exact Quran verse lookup
    if args.surah and args.ayah:
        res = get_exact_ayah(args.surah, args.ayah)
        if not res:
            print(f"Error: Verse {args.surah}:{args.ayah} not found.")
            sys.exit(1)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"### ۞ ซูเราะฮ์ {res['name_th']} ({res['name_ar']}) [{res['surah_number']}:{res['ayah_number']}]")
            print(f"**ประเภท:** {res['revelation_type']} | **ชื่ออังกฤษ:** {res['name_en']}")
            print(f"\n> **ภาษาอาหรับ:** {res['arabic_text']}")
            print(f"\n> **คำแปลไทย:** {res['thai_text']}")
        return

    if not args.query:
        print("Error: Specify --query '...' or (--surah N --ayah N) or (--book BOOK --number N) or (--topic ID) or --mirath or --qawaid or --comparative.")
        sys.exit(1)

    # Search operations
    if args.fatwa and not args.hadith and not args.surah:
        fatwa_res = search_fatwas(args.query, limit=args.limit, category_filter=args.category)
        if args.json:
            print(json.dumps(fatwa_res, ensure_ascii=False, indent=2))
        else:
            print(format_rag_context(args.query, quran_results=None, hadith_results=None, fatwa_results=fatwa_res))
        return

    if args.hadith and not args.surah and not args.fatwa:
        hadith_res = search_hadith(args.query, limit=args.limit, collection_filter=args.book)
        if args.json:
            print(json.dumps(hadith_res, ensure_ascii=False, indent=2))
        else:
            print(format_rag_context(args.query, quran_results=None, hadith_results=hadith_res))
        return

    # Broad search: Quran + Hadith + Fatwa (if applicable)
    quran_res = search_quran(args.query, limit=args.limit, surah_filter=args.surah) if not args.hadith else None
    hadith_res = search_hadith(args.query, limit=args.limit, collection_filter=args.book) if (args.hadith or not args.surah) else None
    fatwa_res = search_fatwas(args.query, limit=args.limit, category_filter=args.category)

    if args.json:
        print(json.dumps({"quran": quran_res, "hadith": hadith_res, "fatwa": fatwa_res}, ensure_ascii=False, indent=2))
    else:
        print(format_rag_context(args.query, quran_results=quran_res, hadith_results=hadith_res, fatwa_results=fatwa_res))

if __name__ == "__main__":
    main()
