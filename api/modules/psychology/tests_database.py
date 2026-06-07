# api/modules/psychology/tests_database.py
"""
بانک جامع آزمون‌های روانشناسی معتبر
هر آزمون شامل: سؤالات، گزینه‌ها، الگوریتم محاسبه، تفسیر نتایج
"""

# ============================================================
# 1. GHQ-28: پرسشنامه سلامت عمومی گلدبرگ
# ============================================================
GHQ28 = {
    "code": "GHQ28",
    "title": "پرسشنامه سلامت عمومی (GHQ-28)",
    "title_en": "General Health Questionnaire",
    "description": "ابزار معتبر غربالگری سلامت روان با ۴ زیرمقیاس: علائم جسمانی، اضطراب/بی‌خوابی، اختلال عملکرد اجتماعی، افسردگی شدید",
    "category": "general_health",
    "duration_minutes": 10,
    "icon": "💚",
    "color": "#10b981",
    "scoring": "likert_4",
    "subscales": ["somatic", "anxiety", "social", "depression"],
    "questions": [
        {"text": "آیا اخیراً سردرد یا درد داشته‌اید؟", "subscale": "somatic"},
        {"text": "آیا احساس ضعف یا بی‌حالی می‌کنید؟", "subscale": "somatic"},
        {"text": "آیا در تنفس مشکل دارید؟", "subscale": "somatic"},
        {"text": "آیا احساس گرگرفتگی یا لرزش دارید؟", "subscale": "somatic"},
        {"text": "آیا اخیراً احساس ناراحتی و بی‌قراری داشته‌اید؟", "subscale": "anxiety"},
        {"text": "آیا نگران چیزی هستید؟", "subscale": "anxiety"},
        {"text": "آیا خوابتان مختل شده؟", "subscale": "anxiety"},
        {"text": "آیا احساس ترس یا وحشت دارید؟", "subscale": "anxiety"},
        {"text": "آیا می‌توانید کارهای روزمره را انجام دهید؟", "subscale": "social"},
        {"text": "آیا از فعالیت‌های مفید لذت می‌برید؟", "subscale": "social"},
        {"text": "آیا در تصمیم‌گیری مشکل دارید؟", "subscale": "social"},
        {"text": "آیا در انجام کارها نقش مفیدی دارید؟", "subscale": "social"},
        {"text": "آیا از زندگی لذت می‌برید؟", "subscale": "depression"},
        {"text": "آیا می‌توانید روی کار تمرکز کنید؟", "subscale": "depression"},
        {"text": "آیا احساس خوشحالی می‌کنید؟", "subscale": "depression"},
        {"text": "آیا می‌توانید کارهای روزانه را انجام دهید؟", "subscale": "depression"},
    ],
    "options": [
        {"label": "بدتر از معمول", "score": 3},
        {"label": "همانند معمول", "score": 2},
        {"label": "بهتر از معمول", "score": 1},
        {"label": "خیلی بهتر از معمول", "score": 0},
    ],
    "interpretation": {
        "0-24": {"level": "سالم", "color": "#10b981", "advice": "سلامت روان شما در وضعیت عالی است. ادامه دهید!"},
        "25-35": {"level": "نیاز به توجه", "color": "#f59e0b", "advice": "علائم خفیفی دارید. تمرینات آرامش‌بخش و ورزش توصیه می‌شود."},
        "36-50": {"level": "نیاز به مشاوره", "color": "#ea580c", "advice": "علائم متوسطی دارید. مراجعه به مشاور توصیه می‌شود."},
        "51+": {"level": "نیاز فوری به کمک", "color": "#dc2626", "advice": "لطفاً در اسرع وقت با یک متخصص سلامت روان مشورت کنید."},
    }
}


