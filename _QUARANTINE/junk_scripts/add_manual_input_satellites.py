from pathlib import Path

print("=" * 80)
print("🔧 FIXING MISSING MOUNTAIN IMPORT")
print("=" * 80)

frontend_path = Path('apps/web/src')
gis_page = frontend_path / 'app/gis/page.tsx'

if gis_page.exists():
    content = gis_page.read_text(encoding='utf-8')
    
    # Add Mountain to imports
    if 'Mountain,' not in content and 'Mountain }' not in content:
        # Find the lucide-react import line
        import_line = "import { "
        if "Satellite, Download, MapPin, TrendingUp, AlertTriangle," in content:
            content = content.replace(
                "import { \n  Satellite, Download, MapPin, TrendingUp, AlertTriangle,\n  Wind, Droplet, Sun, Thermometer, Activity, Database\n} from 'lucide-react';",
                "import { \n  Satellite, Download, MapPin, TrendingUp, AlertTriangle,\n  Wind, Droplet, Sun, Thermometer, Activity, Database, Mountain\n} from 'lucide-react';"
            )
            gis_page.write_text(content, encoding='utf-8')
            print("✅ Added Mountain to imports")
        else:
            # Alternative fix: replace Mountain with MapPin in tabs
            content = content.replace(
                "{ id: 'topographic', label: 'توپوگرافی', icon: Mountain }",
                "{ id: 'topographic', label: 'توپوگرافی', icon: MapPin }"
            )
            gis_page.write_text(content, encoding='utf-8')
            print("✅ Replaced Mountain with MapPin in tabs")
    else:
        print("✅ Mountain already imported")
else:
    print("❌ File not found")

print("\n🚀 Restart server:")
print("   npx next dev -p 3001")