"""
Fix "use client" directive position in all page files
"""
from pathlib import Path
import re

print("=" * 80)
print("FIX 'use client' DIRECTIVE POSITION")
print("=" * 80)

FRONTEND = Path('apps/web/src')

# Find all page.tsx files
page_files = list(FRONTEND.rglob('page.tsx'))
print(f"\nFound {len(page_files)} page files")

fixed_count = 0

for page_file in page_files:
    try:
        content = page_file.read_text(encoding='utf-8')
        
        # Check if "use client" exists
        if '"use client"' not in content and "'use client'" not in content:
            continue
        
        # Check if it's already at the top
        lines = content.split('\n')
        first_non_empty = next((i for i, line in enumerate(lines) if line.strip()), 0)
        
        if lines[first_non_empty].strip() in ['"use client"', "'use client'"]:
            continue  # Already correct
        
        # Remove "use client" from wherever it is
        content = re.sub(r'^\s*["\']use client["\'];?\s*\n', '', content, flags=re.MULTILINE)
        
        # Remove any duplicate imports that might have been added
        # Find all import lines
        import_lines = re.findall(r'^import .+$', content, re.MULTILINE)
        
        # Remove duplicate imports
        seen_imports = set()
        unique_lines = []
        for line in content.split('\n'):
            if line.startswith('import '):
                if line in seen_imports:
                    continue
                seen_imports.add(line)
            unique_lines.append(line)
        
        content = '\n'.join(unique_lines)
        
        # Add "use client" at the very top
        content = '"use client";\n\n' + content.strip()
        
        # Write back
        page_file.write_text(content, encoding='utf-8')
        
        rel_path = page_file.relative_to(FRONTEND)
        print(f"   [FIXED] {rel_path}")
        fixed_count += 1
        
    except Exception as e:
        print(f"   [ERROR] {page_file}: {e}")

print(f"\n{'='*80}")
print(f"Fixed {fixed_count} files")
print(f"{'='*80}")
print("\nNow restart frontend:")
print("   npx next dev -p 3001")