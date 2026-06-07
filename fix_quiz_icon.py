"""
🔧 رفع مشکل import آیکون Quiz
جایگزینی Quiz با HelpCircle
"""
from pathlib import Path
import re

print("=" * 80)
print("🔧 FIXING QUIZ ICON IMPORT ERROR")
print("=" * 80)

frontend_path = Path('apps/web/src')

# Files with Quiz import error
files_to_fix = [
    'app/academy/courses/[id]/page.tsx',
    'app/academy/courses/[id]/lessons/[lessonId]/page.tsx',
]

for file_path in files_to_fix:
    full_path = frontend_path / file_path
    
    if not full_path.exists():
        print(f"❌ File not found: {file_path}")
        continue
    
    print(f"\n📄 Fixing {file_path}...")
    
    content = full_path.read_text(encoding='utf-8')
    original_content = content
    
    # Replace Quiz with HelpCircle in imports
    content = re.sub(
        r'\bQuiz\b',
        'HelpCircle',
        content
    )
    
    # Replace <Quiz /> with <HelpCircle /> in JSX
    content = re.sub(
        r'<Quiz\s*/?>',
        '<HelpCircle />',
        content
    )
    
    # Replace <Quiz className with <HelpCircle className
    content = re.sub(
        r'<Quiz\s+className',
        '<HelpCircle className',
        content
    )
    
    if content != original_content:
        full_path.write_text(content, encoding='utf-8')
        print(f"   ✅ Replaced Quiz with HelpCircle")
        
        # Verify the fix
        if 'Quiz' in content:
            print(f"   ⚠️  Warning: 'Quiz' still found in file")
        else:
            print(f"   ✅ No 'Quiz' references remaining")
        
        if 'HelpCircle' in content:
            print(f"   ✅ HelpCircle is now used")
    else:
        print(f"   ℹ️  No changes needed")

print("\n" + "=" * 80)
print("✅ FIX COMPLETE")
print("=" * 80)
print("\n🚀 Next steps:")
print("   1. Save all files")
print("   2. Browser will auto-reload")
print("   3. Visit: http://localhost:3001/academy/courses/1")
print("   4. The error should be gone!")