# ============================================================
# 2. DASS-21: افسردگی، اضطراب، استرس
# ============================================================
DASS21 = {
    "code": "DASS21",
    "title": "مقیاس افسردگی، اضطراب و استرس (DASS-21)",
    "title_en": "Depression Anxiety Stress Scale",
    "description": "ابزار معتبر بین‌المللی برای ارزیابی سه بعد اصلی سلامت روان: افسردگی، اضطراب و استرس",
    "category": "general_health",
    "duration_minutes": 8,
    "icon": "🧠",
    "color": "#8b5cf6",
    "scoring": "likert_4_dass",
    "subscales": ["depression", "anxiety", "stress"],
    "questions": [
        {"text": "سخت بود که آرام شوم", "subscale": "stress"},
        {"text": "احساس خشکی دهان داشتم", "subscale": "anxiety"},
        {"text": "نتوانستم احساس مثبتی داشته باشم", "subscale": "depression"},
        {"text": "تنگی نفس داشتم", "subscale": "anxiety"},
        {"text": "سخت بودinitiative بگیرم", "subscale": "depression"},
        {"text": "واکنش‌هایم بیش از حد بود", "subscale": "stress"},
        {"text": "احساس لرزش داشتم", "subscale": "anxiety"},
        {"text": "احساس کردم انرژی زیادی مصرف می‌کنم", "subscale": "stress"},
        {"text": "نگران بودم که وحشت‌زده شوم", "subscale": "anxiety"},
        {"text": "احساس کردم چیزی برای لذت بردن ندارم", "subscale": "depression"},
        {"text": "بی‌قرار بودم", "subscale": "stress"},
        {"text": "سخت بود relax کنم", "subscale": "stress"},
        {"text": "افسرده و غمگین بودم", "subscale": "depression"},
        {"text": "بی‌صبر بودم", "subscale": "stress"},
        {"text": "احساس کردم نزدیک است غش کنم", "subscale": "anxiety"},
        {"text": "نتوانستم از هیچ چیز لذت ببرم", "subscale": "depression"},
        {"text": "احساس کردم ارزشی به عنوان آدم ندارم", "subscale": "depression"},
        {"text": "احساس حساسیت بیش از حد داشتم", "subscale": "stress"},
        {"text": "بدون دلیل تپش قلب داشتم", "subscale": "anxiety"},
        {"text": "از پنیک و وحشت بی‌دلیل ترسیدم", "subscale": "anxiety"},
    ],
    "options": [
        {"label": "کاملاً نادرست", "score": 0},
        {"label": "تا حدودی نادرست", "score": 1},
        {"label": "تا حدودی درست", "score": 2},
        {"label": "کاملاً درست", "score": 3},
    ],
    "interpretation": {
        "depression": {
            "0-9": {"level": "طبیعی", "color": "#10b981"},
            "10-13": {"level": "خفیف", "color": "#f59e0b"},
            "14-20": {"level": "متوسط", "color": "#ea580c"},
            "21-27": {"level": "شدید", "color": "#dc2626"},
            "28+": {"level": "بسیار شدید", "color": "#7f1d1d"},
        },
        "anxiety": {
            "0-7": {"level": "طبیعی", "color": "#10b981"},
            "8-9": {"level": "خفیف", "color": "#f59e0b"},
            "10-14": {"level": "متوسط", "color": "#ea580c"},
            "15-19": {"level": "شدید", "color": "#dc2626"},
            "20+": {"level": "بسیار شدید", "color": "#7f1d1d"},
        },
        "stress": {
            "0-14": {"level": "طبیعی", "color": "#10b981"},
            "15-18": {"level": "خفیف", "color": "#f59e0b"},
            "19-25": {"level": "متوسط", "color": "#ea580c"},
            "26-33": {"level": "شدید", "color": "#dc2626"},
            "34+": {"level": "بسیار شدید", "color": "#7f1d1d"},
        }
    }
}


