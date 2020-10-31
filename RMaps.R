library(ggplot2)
library(reshape2)
library(plyr)
library(ggpubr)
library (car)
library(sf)
library(raster)
library(tmap)
library(tmaptools)

ggplot(myMap) + geom_sf(aes(fill = CPUE___))

#tmap /tmaptools

#https://cran.r-project.org/web/packages/tmap/vignettes/tmap-getstarted.html
#https://leaflet-extras.github.io/leaflet-providers/preview/

tm_shape(myMap) + tm_symbols()
data("World")
tm_shape(World) + tm_polygons("HPI")

tmap_mode("view")

tm_shape(World) +
  tm_polygons("HPI")
ttm()



#class(World)
#World
#myMap
#?`tmap-element`

raster::shapefile(spDf, "MyShapefile.shp", overwrite = TRUE)

data(World, metro, rivers, land)

  

tmap_mode("plot")
## tmap mode set to plotting
tm_shape(land) +
  tm_raster("trees", palette = terrain.colors(10)) +
  tm_shape(World) +
  tm_borders("white", lwd = .5) +
  tm_text("iso_a3", size = "AREA") +
  tm_shape(metro) +
  tm_symbols(col = "red", size = "pop2020", scale = .5) +
  tm_legend(show = FALSE)

tmap_mode("view")

tm_shape(World) + 
  tm_polygons(c("HPI", "economy")) +
  tm_facets(sync = TRUE, ncol = 2)

tmap_mode("view")

tmap_mode("plot")
## tmap mode set to plotting

data(NLD_muni)

NLD_muni$perc_men <- NLD_muni$pop_men / NLD_muni$population * 100


tm_shape(NLD_muni) +
  tm_polygons("perc_men", palette = "RdYlBu") +
  tm_facets(by = "province")


tmap_mode("plot")
## tmap mode set to plotting

data(NLD_muni)
tm1 <- tm_shape(NLD_muni) + tm_polygons("population", convert2density = TRUE)
tm2 <- tm_shape(NLD_muni) + tm_bubbles(size = "population")

tmap_arrange(tm1, tm2)
## Legend labels were too wide. Therefore, legend.text.size has been set to 0.27. Increase legend.width (argument of tm_layout) to make the legend wider and therefore the labels larger.
## The legend is too narrow to place all symbol sizes.

tmap_mode("view")
tm_basemap("Stamen.Watercolor") +
  tm_shape(metro) + tm_bubbles(size = "pop2020", col = "red") +
  tm_tiles("Stamen.TonerLabels")

tm_basemap("OpenStreetMap.DE")+
  tm_shape(metro) + tm_symbols(size = "pop2020", col='red', scale=0.5)
  
tmap_mode("plot")
## tmap mode set to plotting

tm_shape(World) +
  tm_polygons("HPI") +
  tm_layout(bg.color = "skyblue", inner.margins = c(0, .02, .02, .02))

tmap_options(bg.color = "black", legend.text.color = "white")

tm_shape(World) +
  tm_polygons("HPI", legend.title = "Happy Planet Index")

tmap_style("classic")
tmap_style("cobalt")
## tmap style set to "classic"
## other available styles are: "white", "gray", "natural", "cobalt", "col_blind", "albatross", "beaver", "bw", "watercolor"

tmap_mode("plot")

tm_shape(World) +
  tm_polygons("HPI", legend.title = "Happy Planet Index")


tmap_options_diff()
## current tmap options (style "classic") that are different from default tmap options (style "white"):
## $sepia.intensity
## [1] 0.7
## 
## $frame.double.line
## [1] TRUE
## 
## $fontfamily
## [1] "serif"
## 
## $compass.type
## [1] "rose"
## 
## $basemaps
## [1] "Esri.WorldTopoMap"
## 
## $basemaps.alpha
## [1] 0.5

# reset the options to the default values
tmap_options_reset()
## tmap options successfully reset


tm <- tm_shape(World) +
  tm_polygons("HPI", legend.title = "Happy Planet Index")

## save an image ("plot" mode)
tmap_save(tm, filename = "world_map.png")

## save as stand-alone HTML file ("view" mode)
tmap_save(tm, filename = "world_map.html")


#It is possible to use tmap in shiny:
tmapOutput("my_tmap")

# in server part
output$my_tmap = renderTmap({
  tm_shape(World) + tm_polygons("HPI", legend.title = "Happy Planet Index")
})


qtm(World, fill = "HPI", fill.pallete = "RdYlGn")

tmap_tip()