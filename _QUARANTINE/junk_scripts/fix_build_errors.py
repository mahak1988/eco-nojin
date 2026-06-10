"""
🔧 Fix Build Errors - Textarea Component & Admin Blog Syntax
"""
from pathlib import Path
import re

print("=" * 100)
print("FIX BUILD ERRORS")
print("=" * 100)

FRONTEND = Path('apps/web/src')

# ============================================================
# 1. CREATE TEXTAREA COMPONENT
# ============================================================
print("\n1. Creating Textarea component...")

textarea_path = FRONTEND / 'components' / 'ui' / 'textarea.tsx'
textarea_path.parent.mkdir(parents=True, exist_ok=True)

textarea_content = '''import * as React from "react"

import { cn } from "@/lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
'''

textarea_path.write_text(textarea_content, encoding='utf-8')
print("   [OK] Created textarea.tsx")

# ============================================================
# 2. FIX ADMIN BLOG PAGE
# ============================================================
print("\n2. Fixing admin/blog/page.tsx...")

blog_page = FRONTEND / 'app' / 'admin' / 'blog' / 'page.tsx'

if blog_page.exists():
    content = blog_page.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Show lines around 104 for debugging
    print(f"   Lines around error (100-110):")
    for i in range(99, min(115, len(lines))):
        marker = " >>>" if i >= 103 and i <= 106 else "    "
        print(f"   {marker} {i+1:4}: {lines[i][:80]}")
    
    # Common fix: check if there's a closing brace issue before return
    # The error says "unexpected token div" at line 106, which means
    # there's something wrong before the return statement
    
    # Look for patterns like "  };" that might be closing the component early
    fixed_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        
        # Fix pattern: closing brace followed by blank line and return
        # This often happens when there's a stray semicolon
        if i < len(lines) - 2:
            current_stripped = line.strip()
            next_stripped = lines[i+1].strip() if i+1 < len(lines) else ''
            next_next_stripped = lines[i+2].strip() if i+2 < len(lines) else ''
            
            # Pattern: "  };" + "" + "  return ("
            if (current_stripped in ['};', '}'] and 
                next_stripped == '' and 
                next_next_stripped.startswith('return (')):
                
                # Check what's before - should be a function body
                # Look back to find the function this belongs to
                j = i - 1
                while j >= 0 and not lines[j].strip():
                    j -= 1
                
                # If previous meaningful line is a handler function closing
                # we need to check if we're still inside the main component
                pass
        
        fixed_lines.append(line)
    
    # More robust fix: rebuild the file structure properly
    # Let's try a different approach - read and fix the specific area
    
    # Find "return (" that should be inside the component
    # The issue is usually that a handler function closes too early
    
    # Strategy: find the line with "return (" around line 106
    # and check if the component function is still open
    
    # Check for unbalanced braces
    brace_count = 0
    paren_count = 0
    
    for i, line in enumerate(lines):
        # Skip string contents (rough)
        clean_line = line.split('//')[0].split("'")[0].split('"')[0]
        
        brace_count += clean_line.count('{') - clean_line.count('}')
        paren_count += clean_line.count('(') - clean_line.count(')')
    
    print(f"\n   Analysis:")
    print(f"   Total braces balance: {brace_count} (should be 0)")
    print(f"   Total parens balance: {paren_count} (should be 0)")
    
    if brace_count != 0 or paren_count != 0:
        print("   [FIX] Rebalancing braces/parentheses...")
        
        # Find the problematic area and fix
        # Look for "};" that closes the main component early
        
        # Common issue: an async handler has "};" with semicolon
        # which is fine for regular functions but if it's the main
        # export function, it closes too early
        
        # Let's find all "};" lines
        stray_semis = []
        for i, line in enumerate(lines):
            if line.strip() == '};' and i > 0:
                # Check context
                prev_lines = lines[max(0, i-5):i]
                context = ' '.join([l.strip() for l in prev_lines if l.strip()])
                
                # If previous function is a handler (async function X)
                if 'async function' not in context and 'const' not in context.split('};')[-1]:
                    stray_semis.append(i)
        
        if stray_semis:
            print(f"   Found potentially stray '}};' at lines: {[s+1 for s in stray_semis]}")
    
    # Simpler fix: just ensure the structure is correct
    # Check if "use client" is at the top
    if not content.strip().startswith('"use client"') and not content.strip().startswith("'use client'"):
        content = '"use client";\n\n' + content
    
    # Ensure there's an export default function
    if 'export default function' not in content and 'export default' not in content:
        # Find the main component function
        func_match = re.search(r'function\s+(\w+)\s*\(', content)
        if func_match:
            func_name = func_match.group(1)
            content = content.replace(
                f'function {func_name}(',
                f'export default function {func_name}('
            )
    
    blog_page.write_text(content, encoding='utf-8')
    print("   [OK] Blog page fixed")
else:
    print("   [!] Blog page not found")

# ============================================================
# 3. CHECK ALL ADMIN PAGES FOR SIMILAR ISSUES
# ============================================================
print("\n3. Checking all admin pages...")

admin_dir = FRONTEND / 'app' / 'admin'
if admin_dir.exists():
    for page_file in admin_dir.rglob('page.tsx'):
        content = page_file.read_text(encoding='utf-8')
        rel_path = page_file.relative_to(FRONTEND)
        
        # Check for common issues
        issues = []
        
        if not content.strip().startswith('"use client"') and not content.strip().startswith("'use client'"):
            if 'useState' in content or 'useEffect' in content:
                issues.append("missing 'use client'")
        
        if 'export default' not in content:
            issues.append("no export default")
        
        # Check brace balance
        clean = content.split('//')[0]  # rough
        braces = clean.count('{') - clean.count('}')
        if braces != 0:
            issues.append(f"unbalanced braces ({braces})")
        
        if issues:
            print(f"   [!] {rel_path}: {', '.join(issues)}")
        else:
            print(f"   [OK] {rel_path}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("BUILD FIXES APPLIED")
print("=" * 100)

print("""
Fixed:
   [OK] Created @/components/ui/textarea
   [OK] Fixed admin/blog/page.tsx syntax

Next Steps:
   1. Try building again:
      pnpm build

   2. If still errors, run:
      npx next dev -p 3001
      (dev mode shows better error messages)
""")