# ============================================================
# 3. CD-RISC: تاب‌آوری کانر-دیویدسون
# ============================================================
CDRISC = {
    "code": "CDRISC",
    "title": "مقیاس تاب‌آوری کانر-دیویدسون (CD-RISC-10)",
    "title_en": "Connor-Davidson Resilience Scale",
    "description": "ابزار معتبر جهانی برای سنجش توانایی سازگاری با سختی‌ها، بحران‌ها و تغییرات",
    "category": "resilience",
    "duration_minutes": 5,
    "icon": "💪",
    "color": "#f59e0b",
    "scoring": "likert_5",
    "questions": [
        "وقتی شرایط سخت می‌شود، می‌توانم با آن سازگار شوم",
        "تمایل دارم به چیزهای جدید فکر کنم",
        "به غریزه خود اعتماد دارم",
        "می‌توانم با تغییرات کنار بیایم",
        "بعد از بیماری یا سختی، بهبود می‌یابم",
        "برای رسیدن به اهدافم تلاش می‌کنم",
        "وقتی شکست می‌خورم، دوباره بلند می‌شوم",
        "فکر می‌کنم خودم قوی هستم",
        "می‌توانم تصمیمات ناخوشایند بپذیرم",
        "باور دارم می‌توانم بر مشکلات غلبه کنم",
    ],
    "options": [
        {"label": "اصلاً درست نیست", "score": 0},
        {"label": "به ندرت درست است", "score": 1},
        {"label": "گاهی درست است", "score": 2},
        {"label": "اغلب درست است", "score": 3},
        {"label": "کاملاً درست است", "score": 4},
    ],
    "interpretation": {
        "0-15": {"level": "تاب‌آوری پایین", "color": "#dc2626", "advice": "با تمرینات ذهن‌آگاهی و تقویت شبکه حمایتی، تاب‌آوری خود را افزایش دهید."},
        "16-25": {"level": "تاب‌آوری متوسط", "color": "#f59e0b", "advice": "تاب‌آوری قابل قبولی دارید. با توسعه مهارت‌های مقابله‌ای، می‌توانید قوی‌تر شوید."},
        "26-32": {"level": "تاب‌آوری بالا", "color": "#10b981", "advice": "شما فردی تاب‌آور هستید. این توانایی را برای کمک به دیگران به کار بگیرید."},
        "33-40": {"level": "تاب‌آوری بسیار بالا", "color": "#059669", "advice": "شما الگوی تاب‌آوری هستید! می‌توانید منتور دیگران باشید."},
    }
}


# ============================================================
# 4. Holland RIASEC: علاقه‌سنجی شغلی
# ============================================================
HOLLAND = {
    "code": "HOLLAND",
    "title": "آزمون علاقه‌سنجی شغلی هالند (RIASEC)",
    "title_en": "Holland Vocational Interest Test",
    "description": "معتبرترین آزمون علاقه‌سنجی شغلی جهان. شش تیپ شخصیتی شغلی را ارزیابی می‌کند",
    "category": "career",
    "duration_minutes": 15,
    "icon": "💼",
    "color": "#3b82f6",
    "scoring": "yes_no",
    "subscales": ["R", "I", "A", "S", "E", "C"],
    "questions": [
        {"text": "کار با دست و ابزار را دوست دارم", "type": "R"},
        {"text": "تعمیر ماشین یا وسایل را دوست دارم", "type": "R"},
        {"text": "کار در فضای باز را ترجیح می‌دهم", "type": "R"},
        {"text": "ورزش‌های فیزیکی را دوست دارم", "type": "R"},
        {"text": "حل مسائل ریاضی و علمی را دوست دارم", "type": "I"},
        {"text": "مطالعه مقالات علمی را دوست دارم", "type": "I"},
        {"text": "کنجکاو هستم و سؤالات زیادی می‌پرسم", "type": "I"},
        {"text": "تحقیق و پژوهش را دوست دارم", "type": "I"},
        {"text": "نقاشی، موسیقی یا نوشتن را دوست دارم", "type": "A"},
        {"text": "ایده‌های خلاقانه دارم", "type": "A"},
        {"text": "از کارهای یکنواخت بیزارم", "type": "A"},
        {"text": "طراحی و خلق چیزهای جدید را دوست دارم", "type": "A"},
        {"text": "کمک به دیگران را دوست دارم", "type": "S"},
        {"text": "معلم یا مشاور شدن را دوست دارم", "type": "S"},
        {"text": "درک احساسات دیگران را دارم", "type": "S"},
        {"text": "کار گروهی را ترجیح می‌دهم", "type": "S"},
        {"text": "رهبری و مدیریت را دوست دارم", "type": "E"},
        {"text": "متقاعد کردن دیگران را دوست دارم", "type": "E"},
        {"text": "راه‌اندازی کسب‌وکار را دوست دارم", "type": "E"},
        {"text": "رقابت را دوست دارم", "type": "E"},
        {"text": "کار با جزئیات و نظم را دوست دارم", "type": "C"},
        {"text": "کار دفتری و اداری را دوست دارم", "type": "C"},
        {"text": "دقت و نظم برایم مهم است", "type": "C"},
        {"text": "پیروی از دستورالعمل‌ها را دوست دارم", "type": "C"},
    ],
    "interpretation": {
        "R": {"name": "واقع‌گرا (Realistic)", "description": "علاقه‌مند به کارهای عملی، فنی و فیزیکی", "careers": ["مهندس", "کشاورز", "تکنسین", "مکانیک", "معمار منظر"]},
        "I": {"name": "جستجوگر (Investigative)", "description": "علاقه‌مند به تحقیق، تحلیل و حل مسئله", "careers": ["دانشمند", "پژوهشگر", "دکتر", "تحلیلگر داده", "اکولوژیست"]},
        "A": {"name": "هنری (Artistic)", "description": "علاقه‌مند به خلاقیت، طراحی و بیان", "careers": ["طراح", "نویسنده", "هنرمند", "گرافیست", "معمار"]},
        "S": {"name": "اجتماعی (Social)", "description": "علاقه‌مند به کمک، آموزش و مشاوره", "careers": ["معلم", "مشاور", "مددکار", "پرستار", "روانشناس"]},
        "E": {"name": "متهور (Enterprising)", "description": "علاقه‌مند به رهبری، فروش و مدیریت", "careers": ["مدیر", "کارآفرین", "بازاریاب", "وکیل", "سیاستمدار"]},
        "C": {"name": "قراردادی (Conventional)", "description": "علاقه‌مند به نظم، جزئیات و سازماندهی", "careers": ["حسابدار", "کارمند بانک", "منشی", "آمارگیر", "مدیر پروژه"]},
    }
}


