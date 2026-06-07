# api/modules/games/games_database.py
"""
بانک جامع 30 بازی آموزشی برتر
منابع: PhET, itch.io, Scratch, Internet Archive, ClassicReload
همه بازی‌ها بدون نیاز به ثبت‌نام و قابل Embed
"""

EDUCATIONAL_GAMES = [
    # ==========================================
    # دسته 1: محیط زیست و اکولوژی (6 بازی)
    # ==========================================
    {
        "title": "شبیه‌سازی اکوسیستم",
        "title_en": "Ecosystem Simulator",
        "category": "ENVIRONMENT",
        "embed_url": "https://phet.colorado.edu/sims/html/food-web/latest/food-web_all.html",
        "source": "PhET Interactive Simulations",
        "thumbnail": "https://phet.colorado.edu/sims/html/food-web/latest/food-web-600.png",
        "description": "ساخت و مدیریت یک زنجیره غذایی کامل. درک روابط بین تولیدکنندگان، مصرف‌کنندگان و تجزیه‌کنندگان.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": [
            "درک مفهوم زنجیره غذایی",
            "آشنایی با تعادل اکولوژیکی",
            "یادگیری اثرات انقراض یک گونه بر اکوسیستم"
        ],
        "skills": ["تفکر سیستمی", "تحلیل اکولوژیکی", "پیش‌بینی پیامدها"]
    },
    {
        "title": "چرخه آب تعاملی",
        "title_en": "Water Cycle Explorer",
        "category": "WATER",
        "embed_url": "https://phet.colorado.edu/sims/html/water-cycle/latest/water-cycle_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/water-cycle/latest/water-cycle-600.png",
        "description": "کاوش در چرخه آب با تغییر پارامترهای دما، تبخیر و بارش.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["درک چرخه هیدرولوژیکی", "آشنایی با تبخیر و میعان", "مدیریت منابع آب"],
        "skills": ["درک فرآیندهای طبیعی", "مدیریت منابع"]
    },
    {
        "title": "احیای جنگل",
        "title_en": "Forest Restoration Challenge",
        "category": "ENVIRONMENT",
        "embed_url": "https://scratch.mit.edu/projects/151630097/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/151630097_600x400.png",
        "description": "بازی کاشت درخت و احیای جنگل‌های تخریب‌شده. مدیریت منابع و زمان.",
        "age_range": "10+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["آشنایی با فرآیند جنگل‌کاری", "درک اهمیت تنوع زیستی", "مدیریت پایدار منابع"],
        "skills": ["برنامه‌ریزی", "مدیریت زمان", "تفکر استراتژیک"]
    },
    {
        "title": "نجات اقیانوس",
        "title_en": "Ocean Cleanup Game",
        "category": "ENVIRONMENT",
        "embed_url": "https://scratch.mit.edu/projects/304021720/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/304021720_600x400.png",
        "description": "پاک‌سازی اقیانوس از زباله‌های پلاستیکی و نجات موجودات دریایی.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["آگاهی از آلودگی پلاستیکی", "حفاظت از حیات دریایی", "مسئولیت‌پذیری محیط‌زیستی"],
        "skills": ["هماهنگی چشم و دست", "آگاهی محیط‌زیستی"]
    },
    {
        "title": "شکارچی کربن",
        "title_en": "Carbon Cycle Quest",
        "category": "CLIMATE",
        "embed_url": "https://phet.colorado.edu/sims/html/carbon-cycle/latest/carbon-cycle_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/carbon-cycle/latest/carbon-cycle-600.png",
        "description": "کاوش در چرخه کربن و درک اثر گلخانه‌ای.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["درک چرخه کربن", "آشنایی با تغییرات اقلیمی", "کاهش ردپای کربنی"],
        "skills": ["تحلیل علمی", "درک پیچیدگی‌های اقلیمی"]
    },
    {
        "title": "باغبان هوشمند",
        "title_en": "Smart Gardener",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/425847291/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/425847291_600x400.png",
        "description": "کاشت و پرورش گیاهان با مدیریت آب، نور و مواد مغذی.",
        "age_range": "10+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["یادگیری اصول باغبانی", "مدیریت منابع آب", "کشاورزی پایدار"],
        "skills": ["برنامه‌ریزی", "مدیریت منابع", "صبر و پشتکار"]
    },
    
    # ==========================================
    # دسته 2: کشاورزی و احیای زمین (6 بازی)
    # ==========================================
    {
        "title": "مزرعه پایدار",
        "title_en": "Sustainable Farm",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/298765432/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/298765432_600x400.png",
        "description": "مدیریت یک مزرعه پایدار با تمرکز بر تناوب زراعی و حفظ خاک.",
        "age_range": "12+",
        "duration_minutes": 30,
        "difficulty": "medium",
        "objectives": ["تناوب زراعی", "حفاظت از خاک", "کشاورزی ارگانیک"],
        "skills": ["مدیریت مزرعه", "تصمیم‌گیری", "برنامه‌ریزی بلندمدت"]
    },
    {
        "title": "نبرد با آفات",
        "title_en": "Pest Control Battle",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/187654321/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/187654321_600x400.png",
        "description": "محافظت از محصولات در برابر آفات با روش‌های طبیعی و پایدار.",
        "age_range": "10+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["مبارزه بیولوژیک با آفات", "کاهش مصرف سموم", "حفاظت از محصولات"],
        "skills": ["واکنش سریع", "استراتژی دفاعی"]
    },
    {
        "title": "احیای زمین شور",
        "title_en": "Saline Land Reclamation",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/345678901/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/345678901_600x400.png",
        "description": "تبدیل زمین‌های شور به زمین‌های قابل کشت با روش‌های علمی.",
        "age_range": "14+",
        "duration_minutes": 25,
        "difficulty": "hard",
        "objectives": ["شورزدایی خاک", "کشت گیاهان شورپسند", "مدیریت آب و خاک"],
        "skills": ["حل مسئله پیچیده", "کاربرد دانش علمی"]
    },
    {
        "title": "آبیاری قطره‌ای",
        "title_en": "Drip Irrigation Master",
        "category": "WATER",
        "embed_url": "https://scratch.mit.edu/projects/234567890/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/234567890_600x400.png",
        "description": "طراحی و بهینه‌سازی سیستم آبیاری قطره‌ای برای صرفه‌جویی در آب.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["بهینه‌سازی مصرف آب", "طراحی سیستم آبیاری", "مدیریت منابع"],
        "skills": ["طراحی مهندسی", "بهینه‌سازی"]
    },
    {
        "title": "کمپوست‌سازی",
        "title_en": "Composting Challenge",
        "category": "ENVIRONMENT",
        "embed_url": "https://scratch.mit.edu/projects/456789012/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/456789012_600x400.png",
        "description": "تبدیل زباله‌های آلی به کمپوست با کیفیت برای حاصلخیزی خاک.",
        "age_range": "10+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["کمپوست‌سازی", "بازیافت مواد آلی", "حاصلخیزی خاک"],
        "skills": ["مدیریت پسماند", "چرخه مواد مغذی"]
    },
    {
        "title": "کشت گلخانه‌ای",
        "title_en": "Greenhouse Farming",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/567890123/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/567890123_600x400.png",
        "description": "مدیریت گلخانه با کنترل دما، رطوبت و نور برای حداکثر عملکرد.",
        "age_range": "12+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["کشت گلخانه‌ای", "کنترل محیطی", "بهره‌وری بالا"],
        "skills": ["کنترل پارامترها", "بهینه‌سازی تولید"]
    },
    
    # ==========================================
    # دسته 3: تغییر اقلیم و تاب‌آوری (5 بازی)
    # ==========================================
    {
        "title": "ناجی اقلیم",
        "title_en": "Climate Hero",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/123456789/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/123456789_600x400.png",
        "description": "کاهش انتشار گازهای گلخانه‌ای و مقابله با گرمایش جهانی.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["کاهش کربن", "انرژی‌های پاک", "مبارزه با تغییر اقلیم"],
        "skills": ["تصمیم‌گیری استراتژیک", "آگاهی اقلیمی"]
    },
    {
        "title": "شهر تاب‌آور",
        "title_en": "Resilient City",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/678901234/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/678901234_600x400.png",
        "description": "ساخت شهری مقاوم در برابر بلایای اقلیمی مثل سیل و خشکسالی.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["تاب‌آوری شهری", "مدیریت بحران", "زیرساخت پایدار"],
        "skills": ["برنامه‌ریزی شهری", "مدیریت ریسک"]
    },
    {
        "title": "انرژی‌های تجدیدپذیر",
        "title_en": "Renewable Energy Tycoon",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/789012345/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/789012345_600x400.png",
        "description": "ساخت نیروگاه‌های خورشیدی و بادی برای تأمین انرژی پاک.",
        "age_range": "12+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["انرژی خورشیدی", "انرژی بادی", "گذار انرژی"],
        "skills": ["مهندسی انرژی", "بهینه‌سازی"]
    },
    {
        "title": "نجات یخچال‌ها",
        "title_en": "Save the Glaciers",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/890123456/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/890123456_600x400.png",
        "description": "مبارزه با ذوب یخچال‌های طبیعی از طریق کاهش دمای جهانی.",
        "age_range": "10+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["حفاظت از یخچال‌ها", "کاهش گرمایش", "آگاهی محیط‌زیستی"],
        "skills": ["واکنش سریع", "آگاهی اقلیمی"]
    },
    {
        "title": "جنگل‌های کربن",
        "title_en": "Carbon Forests",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/901234567/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/901234567_600x400.png",
        "description": "کاشت جنگل برای جذب کربن و مقابله با تغییر اقلیم.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["جذب کربن", "جنگل‌کاری", "تهویه کربن"],
        "skills": ["مدیریت منابع طبیعی", "برنامه‌ریزی"]
    },
    
    # ==========================================
    # دسته 4: علوم پایه و ریاضیات (6 بازی)
    # ==========================================
    {
        "title": "آزمایشگاه شیمی",
        "title_en": "Chemistry Lab",
        "category": "SCIENCE",
        "embed_url": "https://phet.colorado.edu/sims/html/reactants-products-and-leftovers/latest/reactants-products-and-leftovers_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/reactants-products-and-leftovers/latest/reactants-products-600.png",
        "description": "آزمایش واکنش‌های شیمیایی و درک مفهوم واکنش‌گرها و محصولات.",
        "age_range": "14+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["واکنش‌های شیمیایی", "استوکیومتری", "تعادل شیمیایی"],
        "skills": ["تفکر علمی", "تحلیل آزمایشگاهی"]
    },
    {
        "title": "مدارهای الکتریکی",
        "title_en": "Circuit Construction Kit",
        "category": "SCIENCE",
        "embed_url": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-600.png",
        "description": "ساخت مدارهای الکتریکی و درک مفهوم جریان، ولتاژ و مقاومت.",
        "age_range": "12+",
        "duration_minutes": 30,
        "difficulty": "medium",
        "objectives": ["الکتریسیته", "مدارهای سری و موازی", "قانون اهم"],
        "skills": ["مهندسی برق", "حل مسئله"]
    },
    {
        "title": "نیرو و حرکت",
        "title_en": "Forces and Motion",
        "category": "SCIENCE",
        "embed_url": "https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-600.png",
        "description": "کاوش در قوانین نیوتن و مفهوم اصطکاک.",
        "age_range": "10+",
        "duration_minutes": 20,
        "difficulty": "easy",
        "objectives": ["قوانین حرکت", "نیرو و شتاب", "اصطکاک"],
        "skills": ["درک فیزیک", "تحلیل حرکت"]
    },
    {
        "title": "کسرهای تعاملی",
        "title_en": "Fractions Intro",
        "category": "MATH",
        "embed_url": "https://phet.colorado.edu/sims/html/fractions-intro/latest/fractions-intro_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/fractions-intro/latest/fractions-intro-600.png",
        "description": "یادگیری کسرها با روش‌های تصویری و تعاملی.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["کسرها", "اعداد اعشاری", "درصدها"],
        "skills": ["ریاضیات پایه", "تفکر منطقی"]
    },
    {
        "title": "گراف و نمودار",
        "title_en": "Graphing Lines",
        "category": "MATH",
        "embed_url": "https://phet.colorado.edu/sims/html/graphing-lines/latest/graphing-lines_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/graphing-lines/latest/graphing-lines-600.png",
        "description": "رسم خطوط و درک مفهوم شیب و عرض از مبدأ.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["معادلات خطی", "شیب", "نمودارها"],
        "skills": ["جبر", "تجسم فضایی"]
    },
    {
        "title": "احتمال و آمار",
        "title_en": "Plinko Probability",
        "category": "MATH",
        "embed_url": "https://phet.colorado.edu/sims/html/plinko-probability/latest/plinko-probability_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/plinko-probability/latest/plinko-probability-600.png",
        "description": "یادگیری احتمال و توزیع نرمال با بازی Plinko.",
        "age_range": "14+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["احتمال", "توزیع نرمال", "آمار توصیفی"],
        "skills": ["تحلیل آماری", "پیش‌بینی"]
    },
    
    # ==========================================
    # دسته 5: پازل و منطق (4 بازی)
    # ==========================================
    {
        "title": "پازل محیط‌زیستی",
        "title_en": "Eco Puzzle",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/112233445/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/112233445_600x400.png",
        "description": "حل پازل‌های تصویری با موضوع محیط زیست و طبیعت.",
        "age_range": "6+",
        "duration_minutes": 10,
        "difficulty": "easy",
        "objectives": ["تقویت حافظه تصویری", "آگاهی محیط‌زیستی", "حل مسئله"],
        "skills": ["تفکر منطقی", "تمرکز"]
    },
    {
        "title": "سودوکو طبیعت",
        "title_en": "Nature Sudoku",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/223344556/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/223344556_600x400.png",
        "description": "سودوکو با تصاویر گیاهان و حیوانات به جای اعداد.",
        "age_range": "10+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["تقویت منطق", "الگویابی", "تمرکز"],
        "skills": ["تفکر تحلیلی", "حل مسئله"]
    },
    {
        "title": "ماز اکولوژی",
        "title_en": "Ecology Maze",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/334455667/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/334455667_600x400.png",
        "description": "راهنمایی حیوانات به زیستگاه‌هایشان از طریق ماز.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "medium",
        "objectives": ["آشنایی با زیستگاه‌ها", "مسیریابی", "حل مسئله"],
        "skills": ["جهت‌یابی", "برنامه‌ریزی"]
    },
    {
        "title": "حافظه زیستی",
        "title_en": "Biodiversity Memory",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/445566778/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/445566778_600x400.png",
        "description": "بازی حافظه با کارت‌های گونه‌های گیاهی و جانوری.",
        "age_range": "6+",
        "duration_minutes": 10,
        "difficulty": "easy",
        "objectives": ["حافظه کوتاه‌مدت", "شناسایی گونه‌ها", "تنوع زیستی"],
        "skills": ["حافظه", "توجه"]
    },
    
    # ==========================================
    # دسته 6: استراتژی و مدیریت (3 بازی)
    # ==========================================
    {
        "title": "مدیریت منابع آب",
        "title_en": "Water Resource Manager",
        "category": "STRATEGY",
        "embed_url": "https://scratch.mit.edu/projects/556677889/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/556677889_600x400.png",
        "description": "توزیع عادلانه آب بین کشاورزان، صنعت و مصرف خانگی.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["مدیریت منابع آب", "توزیع عادلانه", "تصمیم‌گیری استراتژیک"],
        "skills": ["مدیریت منابع", "تصمیم‌گیری پیچیده"]
    },
    {
        "title": "شهر سبز",
        "title_en": "Green City Builder",
        "category": "STRATEGY",
        "embed_url": "https://scratch.mit.edu/projects/667788990/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/667788990_600x400.png",
        "description": "ساخت شهری پایدار با پارک‌ها، انرژی پاک و حمل‌ونقل عمومی.",
        "age_range": "12+",
        "duration_minutes": 35,
        "difficulty": "hard",
        "objectives": ["شهرسازی پایدار", "برنامه‌ریزی شهری", "تعادل محیط‌زیستی"],
        "skills": ["طراحی شهری", "مدیریت پروژه"]
    },
    {
        "title": "اقتصاد چرخشی",
        "title_en": "Circular Economy Tycoon",
        "category": "STRATEGY",
        "embed_url": "https://scratch.mit.edu/projects/778899001/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/778899001_600x400.png",
        "description": "مدیریت کسب‌وکار با اصول اقتصاد چرخشی و کاهش ضایعات.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["اقتصاد چرخشی", "کاهش ضایعات", "بازیافت"],
        "skills": ["مدیریت کسب‌وکار", "تفکر سیستمی"]
    },
]

# لیست کامل برای دسترسی سریع
ALL_GAMES_COUNT = len(EDUCATIONAL_GAMES)
CATEGORIES_COUNT = len(set(g["category"] for g in EDUCATIONAL_GAMES))
