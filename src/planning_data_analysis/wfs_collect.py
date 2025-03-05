import os
import xml.etree.ElementTree as ET

import geopandas as gpd
import requests


def get_wfs_capabilities(capabilities_url):
    """
    Fetch and parse WFS GetCapabilities response to get available layers.

    Parameters:
    ----------
    capabilities_url : str
        URL for the WFS GetCapabilities request

    Returns:
    -------
    list
        List of available layer names
    """
    response = requests.get(capabilities_url)
    if response.status_code == 200:
        # Parse the XML response
        root = ET.fromstring(response.text)

        # Find all layers (FeatureType Name tags)
        namespaces = {"wfs": "http://www.opengis.net/wfs/2.0"}
        layers = [
            elem.text
            for elem in root.findall(
                ".//{http://www.opengis.net/wfs/2.0}FeatureType/{http://www.opengis.net/wfs/2.0}Name",
                namespaces,
            )
        ]

        # Print the list of layers
        print("Available layers:")
        for layer in layers:
            print(layer)
        return layers
    else:
        print(f"Error fetching capabilities: {response.status_code} - {response.text}")
        return []


def collect_wfs_data(wfs_url, layer_name, output_dir):
    """
    Collect data for a specific WFS layer and save it as a GeoPackage.

    Parameters:
    ----------
    wfs_url : str
        Base URL for the WFS service
    layer_name : str
        Name of the layer to collect
    output_dir : str
        Directory to save the output file
    """
    print(f"\nProcessing layer: {layer_name}")

    # Specify parameters for the layer
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": layer_name,
        "outputFormat": "application/json",
    }

    # Fetch data
    r = requests.get(wfs_url, params=params)

    if r.status_code == 200:
        try:
            response_json = r.json()
            data = gpd.GeoDataFrame.from_features(
                response_json["features"], crs="EPSG:3067"
            )

            # Display and process data
            print(data.head())
            print(f"CRS: {data.crs}")

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Save to file
            output_file = os.path.join(
                output_dir, f"{layer_name.replace(':', '_')}.gpkg"
            )
            data.to_file(output_file, driver="GPKG")
            print(f"Layer '{layer_name}' saved to '{output_file}'")
        except Exception as e:
            print(f"Error processing layer '{layer_name}': {e}")
    else:
        print(f"Error fetching layer '{layer_name}': {r.status_code} - {r.text}")


def collect_wfs_layers(capabilities_url, wfs_url, output_dir):
    """
    Collect data from all available WFS layers.

    Parameters:
    ----------
    capabilities_url : str
        URL for the WFS GetCapabilities request
    wfs_url : str
        Base URL for the WFS service
    output_dir : str
        Directory to save the output files
    """
    # Get available layers
    layers = get_wfs_capabilities(capabilities_url)

    if not layers:
        print("No layers available to process.")
        return

    # Process each layer
    for layer_name in layers:
        collect_wfs_data(wfs_url, layer_name, output_dir)
