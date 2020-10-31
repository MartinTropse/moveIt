library(ggplot2)
library(reshape2)
library(plyr)
library(ggpubr)
library (car)
library(sf)
library(raster)
library(tmap)
library(tmaptools)
library(tidyverse) #include dplyr

setwd("E:/DataAnalys/OX2_SeasonPatternFish")
#df=read.csv("Kattegatt_FishBits.csv", header = TRUE, sep=',')
df=read.csv("Kattegatt_CPUE_0927 .csv", header = TRUE, sep=',')

levels(df)=c("Quarter 1", "Quarter 4")
o=gsub("1","Quarter 1",df$Quarter)
df$Quarter=gsub("4","Quarter 4",o)

#Exclude 2011 & 2019, which lacks quarter sampling
idY = grep("2010|2012|2013|2014|2015|2016|2017|2018", df$Year)
dfY = df[idY,]

sort(unique(df$Species))

#"Gadus morhua","Pleuronectes platessa","Clupea harengus","Scomber scombrus"


###Report Loop###
specVec=c("Nephrops norvegicus")

id = grep(specVec, dfY$Species)
dfSpec=dfY[id,]
dfSpec$CPUE_number_per_hour

cordDf=data.frame(row.names = seq(1, length(dfSpec$ShootLat)))

cordDf$lon = dfSpec$ShootLong
cordDf$lat = dfSpec$ShootLat

spDf=SpatialPointsDataFrame(coords = cordDf, dfSpec, proj4string = CRS(as.character("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")))
myMap=sf::st_read("E:/DataAnalys/OX2_SeasonPatternFish/SecondShape.shp")

list.files()
depth=raster("DepthKG.tif")


names(myMap)[names(myMap) == "CPUE___"] ="CPUE"

str(myMap)

tmap_mode("plot")

tm_basemap("OpenStreetMap.DE")+
  tm_shape(myMap)+  tm_bubbles(size="CPUE", col="CPUE")+
  tm_tiles("Stamen.TonerLabels")

myMap$F_CPUE = as.factor(myMap$CPUE)  

tm_shape(depth)+ tm_raster(palette = "Blues") +
tm_shape(myMap)+ tm_bubbles(col="CPUE", style = "equal", n = 8)

class(myMap$CPUE)

?tm_bubbles

?tm_raster  
tmaptools::palette_explorer()

head(NLD_muni)
head(myMap)
tm2 <- tm_shape(NLD_muni) + tm_bubbles(size = "population")












