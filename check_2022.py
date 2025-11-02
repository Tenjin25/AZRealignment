import json
import pandas as pd

# Load JSON
data = json.load(open('Data/az_county_election_results.json'))
gov_2022 = data['results_by_year']['2022']['governor']['governor_2022']['results']

print("2022 Governor Results from JSON:")
print("=" * 60)

# Show a few counties
for county in ['MARICOPA', 'PIMA', 'APACHE']:
    if county in gov_2022:
        d = gov_2022[county]
        print(f"\n{county}:")
        print(f"  Dem: {d['dem_votes']:,}")
        print(f"  Rep: {d['rep_votes']:,}")
        print(f"  Total: {d['total_votes']:,}")
        print(f"  Winner: {d['winner']} by {d['margin_pct']:.2f}%")

# Show statewide
if 'ARIZONA' in gov_2022:
    d = gov_2022['ARIZONA']
    print(f"\nARIZONA (statewide):")
    print(f"  Dem (Katie Hobbs): {d['dem_votes']:,}")
    print(f"  Rep (Kari Lake): {d['rep_votes']:,}")
    print(f"  Total: {d['total_votes']:,}")
    print(f"  Winner: {d['winner']} by {d['margin_pct']:.2f}%")
    
    # Real 2022 result: Hobbs won by 17,117 votes (0.67% margin)
    print(f"\n  Expected: Hobbs won by ~17,000 votes (~0.67%)")
    print(f"  Actual margin: {abs(d['dem_votes'] - d['rep_votes']):,} votes")
else:
    print("\nNo ARIZONA statewide entry found")
