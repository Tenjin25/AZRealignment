import json

data = json.load(open('Data/az_county_election_results.json'))
pres_2024 = data['results_by_year']['2024']['presidential']['president_2024']['results']

counties = sorted(pres_2024.keys())
print('2024 President counties:')
print(', '.join(counties))
print(f'\nTotal: {len(counties)} counties/entries')

if 'ARIZONA' in pres_2024:
    arizona = pres_2024['ARIZONA']
    print(f'\nARIZONA statewide:')
    print(f'  Dem: {arizona["dem_votes"]:,}')
    print(f'  Rep: {arizona["rep_votes"]:,}')
    print(f'  Winner: {arizona["winner"]} by {arizona["margin_pct"]:.2f}%')
else:
    print('\nNo ARIZONA statewide entry found')

# Check one specific county
if 'MARICOPA' in pres_2024:
    maricopa = pres_2024['MARICOPA']
    print(f'\nMARICOPA:')
    print(f'  Dem: {maricopa["dem_votes"]:,}')
    print(f'  Rep: {maricopa["rep_votes"]:,}')
