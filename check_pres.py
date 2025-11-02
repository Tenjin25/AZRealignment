import json

data = json.load(open('Data/az_county_election_results.json'))

print("Presidential contest names:")
for year in ['2000', '2004', '2008', '2012', '2016', '2020', '2024']:
    if year in data['results_by_year'] and 'presidential' in data['results_by_year'][year]:
        pres_data = data['results_by_year'][year]['presidential']
        contest_key = list(pres_data.keys())[0]
        contest_name = pres_data[contest_key]['contest_name']
        print(f"{year}: '{contest_name}'")
