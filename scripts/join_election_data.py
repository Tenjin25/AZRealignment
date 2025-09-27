import os
import pandas as pd
import geopandas as gpd

# Paths
geojson_path = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\GeoJSONs\tl_2020_04_vtd20.geojson"
csv_path = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\County_Data\20201103__az__general__precinct.csv"
output_path = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\GeoJSONs\tl_2020_04_vtd20_joined.geojson"

# Load precinct GeoJSON
gdf = gpd.read_file(geojson_path)

# Load election data
df = pd.read_csv(csv_path)

# Normalize precinct names for join
def normalize(name):
    return str(name).strip().upper().replace(" ", "").replace("-", "")

gdf['PRECINCT_NORM'] = gdf['PRECINCT'].apply(normalize)
df['PRECINCT_NORM'] = df['precinct'].apply(normalize)

# Merge on normalized precinct name
gdf_joined = gdf.merge(df, on='PRECINCT_NORM', how='left')

# Drop helper column if desired
gdf_joined = gdf_joined.drop(columns=['PRECINCT_NORM'])

# Save to new GeoJSON
gdf_joined.to_file(output_path, driver="GeoJSON")
print(f"Joined data saved to {output_path}")
