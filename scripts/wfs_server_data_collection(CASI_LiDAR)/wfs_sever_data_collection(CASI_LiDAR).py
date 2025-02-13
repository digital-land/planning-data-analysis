import requests
import xml.etree.ElementTree as ET
import geopandas as gpd

# Step 1: GetCapabilities - Fetch and store available layers
capabilities_url = "https://environment.data.gov.uk/spatialdata/casi-and-lidar-habitat-map/wfs?service=WFS&request=GetCapabilities&version=2.0.0"

response = requests.get(capabilities_url)
if response.status_code == 200:
    # Parse the XML response
    root = ET.fromstring(response.text)
    
    # Find all layers (FeatureType Name tags)
    namespaces = {'wfs': 'http://www.opengis.net/wfs/2.0'}
    layers = [
        elem.text for elem in root.findall(".//{http://www.opengis.net/wfs/2.0}FeatureType/{http://www.opengis.net/wfs/2.0}Name", namespaces)
    ]
    
    # Print the list of layers
    print("Available layers:")
    for layer in layers:
        print(layer)
else:
    print(f"Error fetching capabilities: {response.status_code} - {response.text}")
    layers = []  # Set to empty list if fetching fails

# Step 2: Iterate through each layer and fetch data
wfs_url = "https://environment.data.gov.uk/spatialdata/casi-and-lidar-habitat-map/wfs"

for layer_name in layers:
    print(f"\nProcessing layer: {layer_name}")
    
    # Specify parameters for the layer
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": layer_name,  # Use the current layer name
        "outputFormat": "application/json",  # Ensure JSON format
    }
    
    # Fetch data
    r = requests.get(wfs_url, params=params)
    
    if r.status_code == 200:
        try:
            response_json = r.json()  # Parse JSON
            data = gpd.GeoDataFrame.from_features(response_json["features"], crs="EPSG:3067")
            
            # Display and process data
            print(data.head())
            print(f"CRS: {data.crs}")
            
            # Save to file
            output_file = f"{layer_name.replace(':', '_')}.gpkg"
            data.to_file(output_file, driver="GPKG")
            print(f"Layer '{layer_name}' saved to '{output_file}'")
        except Exception as e:
            print(f"Error processing layer '{layer_name}': {e}")
    else:
        print(f"Error fetching layer '{layer_name}': {r.status_code} - {r.text}")