# ============================================================
# 5. Nature Relatedness: ارتباط با طبیعت (اختصاصی اکو نوژین!)
# ============================================================
NATURE_RELATEDNESS = {
    "code": "NR6",
    "title": "مقیاس ارتباط با طبیعت (NR-6)",
    "title_en": "Nature Relatedness Scale",
    "description": "آزمون اختصاصی اکو نوژین برای سنجش میزان ارتباط عاطفی، شناختی و تجربی شما با طبیعت. هرچه بالاتر، تاب‌آوری بیشتر و اضطراب کمتر!",
    "category": "eco",
    "duration_minutes": 3,
    "icon": "🌿",
    "color": "#10b981",
    "scoring": "likert_5",
    "questions": [
        "بودن در طبیعت برایم بسیار لذت‌بخش است",
        "احساس می‌کنم بخشی از چرخه طبیعت هستم",
        "وقتی در طبیعت هستم، احساس آرامش عمیق می‌کنم",
        "نگران وضعیت محیط زیست هستم",
        "رشد گیاهان و تغییر فصل‌ها برایم جذاب است",
        "حاضرم برای حفظ طبیعت از راحتی‌ام بگذرم",
    ],
    "options": [
        {"label": "کاملاً مخالفم", "score": 1},
        {"label": "مخالفم", "score": 2},
        {"label": "نظری ندارم", "score": 3},
        {"label": "موافقم", "score": 4},
        {"label": "کاملاً موافقم", "score": 5},
    ],
    "interpretation": {
        "6-12": {"level": "ارتباط ضعیف با طبیعت", "color": "#dc2626", "advice": "پیشنهاد می‌کنیم هفته‌ای یک‌بار به طبیعت بروید. حتی ۲۰ دقیقه پیاده‌روی در پارک می‌تواند تأثیرگذار باشد."},
        "13-18": {"level": "ارتباط متوسط", "color": "#f59e0b", "advice": "ارتباط خوبی دارید. با باغبانی یا شرکت در فعالیت‌های اکوتوریسم، این ارتباط را عمیق‌تر کنید."},
        "19-24": {"level": "ارتباط قوی", "color": "#10b981", "advice": "شما دوستدار طبیعت هستید! این ارتباط را به دیگران نیز منتقل کنید."},
        "25-30": {"level": "ارتباط بسیار قوی - دوستدار زمین", "color": "#059669", "advice": "شما یک Eco-Warrior هستید! می‌توانید راهنمای اکوتوریسم یا مربی محیط زیست شوید."},
    }
}


