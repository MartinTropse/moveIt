import time
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from zipfile import ZipFile
import os
from pathlib import Path

# Functions that downloads the layers from a specfied webmap. Downloads group layers and layers to individual
# file geodatabases by default (can be changed to different format). Line 10-70 just defines the function,

def downloadWebmap(map_title, map_owner, exprt_path):
    exprt_path = Path(exprt_path)
    exprt_path = exprt_path.joinpath(map_title)
    if not os.path.exists(exprt_path):
        os.mkdir(exprt_path)
    print(f"Downloading layers from {map_title}")
    time.sleep(1)
    print("\nLayers found in the webmap:")
    PortalUrl = "https://calluna.maps.arcgis.com/home/content.html?"
    gis = GIS("Pro")
    # Search for webmap - this returns a list.
    web_map_search = gis.content.search(
        query=f"title:{map_title} AND owner:{map_owner}", item_type="Web Map"
    )
    # Create a WebMap from the 1st item on the list:
    web_map = WebMap(web_map_search[0])

    layer_list_webMap = []
    for layer in web_map.layers:
        layer_list_webMap.append(layer)
        print(layer["title"], "---", layer["layerType"])

    layers_itemId_list_webmap = []
    layers_name_list_webmap = []

    for layer in layer_list_webMap:
        if layer["layerType"] == "ArcGISFeatureLayer":
            try:
                layers_itemId_list_webmap.append(layer["itemId"])
            except KeyError as e:
                print(
                    f"KeyError: {e} was not found in "
                    + layer["title"]
                    + " skipping to next layer"
                )
                continue
            layers_name_list_webmap.append(layer["title"])
        if layer["layerType"] == "GroupLayer":
            for sub_layer in layer["layers"]:
                print(sub_layer["title"])
                layers_name_list_webmap.append(sub_layer["title"])
                layers_itemId_list_webmap.append(sub_layer["itemId"])

    layers_itemId_list_webmap_unique = set(layers_itemId_list_webmap)

    print(layers_itemId_list_webmap_unique)

    for itemId in layers_itemId_list_webmap_unique:
        print(itemId)
        item = gis.content.get(itemId)
        print(f"\nDownloading layer: {item.name}")
        zip_path = exprt_path.joinpath(f"TEMP_{item.name}.zip")
        try:
            result = item.export("TEMP_" + item.title, "File Geodatabase", wait=True)
        except KeyError as e:
            if str(e) == "'exportItemId'":
                print(f"Layer {item.title} does not allow export. Skipping to next layer")
                continue
            else:
                print("An error was raised")
                raise
        result.download(save_path=exprt_path)
        try:
            zip_file = ZipFile(zip_path)
        except Exception as e:
            print("An error was raised, item.name did not match zipfile, attempting with item.title.")
            zip_path = exprt_path.joinpath(f"TEMP_{item.title}.zip")
            zip_file = ZipFile(zip_path)
        zip_file.extractall(path=exprt_path.joinpath(item.name))
        del zip_file
        result.delete()

    print(
        f"\nDownload of {map_title} is complete! \nExport data is located here: {exprt_path}"
    )
    for aFile in os.listdir(exprt_path):
        if aFile.startswith("TEMP_"):
            os.remove(exprt_path.joinpath(aFile))
    # Rename gdbs from this strange id looking name to the name of its parent folder
    # Loop through all subfolders within the parent folder
    for bDir, sDir, aFile in os.walk(exprt_path):
        if str(bDir).endswith(".gdb"):
            head, tail = os.path.split(bDir)
            headSec, tailSec = os.path.split(head)
            newGdbName = tailSec + ".gdb"
            newGdbPath = os.path.join(head, newGdbName)
            os.rename(bDir, newGdbPath)