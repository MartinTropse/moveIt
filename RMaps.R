library(ggplot2)
library(reshape2)
library(plyr)
library(ggpubr)
library (car)
library(sf)
library(raster)
library(tmap)
library(tmaptools)
library(tidyverse)
library(osmdata)
library(osmplotr)
library(ggmap)

#sp = spatial objects 
#sf = simple objects (~dataframe and geofeatures combined into one object)

#Attempts for creating different background maps in R. 
"""
Used tmap and tmaptools which can create great looking leaflet/HTML maps, but does not enable saving of pictures. 
Might exist other possiblities.

Used the get_map from ggmap to download background image, but was only able to download one type of background map, looks 
so-so. Saw another example with the same map. Investigate if there is a solution?

Attempted the opq() and add_osm_feature() to download parts of the OSM map. Works kind, but I can I reconstruct 
a more complete background map like this? Explore a bit more. OSM is very interesting tool, but does not seem 
suitable for this purpose. Found examples that works but layout is not great. 

########################
Other possibilites: 
Georeference a part of the OSM WSM and use as a background raster.

Download ocean background data from naturalearth, check youtube. Quick look.

Get the google API. Can create nice looking maps
https://www.jessesadler.com/post/geocoding-with-r/
"""
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


###Youtube tutorial covering basics of tmap###
#https://www.youtube.com/watch?v=WsbkVkBLkdQ&ab_channel=EcologicalApplicationsinR

#Function to go between wide and long table
fish_long = spread(df, key = Species, value = Count)

#Replace NA
#df[is.na(df)] = 0
#Create a sum column
#df$Sum=rowSums(df[,c(4:14)])
#Transform dataframe to a simple feature 

dfSpec$ShootLat

newSf = st_as_sf(dfSpec, coords = c("ShootLong","ShootLat"), crs=CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"))

#Create BBox
my_bbox = c(xmin = min(dfSpec$ShootLong),
            xmax = max(dfSpec$ShootLong),
            ymin = min(dfSpec$ShootLat),
            ymax = max(dfSpec$ShootLat))
?extract_osm_objects
available_features()

head(available_tags("natural"))

ocean = extract_osm_objects(key='natural',bbox=my_bbox, sf=T)

madridBB=getbb("Madrid")

q <- getbb("Madrid") %>%
  opq() %>%
  add_osm_feature("amenity", "cinema")

#place=ocean
#name=Indian Ocean

str(q) #query structure
cinema <- osmdata_sf(q)

gotbrg=raster::shapefile("Gotenburg.shp")
gotExt=extent(gotbrg)
  
myCheck=st_as_sf(gotbrg)
extCheck=extent(myCheck)

m <- c(-10, 30, 5, 46)
m <- c(12, 56.5, 13.5, 57.5)

out=as.vector(gotExt)

q <- m %>% 
  opq (timeout = 25*100) %>%
  #add_osm_feature("name", "Mercadona") %>%
  add_osm_feature("natural")

str(q)
superMarket=osmdata_sf(q)

str(superMarket)

tmap_mode("view")
tm_shape(superMarket$osm_polygons)+tm_polygons()

mad_map <- get_map(getbb("Madrid"), maptype = "toner-background")
sad_map <- get_map(m, maptype = "watercolor", source = "stamen")


ggmap(sad_map)

ggmap(sad_map)+ geom_sf(data = cinema$osm_points,
                        inherit.aes = FALSE,
                        colour = "#238443",
                        fill = "#004529",
                        alpha = 0.5,
                        size = 4,
                        shape = 21)+ labs(x="", y="")

m <- c(-10, 30, 5, 46)
q <- m %>% 
  opq (timeout = 25*100) %>%
  add_osm_feature("name", "Mercadona") %>%
  add_osm_feature("shop", "supermarket")

mercadona=osmdata_sf(q)

?ggmap

ggplot(mercadona$osm_points) + 
  geom_sf(colour = "#08519c",
          fill = "#08306b",
          size = 1,
          alpha = 5.,
          shape = 21) +
  theme_void()