# ============================================================
# 6. Eco-Anxiety: اضطراب اقلیمی (اختصاصی اکو نوژین!)
# ============================================================
ECO_ANXIETY = {
    "code": "ECOANX",
    "title": "مقیاس اضطراب اقلیمی",
    "title_en": "Eco-Anxiety Scale",
    "description": "آزمون اختصاصی برای سنجش میزان نگرانی شما درباره تغییرات اقلیمی و تأثیر آن بر سلامت روان",
    "category": "eco",
    "duration_minutes": 5,
    "icon": "🌡️",
    "color": "#ef4444",
    "scoring": "likert_5",
    "questions": [
        "وقتی درباره تغییرات اقلیمی فکر می‌کنم، مضطرب می‌شوم",
        "احساس می‌کنم آینده سیاره ما تاریک است",
        "خبرهای مربوط به محیط زیست مرا ناراحت می‌کند",
        "نگران آینده فرزندانم در این سیاره هستم",
        "احساس می‌کنم کاری که می‌کنم کافی نیست",
        "از تصور فاجعه‌های اقلیمی می‌ترسم",
        "گاهی احساس ناامیدی درباره آینده زمین دارم",
        "نگرانم که نسل‌های آینده ما را سرزنش کنند",
    ],
    "options": [
        {"label": "هرگز", "score": 1},
        {"label": "به ندرت", "score": 2},
        {"label": "گاهی", "score": 3},
        {"label": "اغلب", "score": 4},
        {"label": "همیشه", "score": 5},
    ],
    "interpretation": {
        "8-15": {"level": "اضطراب اقلیمی پایین", "color": "#10b981", "advice": "نگرانی شما در حد سالم است. این نگرانی را به اقدام مثبت تبدیل کنید."},
        "16-24": {"level": "اضطراب اقلیمی متوسط", "color": "#f59e0b", "advice": "نگرانی شما قابل درک است. با اقدامات کوچک و پیوسته، احساس کنترل بیشتری پیدا می‌کنید."},
        "25-32": {"level": "اضطراب اقلیمی بالا", "color": "#ea580c", "advice": "این نگرانی بر زندگی شما تأثیر گذاشته. با گروه‌های همفکر ارتباط برقرار کنید و از متخصص کمک بگیرید."},
        "33-40": {"level": "اضطراب اقلیمی شدید", "color": "#dc2626", "advice": "لطفاً با یک روانشناس متخصص در حوزه اکو-سایکولوژی مشورت کنید. شما تنها نیستید."},
    }
}


# ============================================================
# 7. MBI: فرسودگی شغلی
# ============================================================
MBI = {
    "code": "MBI",
    "title": "مقیاس فرسودگی شغلی ماسلاچ (MBI-9)",
    "title_en": "Maslach Burnout Inventory",
    "description": "ابزار استاندارد جهانی برای ارزیابی فرسودگی شغلی در سه بعد: خستگی عاطفی، مسخ شخصیت، و کاهش عملکرد",
    "category": "career",
    "duration_minutes": 5,
    "icon": "🔥",
    "color": "#dc2626",
    "scoring": "likert_7",
    "subscales": ["emotional_exhaustion", "depersonalization", "personal_accomplishment"],
    "questions": [
        {"text": "احساس می‌کنم از نظر عاطفی تخلیه شده‌ام", "subscale": "emotional_exhaustion"},
        {"text": "صبح‌ها با بی‌میلی به سر کار می‌روم", "subscale": "emotional_exhaustion"},
        {"text": "احساس می‌کنم در آستانه فروپاشی هستم", "subscale": "emotional_exhaustion"},
        {"text": "با بعضی افراد مثل اشیاء رفتار می‌کنم", "subscale": "depersonalization"},
        {"text": "سخت است به دیگران اهمیت دهم", "subscale": "depersonalization"},
        {"text": "احساس می‌کنم با بعضی افراد سرد شده‌ام", "subscale": "depersonalization"},
        {"text": "به راحتی می‌فهمم دیگران چه احساسی دارند", "subscale": "personal_accomplishment", "reverse": True},
        {"text": "با انرژی زیاد کارهایم را انجام می‌دهم", "subscale": "personal_accomplishment", "reverse": True},
        {"text": "احساس می‌کنم کارهایم مؤثر است", "subscale": "personal_accomplishment", "reverse": True},
    ],
    "options": [
        {"label": "هرگز", "score": 0},
        {"label": "چند بار در سال یا کمتر", "score": 1},
        {"label": "یک بار در ماه یا کمتر", "score": 2},
        {"label": "چند بار در ماه", "score": 3},
        {"label": "یک بار در هفته", "score": 4},
        {"label": "چند بار در هفته", "score": 5},
        {"label": "هر روز", "score": 6},
    ],
    "interpretation": {
        "0-16": {"level": "بدون فرسودگی", "color": "#10b981", "advice": "تعادل کار-زندگی خوبی دارید."},
        "17-26": {"level": "فرسودگی خفیف", "color": "#f59e0b", "advice": "به استراحت و بازنگری در سبک کاری نیاز دارید."},
        "27-36": {"level": "فرسودگی متوسط", "color": "#ea580c", "advice": "فرسودگی در حال تأثیر بر زندگی شماست. تغییرات جدی لازم است."},
        "37+": {"level": "فرسودگی شدید", "color": "#dc2626", "advice": "نیاز فوری به استراحت طولانی و مشاوره شغلی دارید."},
    }
}


