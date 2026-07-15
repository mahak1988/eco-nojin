import json

with open('dependency_report.json', 'r', encoding='utf-8') as f:
    old = json.load(f)

with open('dependency_progress.json', 'r', encoding='utf-8') as f:
    new = json.load(f)

print('Progress Report:')
print(f'  Modules: {old.get("total_modules", 0)} -> {new.get("total_modules", 0)}')
print(f'  Orphans: {old.get("orphan_count", 0)} -> {new.get("orphan_count", 0)}')
print(f'  Circular: {old.get("circular_count", 0)} -> {new.get("circular_count", 0)}')
