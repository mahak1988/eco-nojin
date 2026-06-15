"""Check for God-Files in the codebase."""
import ast
from pathlib import Path


def check_file(file_path: Path) -> bool:
    """Check if a file is a God-File."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        if len(lines) > 500:
            print(f"❌ God-File detected: {file_path} ({len(lines)} lines)")
            return False
        
        tree = ast.parse(content)
        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
        functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        
        if len(classes) > 5 or len(functions) > 20:
            print(f"❌ God-File detected: {file_path} ({len(classes)} classes, {len(functions)} functions)")
            return False
        
        return True
    except Exception as e:
        print(f"⚠️  Error checking {file_path}: {e}")
        return True


def main():
    """Main function."""
    api_dir = Path('api')
    all_passed = True
    
    for py_file in api_dir.rglob('*.py'):
        if not check_file(py_file):
            all_passed = False
    
    if all_passed:
        print("✅ No God-Files detected!")
        exit(0)
    else:
        print("❌ God-Files detected! Please refactor.")
        exit(1)


if __name__ == "__main__":
    main()
