#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated Audit & Test Suite for Islamic Scholar Agent & RAG System
Covers 4 Dimensions (Minimum 10 cases per dimension, 52 test cases total):
  1. Base Cases (กรณีพื้นฐานปกติ - 14 เคส)
  2. Boundary Cases (กรณีขอบเขต/ค่าสุดทาง - 14 เคส)
  3. Edge Cases (กรณีปลายขอบ/ข้อมูลผิดปกติ/SQL Injection - 13 เคส)
  4. Corner Cases (กรณีซ้อนเงื่อนไขหลายมิติ / Dual Violations - 11 เคส)
"""

import os
import sys
import unittest
import sqlite3

# Ensure UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add path for rag_engine imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from rag_engine import (
    get_connection,
    get_exact_ayah,
    search_quran,
    get_exact_hadith,
    search_hadith,
    get_fatwa,
    search_fatwas,
    calculate_mirath,
    get_qawaid,
    search_qawaid,
    get_comparative_fiqh,
    get_asbab_al_nuzul,
    search_asbab_al_nuzul,
    get_tafsir,
    get_audio_url,
    get_surah_audio_playlist,
    search_sect_texts,
    get_sect_text,
    get_cross_sect_matrix,
    search_cross_sect,
    search_enumbers,
    get_enumber,
    calculate_prayer_times,
    calculate_qibla_bearing,
    search_quran_roots,
    get_quran_root,
    search_prophetic_medicine,
    get_prophetic_medicine,
    get_daily_adhkar,
    search_daily_adhkar,
    get_quran_chronology,
    get_surah_chronology,
    get_tajweed_rules,
    search_tajweed,
    get_islamic_contracts,
    calculate_murabahah,
    get_history_timeline,
    search_history_timeline,
    omni_search,
    DB_PATH
)


# Helper functions for standalone Fiqh calculation validation
def calculate_zakat(cash, gold, debt, nisab_threshold=280000.0):
    net_wealth = (cash + gold) - debt
    if net_wealth >= nisab_threshold:
        return True, net_wealth * 0.025, net_wealth
    else:
        return False, 0.0, net_wealth

def evaluate_aaoifi_stock(core_business_is_halal, market_cap, debt, total_revenue, non_halal_income):
    # Prevent division by zero
    if market_cap <= 0 or total_revenue <= 0:
        return False, 0.0, 0.0, "Invalid market cap or revenue (must be > 0)", 0.0
    
    debt_ratio = (debt / marketCap if False else (debt / market_cap) * 100)
    non_halal_ratio = (non_halal_income / total_revenue) * 100
    tathir_amount = max(0.0, non_halal_income)

    violations = []
    if not core_business_is_halal:
        violations.append("Core business is haram")
    if debt_ratio > 33.00:
        violations.append(f"Debt ratio {debt_ratio:.2f}% exceeds 33.00%")
    if non_halal_ratio > 5.00:
        violations.append(f"Non-halal revenue {non_halal_ratio:.2f}% exceeds 5.00%")

    is_compliant = (len(violations) == 0)
    return is_compliant, debt_ratio, non_halal_ratio, violations, tathir_amount

def allocate_nafaqah(income, wife_needed, kids_needed, parents_needed):
    rem = max(0.0, income)
    
    # Tier 1: Wife (Binding Debt)
    wife_paid = min(rem, wife_needed)
    rem -= wife_paid
    wife_shortfall = max(0.0, wife_needed - wife_paid)

    # Tier 2: Kids
    kids_paid = min(rem, kids_needed)
    rem -= kids_paid
    kids_shortfall = max(0.0, kids_needed - kids_paid)

    # Tier 3: Parents
    parents_paid = min(rem, parents_needed)
    rem -= parents_paid
    parents_shortfall = max(0.0, parents_needed - parents_paid)

    return {
        "wife_paid": wife_paid, "wife_shortfall": wife_shortfall,
        "kids_paid": kids_paid, "kids_shortfall": kids_shortfall,
        "parents_paid": parents_paid, "parents_shortfall": parents_shortfall,
        "remaining_savings": rem
    }


# =====================================================================
# DIMENSION 1: BASE CASES (กรณีพื้นฐานปกติ - 22 เคส)
# =====================================================================

class TestBaseCases(unittest.TestCase):
    """ทดสอบกรณีปกติที่ระบบต้องทำงานถูกต้อง 100% ตามการใช้งานมาตรฐาน"""

    def test_base_01_quran_fatihah(self):
        """ดึงซูเราะฮ์อัล-ฟาติฮะฮ์ อายะฮ์ที่ 1 (บิสมิลลาฮ์)"""
        res = get_exact_ayah(1, 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["surah_number"], 1)
        self.assertEqual(res["ayah_number"], 1)
        self.assertIn("الرَّحْمَٰنِ الرَّحِيمِ", res["arabic_text"])
        self.assertTrue(len(res["thai_text"]) > 0)

    def test_base_02_quran_ayat_al_kursi(self):
        """ดึงอายะฮ์อัล-กุรซีย์ (ซูเราะฮ์อัล-บะเกาะเราะฮ์ 2:255)"""
        res = get_exact_ayah(2, 255)
        self.assertIsNotNone(res)
        self.assertEqual(res["surah_number"], 2)
        self.assertEqual(res["ayah_number"], 255)
        self.assertIn("اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ", res["arabic_text"])
        self.assertIn("อัลลอฮ์", res["thai_text"])

    def test_base_03_hadith_bukhari_first(self):
        """ดึง Sahih al-Bukhari บทที่ 1 (เจตนา / เหนียต)"""
        res = get_exact_hadith("bukhari", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertIn("intention", res["english_text"].lower())
        self.assertEqual(res["grade"], "Sahih")

    def test_base_04_hadith_muslim_first(self):
        """ดึง Sahih Muslim (ตรวจสอบบทนำ #1 และตัวบทศรัทธา/อีหม่าน #93 Hadith Jibril)"""
        m1 = get_exact_hadith("muslim", 1)
        self.assertIsNotNone(m1)
        self.assertEqual(m1["hadith_number"], 1)
        self.assertEqual(m1["grade"], "Sahih")

        # ตรวจสอบตัวบทแบบเต็มในเศาะฮีฮ์มุสลิม (เช่น ฮะดีษญิบรีล #93)
        m93 = get_exact_hadith("muslim", 93)
        self.assertIsNotNone(m93)
        self.assertTrue(len(m93["english_text"]) > 0)
        self.assertTrue(len(m93["arabic_text"]) > 0)
        self.assertEqual(m93["grade"], "Sahih")

    def test_base_05_hadith_abudawud_first(self):
        """ดึง Sunan Abi Dawud บทที่ 1 (ความสะอาด / การปลดทุกข์)"""
        res = get_exact_hadith("abudawud", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertIn("Hasan Sahih", res["grade"])

    def test_base_06_hadith_tirmidhi_first(self):
        """ดึง Jami' at-Tirmidhi บทที่ 1 (การละหมาดไม่ถูกตอบรับไร้ความสะอาด)"""
        res = get_exact_hadith("tirmidhi", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertEqual(res["grade"], "Sahih")

    def test_base_07_hadith_nasai_first(self):
        """ดึง Sunan an-Nasa'i บทที่ 1 (การล้างมือก่อนจุ่มภาชนะวุฎูอ์)"""
        res = get_exact_hadith("nasai", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertEqual(res["grade"], "Sahih")

    def test_base_08_hadith_ibnmajah_first(self):
        """ดึง Sunan Ibn Majah บทที่ 1 (การยึดมั่นในซุนนะฮ์)"""
        res = get_exact_hadith("ibnmajah", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertEqual(res["grade"], "Sahih")

    def test_base_09_hadith_nawawi_first(self):
        """ดึง An-Nawawi 40 บทที่ 1"""
        res = get_exact_hadith("nawawi", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertEqual(res["grade"], "Sahih")

    def test_base_10_hadith_qudsi_first(self):
        """ดึง Hadith Qudsi บทที่ 1"""
        res = get_exact_hadith("qudsi", 1)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 1)
        self.assertEqual(res["grade"], "Sahih")

    def test_base_11_fatwa_stock_screening(self):
        """ดึงฟัตวาเกณฑ์หุ้นฮาลาล AAOIFI Standard 21 (Topic 1)"""
        res = get_fatwa(1)
        self.assertIsNotNone(res)
        self.assertIn("AAOIFI", res["title_th"])
        self.assertIn("33%", res["ruling_summary"])
        self.assertIn("5%", res["ruling_summary"])

    def test_base_12_fatwa_kratom(self):
        """ดึงฟัตวาเรื่องพืชกระท่อมและน้ำท่อม 4x100 (Topic 3)"""
        res = get_fatwa(3)
        self.assertIsNotNone(res)
        self.assertIn("กระท่อม", res["title_th"])
        self.assertIn("ฮะรอม", res["ruling_summary"])

    def test_base_13_fiqh_zakat_standard(self):
        """คำนวณซะกาตมาตรฐาน: เงินสด 350k + ทองคำ 50k - หนี้ 20k = สุทธิ 380k (> 280k)"""
        qualifies, zakat_due, net_wealth = calculate_zakat(350000, 50000, 20000, 280000)
        self.assertTrue(qualifies)
        self.assertEqual(net_wealth, 380000)
        self.assertAlmostEqual(zakat_due, 380000 * 0.025, places=2)

    def test_base_14_fiqh_stock_screen_compliant(self):
        """คัดกรองหุ้นฮาลาลมาตรฐาน: ธุรกิจฮาลาล, หนี้ 22%, รายได้ไม่ฮาลาล 2.4% -> ต้องผ่าน"""
        compliant, debt_r, non_h_r, violations, tathir = evaluate_aaoifi_stock(
            core_business_is_halal=True,
            market_cap=10000000,
            debt=2200000,       # 22%
            total_revenue=5000000,
            non_halal_income=120000 # 2.4%
        )
        self.assertTrue(compliant)
        self.assertEqual(len(violations), 0)
        self.assertEqual(tathir, 120000)

    def test_base_15_mirath_simple_husband_daughter(self):
        """คำนวณมรดกพื้นฐาน: สามี + บุตรสาว 1 คน -> สามี 1/4, บุตรสาว 3/4 (ด้วยร็อดด์)"""
        res = calculate_mirath(1000000, {"husband": True, "daughters": 1})
        self.assertEqual(res["distributable_estate"], 1000000.0)
        self.assertIn("Al-Radd", res["adjustment_type"])
        breakdown = {b["heir"]: b["amount"] for b in res["breakdown"]}
        self.assertEqual(breakdown["สามี (Husband)"], 250000.0)
        self.assertEqual(breakdown["บุตรสาว (1 คน)"], 750000.0)

    def test_base_16_mirath_sons_and_daughters(self):
        """คำนวณมรดกอะเศาะบะฮ์: ภรรยา 1 คน + บุตรชาย 1 คน + บุตรสาว 1 คน -> ชายได้ 2 เท่าของหญิง"""
        res = calculate_mirath(800000, {"wives": 1, "sons": 1, "daughters": 1})
        self.assertEqual(res["distributable_estate"], 800000.0)
        breakdown = {b["heir"]: b["amount"] for b in res["breakdown"]}
        self.assertEqual(breakdown["ภรรยา (1 ท่าน)"], 100000.0)
        self.assertAlmostEqual(breakdown["บุตรชาย (1 คน) [อะเศาะบะฮ์]"], 700000 * (2/3), places=1)
        self.assertAlmostEqual(breakdown["บุตรสาว (1 คน) [อะเศาะบะฮ์ร่วม]"], 700000 * (1/3), places=1)

    def test_base_17_qawaid_retrieval(self):
        """ดึง 5 กฎนิติศาสตร์แม่บท: กฎข้อที่ 1 เรื่องเจตนา"""
        rule = get_qawaid(1)
        self.assertIsNotNone(rule)
        self.assertEqual(rule["id"], 1)
        self.assertIn("الأمور بمقاصدها", rule["title_ar"])
        self.assertIn("เจตนา", rule["title_th"])

    def test_base_18_comparative_fiqh_wudu(self):
        """ดึงเมทริกซ์ 4 มัซฮับ: หัวข้อที่ 1 การสัมผัสผิวหนังสตรีต่างเพศ"""
        res = get_comparative_fiqh(1)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], 1)
        self.assertIn("ไม่เสีย", res["hanafi"]["ruling"])
        self.assertIn("เสียน้ำละหมาดเสมอ", res["shafii"]["ruling"])

    def test_base_19_asbab_al_nuzul_defense(self):
        """ดึง Asbab al-Nuzul: ซูเราะฮ์ 2:190 เรื่องการต่อสู้เพื่อป้องกันตัว"""
        asbab = get_asbab_al_nuzul(2, 190)
        self.assertIsNotNone(asbab)
        self.assertIn("อัล-ฮุดัยบียะฮ์", asbab["context_th"])

    def test_base_20_classical_tafsir_kursi(self):
        """ดึงตัฟซีรคลาสสิก: อายะตุลกุรซีย์ 2:255 ครบ 3 ปราชญ์ (อิบนุกะษีร, ญะลาลัยน์, สะอ์ดี)"""
        tafsir = get_tafsir(2, 255)
        self.assertIsNotNone(tafsir)
        self.assertIn("อายะตุลกุรซีย์", tafsir["ibn_kathir"])
        self.assertIn("กุรซีย์", tafsir["jalalayn"])
        self.assertIn("อากีดะฮ์", tafsir["sadi"])


    def test_base_21_everyayah_audio_url(self):
        """ตรวจสอบความถูกต้องของ URL Audio EveryAyah: 1:1"""
        url = get_audio_url(1, 1, "Alafasy_128kbps")
        self.assertEqual(url, "https://everyayah.com/data/Alafasy_128kbps/001001.mp3")

    def test_base_22_continuous_audio_playlist(self):
        """ตรวจสอบระบบเพลย์ลิสต์เสียงอ่านยาวต่อเนื่อง (Continuous Audio Playlist): ซูเราะฮ์อัล-ฟาติฮะฮ์ 7 วรรค"""
        res = get_surah_audio_playlist(1, "Alafasy_128kbps")
        self.assertIsNotNone(res)
        self.assertEqual(res["surah"], 1)
        self.assertEqual(res["total_ayahs"], 7)
        self.assertEqual(len(res["playlist"]), 7)
        self.assertEqual(res["playlist"][0]["url"], "https://everyayah.com/data/Alafasy_128kbps/001001.mp3")
        self.assertEqual(res["playlist"][6]["url"], "https://everyayah.com/data/Alafasy_128kbps/001007.mp3")

    def test_base_23_sect_texts_lookup(self):
        """ดึงตัวบทปฐมภูมิของนิกายและสำนักคิด: ชีอะฮ์, สะละฟีย์, อิบาดี, ซูฟี"""
        shia_res = search_sect_texts("มนุษย์มีอยู่สองจำพวก", sect_filter="shia")
        self.assertTrue(len(shia_res) > 0)
        self.assertIn("Nahj al-Balagha", shia_res[0]["book_title"])

        salafi_res = search_sect_texts("ชิริก", sect_filter="salafi")
        self.assertTrue(len(salafi_res) > 0)
        self.assertIn("Kitab al-Tawhid", salafi_res[0]["book_title"])

        ibadi_res = search_sect_texts("ตักวา", sect_filter="ibadi")
        self.assertTrue(len(ibadi_res) > 0)
        self.assertIn("Musnad al-Rabi", ibadi_res[0]["book_title"])

        sufi_res = search_sect_texts("กออ้อ", sect_filter="sufi")
        self.assertTrue(len(sufi_res) > 0)
        self.assertIn("Masnavi", sufi_res[0]["book_title"])

    def test_base_24_cross_sect_matrix(self):
        """ตรวจสอบตารางเปรียบเทียบข้ามสำนักคิด (Cross-Sect Matrix): 6 ประเด็นพิพาท"""
        matrix = get_cross_sect_matrix()
        self.assertEqual(len(matrix), 6)

        topic1 = get_cross_sect_matrix(1)
        self.assertIsNotNone(topic1)
        self.assertEqual(topic1["topic_key"], "combining_prayers")
        self.assertIn("จำเป็น", topic1["sunni"]["position"])
        self.assertIn("ปกติทุกวัน", topic1["shia"]["position"])

    def test_base_25_halal_enumbers_lookup(self):
        """สืบค้นฐานข้อมูลสารเจือปนอาหารและสถานะฮาลาล: E100, E120, E441"""
        e100 = get_enumber("E100")
        self.assertIsNotNone(e100)
        self.assertEqual(e100["status"], "Halal")
        self.assertIn("ขมิ้นชัน", e100["origin"])

        e120 = get_enumber("E120")
        self.assertIsNotNone(e120)
        self.assertEqual(e120["status"], "Shubhah")
        self.assertIn("Cochineal", e120["origin"])

        e441 = get_enumber("E441")
        self.assertIsNotNone(e441)
        self.assertEqual(e441["status"], "Shubhah")
        self.assertIn("เจลาติน", e441["name_th"])

    def test_base_26_astronomical_prayer_times_bangkok(self):
        """คำนวณเวลาละหมาดดาราศาสตร์สำหรับกรุงเทพมหานคร (13.7563°N, 100.5018°E)"""
        times = calculate_prayer_times(lat=13.7563, lon=100.5018, date_str="2026-03-21", tz_offset=7)
        self.assertIsNotNone(times)
        p_times = times["times"]
        for key in ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]:
            self.assertIn(key, p_times)
            self.assertRegex(p_times[key], r"^\d{2}:\d{2}$")
        # ตรวจสอบลำดับเวลา: Fajr < Sunrise < Dhuhr < Asr < Maghrib < Isha
        self.assertTrue(p_times["fajr"] < p_times["sunrise"] < p_times["dhuhr"] < p_times["asr"] < p_times["maghrib"] < p_times["isha"])

    def test_base_27_qibla_bearing_bangkok(self):
        """คำนวณทิศกิบลัตสู่อัลกะอ์บะฮ์จากกรุงเทพฯ (~286.88° ทิศ WNW)"""
        qibla = calculate_qibla_bearing(lat=13.7563, lon=100.5018)
        self.assertIsNotNone(qibla)
        self.assertAlmostEqual(qibla["bearing_degrees"], 286.88, delta=1.0)
        self.assertEqual(qibla["compass_direction"], "WNW")
        self.assertGreater(qibla["distance_km"], 6400.0)

    def test_base_28_quran_roots_explorer(self):
        """สืบค้นรากศัพท์สามอักษรกุรอาน: س ل م (S-L-M) และ ر ح م (R-H-M)"""
        root_slm = get_quran_root("س ل م")
        self.assertIsNotNone(root_slm)
        self.assertEqual(root_slm["transliteration"], "S-L-M")
        self.assertEqual(root_slm["occurrences_count"], 140)
        self.assertIn("สันติภาพ", root_slm["meaning_th"])
        self.assertTrue(any("إسلام" in d for d in root_slm["derivatives"]))

        roots_rhm = search_quran_roots("เมตตา")
        self.assertTrue(len(roots_rhm) > 0)
        self.assertTrue(any(r["root_lat"] == "R-H-M" for r in roots_rhm))

    def test_base_29_prophetic_medicine_and_bioethics(self):
        """สืบค้นการแพทย์ตามซุนนะฮ์และชีวจริยธรรม: ฮับบะตุสเสาดาอ์, น้ำผึ้ง, IVF"""
        med_seed = get_prophetic_medicine(1)
        self.assertIsNotNone(med_seed)
        self.assertEqual(med_seed["evidence_level"], "strong_evidence")
        self.assertIn("Thymoquinone", med_seed["modern_evidence"])

        med_ivf = search_prophetic_medicine("IVF")
        self.assertTrue(len(med_ivf) > 0)
        self.assertEqual(med_ivf[0]["category"], "bioethics")
        self.assertIn("เซลล์สืบพันธุ์ของสามีภรรยา", med_ivf[0]["bioethics_note"])

    def test_base_30_daily_adhkar_and_tasbih(self):
        """ดึงบทอัซการ์ประจำวันและจำนวนรอบ: ยามเช้า, ยามเย็น, หลังละหมาด 33 ครั้ง"""
        morning_adhkar = get_daily_adhkar("morning")
        self.assertGreaterEqual(len(morning_adhkar), 2)
        self.assertTrue(any(a["repeat_count"] == 100 for a in morning_adhkar))

        after_prayer = get_daily_adhkar("after_prayer")
        self.assertTrue(any(a["repeat_count"] == 33 for a in after_prayer))

        search_res = search_daily_adhkar("กังวล")
        self.assertTrue(len(search_res) > 0)
        self.assertIn("al-hammi", search_res[0]["transliteration"])

    def test_base_31_quran_chronology(self):
        """ตรวจสอบลำดับการประทานอัลกุรอาน (Tartib al-Nuzul): ซูเราะฮ์แรก 96, ซูเราะฮ์ท้ายสุด 110"""
        chronology = get_quran_chronology()
        self.assertEqual(chronology[0]["revelation_order"], 1)
        self.assertEqual(chronology[0]["surah_number"], 96)  # Al-Alaq
        self.assertEqual(chronology[-1]["revelation_order"], 114)
        self.assertEqual(chronology[-1]["surah_number"], 110)  # An-Nasr

        surah_fatihah = get_surah_chronology(1)
        self.assertIsNotNone(surah_fatihah)
        self.assertEqual(surah_fatihah["revelation_order"], 5)

    def test_base_32_tajweed_rules(self):
        """ตรวจสอบคู่มือกฎตัจญ์วีดและสัทศาสตร์: Idgham, Ikhfa, Qalqalah"""
        rules = get_tajweed_rules()
        self.assertEqual(len(rules), 6)
        
        idgham = [r for r in rules if r["rule_en"] == "Idgham"][0]
        self.assertEqual(idgham["category"], "noon_sakinah")
        self.assertIn("مَن يَقُولُ", idgham["arabic_example"])

        qalqalah = [r for r in rules if r["rule_en"] == "Qalqalah"][0]
        self.assertIn("ق ط ب ج د", qalqalah["description_th"])

    def test_base_33_islamic_contracts_murabahah(self):
        """คำนวณสินเชื่อ Murabahah เทียบดอกเบี้ย: เงินต้น 100,000 กำไร 5% 12 เดือน"""
        contracts = get_islamic_contracts()
        self.assertEqual(len(contracts), 6)
        
        calc = calculate_murabahah(principal=100000.0, profit_rate=0.05, tenure_months=12)
        self.assertEqual(calc["total_profit"], 5000.0)
        self.assertEqual(calc["total_price"], 105000.0)
        self.assertEqual(calc["monthly_payment"], 8750.0)
        self.assertIn("conventional_comparison", calc)

    def test_base_34_history_timeline_eras(self):
        """ตรวจสอบไทม์ไลน์ 1,300 ปีแห่งอารยธรรมอิสลาม: 10 ยุคสมัย (610 - 2024 CE)"""
        timeline = get_history_timeline()
        self.assertEqual(len(timeline), 10)
        self.assertEqual(timeline[0]["start_year_ce"], 610)
        self.assertEqual(timeline[6]["era_name_en"], "Ottoman Empire")

        search_baghdad = search_history_timeline("Baghdad")
        self.assertTrue(len(search_baghdad) > 0)
        self.assertEqual(search_baghdad[0]["id"], 4)  # Abbasid

    def test_base_35_omni_search_engine(self):
        """ค้นหาข้ามทุกมอดูลด้วย Omni-Search: ค้นคำว่า 'น้ำผึ้ง' และ 'มุรอบะฮะฮ์'"""
        honey_res = omni_search("น้ำผึ้ง")
        self.assertTrue(len(honey_res) > 0)
        self.assertEqual(honey_res[0]["module"], "Prophetic Medicine & Bioethics")

        murabahah_res = omni_search("มุรอบะฮะฮ์")
        self.assertTrue(len(murabahah_res) > 0)
        self.assertEqual(murabahah_res[0]["module"], "Islamic Contracts")

    def test_base_36_typography_tokens_standard(self):
        """ตรวจสอบมาตรฐาน Typography ระบบ 3 ฟอนต์และ 8-Step Scale ใน Islam_Interactive_Explorer.html"""
        import os, re
        html_path = os.path.join(os.path.dirname(__file__), "Islam_Interactive_Explorer.html")
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check :root font stacks
        self.assertIn("--font-sans:", content)
        self.assertIn("--font-arabic:", content)
        self.assertIn("--font-mono:", content)

        # Check 8-step size scale
        for token in ["--text-2xs", "--text-xs", "--text-sm", "--text-base", "--text-md", "--text-lg", "--text-xl", "--text-2xl", "--text-hero"]:
            self.assertIn(f"{token}:", content)

        # Zero syntax blunders
        self.assertNotIn("'Inter', monospace", content)
        self.assertNotIn("'Inter',monospace", content)

        # Zero 10px illegible text in CSS
        style_match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
        self.assertTrue(style_match is not None)
        css_text = style_match.group(1)
        self.assertEqual(len(re.findall(r"font-size:\s*10px", css_text)), 0)

    def test_base_37_audio_station_hermeneutics_coverage(self):
        """ตรวจสอบความสมบูรณ์ของแท่นศึกษาเสียงอ่านและคลังวิเคราะห์ตัวบทกุรอาน 4 มิติ"""
        import os, re
        html_path = os.path.join(os.path.dirname(__file__), "Islam_Interactive_Explorer.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check analysis card UI
        self.assertIn('id="verseAnalysisCard"', content)
        self.assertIn('id="analysisMorphology"', content)
        self.assertIn('id="analysisContext"', content)
        self.assertIn('id="analysisTafsir"', content)
        self.assertIn('id="analysisFiqh"', content)

        # Check Related Prophetic Hadiths cross-reference card UI
        self.assertIn('id="verseHadithCard"', content)
        self.assertIn('id="analysisHadithBadge"', content)
        self.assertIn('id="analysisHadithText"', content)
        self.assertIn('id="analysisHadithRelation"', content)

        # Check Al-Fatihah all 7 verses in FAMOUS_AYAHS
        for a in range(1, 8):
            self.assertIn(f'"1:{a}":', content)

        # Check landmark verses
        for v in ["2:255", "4:11", "103:1", "112:1", "113:1", "114:1"]:
            self.assertIn(f'"{v}":', content)
            self.assertIn(f'"{v}": {{', content)


    def test_base_38_all_114_surahs_quran_corpus_coverage(self):
        """ตรวจสอบความสมบูรณ์ของคลังอัลกุรอาน 114 ซูเราะฮ์ ครบ 6,236 อายะฮ์ใน QURAN_CORPUS และ SURAHS_META"""
        import os, re
        html_path = os.path.join(os.path.dirname(__file__), "Islam_Interactive_Explorer.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check QURAN_CORPUS and SURAHS_META declarations
        self.assertIn("const QURAN_CORPUS =", content)
        self.assertIn("const SURAHS_META =", content)

        # Check first and last verses of Quran
        self.assertIn('"1:1":', content)
        self.assertIn('"114:6":', content)

        # Check long surahs boundaries
        self.assertIn('"2:286":', content)  # Al-Baqarah last ayah
        self.assertIn('"3:200":', content)  # Aal-Imran last ayah
        self.assertIn('"4:176":', content)  # An-Nisa last ayah

        # Check UI components
        self.assertIn('id="ayahSegmentTabs"', content)
        self.assertIn('class="surah-fast-strip"', content)
        self.assertIn('class="study-mode-bar"', content)
        self.assertIn('id="viewArch"', content)






# =====================================================================
# DIMENSION 2: BOUNDARY CASES (กรณีขอบเขต/ค่าสุดทาง - 18 เคส)
# =====================================================================

class TestBoundaryCases(unittest.TestCase):
    """ทดสอบค่าต่ำสุด สูงสุด และจุดตัดเกณฑ์ (Threshold Boundaries)"""


    def test_boundary_01_quran_first_verse(self):
        """ขอบเขตต่ำสุดของอัลกุรอาน: ซูเราะฮ์ 1 อายะฮ์ 1"""
        res = get_exact_ayah(1, 1)
        self.assertIsNotNone(res)

    def test_boundary_02_quran_last_verse(self):
        """ขอบเขตสูงสุดของอัลกุรอาน: ซูเราะฮ์ 114 อายะฮ์ 6 (อัน-นาส วรรคสุดท้าย)"""
        res = get_exact_ayah(114, 6)
        self.assertIsNotNone(res)
        self.assertIn("مِنَ الْجِنَّةِ وَالنَّاسِ", res["arabic_text"])

    def test_boundary_03_quran_longest_surah_max_verse(self):
        """ซูเราะฮ์ที่ยาวที่สุด (อัล-บะเกาะเราะฮ์): อายะฮ์สุดท้ายที่ 286"""
        res = get_exact_ayah(2, 286)
        self.assertIsNotNone(res)
        self.assertIn("لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا", res["arabic_text"])

    def test_boundary_04_quran_shortest_surah_max_verse(self):
        """ซูเราะฮ์ที่สั้นที่สุด (อัล-เกาษัร): อายะฮ์สุดท้ายที่ 3"""
        res = get_exact_ayah(108, 3)
        self.assertIsNotNone(res)
        self.assertIn("إِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ", res["arabic_text"])

    def test_boundary_05_hadith_bukhari_max_bound(self):
        """บทสุดท้ายของ Sahih al-Bukhari: บทที่ 7563 (กิตาบุต-เตาฮีด วรรคจบ)"""
        res = get_exact_hadith("bukhari", 7563)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 7563)

    def test_boundary_06_hadith_muslim_max_bound(self):
        """บทสุดท้ายของ Sahih Muslim: บทที่ 7563"""
        res = get_exact_hadith("muslim", 7563)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 7563)

    def test_boundary_07_hadith_abudawud_max_bound(self):
        """บทสุดท้ายของ Sunan Abi Dawud: บทที่ 5274"""
        res = get_exact_hadith("abudawud", 5274)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 5274)

    def test_boundary_08_hadith_tirmidhi_max_bound(self):
        """บทสุดท้ายของ Jami' at-Tirmidhi: บทที่ 3956"""
        res = get_exact_hadith("tirmidhi", 3956)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 3956)

    def test_boundary_09_hadith_nasai_max_bound(self):
        """บทสุดท้ายของ Sunan an-Nasa'i: บทที่ 5758"""
        res = get_exact_hadith("nasai", 5758)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 5758)

    def test_boundary_10_hadith_ibnmajah_max_bound(self):
        """บทสุดท้ายของ Sunan Ibn Majah: บทที่ 4341"""
        res = get_exact_hadith("ibnmajah", 4341)
        self.assertIsNotNone(res)
        self.assertEqual(res["hadith_number"], 4341)

    def test_boundary_11_zakat_exact_nisab(self):
        """จุดตัดนิศอบพอดีเป๊ะ: 280,000.00 บาท -> วาญิบต้องจ่าย 7,000 บาท"""
        qualifies, zakat_due, net = calculate_zakat(280000, 0, 0, 280000)
        self.assertTrue(qualifies)
        self.assertEqual(zakat_due, 7000.0)

    def test_boundary_12_zakat_just_below_nisab(self):
        """จุดตัดต่ำกว่านิศอบ 1 บาท: 279,999.00 บาท -> ไม่บังคับจ่าย (0 บาท)"""
        qualifies, zakat_due, net = calculate_zakat(279999, 0, 0, 280000)
        self.assertFalse(qualifies)
        self.assertEqual(zakat_due, 0.0)

    def test_boundary_13_stock_debt_exact_threshold(self):
        """จุดตัดหนี้สินดอกเบี้ย AAOIFI: 33.00% (ผ่าน) vs 33.01% (ตก)"""
        # 33.00%
        pass_compliant, debt_r, _, _, _ = evaluate_aaoifi_stock(True, 100000, 33000, 100000, 0)
        self.assertTrue(pass_compliant)
        self.assertAlmostEqual(debt_r, 33.00, places=2)

        # 33.01%
        fail_compliant, debt_r2, _, violations, _ = evaluate_aaoifi_stock(True, 100000, 33010, 100000, 0)
        self.assertFalse(fail_compliant)
        self.assertTrue(any("Debt ratio" in v for v in violations))

    def test_boundary_14_stock_nonhalal_exact_threshold(self):
        """จุดตัดรายได้ไม่ฮาลาล AAOIFI: 5.00% (ผ่าน) vs 5.01% (ตก)"""
        # 5.00%
        pass_compliant, _, non_h, _, _ = evaluate_aaoifi_stock(True, 100000, 0, 100000, 5000)
        self.assertTrue(pass_compliant)
        self.assertAlmostEqual(non_h, 5.00, places=2)

        # 5.01%
        fail_compliant, _, non_h2, violations, _ = evaluate_aaoifi_stock(True, 100000, 0, 100000, 5010)
        self.assertFalse(fail_compliant)
        self.assertTrue(any("Non-halal revenue" in v for v in violations))

    def test_boundary_15_mirath_wills_cap(self):
        """จุดตัดพินัยกรรม (อัล-วะศียะฮ์): ห้ามเกิน 1/3 ของกองมรดกสุทธิหลังหักหนี้สินและค่าทำศพ"""
        # กองมรดก 1,000,000 - หนี้ 50,000 - ค่าศพ 50,000 = สุทธิ 900,000
        # ขอทำพินัยกรรม 500,000 (เกิน 1/3) -> ระบบต้องจำกัดเพดานเหลือ 1/3 พอดี คือ 300,000 บาท
        res = calculate_mirath(
            estate=1000000, debts=50000, funeral=50000, wills=500000,
            heirs={"sons": 1}
        )
        self.assertEqual(res["wills_allowed"], 300000.0)
        self.assertEqual(res["distributable_estate"], 600000.0)
        self.assertEqual(res["breakdown"][0]["amount"], 600000.0)

    def test_boundary_16_mirath_single_daughter(self):
        """จุดตัดบุตรสาวคนเดียว: ได้รับฟัรฎ์ 1/2 และรับส่วนเหลือคืนผ่านอัร-ร็อดด์ (Al-Radd) รวมเป็น 100%"""
        res = calculate_mirath(
            estate=1000000, debts=0, funeral=0, wills=0,
            heirs={"daughters": 1}
        )
        self.assertIn("Al-Radd", res["adjustment_type"])
        self.assertEqual(len(res["breakdown"]), 1)
        self.assertEqual(res["breakdown"][0]["percentage"], 100.0)
        self.assertEqual(res["breakdown"][0]["amount"], 1000000.0)

    def test_boundary_17_mirath_multiple_daughters(self):
        """จุดตัดบุตรสาวหลายคน (ไม่มีบุตรชาย): ได้รับฟัรฎ์ 2/3 และรับส่วนเหลือคืนผ่านอัร-ร็อดด์ (Al-Radd) รวมเป็น 100% (แบ่งคนละครึ่ง)"""
        res = calculate_mirath(
            estate=1200000, debts=0, funeral=0, wills=0,
            heirs={"daughters": 2}
        )
        self.assertIn("Al-Radd", res["adjustment_type"])
        self.assertEqual(res["breakdown"][0]["percentage"], 100.0)
        self.assertEqual(res["breakdown"][0]["amount"], 1200000.0)

    def test_boundary_18_mirath_awl_exact(self):
        """จุดตัดการทอนสัดส่วนอัล-เอาล์ (Al-Awl): สามี (1/2) + พี่สาว 2 คน (2/3) -> เศษส่วนรวม 7/6 ทอนเหลือ 3/7 และ 4/7"""
        res = calculate_mirath(
            estate=700000, debts=0, funeral=0, wills=0,
            heirs={"husband": True, "sisters": 2}
        )
        self.assertIn("Al-Awl", res["adjustment_type"])
        husband_item = next(b for b in res["breakdown"] if "สามี" in b["heir"])
        sisters_item = next(b for b in res["breakdown"] if "พี่สาว" in b["heir"])
        self.assertEqual(husband_item["fraction_str"], "3/7")
        self.assertEqual(husband_item["amount"], 300000.0)
        self.assertEqual(sisters_item["fraction_str"], "4/7")
        self.assertEqual(sisters_item["amount"], 400000.0)

    def test_boundary_19_prayer_times_equator_and_solstices(self):
        """ขอบเขตการคำนวณเวลาละหมาด: เส้นศูนย์สูตร (Equator) และวันวิษุวัต / ครีษมายัน"""
        # เส้นศูนย์สูตร (Lat 0°, Lon 0°, UTC+0) วันวิษุวัต (Equinox 21 มี.ค.)
        eq_times = calculate_prayer_times(lat=0.0, lon=0.0, date_str="2026-03-21", tz_offset=0)
        self.assertIsNotNone(eq_times)
        p = eq_times["times"]
        self.assertIn("12:", p["dhuhr"])
        self.assertIn("06:", p["sunrise"])
        self.assertIn("18:", p["maghrib"])

        # ละติจูดสูง (ลอนดอน 51.5074°N) ในวันครีษมายัน (Summer Solstice 21 มิ.ย.)
        london_solstice = calculate_prayer_times(lat=51.5074, lon=-0.1278, date_str="2026-06-21", tz_offset=1)
        self.assertIsNotNone(london_solstice)
        self.assertTrue(london_solstice["times"]["fajr"] < london_solstice["times"]["sunrise"])

    def test_boundary_20_qibla_bearing_kaaba_singularity(self):
        """จุดตัดทิศกิบลัต ณ พิกัดมหาอัลกะอ์บะฮ์ (Kaaba Singularity Distance ~0 km)"""
        kaaba = calculate_qibla_bearing(lat=21.422487, lon=39.826206)
        self.assertIsNotNone(kaaba)
        self.assertEqual(kaaba["distance_km"], 0.0)

        near_kaaba = calculate_qibla_bearing(lat=21.4225, lon=39.8262)
        self.assertLess(near_kaaba["distance_km"], 0.1)

    def test_boundary_21_enumber_boundaries(self):
        """ขอบเขตดัชนี E-Number: รหัสต่ำสุด E100, สูงสุด E920 และความยืดหยุ่นของ Input"""
        e_min = get_enumber("E100")
        self.assertIsNotNone(e_min)
        self.assertEqual(e_min["code"], "E100")

        e_max = get_enumber("E920")
        self.assertIsNotNone(e_max)
        self.assertEqual(e_max["code"], "E920")
        self.assertIn("เส้นผมมนุษย์", e_max["origin"])

        # ยืดหยุ่นพิมพ์ตัวเล็ก e120 หรือเลขเดี่ยว 120
        e_lower = get_enumber("e120")
        self.assertIsNotNone(e_lower)
        self.assertEqual(e_lower["code"], "E120")

        e_num_only = get_enumber("120")
        self.assertIsNotNone(e_num_only)
        self.assertEqual(e_num_only["code"], "E120")

    def test_boundary_22_asr_hanafi_vs_standard(self):
        """จุดตัดเปรียบเทียบเวลาอัศรี: มัซฮับฮะนะฟี (เงา 2 เท่า) ต้องมาทีหลังมาตรฐาน (เงา 1 เท่า) เสมอ"""
        times_standard = calculate_prayer_times(lat=13.7563, lon=100.5018, date_str="2026-03-21", tz_offset=7, asr_hanafi=False)
        times_hanafi = calculate_prayer_times(lat=13.7563, lon=100.5018, date_str="2026-03-21", tz_offset=7, asr_hanafi=True)

        std_asr = times_standard["times"]["asr"]
        hanafi_asr = times_hanafi["times"]["asr"]
        self.assertGreater(hanafi_asr, std_asr, "เวลาอัศรีฮะนะฟีต้องช้ากว่าเวลามาตรฐานเพราะรอให้เงายาวเป็น 2 เท่า")

    def test_boundary_23_murabahah_zero_profit_rate(self):
        """จุดตัด Murabahah อัตรากำไร 0%: ราคารวมต้องเท่ากับเงินต้นพอดี"""
        calc = calculate_murabahah(principal=50000.0, profit_rate=0.0, tenure_months=10)
        self.assertEqual(calc["total_profit"], 0.0)
        self.assertEqual(calc["total_price"], 50000.0)
        self.assertEqual(calc["monthly_payment"], 5000.0)

    def test_boundary_24_chronology_first_and_last_bounds(self):
        """ขอบเขตการประทาน: ซูเราะฮ์แรก 96 (Al-Alaq) และซูเราะฮ์สุดท้าย 110 (An-Nasr)"""
        s_first = get_surah_chronology(96)
        s_last = get_surah_chronology(110)
        self.assertEqual(s_first["revelation_order"], 1)
        self.assertEqual(s_last["revelation_order"], 114)

    def test_boundary_25_timeline_earliest_latest_bounds(self):
        """ขอบเขตไทม์ไลน์: ยุคแรกสุด 610 CE ถึงยุคปัจจุบัน (>= 2024 CE)"""
        timeline = get_history_timeline()
        self.assertEqual(timeline[0]["start_year_ce"], 610)
        self.assertGreaterEqual(timeline[-1]["end_year_ce"], 2024)




