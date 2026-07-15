import subprocess
import sys
import os
from pathlib import Path

def freeze_dependencies():
    """Extracts pinned dependencies from the current virtual environment."""
    output_file = Path("requirements.lock")
    print(f"[*] Scanning active environment: {sys.executable}")
    
    try:
        # Run pip freeze
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'freeze'],
            capture_output=True, text=True, check=True
        )
        
        # Filter out editable installs and local paths for clean production requirements
        pinned_deps = []
        for line in result.stdout.splitlines():
            if not line.startswith('-e ') and not line.startswith('#') and ' @ ' not in line:
                pinned_deps.append(line)
                
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(pinned_deps)))
            
        print(f"[+] SUCCESS: Generated '{output_file}' with {len(pinned_deps)} pinned packages.")
        print("[*] ACTION: Review this file and replace your loose 'requirements.txt' content with it.")
        
    except subprocess.CalledProcessError as e:
        print(f"[-] ERROR: Failed to run pip freeze. Details: {e}")
    except Exception as e:
        print(f"[-] UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    freeze_dependencies()