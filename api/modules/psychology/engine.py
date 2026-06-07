# api/modules/psychology/engine.py
from typing import List, Dict, Any

# رجیستری ۲۵+ آزمون تخصصی
TEST_REGISTRY = {
    # --- بالینی ---
    "NEO_FFI": {"title": "پنج عاملی شخصیت نئو (NEO-FFI)", "category": "CLINICAL", "scoring": "T_SCORE", "subscales": ["N", "E", "O", "A", "C"]},
    "MMPI_SHORT": {"title": "فرم کوتاه MMPI-2-RF", "category": "CLINICAL", "scoring": "T_SCORE", "subscales": ["RCd", "BXD", "SFD"]},
    "MBTI_SHORT": {"title": "تیپ شخصیتی مایرز-بریگز", "category": "CLINICAL", "scoring": "CATEGORICAL", "subscales": ["EI", "SN", "TF", "JP"]},
    "GAD7": {"title": "اختلال اضطراب فراگیر (GAD-7)", "category": "CLINICAL", "scoring": "SUM"},
    "PHQ9": {"title": "غربالگری افسردگی (PHQ-9)", "category": "CLINICAL", "scoring": "SUM"},
    "CDRISC10": {"title": "تاب‌آوری کانر-دیویدسون", "category": "CLINICAL", "scoring": "SUM"},
    "SWLS": {"title": "رضایت از زندگی", "category": "CLINICAL", "scoring": "SUM"},
    "STAI_SHORT": {"title": "اضطراب حالت-صفت اشپیلبرگر", "category": "CLINICAL", "scoring": "SUM"},
    " Rosenberg_SE": {"title": "عزت نفس روزنبرگ", "category": "CLINICAL", "scoring": "SUM"},
    "GRIT": {"title": "مقیاس پشتکار و اشتیاق (Grit)", "category": "CLINICAL", "scoring": "SUM"},
    
    # --- اکو-روانشناسی ---
    "BIOPHILIA": {"title": "شاخص بیوفیلیا (دوستی با حیات)", "category": "ECO_PSYCHOLOGY", "scoring": "AVERAGE", "subscales": ["UTIL", "NAT", "SYMB"]},
    "CNS": {"title": "ارتباط با طبیعت (Connectedness to Nature)", "category": "ECO_PSYCHOLOGY", "scoring": "AVERAGE"},
    "ENV_IDENTITY": {"title": "هویت محیط‌زیستی", "category": "ECO_PSYCHOLOGY", "scoring": "SUM"},
    "RESTORATIVE": {"title": "محیط‌های احیاکننده", "category": "ECO_PSYCHOLOGY", "scoring": "SUM", "subscales": ["BEING", "FASC", "COMP"]},
    "PEBS": {"title": "رفتارهای زیست‌محیطی مثبت", "category": "ECO_PSYCHOLOGY", "scoring": "SUM"},
    "NATURE_AWE": {"title": "حس شگفتی در طبیعت", "category": "ECO_PSYCHOLOGY", "scoring": "SUM"},
    "ECO_GRIEF": {"title": "سوگ محیط‌زیستی", "category": "ECO_PSYCHOLOGY", "scoring": "SUM"},
    "EARTH_CARE": {"title": "اخلاق مراقبت از زمین", "category": "ECO_PSYCHOLOGY", "scoring": "SUM"},
    
    # --- تاب‌آوری اقلیمی ---
    "CCAS": {"title": "اضطراب تغییر اقلیم", "category": "CLIMATE_RESILIENCE", "scoring": "SUM", "subscales": ["COG", "FUNC"]},
    "SOLASTALGIA": {"title": "سولاستالژیا (دلتنگی محیطی)", "category": "CLIMATE_RESILIENCE", "scoring": "SUM"},
    "CLIMATE_RESILIENCE": {"title": "شاخص تاب‌آوری اقلیمی", "category": "CLIMATE_RESILIENCE", "scoring": "AVERAGE", "subscales": ["PREP", "ADAPT", "RECOV"]},
    "DROUGHT_COPING": {"title": "راهکارهای مقابله با خشکسالی", "category": "CLIMATE_RESILIENCE", "scoring": "SUM", "subscales": ["PROB", "EMOT", "AVOID"]},
    "WATER_ANXIETY": {"title": "اضطراب کم‌آبی", "category": "CLIMATE_RESILIENCE", "scoring": "SUM"},
    
    # --- همگرومی و اجتماعی ---
    "ALTRUISM": {"title": "نوع‌دوستی و رفتار کمک‌رسان", "category": "PRO_SOCIAL", "scoring": "SUM"},
    "COOPERATION": {"title": "تمایل به همکاری و همگرومی", "category": "PRO_SOCIAL", "scoring": "AVERAGE", "subscales": ["TRUST", "SHARE", "TEAM"]},
    "COMMUNITY_RES": {"title": "تاب‌آوری جامعه محلی", "category": "PRO_SOCIAL", "scoring": "SUM"},
    "ECO_EMPATHY": {"title": "همدلی با طبیعت و موجودات", "category": "PRO_SOCIAL", "scoring": "SUM"},
    "WATER_ETHIC": {"title": "اخلاق آب و انصاف", "category": "PRO_SOCIAL", "scoring": "SUM"},
    "FUTURE_THINK": {"title": "تفکر آینده‌نگر بین‌نسلی", "category": "PRO_SOCIAL", "scoring": "SUM"},
    
    # --- شغلی/کشاورزی ---
    "FARMER_STRESS": {"title": "استرس ویژه کشاورزان", "category": "OCCUPATIONAL", "scoring": "SUM", "subscales": ["FIN", "WEATHER", "PHYS"]},
    "AGRI_BURNOUT": {"title": "فرسودگی شغلی کشاورزی", "category": "OCCUPATIONAL", "scoring": "SUM"},
    "STEWARDSHIP": {"title": "اخلاق مراقبت از زمین", "category": "OCCUPATIONAL", "scoring": "SUM"},
    "INNOVATION_ADOPT": {"title": "پذیرش نوآوری پایدار", "category": "OCCUPATIONAL", "scoring": "SUM"},
}

