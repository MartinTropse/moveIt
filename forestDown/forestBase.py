import os
import re
import arcpy
from arcpy import env

def forestAreamap(downPath, prjCode, expand_factor, move_left_factor, dpi = 300):
    # Loop that goes through the download folders and identifies the geodatabases.
    gdbPaths = []
    prjCode2 = prjCode[:-1]

    for bDir, sDir, mFiles in os.walk(downPath):
        for folder in sDir:
            try:
                if (hasattr(re.search(f"{prjCode}.+\.gdb$", folder), "group")):
                    gdbPaths.append(os.path.join(bDir, folder))
                elif (hasattr(re.search(f"{prjCode2}.+\.gdb$", folder), "group")):
                    gdbPaths.append(os.path.join(bDir, folder))
            except Exception as e:
                print(e)

    layerPaths = []

    for aGdb in gdbPaths:
        arcpy.env.workspace = aGdb
        datasets = arcpy.ListDatasets(feature_type="feature")
        datasets = [""] + datasets if datasets is not None else []
        for ds in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                layerPaths.append(os.path.join(arcpy.env.workspace, ds, fc))

    # Identify specific layers.
    AreaRgx = "(?i).+\.gdb.+projekt(om| om|_om).+"
    BuffRgx = "(?i).+\.gdb.+buff(.+1|1)"

    AreaGdb = [i for i in layerPaths if re.search(AreaRgx, i)][0]
    BuffGdb = [i for i in layerPaths if re.search(BuffRgx, i)][0]
    projAreaList = [AreaGdb, BuffGdb]

    aprx_path = os.path.join(downPath, "forestBlank.aprx")
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    m = aprx.listMaps("Map")[0]
    s = aprx.listMaps("Small")[0]

    for gdbLyr in projAreaList:
        arcpy.env.workspace = os.path.split(gdbLyr)[0]
        featureLyr = os.path.basename(gdbLyr)
        arcpy.MakeFeatureLayer_management(gdbLyr, featureLyr)
        gdbPath, layer = os.path.split(gdbLyr) 
        lyrxName = layer + ".lyrx"
        lyrxPath = os.path.join(downPath, lyrxName)
        arcpy.management.SaveToLayerFile(layer, lyrxPath)
        lyrxLayer = arcpy.mp.LayerFile(lyrxPath)
        m.addLayer(lyrxLayer)
        s.addLayer(lyrxLayer)
        if bool(re.search("(?i)buff.+", featureLyr)):#Search name string containing habitat
            arcpy.MakeFeatureLayer_management(gdbLyr, featureLyr)
            #Section that sets and adjust the map extent (via the expand_factor and move_left_factor variables), with the project area as a startpoint
            project_area_extentFar = arcpy.Describe(featureLyr).extent #This becomes the map extent for the overview map
            project_area_extentClose = arcpy.Describe(featureLyr).extent #This becomes the map extent for the project area map
            height = project_area_extentClose.height  
            width = project_area_extentClose.width
            project_area_extentClose.XMin -= width * expand_factor
            project_area_extentClose.YMin -= height * expand_factor
            project_area_extentClose.XMax += width * expand_factor 
            project_area_extentClose.YMax += height * expand_factor
            # Move to the left
            project_area_extentClose.XMin += width * move_left_factor
            project_area_extentClose.XMax += width * move_left_factor
            #Set the map extent for smaller overview map
            project_area_extentFar.XMin -= width * 16 #The set expand factor for the overview map
            project_area_extentFar.YMin -= height * 16
            project_area_extentFar.XMax += width * 16
            project_area_extentFar.YMax += height * 16

    BuffGdb = os.path.normpath(BuffGdb)
    buffName = BuffGdb.split(os.sep)[len(BuffGdb.split(os.sep)) - 1]

    AreaGdb = os.path.normpath(AreaGdb)
    areaName = AreaGdb.split(os.sep)[len(AreaGdb.split(os.sep)) - 1]

    buffLyr = m.listLayers(buffName)[0]
    buffLyr.name = "1 km buffertzon"

    projLyr = m.listLayers(areaName)[0]
    projLyr.name = "Projektområde"

    proj_cim = projLyr.getDefinition("V3")
    buff_cim = buffLyr.getDefinition("V3")

    proj_cim.renderer.symbol.symbol.symbolLayers[0].color.values = [255, 0, 197, 100]
    proj_cim.renderer.symbol.symbol.symbolLayers[0].width = 1.0
    # proj_cim.renderer.symbol.symbol.symbolLayers[1].color.values = [255, 0, 197, 100]
    proj_cim.renderer.symbol.symbol.symbolLayers[1].enable = "False"
    projLyr.setDefinition(proj_cim)

    buff_cim.renderer.symbol.symbol.symbolLayers[0].width = 1.5
    buff_cim.renderer.symbol.symbol.symbolLayers[0].color.values = [45, 45, 44, 100]
    buff_cim.renderer.symbol.symbol.symbolLayers[1].enable = "False"
    buffLyr.setDefinition(buff_cim)

    layout = aprx.listLayouts("Kartmall - Rapportanpassad fyrkantig")[0]
    map_frame = layout.listElements("MAPFRAME_ELEMENT", "braveNewFrame")[0]
    small_frame = layout.listElements("MAPFRAME_ELEMENT", "smallFrame")[0]

    lay_legend = layout.listElements("legend_element", "*")[0]
    lay_legend.items[0]

    map_frame.camera.setExtent(project_area_extentClose)
    small_frame.camera.setExtent(project_area_extentFar)

    output_path = os.path.join(downPath, (prjCode + "_SurveyAreaMap.jpg"))

    layout.exportToJPEG(output_path, resolution=dpi)
    aprx.saveACopy(os.path.join(downPath, prjCode + "_SurveyAreaMap.aprx"))
    print(f"Copied map image and ArcGIS-projekt file to\n{output_path}")
    return output_path

