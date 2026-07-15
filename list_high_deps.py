import json

with open('dependency_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

modules = report.get('modules', [])
high_deps = [(m['name'], len(m.get('imports', []))) for m in modules if len(m.get('imports', [])) > 10]
high_deps.sort(key=lambda x: x[1], reverse=True)

print('Modules with >10 dependencies:')
for name, count in high_deps:
    print(f'  {name}: {count} imports')

with open('high_dependency_modules.txt', 'w', encoding='utf-8') as f:
    f.write('Modules with >10 dependencies:\n')
    for name, count in high_deps:
        f.write(f'  {name}: {count} imports\n')

print(f'\nFull list saved to high_dependency_modules.txt')