# =====================================================================
# DIMENSION 3: EDGE CASES (กรณีปลายขอบ/ข้อมูลผิดปกติ/ความปลอดภัย - 17 เคส)
# =====================================================================

class TestEdgeCases(unittest.TestCase):
    """ทดสอบกรณีข้อมูลผิดปกติ ค่าว่าง อักขระพิเศษ และการป้องกันการโจมตี (SQL Injection)"""


    def test_edge_01_empty_query(self):
        """ค้นหาด้วยข้อความว่างเปล่าต้องไม่เกิด Unhandled Exception"""
        q_res = search_quran("", limit=5)
        h_res = search_hadith("", limit=5)
        f_res = search_fatwas("", limit=5)
        self.assertIsInstance(q_res, list)
        self.assertIsInstance(h_res, list)
        self.assertIsInstance(f_res, list)

    def test_edge_02_whitespace_only_query(self):
        """ค้นหาด้วยช่องว่างและ tab ต้องคืนค่ารายการอย่างปลอดภัย"""
        res = search_hadith("   \t\n  ", limit=3)
        self.assertIsInstance(res, list)

    def test_edge_03_nonexistent_surah_zero(self):
        """เรียกซูเราะฮ์ที่ 0 ซึ่งไม่มีอยู่จริง -> ต้องคืนค่า None"""
        res = get_exact_ayah(0, 1)
        self.assertIsNone(res)

    def test_edge_04_nonexistent_surah_overflow(self):
        """เรียกซูเราะฮ์ที่ 115 (กุรอานมี 114 ซูเราะฮ์) -> ต้องคืนค่า None"""
        res = get_exact_ayah(115, 1)
        self.assertIsNone(res)

    def test_edge_05_nonexistent_ayah_in_surah_1(self):
        """เรียกซูเราะฮ์ 1 อายะฮ์ที่ 8 (อัล-ฟาติฮะฮ์มีเพียง 7 อายะฮ์) -> ต้องคืนค่า None"""
        res = get_exact_ayah(1, 8)
        self.assertIsNone(res)

    def test_edge_06_nonexistent_hadith_book(self):
        """เรียกคัมภีร์ฮะดีษที่ไม่มีอยู่จริง -> ต้องคืนค่า None"""
        res = get_exact_hadith("invalid_book_name", 1)
        self.assertIsNone(res)

    def test_edge_07_hadith_number_overflow(self):
        """เรียกฮะดีษบุคอรีบทที่ 999999 ซึ่งเกินจำนวนจริง -> ต้องคืนค่า None"""
        res = get_exact_hadith("bukhari", 999999)
        self.assertIsNone(res)

    def test_edge_08_nonexistent_fatwa_id(self):
        """เรียกฟัตวา Topic ID 999 ซึ่งไม่มีอยู่ -> ต้องคืนค่า None"""
        res = get_fatwa(999)
        self.assertIsNone(res)

    def test_edge_09_sql_injection_defense_union(self):
        """ทดสอบส่ง SQL Injection แบบ UNION SELECT ในฟังก์ชันค้นหา"""
        malicious_query = "' UNION SELECT 1,2,3,4,5,6,7,8 --"
        # ต้องไม่พังและไม่ทำให้ Schema รั่วไหล
        try:
            res = search_hadith(malicious_query, limit=3)
            self.assertIsInstance(res, list)
        except Exception as e:
            self.fail(f"SQL Injection broke the search: {e}")

    def test_edge_10_sql_injection_defense_drop(self):
        """ทดสอบส่ง SQL Injection คำสั่ง DROP TABLE"""
        malicious_drop = "'; DROP TABLE hadiths; --"
        search_hadith(malicious_drop, limit=2)
        
        # ตรวจสอบว่าตาราง hadiths ยังคงอยู่สมบูรณ์ ไม่ถูก Drop
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM hadiths")
            count = c.fetchone()[0]
            self.assertEqual(count, 34614, "Security breach: hadiths table corrupted or dropped!")
        finally:
            conn.close()

    def test_edge_11_special_characters_handling(self):
        """ทดสอบการค้นหาด้วยอักขระพิเศษ * ? [ ] ( ) \\ / $ ^ +"""
        specials = "* ? [ ] ( ) \\ / $ ^ +"
        res = search_quran(specials, limit=3)
        self.assertIsInstance(res, list)

    def test_edge_12_financial_zero_division_prevention(self):
        """ป้องกันข้อผิดพลาด ZeroDivisionError ในโปรแกรมคัดกรองหุ้นเมื่อ Market Cap = 0 หรือ Revenue = 0"""
        compliant, debt_r, non_h, violations, _ = evaluate_aaoifi_stock(True, market_cap=0, debt=1000, total_revenue=0, non_halal_income=50)
        self.assertFalse(compliant)
        self.assertEqual(debt_r, 0.0)
        self.assertEqual(non_h, 0.0)

    def test_edge_13_financial_negative_inputs(self):
        """ทดสอบค่าเงินติดลบในเครื่องมือคำนวณซะกาตและนาฟะเกาะฮ์"""
        qualifies, zakat_due, net = calculate_zakat(cash=-100000, gold=0, debt=50000, nisab_threshold=280000)
        self.assertFalse(qualifies)
        self.assertEqual(zakat_due, 0.0)

        # นาฟะเกาะฮ์รายได้ติดลบ
        res = allocate_nafaqah(income=-5000, wife_needed=10000, kids_needed=5000, parents_needed=3000)
        self.assertEqual(res["wife_paid"], 0.0)
        self.assertEqual(res["wife_shortfall"], 10000.0)

    def test_edge_14_mirath_zero_estate(self):
        """กรณีปลายขอบ: กองมรดกเป็น 0 บาท ไม่เกิด DivisionByZeroException และปันส่วนเป็น 0 บาท"""
        res = calculate_mirath(estate=0, debts=0, funeral=0, wills=0, heirs={"sons": 2, "daughters": 1})
        self.assertEqual(res["distributable_estate"], 0.0)
        for b in res["breakdown"]:
            self.assertEqual(b["amount"], 0.0)

    def test_edge_15_mirath_negative_estate(self):
        """กรณีปลายขอบ: ป้อนมูลค่ามรดกติดลบ ระบบต้องปรับเป็น 0.0 โดยไม่แครช"""
        res = calculate_mirath(estate=-500000, debts=0, funeral=0, wills=0, heirs={"wife": 1})
        self.assertEqual(res["distributable_estate"], 0.0)
        self.assertEqual(res["breakdown"][0]["amount"], 0.0)

    def test_edge_16_mirath_debts_exceed_estate(self):
        """กรณีปลายขอบ: หนี้สินและค่าทำศพท่วมกองมรดก (มรดก 100,000 หนี้ 300,000) -> มรดกสุทธิเหลือ 0 และทายาทไม่ได้มรดก"""
        res = calculate_mirath(estate=100000, debts=300000, funeral=50000, wills=50000, heirs={"sons": 1})
        self.assertEqual(res["wills_allowed"], 0.0)
        self.assertEqual(res["distributable_estate"], 0.0)
        self.assertEqual(res["breakdown"][0]["amount"], 0.0)

    def test_edge_17_qawaid_nonexistent_rule(self):
        """กรณีปลายขอบ: ค้นหากฎแม่บทที่ไม่มีอยู่ หรือเรียกดู ID นอกขอบเขต -> คืนค่าว่าง/None โดยปลอดภัย"""
        not_found = search_qawaid("ไม่มีกฎข้อนี้แน่นอนในสารบบ12345")
        self.assertEqual(len(not_found), 0)
        invalid_id = get_qawaid(rule_id=999)
        self.assertIsNone(invalid_id)

    def test_edge_18_enumber_invalid_and_sql_injection(self):
        """กรณีปลายขอบ: รหัส E-Number ที่ไม่มีอยู่ และการทดสอบ Injection Strings"""
        e_invalid = get_enumber("E9999")
        self.assertIsNone(e_invalid)

        # SQL Injection attempt
        sqli_res = search_enumbers("'; DROP TABLE halal_enumbers; --")
        self.assertEqual(len(sqli_res), 0)

        # ตรวจสอบว่าตารางยังคงอยู่และทำงานได้ปกติหลัง Injection
        e_valid = get_enumber("E100")
        self.assertIsNotNone(e_valid)

    def test_edge_19_quran_roots_spacing_variants(self):
        """กรณีปลายขอบ: รากศัพท์ที่มีช่องว่าง (س ل م) หรือเขียนติดกัน (سلم) หรือตัวพิมพ์เล็ก-ใหญ่"""
        root_spaced = get_quran_root("س ل م")
        root_joined = get_quran_root("سلم")
        self.assertIsNotNone(root_spaced)
        self.assertIsNotNone(root_joined)
        self.assertEqual(root_spaced["id"], root_joined["id"])

        root_lower = get_quran_root("s-l-m")
        self.assertIsNotNone(root_lower)
        self.assertEqual(root_lower["transliteration"], "S-L-M")

        not_found = get_quran_root("nonexistent_root_999")
        self.assertIsNone(not_found)

    def test_edge_20_sect_texts_empty_and_special_chars(self):
        """กรณีปลายขอบ: การค้นหาตัวบทนิกายด้วยเครื่องหมายคำพูดเปิดทิ้งไว้ หรือตัวกรองนิกายที่ไม่รู้จัก"""
        res_quote = search_sect_texts('"unclosed quote', limit=5)
        self.assertIsInstance(res_quote, list)

        res_unknown_sect = search_sect_texts("ศรัทธา", sect_filter="non_existent_sect")
        self.assertEqual(len(res_unknown_sect), 0)

    def test_edge_21_negative_coordinates_prayer(self):
        """กรณีปลายขอบ: พิกัดซีกโลกใต้ (Southern Hemisphere) และลองจิจูดฝั่งตะวันตก (Western Longitude)"""
        # ซิดนีย์ ออสเตรเลีย (Lat -33.8688°S, Lon 151.2093°E, UTC+10)
        sydney = calculate_prayer_times(lat=-33.8688, lon=151.2093, date_str="2026-03-21", tz_offset=10)
        self.assertIsNotNone(sydney)
        for t in sydney["times"].values():
            self.assertRegex(t, r"^\d{2}:\d{2}$")

        # ริโอเดจาเนโร บราซิล (Lat -22.9068°S, Lon -43.1729°W, UTC-3)
        rio = calculate_prayer_times(lat=-22.9068, lon=-43.1729, date_str="2026-03-21", tz_offset=-3)
        self.assertIsNotNone(rio)
        for t in rio["times"].values():
            self.assertRegex(t, r"^\d{2}:\d{2}$")

    def test_edge_22_empty_omni_search_query(self):
        """กรณีปลายขอบ: ค้นหาคำว่างใน Omni-Search ต้องไม่ Crash และคืนค่าว่างอย่างปลอดภัย"""
        res = omni_search("")
        self.assertIsInstance(res, list)

    def test_edge_23_nonexistent_surah_chronology(self):
        """กรณีปลายขอบ: ซูเราะฮ์หมายเลข 0 หรือ 999 ในตารางลำดับการประทานต้องคืน None"""
        self.assertIsNone(get_surah_chronology(0))
        self.assertIsNone(get_surah_chronology(999))

    def test_edge_24_unknown_medicine_and_contract(self):
        """กรณีปลายขอบ: ค้นหายาสมุนไพรและสัญญาที่ไม่รู้จักต้องไม่ Crash"""
        med = search_prophetic_medicine("สมุนไพรที่ไม่เคยมีในโลกxyz")
        self.assertEqual(len(med), 0)
        contract = get_islamic_contracts("invalid_type_xyz")
        self.assertEqual(len(contract), 0)