for(art in specVec){
  id = grep(art, dfY$Species)
  dfSpec=dfY[id,]
  #Create Decimal depth
  dfSpec$decDepth=round_any(dfSpec$Depth, 10)  
  #Split Data by quarter
  idQ=grep("Quarter 1", dfSpec$Quarter)
  idQ4=grep("Quarter 4", dfSpec$Quarter)
  dfQ1=dfSpec[idQ,]
  dfQ4=dfSpec[idQ4,]
  dfSpec$decDepth=round_any(dfSpec$Depth, 10)
  
  #Summary of CPUE per quarter and decimal depth 
  Q1DecDpt=melt(tapply(dfQ1$CPUE_number_per_hour, dfQ1$decDepth, mean))
  Q1DecDpt$Quarter = rep("Quarter 1",length(Q1DecDpt$Var1))
  Q4DecDpt=melt(tapply(dfQ4$CPUE_number_per_hour, dfQ4$decDepth, mean))
  Q4DecDpt$Quarter = rep("Quarter 4",length(Q4DecDpt$Var1))
  DecDptCPUE=rbind(Q4DecDpt,Q1DecDpt)
  DecDptCPUE$value=as.integer(DecDptCPUE$value)
  
  #Depth Date graph
  x<-paste("2020",substring(dfSpec$DateTime,1,5),sep = "/")
  dfSpec$NewDate= as.Date(x, "%Y/%d/%m")

  #Depth Decimal graph
  pltDQC=ggplot(data=DecDptCPUE, aes(x=as.factor(Var1), y=value, fill=as.factor(value)))
  pltDQC = pltDQC + geom_bar(stat="identity")
  pltDQC = pltDQC + facet_grid(.~Quarter)
  pltDQC = pltDQC + theme_bw(13)+ylab("Mean CPUE")+xlab("Depth")
  pltDQC = pltDQC + theme(legend.title = element_blank())
  pltDQC = pltDQC + ggtitle(paste0(art, ", Mean CPUE by depth"))
  
  pltQ_CPUE2 = ggplot(data=dfSpec, aes(y=CPUE_number_per_hour, x=NewDate, color=as.factor(Quarter)))
  pltQ_CPUE2 = pltQ_CPUE2 + geom_point()
  pltQ_CPUE2 = pltQ_CPUE2 + theme_bw(13)
  pltQ_CPUE2 = pltQ_CPUE2 + xlab("")+ylab("CPUE per hour")+theme(legend.title = element_blank())
  pltQ_CPUE2 = pltQ_CPUE2 + ggtitle(paste0(art, ", Hour CPUE by date and quarter"))
  
  mean_QCPUE=melt(tapply(dfSpec$CPUE_number_per_hour, dfSpec$Quarter, mean), value.name = "M_CPUE")
  sd_QCPUE=melt(tapply(dfSpec$CPUE_number_per_hour, dfSpec$Quarter, sd), value.name = "SD_CPUE")
  mean_QCPUE$SD_CPUE = sd_QCPUE$SD_CPUE
  
  pltQ_CPUE = ggplot(data=dfSpec, aes(x=as.factor(Quarter), y=log(CPUE_number_per_hour), fill=as.factor(Quarter)))
  pltQ_CPUE = pltQ_CPUE+geom_violin(trim = FALSE) + geom_boxplot(width=0.02,fill="white",lwd=0.1) 
  pltQ_CPUE = pltQ_CPUE + theme_bw(13)
  pltQ_CPUE = pltQ_CPUE + theme(legend.title = element_blank())+xlab("")+ylab("LogScale CPUE per hour")
  pltQ_CPUE = pltQ_CPUE + ggtitle(paste0(art, ", Hour CPUE by quarter"))  
  
  #CPUE Longitude
  longiDf=rbind(dfQ1, dfQ4)
  pltLong=ggplot(data=longiDf, aes(x=ShootLong, y=CPUE_number_per_hour, color=Quarter))
  pltLong = pltLong + geom_point(stat="identity")
  pltLong = pltLong + facet_grid(~Quarter)
  pltLong = pltLong + theme_bw(13)+xlab("Longitude")+ylab("CPUE per hour")+theme(legend.position = "none")   
  pltLong = pltLong + ggtitle(paste0(art, ", CPUE by longitude"))
  
  pltLat=ggplot(data=longiDf, aes(x=ShootLat, y=CPUE_number_per_hour, color=Quarter))
  pltLat = pltLat + geom_point(stat="identity")
  pltLat = pltLat + facet_grid(~Quarter)
  pltLat = pltLat + theme_bw(13)+xlab("Lattitude")+ylab("CPUE per hour")+theme(legend.position = "none")
  pltLat = pltLat + ggtitle(paste0(art, ", CPUE by latitude"))
  
  myPdf=ggarrange(pltLong, pltLat, pltDQC, nrow = 1, ncol = 1)
  myPdf2=ggarrange(pltQ_CPUE2, pltQ_CPUE,nrow = 2, ncol = 1)
  
  X=paste0(art,".pdf")
  ggexport(myPdf, myPdf2, filename = X)        
}


#Seperate script to check for species above a certain count and their season ratio. 

specList=sort(unique(df$Species))

#Goes through all species without conditions
for(x in specList){
  artId=grep(x, df$Species)
  artDf = df[artId, ]
  y=length(artDf$CPUE_number_per_hour)
  z=sum(artDf$CPUE_number_per_hour)
  print(x)
  print(paste("Observation count:",y))
  print(paste("Observation sum:",z))
  #Compares the sum of catch per quarter
  q1Id=grep("Quarter 1", artDf$Quarter)
  q4Id=grep("Quarter 4", artDf$Quarter)
  q1Df=artDf[q1Id,]
  q4Df=artDf[q4Id,]
  q1Sum = sum(q1Df$CPUE_number_per_hour)  
  q4Sum = sum(q4Df$CPUE_number_per_hour)  
  print(q4Sum/q1Sum)
}

