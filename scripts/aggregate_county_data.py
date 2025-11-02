import os
import pandas as pd
import re
import json
from pathlib import Path

# Paths
county_data_dir = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\County_Data"
output_file = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\az_county_election_results.json"
categorization_file = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\categorization_system.json"

# Arizona counties for normalization
az_counties = [
    'Apache', 'Cochise', 'Coconino', 'Gila', 'Graham', 'Greenlee',
    'La Paz', 'Maricopa', 'Mohave', 'Navajo', 'Pima', 'Pinal',
    'Santa Cruz', 'Yavapai', 'Yuma'
]

def load_categorization_system():
    """Load the categorization system from JSON"""
    try:
        with open(categorization_file, 'r') as f:
            data = json.load(f)
            return data['categorization_system']['competitiveness_scale']
    except Exception as e:
        print(f"Warning: Could not load categorization system: {e}")
        return None

def get_competitiveness_category(margin_pct, winner):
    """Get competitiveness category based on margin and winner"""
    categorization = load_categorization_system()
    if not categorization:
        return None, None
    
    margin_pct = abs(margin_pct)
    
    # Tossup check
    if margin_pct < 0.5:
        return "Tossup", "#f7f7f7"
    
    # Get appropriate scale
    scale = categorization.get('Republican' if winner == 'REP' else 'Democratic', [])
    
    # Find matching category
    for category in scale:
        min_val = category.get('threshold_min', 0)
        max_val = category.get('threshold_max')
        
        if max_val is None:  # Annihilation (40%+)
            if margin_pct >= min_val:
                return f"{category['category']} {winner}", category['color']
        else:
            if min_val <= margin_pct < max_val:
                return f"{category['category']} {winner}", category['color']
    
    return None, None

def normalize_county_name(name):
    """Normalize county names for consistency"""
    if pd.isna(name):
        return None
    name = str(name).strip()
    # Remove 'County' suffix if present
    name = re.sub(r'\s+County$', '', name, flags=re.IGNORECASE)
    # Standardize La Paz
    name = re.sub(r'La\s*Paz', 'La Paz', name, flags=re.IGNORECASE)
    return name.title()

def extract_year_from_filename(filename):
    """Extract year from filename like '20001107__az__general.csv'"""
    match = re.match(r'(\d{4})\d{4}__az__general', filename)
    if match:
        return int(match.group(1))
    return None

def is_statewide_office(office_name):
    """
    Check if an office is a statewide election in Arizona.
    Includes: President, US Senate, Governor, Secretary of State, Attorney General,
    Treasurer, Superintendent of Public Instruction, State Mine Inspector, Corporation Commission.
    """
    if pd.isna(office_name):
        return False
    
    office_lower = str(office_name).lower()
    statewide_keywords = [
        'president', 'presidential',
        'u.s. senate', 'us senate', 'united states senator', 'u.s. senator', 'senator',
        'governor',
        'secretary of state',
        'attorney general',
        'treasurer',
        'superintendent of public instruction', 'superintendent',
        'state mine inspector', 'mine inspector',
        'corporation commission', 'corporation commissioner'
    ]
    
    return any(keyword in office_lower for keyword in statewide_keywords)

def get_office_category(office_name):
    """Categorize office type for nested structure"""
    office_lower = office_name.lower()
    
    if 'president' in office_lower:
        return 'presidential'
    elif 'senate' in office_lower or 'senator' in office_lower:
        return 'us_senate'
    elif 'governor' in office_lower:
        return 'governor'
    elif 'secretary of state' in office_lower:
        return 'secretary_of_state'
    elif 'attorney general' in office_lower:
        return 'attorney_general'
    elif 'treasurer' in office_lower:
        return 'treasurer'
    elif 'superintendent' in office_lower:
        return 'superintendent'
    elif 'mine inspector' in office_lower:
        return 'mine_inspector'
    elif 'corporation commission' in office_lower:
        return 'corporation_commission'
    else:
        return 'other'

