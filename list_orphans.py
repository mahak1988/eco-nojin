import json

with open('dependency_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

orphans = report.get('orphan_files', [])

print(f'Total orphans: {len(orphans)}')
print('\nFirst 100 orphans:')
for i, orphan in enumerate(orphans[:100], 1):
    print(f'{i:3d}. {orphan}')

with open('orphans_list.txt', 'w', encoding='utf-8') as f:
    f.write(f'Total orphans: {len(orphans)}\n\n')
    for i, orphan in enumerate(orphans, 1):
        f.write(f'{i:3d}. {orphan}\n')

print(f'\nFull list saved to orphans_list.txt')