# ============================================================
# 8. PHQ-9: غربالگری افسردگی
# ============================================================
PHQ9 = {
    "code": "PHQ9",
    "title": "پرسشنامه سلامت بیمار (PHQ-9)",
    "title_en": "Patient Health Questionnaire",
    "description": "ابزار استاندارد غربالگری افسردگی که در کلینیک‌های سراسر جهان استفاده می‌شود",
    "category": "general_health",
    "duration_minutes": 5,
    "icon": "😔",
    "color": "#6366f1",
    "scoring": "likert_4_phq",
    "questions": [
        "کم‌علاقگی یا عدم لذت از انجام کارها",
        "احساس افسردگی، ناامیدی یا بی‌آیندگی",
        "مشکل در به خواب رفتن، بیدار ماندن یا خواب زیاد",
        "احساس خستگی یا نداشتن انرژی",
        "کم‌اشتهایی یا پرخوری",
        "احساس بدی درباره خودتان - یا اینکه شکست خورده‌اید",
        "مشکل در تمرکز روی کارها",
        "حرکت یا صحبت کردن کندتر، یا بی‌قراری",
        "افکار مرگ یا آسیب به خود",
    ],
    "options": [
        {"label": "اصلاً", "score": 0},
        {"label": "چند روز", "score": 1},
        {"label": "بیشتر از نیمی از روزها", "score": 2},
        {"label": "تقریباً هر روز", "score": 3},
    ],
    "interpretation": {
        "0-4": {"level": "حداقل افسردگی", "color": "#10b981"},
        "5-9": {"level": "افسردگی خفیف", "color": "#f59e0b"},
        "10-14": {"level": "افسردگی متوسط", "color": "#ea580c"},
        "15-19": {"level": "افسردگی نسبتاً شدید", "color": "#dc2626"},
        "20-27": {"level": "افسردگی شدید", "color": "#7f1d1d"},
    }
}


# ============================================================
# 9. Satisfaction with Life: رضایت از زندگی
# ============================================================
SWLS = {
    "code": "SWLS",
    "title": "مقیاس رضایت از زندگی (SWLS)",
    "title_en": "Satisfaction with Life Scale",
    "description": "ابزار معتبر دینر برای سنجش ارزیابی شناختی از کیفیت زندگی",
    "category": "wellbeing",
    "duration_minutes": 3,
    "icon": "😊",
    "color": "#fbbf24",
    "scoring": "likert_7",
    "questions": [
        "در بیشتر موارد، زندگی من به ایده‌آل‌هایم نزدیک است",
        "شرایط زندگی‌ام عالی است",
        "از زندگی‌ام راضی هستم",
        "تاکنون چیزهای مهمی که در زندگی می‌خواستم را به دست آورده‌ام",
        "اگر می‌توانستم تقریباً هیچ چیز را در زندگی‌ام تغییر ندهم",
    ],
    "options": [
        {"label": "کاملاً مخالفم", "score": 1},
        {"label": "مخالفم", "score": 2},
        {"label": "کمی مخالفم", "score": 3},
        {"label": "نظری ندارم", "score": 4},
        {"label": "کمی موافقم", "score": 5},
        {"label": "موافقم", "score": 6},
        {"label": "کاملاً موافقم", "score": 7},
    ],
    "interpretation": {
        "5-9": {"level": "نارضایتی شدید", "color": "#dc2626"},
        "10-14": {"level": "نارضایتی", "color": "#ea580c"},
        "15-19": {"level": "کمی نارضایت", "color": "#f59e0b"},
        "20-24": {"level": "خنثی", "color": "#64748b"},
        "25-29": {"level": "راضی", "color": "#10b981"},
        "30-35": {"level": "راضی‌تر", "color": "#059669"},
        "36-40": {"level": "بسیار راضی", "color": "#047857"},
    }
}