def aggregate_county_level(df, year):
    """Aggregate precinct-level data to county level with nested structure"""
    if 'county' not in df.columns:
        return None
    
    # Filter for statewide offices only
    if 'office' in df.columns:
        df = df[df['office'].apply(is_statewide_office)]
        if df.empty:
            return None
    
    # Special handling for 2018: county names are in 'precinct' column
    if year == 2018 and 'precinct' in df.columns:
        # Check if first county value is "Arizona" (indicating county names are in precinct column)
        if df['county'].iloc[0] == 'Arizona':
            df['county'] = df['precinct']
    
    # Normalize county names
    df['county'] = df['county'].apply(normalize_county_name)
    
    # Filter out TOTAL rows (statewide already calculated separately)
    df = df[df['county'] != 'Total']
    
    # Group by county and office, sum votes
    grouped = df.groupby(['county', 'office', 'party']).agg({
        'votes': 'sum'
    }).reset_index()
    
    # Get candidate names if available
    candidate_map = {}
    if 'candidate' in df.columns:
        for _, row in df.iterrows():
            key = (row['office'], row['party'])
            if key not in candidate_map and not pd.isna(row.get('candidate')):
                candidate_map[key] = row['candidate']
    
    # Build nested structure
    result = {}
    
    for office in grouped['office'].unique():
        office_data = grouped[grouped['office'] == office]
        office_category = get_office_category(office)
        office_key = office.lower().replace(' ', '_').replace('.', '').replace(',', '')
        contest_key = f"{office_key}_{year}"
        
        # Normalize office names for display
        display_name = office
        if office.lower() in ['president', 'president and vice president of the united states']:
            display_name = 'US President'
        elif 'u.s. senate' in office.lower() or 'us senate' in office.lower() or office.lower() == 'senator':
            display_name = 'US Senate'
        
        if office_category not in result:
            result[office_category] = {}
        
        result[office_category][contest_key] = {
            'contest_name': display_name,
            'results': {}
        }
        
        for county in office_data['county'].unique():
            if pd.isna(county):
                continue
            
            county_office_data = office_data[office_data['county'] == county]
            
            # Get votes by party (handle potential data issues)
            try:
                dem_votes = int(float(county_office_data[county_office_data['party'] == 'DEM']['votes'].sum())) if 'DEM' in county_office_data['party'].values else 0
                rep_votes = int(float(county_office_data[county_office_data['party'] == 'REP']['votes'].sum())) if 'REP' in county_office_data['party'].values else 0
                other_votes = int(float(county_office_data[~county_office_data['party'].isin(['DEM', 'REP'])]['votes'].sum()))
                total_votes = int(float(county_office_data['votes'].sum()))
            except (ValueError, OverflowError):
                # Skip counties with corrupted vote data
                continue
            two_party_total = dem_votes + rep_votes
            
            # Calculate margin and competitiveness
            if two_party_total > 0:
                margin = abs(rep_votes - dem_votes)
                margin_pct = round((margin / two_party_total) * 100, 2)
                winner = 'REP' if rep_votes > dem_votes else 'DEM'
                competitiveness_cat, color = get_competitiveness_category(margin_pct, winner)
                
                # Parse competitiveness category
                if competitiveness_cat:
                    parts = competitiveness_cat.split(' ')
                    category = parts[0] if len(parts) > 0 else 'Unknown'
                    party = parts[1] if len(parts) > 1 else winner
                    code = f"{party[0]}_{category.upper()}"
                else:
                    category = 'Unknown'
                    party = winner
                    code = 'UNKNOWN'
                    color = '#cccccc'
            else:
                margin = 0
                margin_pct = 0
                winner = None
                category = 'No Data'
                party = None
                code = 'NO_DATA'
                color = '#cccccc'
            
            # Get candidate names
            dem_candidate = candidate_map.get((office, 'DEM'), 'Unknown')
            rep_candidate = candidate_map.get((office, 'REP'), 'Unknown')
            
            result[office_category][contest_key]['results'][county.upper()] = {
                'county': county.upper(),
                'contest': office,
                'year': str(year),
                'dem_candidate': dem_candidate,
                'rep_candidate': rep_candidate,
                'dem_votes': dem_votes,
                'rep_votes': rep_votes,
                'other_votes': other_votes,
                'total_votes': total_votes,
                'two_party_total': two_party_total,
                'margin': margin,
                'margin_pct': margin_pct,
                'winner': winner,
                'competitiveness': {
                    'category': category,
                    'party': party,
                    'code': code,
                    'color': color
                }
            }
    
    return result

def merge_year_data(existing_data, new_data):
    """Merge new county data into existing year data"""
    if not existing_data:
        return new_data
    
    for office_cat, contests in new_data.items():
        if office_cat not in existing_data:
            existing_data[office_cat] = contests
        else:
            for contest_key, contest_data in contests.items():
                if contest_key not in existing_data[office_cat]:
                    existing_data[office_cat][contest_key] = contest_data
                else:
                    # Merge results from multiple files (e.g., 2024 county-specific files)
                    existing_data[office_cat][contest_key]['results'].update(contest_data['results'])
    
    return existing_data

