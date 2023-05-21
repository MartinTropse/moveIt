import os
import re
import arcpy
from arcpy import env

def eagleAreamap(prjPath, prjCode, xDim=1.1, yDim=1.1, dpi=300):
    gdbPaths = []
    for bDir, sDir, mFiles in os.walk(prjPath):
        for folder in sDir:
            if hasattr(re.search(f"{prjCode}.+\.gdb$", folder), "group"):
                gdbPaths.append(os.path.join(bDir, folder))

    layerPaths = []

    for aGdb in gdbPaths:
        arcpy.env.workspace = aGdb
        datasets = arcpy.ListDatasets(feature_type="feature")
        datasets = [""] + datasets if datasets is not None else []
        for ds in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                layerPaths.append(os.path.join(arcpy.env.workspace, ds, fc))

    # Identify specific layers.
    AreaRgx = "(?i).+\.gdb.+projekto.+"
    BuffRgx = "(?i).+\.gdb.+buff.+"

    AreaGdb = [i for i in layerPaths if re.search(AreaRgx, i)][0]
    BuffGdb = [i for i in layerPaths if re.search(BuffRgx, i)][0]
    projAreaList = [AreaGdb, BuffGdb]

    aprx_path = os.path.join(prjPath, "blank.aprx")
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    m = aprx.listMaps("Map")[0]

    xmax = 0
    xmin = 1000000000
    ymax = 0
    ymin = 1000000000

    for gdbLayer in projAreaList:
        gdbPath, layer = os.path.split(gdbLayer)
        fldPath = os.path.split(gdbPath)
        lyrxExp = layer + ".lyrx"
        tempLayer = arcpy.MakeFeatureLayer_management(gdbLayer, layer)
        arcpy.env.workspace = fldPath[0]
        arcpy.management.SaveToLayerFile(layer, lyrxExp)
        lyrxLayer = arcpy.mp.LayerFile(os.path.join(fldPath[0], lyrxExp))
        m.addLayer(lyrxLayer)
        desc = arcpy.Describe(tempLayer)
        extent = desc.extent
        if extent.XMax > xmax:
            xmax = extent.XMax
        if extent.XMin < xmin:
            xmin = extent.XMin
        if extent.YMax > ymax:
            ymax = extent.YMax
        if extent.YMin < ymin:
            ymin = extent.YMin

    buffLyr = m.listLayers("JPN0021_buff3km")[0]
    buffLyr.name = "3 km buffertzon"

    projLyr = m.listLayers("Projektomrade2")[0]
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

    # Set the extent of the exported map
    extent.YMax = ymax + (ymax - ymin) * yDim
    extent.XMax = xmax + (xmax - xmin) * xDim
    extent.YMin = ymin - (ymax - ymin) * yDim
    extent.XMin = xmin - (xmax - xmin) * xDim

    layout = aprx.listLayouts("Kartmall - Rapportanpassad fyrkantig")[0]
    map_frame = layout.listElements("MAPFRAME_ELEMENT", "braveNewFrame")[0]

    lay_legend = layout.listElements("legend_element", "*")[0]
    lay_legend.items[0]

    map_frame.camera.setExtent(extent)
    output_path = os.path.join(prjPath, (prjCode + "_SurveyAreaMap.jpg"))

    layout.exportToJPEG(output_path, resolution = dpi)
    aprx.saveACopy(os.path.join(prjPath, prjCode + "_SurveyAreaMap.aprx"))
    print(f"Copied map image and ArcGIS-projekt file to\n{output_path}")
    return output_path



whiteTail = [
    "och havsörn",
    "havs- och",
    ", men i förekommande fall även havsörn",
    "Havsörn är också upptagen i EU.+",
    "och.+observationer av havsörn\.", 
    "Även havsörnen är upptagen i EU:s fågeldirektiv.+",
    "Havsörnen söker sin föda i första hand vid.+",
    "Havsörnsparen lever i livslånga förhållanden.+",
    "Häckande havsörnar i södra och mellersta.+",
    "Efter att tidigare ha varit försvunnen i stora delar av landet häckar havsörnen.+",
    "Enligt den europeiska fyndstatistiken har betydligt fler havsörnar.+",
    "/Projekt Havsörn",
    "resp. Havsörn.",
    "För havsörn är det däremot rimligt.+"
]


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