# ============================================================
# لیست تمام آزمون‌ها
# ============================================================
ALL_TESTS = {
    "GHQ28": GHQ28,
    "DASS21": DASS21,
    "CDRISC": CDRISC,
    "HOLLAND": HOLLAND,
    "NR6": NATURE_RELATEDNESS,
    "ECOANX": ECO_ANXIETY,
    "MBI": MBI,
    "PHQ9": PHQ9,
    "SWLS": SWLS,
}


def get_test_by_code(code: str):
    return ALL_TESTS.get(code)


def calculate_score(test_code: str, answers: list):
    """محاسبه نمره و تفسیر نتیجه"""
    test = ALL_TESTS.get(test_code)
    if not test:
        return {"error": "آزمون یافت نشد"}
    
    scoring = test["scoring"]
    
    # محاسبه نمره کل
    if scoring in ["likert_4", "likert_5", "likert_7", "likert_4_phq", "likert_4_dass"]:
        total = sum(a.get("score", 0) for a in answers)
    elif scoring == "yes_no":
        total = sum(1 for a in answers if a.get("answer") is True)
    else:
        total = sum(a.get("score", 0) for a in answers)
    
    # تفسیر بر اساس بازه
    interpretation = test.get("interpretation", {})
    
    # اگر آزمون چندبعدی است
    if "subscales" in test:
        subscale_scores = {}
        for i, q in enumerate(test.get("questions", [])):
            subscale = q.get("subscale") if isinstance(q, dict) else None
            if subscale and i < len(answers):
                if subscale not in subscale_scores:
                    subscale_scores[subscale] = 0
                score = answers[i].get("score", 0)
                if scoring == "likert_4_dass":
                    score *= 2  # DASS-21 needs multiplication by 2
                subscale_scores[subscale] += score
        
        # تفسیر هر زیرمقیاس
        subscale_interpretations = {}
        for subscale, score in subscale_scores.items():
            if subscale in interpretation:
                for range_key, interp in interpretation[subscale].items():
                    max_val = int(range_key.replace("+", "999"))
                    if score <= max_val:
                        subscale_interpretations[subscale] = {
                            "score": score,
                            **interp
                        }
                        break
        
        return {
            "total_score": total,
            "subscale_scores": subscale_scores,
            "subscale_interpretations": subscale_interpretations,
            "test_info": {
                "code": test["code"],
                "title": test["title"],
                "category": test["category"],
            }
        }
    
    # تفسیر برای آزمون‌های تک‌بعدی
    result = None
    for range_key, interp in interpretation.items():
        max_val = int(range_key.replace("+", "999"))
        if total <= max_val:
            result = {
                "total_score": total,
                "level": interp.get("level"),
                "color": interp.get("color"),
                "advice": interp.get("advice", ""),
                "test_info": {
                    "code": test["code"],
                    "title": test["title"],
                    "category": test["category"],
                }
            }
            break
    
    return result


def get_holland_result(answers: list):
    """محاسبه ویژه آزمون هالند"""
    test = HOLLAND
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    
    for i, q in enumerate(test["questions"]):
        if i < len(answers) and answers[i].get("answer") is True:
            scores[q["type"]] += 1
    
    # مرتب‌سازی بر اساس نمره
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3_code = "".join([t[0] for t in sorted_types[:3]])
    
    return {
        "scores": scores,
        "top_3_code": top_3_code,
        "top_3_types": [
            {
                "code": t[0],
                "score": t[1],
                **test["interpretation"][t[0]]
            }
            for t in sorted_types[:3]
        ],
        "test_info": {
            "code": test["code"],
            "title": test["title"],
        }
    }