def main():
    results_by_year = {}
    
    # Process each CSV file
    for filename in sorted(os.listdir(county_data_dir)):
        if not filename.endswith('.csv'):
            continue
        
        filepath = os.path.join(county_data_dir, filename)
        year = extract_year_from_filename(filename)
        
        if year is None:
            print(f"Skipping {filename} - couldn't extract year")
            continue
        
        print(f"Processing {filename} (Year: {year})...")
        
        try:
            df = pd.read_csv(filepath, low_memory=False)
            
            # Convert votes column to numeric (handles string values)
            if 'votes' in df.columns:
                df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
            
            # Filter for statewide offices only
            if 'office' in df.columns:
                df = df[df['office'].apply(is_statewide_office)]
                if df.empty:
                    print(f"  No statewide elections found in {filename}")
                    continue
            
            # Aggregate to county level
            year_data = aggregate_county_level(df, year)
            
            if year_data:
                # Merge with existing data for this year (handles multiple files per year)
                year_str = str(year)
                if year_str in results_by_year:
                    results_by_year[year_str] = merge_year_data(results_by_year[year_str], year_data)
                else:
                    results_by_year[year_str] = year_data
                
                # Count contests and counties
                total_contests = sum(len(contests) for contests in year_data.values())
                counties_set = set()
                for office_type in year_data.values():
                    for contest in office_type.values():
                        counties_set.update(contest['results'].keys())
                
                print(f"  ✓ Aggregated {total_contests} contests across {len(counties_set)} counties")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Recalculate statewide ARIZONA totals from all counties
    for year_str, year_data in results_by_year.items():
        for office_cat, contests in year_data.items():
            for contest_key, contest_data in contests.items():
                results = contest_data['results']
                
                # Sum votes from all actual counties (excluding ARIZONA if it exists)
                dem_total = 0
                rep_total = 0
                other_total = 0
                
                for county, county_data in results.items():
                    if county != 'ARIZONA':
                        dem_total += county_data['dem_votes']
                        rep_total += county_data['rep_votes']
                        other_total += county_data['other_votes']
                
                total_votes = dem_total + rep_total + other_total
                two_party_total = dem_total + rep_total
                
                if two_party_total > 0:
                    margin = abs(rep_total - dem_total)
                    margin_pct = round((margin / two_party_total) * 100, 2)
                    winner = 'REP' if rep_total > dem_total else 'DEM'
                    competitiveness_cat, color = get_competitiveness_category(margin_pct, winner)
                    
                    if competitiveness_cat:
                        parts = competitiveness_cat.split(' ')
                        category = parts[0] if len(parts) > 0 else 'Unknown'
                        party = parts[1] if len(parts) > 1 else winner
                        code = f"{party[0]}_{category.upper()}"
                    else:
                        category = 'Unknown'
                        party = winner
                        code = 'UNKNOWN'
                        color = '#cccccc'
                    
                    # Update or create ARIZONA statewide entry
                    results['ARIZONA'] = {
                        'county': 'ARIZONA',
                        'contest': contest_data['contest_name'],
                        'year': year_str,
                        'dem_candidate': results.get(list(results.keys())[0], {}).get('dem_candidate', 'Unknown') if results else 'Unknown',
                        'rep_candidate': results.get(list(results.keys())[0], {}).get('rep_candidate', 'Unknown') if results else 'Unknown',
                        'dem_votes': dem_total,
                        'rep_votes': rep_total,
                        'other_votes': other_total,
                        'total_votes': total_votes,
                        'two_party_total': two_party_total,
                        'margin': margin,
                        'margin_pct': margin_pct,
                        'winner': winner,
                        'competitiveness': {
                            'category': category,
                            'party': party,
                            'code': code,
                            'color': color
                        }
                    }
    
    # Save nested JSON structure
    if results_by_year:
        output_data = {
            'results_by_year': results_by_year
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✓ Aggregated data saved to: {output_file}")
        print(f"  Years covered: {sorted(results_by_year.keys())}")
        print(f"  Total contests: {sum(sum(len(contests) for contests in year_data.values()) for year_data in results_by_year.values())}")
    else:
        print("No data to aggregate!")

if __name__ == "__main__":
    main()