# =====================================================================
# DIMENSION 4: CORNER CASES (กรณีซ้อนเงื่อนไขหลายมิติ - 15 เคส)
# =====================================================================

class TestCornerCases(unittest.TestCase):
    """ทดสอบสภาวะทับซ้อนหลายมิติ ความสัมพันธ์ระหว่างเงื่อนไข และความสมบูรณ์ของความสัมพันธ์ข้ามตาราง"""

    def test_corner_01_stock_haram_core_zero_debt(self):
        """สภาวะมุม: ธุรกิจเป็นฮะรอม (เช่น คาสิโน/สุรา) แม้จะมีหนี้สิน 0% และไม่มีรายได้ไม่ฮาลาลอื่นเลย -> ต้องตกเกณฑ์ฮาลาล 100%"""
        compliant, _, _, violations, _ = evaluate_aaoifi_stock(
            core_business_is_halal=False, # ฮะรอม
            market_cap=10000000,
            debt=0,                       # หนี้ 0% (ผ่านเกณฑ์การเงิน)
            total_revenue=5000000,
            non_halal_income=0            # รายได้อื่น 0% (ผ่านเกณฑ์การเงิน)
        )
        self.assertFalse(compliant, "Haram business must never pass even with zero debt!")
        self.assertIn("Core business is haram", violations)

    def test_corner_02_stock_dual_violation(self):
        """สภาวะมุม: ธุรกิจฮาลาล แต่ทำผิดทั้งหนี้สินเกิน 33% และรายได้ไม่ฮาลาลเกิน 5% พร้อมกัน -> ต้องตรวจจับได้ครบทั้ง 2 ข้อ"""
        compliant, debt_r, non_h_r, violations, tathir = evaluate_aaoifi_stock(
            core_business_is_halal=True,
            market_cap=10000000,
            debt=5000000,       # 50% (> 33%)
            total_revenue=10000000,
            non_halal_income=1500000 # 15% (> 5%)
        )
        self.assertFalse(compliant)
        self.assertEqual(len(violations), 2)
        self.assertTrue(any("Debt ratio" in v for v in violations))
        self.assertTrue(any("Non-halal revenue" in v for v in violations))
        self.assertEqual(tathir, 1500000)

    def test_corner_03_nafaqah_zero_income_with_dependents(self):
        """สภาวะมุม: สามีรายได้ 0 บาท แต่มีภรรยา บุตร และบิดามารดา -> ค่าใช้จ่ายภรรยาต้องบันทึกเป็นหนี้ค้างสะสม"""
        res = allocate_nafaqah(income=0, wife_needed=12000, kids_needed=8000, parents_needed=4000)
        self.assertEqual(res["wife_paid"], 0.0)
        self.assertEqual(res["wife_shortfall"], 12000.0, "Wife entitlement must be recorded as an established debt!")
        self.assertEqual(res["kids_paid"], 0.0)
        self.assertEqual(res["parents_paid"], 0.0)
        self.assertEqual(res["remaining_savings"], 0.0)

    def test_corner_04_nafaqah_partial_waterfall(self):
        """สภาวะมุม: รายได้ไม่พอจ่ายครบ จ่ายภรรยาครบ 100% บุตรได้บางส่วน และบิดามารดาไม่ได้เลย"""
        res = allocate_nafaqah(income=15000, wife_needed=10000, kids_needed=10000, parents_needed=5000)
        self.assertEqual(res["wife_paid"], 10000.0)
        self.assertEqual(res["wife_shortfall"], 0.0)
        self.assertEqual(res["kids_paid"], 5000.0)
        self.assertEqual(res["kids_shortfall"], 5000.0)
        self.assertEqual(res["parents_paid"], 0.0)
        self.assertEqual(res["parents_shortfall"], 5000.0)

    def test_corner_05_fts_multi_concept_thai(self):
        """สภาวะมุม: ค้นหาด้วยคำผสมภาษาไทยหลายแนวคิดที่ไม่เกี่ยวข้องกัน 'ละหมาด ดอกเบี้ย'"""
        res = search_hadith("ละหมาด ดอกเบี้ย", limit=5)
        self.assertIsInstance(res, list)
        self.assertTrue(len(res) > 0, "Multi-concept Thai search should yield ranked results")

    def test_corner_06_fts_thai_english_mixed(self):
        """สภาวะมุม: ค้นหาคำผสมสองภาษา 'ซะกาต zakat gold'"""
        res = search_hadith("ซะกาต zakat gold", limit=5)
        self.assertIsInstance(res, list)
        self.assertTrue(len(res) > 0)

    def test_corner_07_hadith_grade_integrity_bukhari_muslim(self):
        """ตรวจสอบความถูกต้องของข้อมูล: ฮะดีษในบุคอรีและมุสลิมทุกบทต้องมีสถานะ Sahih 100%"""
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM hadiths WHERE collection IN ('bukhari', 'muslim') AND grade != 'Sahih'")
            invalid_count = c.fetchone()[0]
            self.assertEqual(invalid_count, 0, "All Bukhari and Muslim hadiths must have grade 'Sahih'!")
        finally:
            conn.close()

    def test_corner_08_quran_surah_name_integrity(self):
        """ตรวจสอบความถูกต้องของข้อมูล: ทั้ง 114 ซูเราะฮ์ต้องมีชื่ออาหรับ อังกฤษ และไทยครบถ้วน"""
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM surahs WHERE name_ar = '' OR name_en = '' OR name_th = ''")
            empty_names = c.fetchone()[0]
            self.assertEqual(empty_names, 0, "All 114 Surahs must have non-empty Arabic, English, and Thai names!")

            c.execute("SELECT COUNT(*) FROM surahs")
            total_surahs = c.fetchone()[0]
            self.assertEqual(total_surahs, 114)
        finally:
            conn.close()

    def test_corner_09_zakat_negative_net_wealth(self):
        """สภาวะมุม: ทรัพย์สินติดลบ (เงินสด 10,000 หนี้สิน 50,000) -> ซะกาตต้องเป็น 0 บาทเสมอ"""
        qualifies, zakat_due, net = calculate_zakat(10000, 0, 50000, 280000)
        self.assertFalse(qualifies)
        self.assertEqual(zakat_due, 0.0)
        self.assertEqual(net, -40000)

    def test_corner_10_fatwa_evidence_containment(self):
        """ตรวจสอบว่าคำวินิจฉัยฟัตวาทั้ง 9 ประเด็นมีตัวบทอ้างอิงและสภาชี้ขาดครบทุกแถว"""
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM contemporary_fatwas WHERE primary_evidences = '' OR authorities = ''")
            missing_evidences = c.fetchone()[0]
            self.assertEqual(missing_evidences, 0, "All fatwas must have primary evidences and authorities!")

            c.execute("SELECT COUNT(*) FROM contemporary_fatwas")
            total_fatwas = c.fetchone()[0]
            self.assertGreaterEqual(total_fatwas, 80)
        finally:
            conn.close()

    def test_corner_11_cross_table_integrity(self):
        """ตรวจสอบความสมบูรณ์เชิงสัมพันธ์: อายะฮ์ทั้ง 6,236 วรรคต้องผูกกับ Surah 1-114 อย่างถูกต้อง"""
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("""
            SELECT COUNT(*)
            FROM quran q
            LEFT JOIN surahs s ON q.surah_number = s.number
            WHERE s.number IS NULL
            """)
            orphan_verses = c.fetchone()[0]
            self.assertEqual(orphan_verses, 0, "Found orphan Quran verses not linked to a valid Surah!")
        finally:
            conn.close()

    def test_corner_12_mirath_hajb_sons_block_brothers(self):
        """สภาวะมุมการกีดกัน (Al-Hajb al-Hirman): บุตรชายตัดสิทธิพี่น้องทั้งหมดโดยสิ้นเชิง"""
        res = calculate_mirath(
            estate=1000000, debts=0, funeral=0, wills=0,
            heirs={"sons": 1, "brothers": 2, "sisters": 2}
        )
        self.assertTrue(any("บุตรชายกีดกันพี่น้องทั้งหมด" in note for note in res["hajb_notes"]))
        # ตรวจสอบว่าใน breakdown มีเฉพาะบุตรชายเท่านั้น
        self.assertEqual(len(res["breakdown"]), 1)
        self.assertIn("บุตรชาย", res["breakdown"][0]["heir"])
        self.assertEqual(res["breakdown"][0]["amount"], 1000000.0)

    def test_corner_13_mirath_hajb_father_blocks_brothers(self):
        """สภาวะมุมการกีดกัน (Al-Hajb al-Hirman): บิดาตัดสิทธิพี่น้องทั้งหมดโดยสิ้นเชิง"""
        res = calculate_mirath(
            estate=500000, debts=0, funeral=0, wills=0,
            heirs={"father": True, "brothers": 3, "sisters": 1}
        )
        self.assertTrue(any("บิดากีดกันพี่น้องทั้งหมด" in note for note in res["hajb_notes"]))
        self.assertEqual(len(res["breakdown"]), 1)
        self.assertIn("บิดา", res["breakdown"][0]["heir"])
        self.assertEqual(res["breakdown"][0]["amount"], 500000.0)

    def test_corner_14_mirath_complex_awl_27(self):
        """สภาวะมุมกรณีประวัติศาสตร์อัล-มิมบะรียะฮ์ (Al-Minbariyyah): ภรรยา + บุตรสาว 2 + บิดา + มารดา ฐานเศษส่วนขยายเป็น 27"""
        # ภรรยา (1/8=3/24), บุตรสาว 2 (2/3=16/24), บิดา (1/6=4/24), มารดา (1/6=4/24) -> รวม 27/24
        # ปรับทอนสัดส่วนอัล-เอาล์เป็นส่วน 27: ภรรยาเหลือ 3/27 (1/9), บุตรสาว 16/27, บิดา 4/27, มารดา 4/27
        estate_amt = 2700000.0
        res = calculate_mirath(
            estate=estate_amt, debts=0, funeral=0, wills=0,
            heirs={"wives": 1, "daughters": 2, "father": True, "mother": True}
        )
        self.assertIn("Al-Awl", res["adjustment_type"])
        wife_share = next(b for b in res["breakdown"] if "ภรรยา" in b["heir"])
        daughters_share = next(b for b in res["breakdown"] if "บุตรสาว" in b["heir"])
        father_share = next(b for b in res["breakdown"] if "บิดา" in b["heir"])
        mother_share = next(b for b in res["breakdown"] if "มารดา" in b["heir"])

        self.assertEqual(wife_share["fraction_str"], "1/9") # 3/27 ลดรูปเป็น 1/9
        self.assertEqual(wife_share["amount"], 300000.0)

        self.assertEqual(daughters_share["fraction_str"], "16/27")
        self.assertEqual(daughters_share["amount"], 1600000.0)

        self.assertEqual(father_share["fraction_str"], "4/27")
        self.assertEqual(father_share["amount"], 400000.0)

        self.assertEqual(mother_share["fraction_str"], "4/27")
        self.assertEqual(mother_share["amount"], 400000.0)

        total_distributed = sum(b["amount"] for b in res["breakdown"])
        self.assertEqual(total_distributed, estate_amt)

    def test_corner_15_qawaid_search_bilingual(self):
        """สภาวะมุมการสืบค้นสองภาษาและแอปพลิเคชันร่วมสมัย: ค้นหาคำไทย อาหรับ ทับศัพท์ และคีย์เวิร์ดร่วมสมัย"""
        res_th = search_qawaid("เจตนา")
        self.assertTrue(any(r["id"] == 1 for r in res_th))

        res_ar = search_qawaid("Al-Yaqin")
        self.assertTrue(any(r["id"] == 2 for r in res_ar))

        res_modern = search_qawaid("มลพิษ")
        self.assertTrue(any(r["id"] == 4 for r in res_modern))

    def test_corner_16_cross_sect_matrix_completeness(self):
        """สภาวะมุม: ความสมบูรณ์ของเมทริกซ์ข้าม 4 สำนักคิด ทุกหัวข้อต้องมีข้อมูลครบทั้ง ซุนนี, สะลัฟ, ชีอะฮ์, อิบาดี"""
        matrix = get_cross_sect_matrix()
        self.assertEqual(len(matrix), 6)
        for topic in matrix:
            self.assertIn("topic_key", topic)
            self.assertIn("topic_th", topic)
            self.assertIn("key_difference", topic)
            self.assertIn("primary_sources", topic)
            self.assertTrue(len(topic["key_difference"]) > 10)
            self.assertTrue(len(topic["primary_sources"]) > 5)

            for sect in ["sunni", "salafi", "shia", "ibadi"]:
                self.assertIn(sect, topic)
                sect_info = topic[sect]
                self.assertTrue(len(sect_info["position"]) > 0)
                self.assertTrue(len(sect_info["detail"]) > 10)
                self.assertTrue(len(sect_info["evidences"]) > 0)

    def test_corner_17_enumbers_shubhah_fatwa_presence(self):
        """สภาวะมุม: สารเจือปนสถานะชุบฮาต (Shubhah) ทุกตัวต้องมีคำชี้แจงและแหล่งอ้างอิงฟัตวาที่ระบุเงื่อนไขชัดเจน"""
        shubhah_list = search_enumbers("", limit=50, status_filter="shubhah")
        self.assertTrue(len(shubhah_list) >= 5)
        for item in shubhah_list:
            self.assertEqual(item["status"], "Shubhah")
            self.assertTrue(len(item["fatwa_sources"]) > 15, f"{item['code']} must cite clear fatwa authority!")
            self.assertTrue(len(item["description_th"]) > 20)

    def test_corner_18_quran_roots_all_contain_theology_and_ayah(self):
        """สภาวะมุม: รากศัพท์กุรอานทั้งหมดในระบบต้องมีข้อมูลเชิงศาสนศาสตร์ ความถี่ และตัวอย่างอายะฮ์ครบถ้วน"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT root_ar, root_lat, frequency_in_quran, derived_words, sample_ayah, theological_significance FROM quran_roots")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 8)
            for r in rows:
                root_ar, root_lat, freq, derivs, ayah, theology = r
                self.assertGreater(freq, 50, f"Root {root_lat} frequency should be verified high-occurrence")
                self.assertTrue(len(ayah) > 10)
                self.assertTrue(len(theology) > 20)
                import json
                d_list = json.loads(derivs)
                self.assertGreaterEqual(len(d_list), 4, f"Root {root_lat} should have morphology derivatives")
        finally:
            conn.close()

    def test_corner_19_qibla_compass_360_wrapping(self):
        """สภาวะมุม: การคำนวณมุมเล็งกิบลัตทั่วโลกต้องอยู่ในช่วง [0.0, 360.0) และมีทิศ 16 จุดที่สมเหตุสมผล"""
        global_cities = [
            ("Tokyo", 35.6762, 139.6503, "WNW"),
            ("London", 51.5074, -0.1278, "ESE"),
            ("Honolulu", 21.3069, -157.8583, "NNW"),
            ("Cape Town", -33.9249, 18.4241, "NNE"),
            ("Buenos Aires", -34.6037, -58.3816, "ENE"),
        ]
        for name, lat, lon, expected_dir in global_cities:
            q = calculate_qibla_bearing(lat, lon)
            self.assertGreaterEqual(q["bearing_degrees"], 0.0, f"{name} bearing must be >= 0")
            self.assertLess(q["bearing_degrees"], 360.0, f"{name} bearing must be < 360")
            self.assertEqual(q["compass_direction"], expected_dir, f"{name} expected compass point {expected_dir} but got {q['compass_direction']}")
            self.assertGreater(q["distance_km"], 1000.0)

    def test_corner_20_omni_multi_module_cross_resonance(self):
        """สภาวะมุม: คำค้น 'อัลลอฮ์' ต้องให้ผลลัพธ์ปรากฏในหลายโมดูลพร้อมกัน (Adhkar, Chronology, Contracts)"""
        res = omni_search("อัลลอฮ์", limit=10)
        self.assertGreater(len(res), 1)
        modules = {r["module"] for r in res}
        self.assertGreaterEqual(len(modules), 2, "Common theological terms should resonate across multiple knowledge modules")

    def test_corner_21_murabahah_mathematical_parity(self):
        """สภาวะมุม: การคำนวณ Murabahah ยอดผ่อนชำระต่อเดือน * จำนวนเดือน ต้องเท่ากับ ราคารวม"""
        test_cases = [
            (120000.0, 0.06, 12),
            (500000.0, 0.08, 60),
            (1000000.0, 0.045, 120),
        ]
        for principal, rate, tenure in test_cases:
            calc = calculate_murabahah(principal, rate, tenure)
            expected_total = principal + (principal * rate)
            self.assertAlmostEqual(calc["total_price"], expected_total, delta=0.01)
            self.assertAlmostEqual(calc["monthly_payment"] * tenure, calc["total_price"], delta=0.01)

    def test_corner_22_contemporary_fatwas_expansion(self):
        """สภาวะมุม: ตรวจสอบความแม่นยำของการค้นหาฟัตวาร่วมสมัย 8 หัวข้อใหม่ (Crypto, BNPL, Aesthetics, IVF, Euthanasia)"""
        # 1. Crypto / Bitcoin
        crypto_res = search_fatwas("บิตคอยน์")
        self.assertGreaterEqual(len(crypto_res), 1)
        self.assertIn("บิตคอยน์", crypto_res[0]["title_th"])
        self.assertIn("SAC", crypto_res[0]["authorities"])

        # 2. BNPL / SPayLater
        bnpl_res = search_fatwas("SPayLater")
        self.assertGreaterEqual(len(bnpl_res), 1)
        self.assertIn("SPayLater", bnpl_res[0]["title_th"])
        self.assertIn("ผ่อนสินค้า", bnpl_res[0]["title_th"])

        # 3. Cosmetic Surgery
        cosmetic_res = search_fatwas("ศัลยกรรม")
        self.assertGreaterEqual(len(cosmetic_res), 1)
        self.assertIn("ศัลยกรรม", cosmetic_res[0]["title_th"])
        self.assertIn("อิซาละตุล อัยบ์", cosmetic_res[0]["ruling_summary"])

        # 4. IVF & Surrogacy
        ivf_res = search_fatwas("อุ้มบุญ")
        self.assertGreaterEqual(len(ivf_res), 1)
        self.assertIn("อุ้มบุญ", ivf_res[0]["title_th"])
        self.assertIn("100%", ivf_res[0]["ruling_summary"])

        # 5. Euthanasia & DNR
        euthanasia_res = search_fatwas("การุณยฆาต")
        self.assertGreaterEqual(len(euthanasia_res), 1)
        self.assertIn("การุณยฆาต", euthanasia_res[0]["title_th"])
        self.assertIn("สมองตาย", euthanasia_res[0]["ruling_summary"])

        # 6. Gacha & Loot Boxes
        gacha_res = search_fatwas("กาชา")
        self.assertGreaterEqual(len(gacha_res), 1)
        self.assertTrue(any("กาชา" in r["title_th"] for r in gacha_res))
        self.assertTrue(any("ฮะรอม" in r["ruling_summary"] for r in gacha_res))

        # 7. Pet Neutering
        neutering_res = search_fatwas("ทำหมัน")
        self.assertGreaterEqual(len(neutering_res), 1)
        self.assertIn("ทำหมัน", neutering_res[0]["title_th"])

        # 8. Buffet Dining
        buffet_res = search_fatwas("บุฟเฟต์")
        self.assertGreaterEqual(len(buffet_res), 1)
        self.assertIn("บุฟเฟต์", buffet_res[0]["title_th"])
        self.assertIn("อนุมัติ", buffet_res[0]["ruling_summary"])

        # 9. DNA Testing
        dna_res = search_fatwas("DNA")
        self.assertGreaterEqual(len(dna_res), 1)
        self.assertIn("DNA", dna_res[0]["title_th"])

        # 10. Carbon Credits
        carbon_res = search_fatwas("คาร์บอนเครดิต")
        self.assertGreaterEqual(len(carbon_res), 1)
        self.assertIn("คาร์บอนเครดิต", carbon_res[0]["title_th"])

        # 11. Space Worship
        space_res = search_fatwas("อวกาศ")
        self.assertGreaterEqual(len(space_res), 1)
        self.assertTrue(any("อวกาศ" in r["title_th"] for r in space_res))

        # 12. Gene Editing / CRISPR
        crispr_res = search_fatwas("ตัดต่อยีน")
        self.assertGreaterEqual(len(crispr_res), 1)
        self.assertTrue(any("ตัดต่อยีน" in r["title_th"] for r in crispr_res))

        # 13. Sex Selection (PGD)
        pgd_res = search_fatwas("เลือกเพศ")
        self.assertGreaterEqual(len(pgd_res), 1)
        self.assertTrue(any("เลือกเพศ" in r["title_th"] for r in pgd_res))

        # 14. DeFi Staking
        staking_res = search_fatwas("Staking")
        self.assertGreaterEqual(len(staking_res), 1)
        self.assertTrue(any("Staking" in r["title_th"] for r in staking_res))

        # 15. Microblading
        microblading_res = search_fatwas("สักคิ้ว")
        self.assertGreaterEqual(len(microblading_res), 1)
        self.assertTrue(any("สักคิ้ว" in r["title_th"] for r in microblading_res))

        # 16. Adoption & Kafalah
        adoption_res = search_fatwas("บุตรบุญธรรม")
        self.assertGreaterEqual(len(adoption_res), 1)
        self.assertTrue(any("บุตรบุญธรรม" in r["title_th"] for r in adoption_res))

        # 17. Forensic Autopsy
        autopsy_res = search_fatwas("ผ่าชันสูตร")
        self.assertGreaterEqual(len(autopsy_res), 1)
        self.assertTrue(any("ชันสูตร" in r["title_th"] for r in autopsy_res))

        # 18. Short Selling
        short_res = search_fatwas("ขายชอร์ต")
        self.assertGreaterEqual(len(short_res), 1)
        self.assertTrue(any("ขายชอร์ต" in r["title_th"] for r in short_res))

        # 19. Credit Card Cashback
        cashback_res = search_fatwas("Cashback")
        self.assertGreaterEqual(len(cashback_res), 1)
        self.assertTrue(any("Cashback" in r["title_th"] for r in cashback_res))

        # 20. Interfaith Greetings
        interfaith_res = search_fatwas("ต่างศาสนา")
        self.assertGreaterEqual(len(interfaith_res), 1)
        self.assertTrue(any("ต่างศาสนา" in r["title_th"] for r in interfaith_res))

        # 21. Digital Estate & Inheritance
        digital_res = search_fatwas("มรดกบัญชีดิจิทัล")
        self.assertGreaterEqual(len(digital_res), 1)
        self.assertTrue(any("มรดกบัญชีดิจิทัล" in r["title_th"] for r in digital_res))

        # 22. Fetal Anomalies & Abortion
        abortion_res = search_fatwas("ทารกในครรภ์")
        self.assertGreaterEqual(len(abortion_res), 1)
        self.assertTrue(any("ทารกในครรภ์" in r["title_th"] for r in abortion_res))

        # 23. Xenotransplantation
        xeno_res = search_fatwas("ปลูกถ่ายอวัยวะ")
        self.assertGreaterEqual(len(xeno_res), 1)
        self.assertTrue(any("ปลูกถ่ายอวัยวะ" in r["title_th"] for r in xeno_res))

        # 24. Cultured Meat
        cultured_res = search_fatwas("เนื้อเพาะเลี้ยง")
        self.assertGreaterEqual(len(cultured_res), 1)
        self.assertTrue(any("เนื้อเพาะเลี้ยง" in r["title_th"] for r in cultured_res))

        # 25. Permanent Sterilization (Vasectomy)
        steril_res = search_fatwas("ทำหมันถาวร")
        self.assertGreaterEqual(len(steril_res), 1)
        self.assertTrue(any("ทำหมันถาวร" in r["title_th"] for r in steril_res))

        # 26. Porcine Gelatin
        gelatin_res = search_fatwas("เจลาติน")
        self.assertGreaterEqual(len(gelatin_res), 1)
        self.assertTrue(any("เจลาติน" in r["title_th"] for r in gelatin_res))

        # 27. Lawyering in Civil Courts
        law_res = search_fatwas("ทนายความ")
        self.assertGreaterEqual(len(law_res), 1)
        self.assertTrue(any("ทนายความ" in r["title_th"] for r in law_res))

        # 28. Insurance & Takaful
        ins_res = search_fatwas("ประกันภัย")
        self.assertGreaterEqual(len(ins_res), 1)
        self.assertTrue(any("ประกันภัย" in r["title_th"] for r in ins_res))

        # 29. Bariatric Surgery
        baria_res = search_fatwas("ผ่าตัดกระเพาะ")
        self.assertGreaterEqual(len(baria_res), 1)
        self.assertTrue(any("ผ่าตัดกระเพาะ" in r["title_th"] for r in baria_res))

        # 30. Gold Installment
        gold_res = search_fatwas("ซื้อทองคำ")
        self.assertGreaterEqual(len(gold_res), 1)
        self.assertTrue(any("ซื้อทองคำ" in r["title_th"] for r in gold_res))

        # 31. Astrology & Horoscopes
        astro_res = search_fatwas("ดูดวง")
        self.assertGreaterEqual(len(astro_res), 1)
        self.assertTrue(any("ดูดวง" in r["title_th"] for r in astro_res))

        # 32. Software Piracy
        piracy_res = search_fatwas("ละเมิดลิขสิทธิ์")
        self.assertGreaterEqual(len(piracy_res), 1)
        self.assertTrue(any("ละเมิดลิขสิทธิ์" in r["title_th"] for r in piracy_res))

        # 33. Social Egg Freezing
        egg_res = search_fatwas("แช่แข็งไข่")
        self.assertGreaterEqual(len(egg_res), 1)
        self.assertTrue(any("แช่แข็งไข่" in r["title_th"] for r in egg_res))

        # 34. Thread Lift & Fillers
        thread_res = search_fatwas("ร้อยไหม")
        self.assertGreaterEqual(len(thread_res), 1)
        self.assertTrue(any("ร้อยไหม" in r["title_th"] for r in thread_res))

        # 35. Pure CBD from Hemp
        cbd_res = search_fatwas("CBD")
        self.assertGreaterEqual(len(cbd_res), 1)
        self.assertTrue(any("CBD" in r["title_th"] for r in cbd_res))

        # 36. Live-Commerce & Online Auctions
        live_res = search_fatwas("ไลฟ์สด")
        self.assertGreaterEqual(len(live_res), 1)
        self.assertTrue(any("ไลฟ์สด" in r["title_th"] for r in live_res))

        # 37. Game & Animation Mythology
        myth_res = search_fatwas("เทพปกรณัม")
        self.assertGreaterEqual(len(myth_res), 1)
        self.assertTrue(any("เทพปกรณัม" in r["title_th"] for r in myth_res))

        # 38. Stablecoins & Zakat
        stable_res = search_fatwas("USDT")
        self.assertGreaterEqual(len(stable_res), 1)
        self.assertTrue(any("สเตเบิลคอยน์" in r["title_th"] for r in stable_res))

        # 39. HPV Vaccination
        hpv_res = search_fatwas("HPV")
        self.assertGreaterEqual(len(hpv_res), 1)
        self.assertTrue(any("HPV" in r["title_th"] for r in hpv_res))

        # 40. CCTV & Privacy
        cctv_res = search_fatwas("CCTV")
        self.assertGreaterEqual(len(cctv_res), 1)
        self.assertTrue(any("CCTV" in r["title_th"] for r in cctv_res))

        # 41. Dental Veneers
        veneer_res = search_fatwas("วีเนียร์")
        self.assertGreaterEqual(len(veneer_res), 1)
        self.assertTrue(any("วีเนียร์" in r["title_th"] for r in veneer_res))

        # 42. Food Delivery Riders
        rider_res = search_fatwas("ไรเดอร์")
        self.assertGreaterEqual(len(rider_res), 1)
        self.assertTrue(any("ไรเดอร์" in r["title_th"] for r in rider_res))

        # 43. Influencer & Sponsorships
        infl_res = search_fatwas("อินฟลูเอนเซอร์")
        self.assertGreaterEqual(len(infl_res), 1)
        self.assertTrue(any("อินฟลูเอนเซอร์" in r["title_th"] for r in infl_res))

        # 44. Student Loans (กยศ.)
        loan_res = search_fatwas("กยศ")
        self.assertGreaterEqual(len(loan_res), 1)
        self.assertTrue(any("กยศ" in r["title_th"] for r in loan_res))

        # 45. Futures & Leverage Trading
        fut_res = search_fatwas("ฟิวเจอร์ส")
        self.assertGreaterEqual(len(fut_res), 1)
        self.assertTrue(any("ฟิวเจอร์ส" in r["title_th"] for r in fut_res))

        # 46. AI Griefbots & Voice Cloning
        grief_res = search_fatwas("แชตบอต")
        self.assertGreaterEqual(len(grief_res), 1)
        self.assertTrue(any("แชตบอต" in r["title_th"] for r in grief_res))

        # 47. Boycott & BDS Movement
        bds_res = search_fatwas("คว่ำบาตร")
        self.assertGreaterEqual(len(bds_res), 1)
        self.assertTrue(any("คว่ำบาตร" in r["title_th"] for r in bds_res))

        # 48. Insect Protein & Cricket Flour
        insect_res = search_fatwas("จิ้งหรีด")
        self.assertGreaterEqual(len(insect_res), 1)
        self.assertTrue(any("จิ้งหรีด" in r["title_th"] for r in insect_res))

        # 49. Muslim Dating Apps
        dating_res = search_fatwas("หาคู่")
        self.assertGreaterEqual(len(dating_res), 1)
        self.assertTrue(any("หาคู่" in r["title_th"] for r in dating_res))

        # 50. Ketamine & Psychedelic Therapy
        keta_res = search_fatwas("เคตามีน")
        self.assertGreaterEqual(len(keta_res), 1)
        self.assertTrue(any("เคตามีน" in r["title_th"] for r in keta_res))

        # 51. Prayer & Charity for Non-Muslim Deceased
        inter_res = search_fatwas("อุทิศส่วนกุศล")
        self.assertGreaterEqual(len(inter_res), 1)
        self.assertTrue(any("อุทิศส่วนกุศล" in r["title_th"] for r in inter_res))

        # 52. Extended Warranty & Protection Plans
        warr_res = search_fatwas("AppleCare")
        self.assertGreaterEqual(len(warr_res), 1)
        self.assertTrue(any("AppleCare" in r["title_th"] for r in warr_res))





# =====================================================================
# TEST RUNNER & AUDIT SUMMARY GENERATOR
# =====================================================================

def run_audit_suite():
    print("=" * 75)
    print("  ISLAMIC SCHOLAR AGENT & RAG SYSTEM: COMPREHENSIVE AUDIT SUITE")
    print("  4 Dimensions: Base Cases | Boundary Cases | Edge Cases | Corner Cases")
    print(f"  Database Target: {DB_PATH}")
    print("=" * 75)

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestBaseCases))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaryCases))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCornerCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total_tests = result.testsRun
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    passed_tests = total_tests - (failed_tests + error_tests)
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print("\n" + "=" * 75)
    print("  AUDIT SUMMARY RESULTS")
    print(f"  Total Test Cases Evaluated: {total_tests}")
    print(f"  Passed: {passed_tests} | Failed: {failed_tests} | Errors: {error_tests}")
    print(f"  Pass Rate: {pass_rate:.2f}%")
    print("=" * 75)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_audit_suite()
    sys.exit(0 if success else 1)