#Goes through all species but only prints those that match conditions 
for(x in specList){
  artId=grep(x, df$Species)
  artDf = df[artId, ]
  Obs=length(artDf$CPUE_number_per_hour)
  CSum=sum(artDf$CPUE_number_per_hour)
  q1Id=grep("Quarter 1", artDf$Quarter)
  q4Id=grep("Quarter 4", artDf$Quarter)
  q1Df=artDf[q1Id,]
  q4Df=artDf[q4Id,]
  q1Sum = sum(q1Df$CPUE_number_per_hour)  
  q4Sum = sum(q4Df$CPUE_number_per_hour)  
  qDif=q4Sum/q1Sum
  if(Obs > 2000){
    cat("\n")
    print(x)
    print(paste("Observation count:",Obs))
    print(paste("Observation sum:",CSum))
    print(paste("Observation sum:",CSum, ""))
    print(paste("Quarter sum ratio:",qDif, ""))
  }
}

coolSpec=c("Clupea harengus","Eutrigla gurnardus","Gadus morhua","Hippoglossoides platessoides","Limanda limanda", "Merlangius merlangus", "Merluccius merluccius", "Pleuronectes platessa", "Sprattus sprattus")

#Plot of yearly CPUE patterns 
for(x in coolSpec){
  coolId=grep(x, df$Species)
  coolDf = df[coolId,]
  #plot(x=coolDf$Year, y=coolDf$CPUE_number_per_hour)
  yearGG=ggplot(data=coolDf, aes(x=coolDf$Year, y=coolDf$CPUE_number_per_hour, color=coolDf$Quarter))
  yearGG = yearGG + geom_point() + theme_bw() + xlab("") + ylab("CPUE per Hour")+ ggtitle(x)
  yearGG = yearGG + theme(legend.title = element_blank(), legend.position = "bottom") 
  yearOBS=ggplot(data=coolDf, aes(x=as.factor(Year)))
  yearOBS = yearOBS + geom_histogram(stat="count", color="black", fill="white") + theme_bw() + ggtitle(x)
  yearOBS = yearOBS + theme(legend.title = element_blank(), axis.text.x = element_text(angle=90)) + ylab("Trawling Count") + xlab("Year")   
  pdfName = paste0(x, "_yearCPUE.pdf")
  yearPdf=ggarrange(yearGG, yearOBS, nrow = 2, ncol = 1)
  ggexport(yearPdf, filename = pdfName)
}
getwd()
# Basic histogram
ggplot(df, aes(x=weight)) + geom_histogram()
# Change the width of bins
ggplot(df, aes(x=weight)) + 
  geom_histogram(binwidth=1)
# Change colors
p<-ggplot(df, aes(x=weight)) + 
  geom_histogram(color="black", fill="white")


setwd("E:/DataAnalys/OX2_SeasonPatternFish/ModelleringAvFisk/ModelBas/Arter")

for(art in coolSpec){
  artId=grep(art, df$Species)
  artDf = df[artId, ]
  names(artDf)[names(artDf) == "CPUE_number_per_hour"] <- "CPUE"
  artDf$CPUE = as.integer(artDf$CPUE)
  art1999 = artDf[which(artDf$Year >= 1999), ]  
  write.csv(art1999, file = paste0(art, "1999_2019.csv"), row.names = FALSE, fileEncoding = "UTF-8")
}


#CPUE plot Quarter
#QCPUE=melt(tapply(dfSpec$CPUE_number_per_hour, dfSpec$Quarter, sum))
#pltQC=ggplot(data=QCPUE, aes(x=as.factor(Var1), y=value, fill=as.factor(Var1)))
#pltQC = pltQC + geom_bar(stat="identity")
#pltQC = pltQC + theme_bw(12)+ylab("CPUE")+xlab("Season")
#pltQC = pltQC + theme(legend.title = element_blank())
#pltQ_CPUE = ggplot(data=mean_QCPUE, aes(x=as.factor(Var1), y=M_CPUE, fill=as.factor(Var1)))
#pltQ_CPUE = pltQ_CPUE+geom_bar(stat="identity") +  
#geom_errorbar(aes(ymin=M_CPUE-SD_CPUE, ymax=M_CPUE+SD_CPUE), width=.1,position = position_dodge(.9))  
#pltDptDate=ggplot(data=dfSpec, aes(x=NewDate, y=Depth))
#pltDptDate = pltDptDate + geom_point()
#pltDptDate = pltDptDate + theme_bw(13)+xlab("")
#pltDptDate = pltDptDate + ggtitle(paste0(art, ", CPUE by depth"))