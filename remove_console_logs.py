from pathlib import Path
import re

print("🔧 Removing console.log statements...")

frontend_path = Path('apps/web')
removed_count = 0

for ts_file in frontend_path.rglob('*.ts'):
    if 'node_modules' in str(ts_file) or '.next' in str(ts_file):
        continue
    
    try:
        content = ts_file.read_text(encoding='utf-8')
        original = content
        
        # Remove console.log
        content = re.sub(r'\s*console\.log\([^)]*\);?\n?', '\n', content)
        
        if content != original:
            ts_file.write_text(content, encoding='utf-8')
            removed_count += 1
    
    except Exception as e:
        print(f"Error: {e}")

print(f"✅ Removed console.log from {removed_count} files")
