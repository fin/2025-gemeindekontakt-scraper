#!/usr/bin/env python3
"""
Combine all municipality JSON files into a single CSV file.
"""

import json
import csv
import glob
from pathlib import Path
from datetime import date


def load_all_municipalities():
    """Load all municipality JSON files and combine them."""
    municipalities = []

    json_files = glob.glob('output/*.json')

    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    municipalities.extend(data)
                    print(f"✓ Loaded {len(data):4} municipalities from {Path(json_file).name}")
                else:
                    print(f"⚠ Skipping {json_file} - not a list")
        except Exception as e:
            print(f"✗ Error loading {json_file}: {e}")

    return municipalities


def write_csv(municipalities, output_file):
    """Write municipalities to CSV file."""
    if not municipalities:
        print("No municipalities to write!")
        return

    # Define CSV columns (all possible fields)
    fieldnames = [
        'bundesland',
        'name',
        'bezirk',
        'plz',
        'address',
        'phone',
        'fax',
        'email',
        'website',
        'source_url',
        'scraped_at'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for muni in municipalities:
            # Write only the fields that exist
            row = {key: muni.get(key, '') for key in fieldnames}
            writer.writerow(row)

    print(f"\n✓ Wrote {len(municipalities)} municipalities to {output_file}")


def main():
    print("=" * 60)
    print("Combining Municipality Data")
    print("=" * 60)
    print()

    # Load all data
    municipalities = load_all_municipalities()

    if not municipalities:
        print("\n✗ No municipalities loaded!")
        return

    # Generate output filename with today's date
    today = date.today().isoformat()
    output_file = f'all_municipalities_{today}.csv'

    # Write to CSV
    write_csv(municipalities, output_file)

    # Print summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)

    by_state = {}
    for muni in municipalities:
        state = muni.get('bundesland', 'Unknown')
        by_state[state] = by_state.get(state, 0) + 1

    print("\nMunicipalities by state:")
    for state in sorted(by_state.keys()):
        print(f"  {state:20} {by_state[state]:4}")

    print(f"\nTotal: {len(municipalities)} municipalities")

    # Data quality metrics
    with_email = sum(1 for m in municipalities if m.get('email'))
    with_phone = sum(1 for m in municipalities if m.get('phone'))
    with_address = sum(1 for m in municipalities if m.get('address'))
    with_website = sum(1 for m in municipalities if m.get('website'))

    print("\nData completeness:")
    print(f"  Email addresses:  {with_email:4} ({100*with_email/len(municipalities):.1f}%)")
    print(f"  Phone numbers:    {with_phone:4} ({100*with_phone/len(municipalities):.1f}%)")
    print(f"  Addresses:        {with_address:4} ({100*with_address/len(municipalities):.1f}%)")
    print(f"  Websites:         {with_website:4} ({100*with_website/len(municipalities):.1f}%)")


if __name__ == '__main__':
    main()