def calculate_result(test_code: str, answers: List[Dict], questions_meta: List[Dict]) -> Dict[str, Any]:
    meta = TEST_REGISTRY.get(test_code, {})
    scoring = meta.get("scoring", "SUM")
    
    subscale_scores = {}
    for i, ans in enumerate(answers):
        if i >= len(questions_meta): break
        q_meta = questions_meta[i]
        sub = q_meta.get("subscale_code", "TOTAL")
        if sub not in subscale_scores: subscale_scores[sub] = 0
        
        score = ans.get("score_value", 0)
        if q_meta.get("is_reverse_scored", False):
            score = 6 - score # فرض بر مقیاس 5 گزینه‌ای
            
        subscale_scores[sub] += score

    # تفسیر ساده بر اساس میانگین یا جمع
    total_score = sum(subscale_scores.values())
    max_possible = len(answers) * 5
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    level = "پایین"
    advice = "نیاز به تقویت این جنبه دارید."
    color = "#ef4444"
    
    if percentage > 75:
        level = "بسیار بالا"
        advice = "شما در این زمینه الگو هستید. می‌توانید به دیگران آموزش دهید."
        color = "#10b981"
    elif percentage > 50:
        level = "متوسط رو به بالا"
        advice = "وضعیت خوبی دارید، با تمرین می‌توانید بهتر شوید."
        color = "#f59e0b"
    elif percentage > 25:
        level = "متوسط"
        color = "#3b82f6"

    return {
        "test_code": test_code,
        "test_title": meta.get("title", test_code),
        "subscale_scores": subscale_scores,
        "total_score": round(total_score, 1),
        "percentage": round(percentage, 1),
        "level": level,
        "advice": advice,
        "color": color
    }
