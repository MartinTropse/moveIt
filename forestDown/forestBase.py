import os
import re
import arcpy
from arcpy import env
import xlwings as xw
import pywintypes
import numpy as np
import pandas as pd

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
    
def create_tableBilaga_1(master_wb, trckObsDf, specObsDf, reportBase):
    
    # Concat the 2 dataframes (track, spec)
    trckObsDf_specObsDf = pd.concat([trckObsDf,specObsDf], ignore_index=True)
    # Remove white spaces from beginning or end of komment column
    # (I did that because of https://superuser.com/questions/727108/get-rid-of-extra-space-in-cell-when-using-text-wrap)
    # But did not really eliminate the white space in the wrapped text column.
    trckObsDf_specObsDf['KOMMENTAR'] = trckObsDf_specObsDf['KOMMENTAR'].str.strip()
    # Create N and E columns.
    # Split the 'Shape' column into two separate columns
    trckObsDf_specObsDf['E'] = trckObsDf_specObsDf['Shape'].apply(lambda x: int(x[0]))
    trckObsDf_specObsDf['N'] = trckObsDf_specObsDf['Shape'].apply(lambda x: int(x[1]))
    # Sort based on date-time
    # Create datetime column for sorting
    trckObsDf_specObsDf['DATUM'] = trckObsDf_specObsDf['DATUM'].astype(str)
    trckObsDf_specObsDf['DATUM'] = trckObsDf_specObsDf['DATUM'].str.split('T').str[0]
    trckObsDf_specObsDf['datetime'] = pd.to_datetime(trckObsDf_specObsDf['DATUM'] + ' ' + trckObsDf_specObsDf['TID'])
    trckObsDf_specObsDf_sorted = trckObsDf_specObsDf.sort_values(by='datetime')
    # Drop the collumns that are not needed.
    columns_of_interest = ['OBJECTID', 'DATUM', 'TID', 'N', 'E', 'TYP_AV_OBS', 'ART', 'KON', 'KOMMENTAR']
    trckObsDf_specObsDf_sorted = trckObsDf_specObsDf_sorted.drop(
            columns=[col for col in trckObsDf_specObsDf_sorted.columns if col not in columns_of_interest]
            )
    # Change the date format from 2022-05-15 to 15/5 2022 for example
    trckObsDf_specObsDf_sorted['DATUM'] = pd.to_datetime(trckObsDf_specObsDf_sorted['DATUM'])
    trckObsDf_specObsDf_sorted['DATUM'] = trckObsDf_specObsDf_sorted['DATUM'].dt.strftime('%d/%m %Y')
    # Rename the columns to match the report table.
    trckObsDf_specObsDf_sorted = trckObsDf_specObsDf_sorted.rename(columns={
        "OBJECTID": "ID",
        "DATUM": "Datum",
        "TID": "Tid",
        "TYP_AV_OBS" : "Obstyp",
        "ART": "Art",
        "KON": "Kön",
        "KOMMENTAR": "Kommentar"
        })
    # Reorder the columns as they should be based on the report template.
    column_order = ['ID', 'Datum', 'Tid', 'N', 'E', 'Obstyp', 'Art', 'Kön', 'Kommentar']
    trckObsDf_specObsDf_sorted = trckObsDf_specObsDf_sorted[column_order]
    # Break the df into chunks
    num_all_chunks , final_table_chunks = reportBase.break_df_into_chunks(trckObsDf_specObsDf_sorted, 30, 35)
    # xlwings stuff below.
    for chunk_num, chunk in enumerate(final_table_chunks):
        # xlwings stuff below, make the table exactly as we want it.
        try:
            sheet = master_wb.sheets[f'Bilaga_1_{chunk_num + 1}'] # Check if sheet already exists
            # We need to delete it, because during development,
            # if i kept writing stuff on the sheet that already exists
            # then the values were changing. 
            sheet.delete() # If it exists delete it.
            sheet = master_wb.sheets.add(f'Bilaga_1_{chunk_num + 1}', after=master_wb.sheets[-1]) # And add it again empty.
        except pywintypes.com_error: # if the above try throws a com_error.
            sheet = master_wb.sheets.add(f'Bilaga_1_{chunk_num + 1}', after=master_wb.sheets[-1]) # Or add sheet as last sheet.
        # Add the final_table to the wb_master
        sheet.range('A1').value = chunk
        # Delete the index of the df from the wb_master
        sheet.range('A:A').api.Delete()
        # Format the table in the xlsx, adjust column width 
        sheet.api.Cells.Select()
        sheet.api.Cells.ColumnWidth = 10 # A value that is big enough? The user can change that manually?
        # Add cell borders.
        # Find the last row with data.
        last_row = sheet.range('A1').expand('down').last_cell.row
        last_column = sheet.range('A1').expand('right').last_cell.column
        data_range = sheet.range((1, 1), (last_row, last_column))
        data_range.api.Borders.Weight = 2
        # Center all cells Horizontal center
        data_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter
        # Center all cells Vertical center
        data_range.api.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter
        # Set font size to 9.
        data_range.api.Font.Size = 9
        # Set font name to Arial
        data_range.api.Font.Name = "Arial"
        # Change the fill color of the header cell to gray && make the text bold.
        first_row_range = sheet.range((1, 1), (1, last_column))
        first_row_range.api.Interior.Color = 13882323  # RGB color code for gray
        first_row_range.api.Font.Bold = True # Bold header.
        first_row_range.api.Cells.RowHeight = 20
        first_row_range.api.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter
        first_row_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignLeft
        # Change width of ID col.
        first_col_range = sheet.range((1, 1), (last_row, 1))
        first_col_range.api.Cells.ColumnWidth = 4
        # Change width of Kommentar col.
        last_col_range = sheet.range((1, last_column), (last_row, last_column))
        last_col_range.api.Cells.WrapText = True # Enable text wrapping
        last_col_range.api.Cells.ColumnWidth = 20
        last_col_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignLeft # Horizontal allign comment to left.
        # Change width of Obstyp col.
        obstyp_col_range = sheet.range((1, last_column-3), (last_row, last_column-3))
        obstyp_col_range.api.Cells.ColumnWidth = 14
        # Change width of Tid col.
        tid_col_range = sheet.range((1, last_column-6), (last_row, last_column-6))
        tid_col_range.api.Cells.ColumnWidth = 5
    master_wb.save()  