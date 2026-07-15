import os
from pathlib import Path
from collections import defaultdict

def find_large_files(root_dir=".", size_threshold_mb=5):
    """Scans for large files that might be accidentally committed to Git."""
    root_path = Path(root_dir).resolve()
    large_files = []
    
    # Directories that are typically ignored by Git but might contain huge files
    skip_dirs = {'.git', 'node_modules', '.venv', '__pycache__', '.next', 'dist', 'build', 'migrations'}
    
    print(f"[*] Scanning {root_path} for files larger than {size_threshold_mb}MB...")
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Modify dirnames in-place to skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > size_threshold_mb:
                    large_files.append((str(file_path.relative_to(root_path)), size_mb))
            except OSError:
                pass
                
    # Sort results
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "="*70)
    print(f"📊 BLOAT DETECTION REPORT: {len(large_files)} large files found")
    print("="*70)
    
    if not large_files:
        print("✅ Repository looks clean. No large files detected.")
    else:
        for path, size in large_files[:15]: # Show top 15
            print(f"  ⚠️  {size:8.2f} MB  ->  {path}")
            
        print("\n💡 STRATEGIC RECOMMENDATION:")
        print("  If these files are assets (images, videos, models), move them to S3/CDN.")
        print("  If they are build artifacts, ensure they are listed in your .gitignore.")
        print("  If they are already committed, use 'git filter-repo' to remove them from history.")
        
    print("="*70 + "\n")

if __name__ == "__main__":
    find_large_files()