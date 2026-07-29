#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify and sort i18n JSON files (fa.json & en.json)
Phase 1-2 of the i18n cleanup plan
"""
import json
from pathlib import Path

LOCALES_DIR = Path("apps/web/src/i18n/locales")

def flatten_dict(d, parent_key='', sep='.'):
    """Convert nested dict to flat dict for easy comparison"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep='.'):
    """Convert flat dict back to nested structure"""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def sort_dict(d):
    """Recursively sort dictionary keys alphabetically"""
    if not isinstance(d, dict):
        return d
    return {k: sort_dict(v) for k, v in sorted(d.items())}

def main():
    print("=" * 60)
    print("  🔍 i18n Verification & Sorting Tool")
    print("=" * 60)
    
    # Read both files
    fa_file = LOCALES_DIR / "fa.json"
    en_file = LOCALES_DIR / "en.json"
    
    with open(fa_file, 'r', encoding='utf-8') as f:
        fa_data = json.load(f)
    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    # Flatten for comparison
    fa_flat = flatten_dict(fa_data)
    en_flat = flatten_dict(en_data)
    
    fa_keys = set(fa_flat.keys())
    en_keys = set(en_flat.keys())
    
    print(f"\n📊 Key Statistics:")
    print(f"   fa.json: {len(fa_keys)} keys")
    print(f"   en.json: {len(en_keys)} keys")
    
    # Check for differences
    only_in_fa = fa_keys - en_keys
    only_in_en = en_keys - fa_keys
    
    if only_in_fa:
        print(f"\n⚠️  Keys in fa.json but NOT in en.json ({len(only_in_fa)}):")
        for k in sorted(only_in_fa):
            print(f"   - {k}: \"{fa_flat[k]}\"")
    
    if only_in_en:
        print(f"\n⚠️  Keys in en.json but NOT in fa.json ({len(only_in_en)}):")
        for k in sorted(only_in_en):
            print(f"   - {k}: \"{en_flat[k]}\"")
    
    if not only_in_fa and not only_in_en:
        print("\n✅ Both files have IDENTICAL key structures!")
    
    # Check for empty/null values
    print("\n🔍 Checking for empty/null values...")
    empty_fa = [k for k, v in fa_flat.items() if not v]
    empty_en = [k for k, v in en_flat.items() if not v]
    
    if empty_fa:
        print(f"⚠️  Empty values in fa.json: {empty_fa}")
    if empty_en:
        print(f"⚠️  Empty values in en.json: {empty_en}")
    if not empty_fa and not empty_en:
        print("✅ No empty/null values found in either file!")
    
    # Check for noise keys (dependencies, component names, CLI errors)
    print("\n🔍 Checking for noise keys...")
    noise_patterns = ['dependencies.', 'devDependencies.', 'exports.', 'engines.', 
                      'scripts.', 'Checkbox', 'Modal', 'CMHeader', 'BulkLocale',
                      'Argument check', 'Unknown command', 'strapi']
    
    noise_fa = [k for k in fa_keys if any(p in k for p in noise_patterns)]
    noise_en = [k for k in en_keys if any(p in k for p in noise_patterns)]
    
    if noise_fa:
        print(f"⚠️  Noise keys in fa.json: {noise_fa}")
    if noise_en:
        print(f"⚠️  Noise keys in en.json: {noise_en}")
    if not noise_fa and not noise_en:
        print("✅ No noise keys found in either file!")
    
    # Sort both files
    print("\n📝 Sorting files alphabetically...")
    fa_sorted = sort_dict(fa_data)
    en_sorted = sort_dict(en_data)
    
    # Write sorted files
    with open(fa_file, 'w', encoding='utf-8') as f:
        json.dump(fa_sorted, f, ensure_ascii=False, indent=2)
    print(f"   ✅ fa.json sorted and saved")
    
    with open(en_file, 'w', encoding='utf-8') as f:
        json.dump(en_sorted, f, ensure_ascii=False, indent=2)
    print(f"   ✅ en.json sorted and saved")
    
    # Final summary
    print("\n" + "=" * 60)
    print("  📋 FINAL REPORT")
    print("=" * 60)
    print(f"  Total valid keys: {len(fa_keys)}")
    print(f"  Files reviewed: fa.json, en.json")
    print(f"  Files updated: fa.json (sorted), en.json (sorted)")
    print(f"  fa.json ↔ en.json sync: {'✅ 100%' if not only_in_fa and not only_in_en else '⚠️  See differences above'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