month_namesDict = {
    'January': 'januari',
    'February': 'februari',
    'March': 'mars',
    'April': 'april',
    'May': 'maj',
    'June': 'juni',
    'July': 'juli',
    'August': 'augusti',
    'September': 'september',
    'October': 'oktober',
    'November': 'november',
    'December': 'december'
}
#Dictionary to convert interge to numeric str
num_dict = {"1":"en",
            "2":"två",
            "3":"tre",
            "4":"fyra",
            "5":"fem",
            "6":"sex",
            "7":"sju",
            "8":"åtta",
            "9":"nio"}

def letter(index):
    if 0 <= index < 26:
        return chr(ord('A') + index)
    else:
        return None  # Handle out-of-range indices

def forestspelplatsMap(downPath, prjCode, expand_factor, dpi):
    """A function that generates a map of mating grounds for forestBirds, using lyrx/aprx file from github repository together with download webmap data from AGOl
    Parameter: PrjCode: String with the project code, downPath: String with the path to the download folder with the AGOL data, expand_factor: Float/integer setting how much map the extent should extend beyond the largest layer, dpi: integer setting the pixel density of the exported map"""
    # Set overwriteOutput to True to overwrite existing data
    arcpy.env.overwriteOutput = True

    # Look through the downloaded folders and locate all gdb-files
    gdbPaths = []
    for bDir, sDir, mFiles in os.walk(downPath):
        for folder in sDir:
            # Search for folders with names containing the specified prjCode and ending with .gdb or .gdb[some_suffix]
            if hasattr(re.search(f"{prjCode}(\.gdb$|.+\.gdb$)", folder), "group"):
                gdbPaths.append(os.path.join(bDir, folder))

    # Goes through and store paths to all layers within the gdb-files
    layerPaths = []
    for aGdb in gdbPaths:
        arcpy.env.workspace = aGdb
        datasets = arcpy.ListDatasets(feature_type="feature")
        datasets = [""] + datasets if datasets is not None else []
        for ds in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                layerPaths.append(os.path.join(arcpy.env.workspace, ds, fc))

    # Define regular expressions to search for specific layer names within the layer paths
    ArtPointRgx = "(?i).+\.gdb.+obspkt.+art"
    ArtGdb = [i for i in layerPaths if re.search(ArtPointRgx, i)][0]

    SparPointRgx = "(?i).+\.gdb.+obspkt.+spar"
    SparGdb = [i for i in layerPaths if re.search(SparPointRgx, i)][0]

    SpelPlatsYtaRgx = "(?i).+\.gdb.+inventering.+yta"
    SpelPlatsGdb = [i for i in layerPaths if re.search(SpelPlatsYtaRgx, i)][0]

    # Define the order of gdb-files to be processed (has some impact on map extent)
    projAreaList = [ArtGdb, SparGdb, SpelPlatsGdb]

    lyrxDown = os.path.join(downPath, "Lyrx")
    lyrxPaths = []

    # Loop to locate and store paths to lyrx-files, used for applying symbology on downloaded layers
    for mDir, sDir, files in os.walk(lyrxDown):
        for file in files:
            # Search for files with .lyrx extension
            if hasattr(re.search("\.lyrx$", file), "group"):
                lyrxPaths.append(os.path.join(mDir, file))

    # Loop through each gdb file in the projAreaList
    for gdbLayr in projAreaList:
        arcpy.env.workspace = os.path.split(gdbLayr)[0]
        featureLyr = os.path.basename(gdbLayr)

        # Section for Obspkt Art layer (loading, applying symbology from lyrx import, exporting new lyrx file to download folder)
        if re.search("(?i).+obspkt.+art", featureLyr): # Search name string matching project layer.
            arcpy.MakeFeatureLayer_management(gdbLayr, featureLyr)
            ArtName = featureLyr
            for lyrSymb in lyrxPaths:
                if re.search("(?i)Obspktart.+\.lyrx", lyrSymb):
                    arcpy.management.ApplySymbologyFromLayer(featureLyr, lyrSymb) # Adds the symbology layer from pre-existing layer to the new layer downloaded from AGOL
                    ArtLyrNew = os.path.join(downPath, ArtName + ".lyrx")
                    arcpy.management.SaveToLayerFile(featureLyr, ArtLyrNew)

        # Section for Obspkt Spar layer (loading, applying symbology from lyrx import, exporting new lyrx file to download folder)
        if re.search("(?i).+obspkt.+spar", featureLyr): # Search name string matching project layer.
            arcpy.MakeFeatureLayer_management(gdbLayr, featureLyr)
            SparName = featureLyr
            for lyrSymb in lyrxPaths:
                if re.search("(?i)Obspktspar.+\.lyrx", lyrSymb):
                    arcpy.management.ApplySymbologyFromLayer(featureLyr, lyrSymb) # Adds the symbology layer from pre-existing layer to the new layer downloaded from AGOL
                    SparLyrNew = os.path.join(downPath, SparName + ".lyrx")
                    arcpy.management.SaveToLayerFile(featureLyr, SparLyrNew)

        # Section for Spelplats layer (loading, applying symbology from lyrx import, exporting new lyrx file to download folder)
        if re.search("(?i).+inventering.+yta", featureLyr): # Search name string matching rovobs punkter layer.
            arcpy.MakeFeatureLayer_management(gdbLayr, featureLyr)
            SpelName = featureLyr
            for lyrSym in lyrxPaths:
                if re.search("(?i)Spelplatsinventering.+\.lyrx", lyrSym):
                    arcpy.management.ApplySymbologyFromLayer(featureLyr, lyrSym) # Adds the symbology layer from pre-existing layer to the new layer downloaded from AGOL
                    SpelLyrNew = os.path.join(downPath, SpelName + ".lyrx")
                    arcpy.management.SaveToLayerFile(featureLyr, SpelLyrNew)

    #Locates the extent of the mating ground, and then expand the project area extent with the set expand_factor 
    for gdbLayr in projAreaList:
        arcpy.env.workspace = os.path.split(gdbLayr)[0]
        featureLyr = os.path.basename(gdbLayr)
        if re.search("(?i).+inventering.+yta", featureLyr):
            project_area_extent = arcpy.Describe(featureLyr).extent
            height = project_area_extent.height
            width = project_area_extent.width
            project_area_extent.XMin -= width * expand_factor
            project_area_extent.YMin -= height * expand_factor
            project_area_extent.XMax += width * expand_factor
            project_area_extent.YMax += height * expand_factor

    # Create a new ArcGIS project
    aprxPath = os.path.join(downPath, "forestBlank.aprx")
    aprx = arcpy.mp.ArcGISProject(aprxPath)
    # Pulls out the map object, which layers will later be sent into.
    m = aprx.listMaps("Spelplats")[0]

    newLyrList = [ArtLyrNew, SparLyrNew, SpelLyrNew]

    # Add each new layer to the map object
    for birdLyrx in newLyrList:
        birdLyrObjct = arcpy.mp.LayerFile(birdLyrx)
        m.addLayer(birdLyrObjct)

    ArtLyr = m.listLayers(ArtName)[0]
    SparLyr = m.listLayers(SparName)[0]
    SpelLyr = m.listLayers(SpelName)[0]

    #nameList = [m.listLayers()[layerIndx].name for layerIndx in range(len(m.listLayers())-1)] # Uncomment to see names and order of added layers.

    #Move the layers in the desired order
    m.moveLayer(SparLyr, ArtLyr, "BEFORE")

    #Rename the layers
    ArtLyr.name = "Observationspunkt"
    SparLyr.name = "Tjäder spillning"
    SpelLyr.name = "Spelplats Tjäder"

    # Use this line to check the order of layers and see that the movement changes became as intended
    # Get the layout and map frame
    layout = aprx.listLayouts("Kartmall - spelplats")[0]
    map_frame = layout.listElements("MAPFRAME_ELEMENT", "braveNewFrame")[0]

    # Zoom out to the specified extent
    map_frame.camera.setExtent(project_area_extent)

    # Set the scale bar width relative to the layout size
    scale_bar = layout.listElements("MAPSURROUND_ELEMENT", "Skalstock vit")[0]

    # Assuming you want the scale bar width to be a certain percentage of the layout width
    scale_bar_percentage = 25  # Adjust this percentage as needed
    scale_bar_width = (layout.pageWidth * scale_bar_percentage) / 100

    scale_bar.elementWidth = scale_bar_width

    # Get the legend element
    legend = layout.listElements("LEGEND_ELEMENT", "Legend")[0]

    # Export the layout to a JPEG file with the specified resolution
    output_jpg_path = os.path.join(downPath, (prjCode + "_spelPlatsmap.jpg"))
    layout.exportToJPEG(output_jpg_path, resolution=dpi)

    # Save a copy of the ArcGIS project
    aprx.saveACopy(os.path.join(downPath, (prjCode + "_spelPlatsmap.aprx")))

    # Clean up resources and return a success message
    del aprx
    return output_jpg_path