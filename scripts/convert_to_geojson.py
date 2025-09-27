import os
import geopandas as gpd

input_dir = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\VTDs"
output_dir = r"C:\Users\Shama\OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\AZRealignments\Data\GeoJSONs"

os.makedirs(output_dir, exist_ok=True)

for root, dirs, files in os.walk(input_dir):
    for filename in files:
        if filename.lower().endswith('.shp'):
            input_path = os.path.join(root, filename)
            gdf = gpd.read_file(input_path)
            out_name = os.path.splitext(filename)[0] + ".geojson"
            output_path = os.path.join(output_dir, out_name)
            gdf.to_file(output_path, driver="GeoJSON")
            print(f"Converted: {input_path} -> {output_path}")

print("All shapefiles converted to GeoJSON.")
