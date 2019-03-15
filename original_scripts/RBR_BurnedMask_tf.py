#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:03:40 2018
@author: Gonzalo Otón & Magí Franquesa
Description: This script gets a burned area mask and as a second step it gets its severity using RBR.
Parameters:
    Sensor = Variable for parameter changes among sensors. 0=Sentinel, 1=Landsat8, 2=Landsat7
    NoData = Values no data. It can switch among sensors. Sentinel has not defined it and by default we put = -9999. Check the input data.
    ScaleFactor = Number by which the data is scaled. It can switch among sensors. Check the input data.
    Version = Trial version.
    Path = Main directory.
    PathPost,PathPre = Directory of Paths to images.
    PathPostNIR,PathPreNIR,PathPostSMIR...= Path to tiff.
    PathIndex = Output Path.
    Open files: Inside the script, we open '.tif' and transform it into an array. If the input is not 'tif', it must be modified.
    
    Bands corresponding to the different sensors
    Bands Sentinel: NIR=Band 8, SMIR=Band 11, SWIR=Band 12
    Bands Landsat 8: NIR=Band 5, SMIR=Band 6, SWIR=Band 7
    Bands Landsat 7: NIR=Band 4, SMIR=Band 5, SWIR=Band 7
"""

import numpy as np
import gdal
import os

def Fold(Path):
    if not os.path.isdir(Path):
        os.makedirs(Path)
    Path = Path + "/"
    return Path

Sensor=0
'''
0=Sentinel
1=Landsat8
2=Landsat7
'''

if Sensor == 0:  
    ##print 'Sentinel'
    Path='E:\\Projects\\Multiply\\PostProcessing\\TestingArea\\'
    
    PathPost=Path+'2017-11-11\\S2-29TNE2017-11-11\\'
    PathPostNIR=PathPost+'B8A_sur.tif'
    PathPostSMIR=PathPost+'B11_sur.tif'
    PathPostSWIR=PathPost+'B12_sur.tif'
    
    PathPre=Path+'2017-10-12\\S2-29TNE2017-10-12\\'
    PathPreNIR=PathPre+'B8A_sur.tif'
    PathPreSMIR=PathPre+'B11_sur.tif'
    PathPreSWIR=PathPre+'B12_sur.tif'
    
    NoData=-9999
    ScaleFactor=0.0001
    Version='_3'
    PathIndex=Fold(Path+'october2017_november2017/RBR_BurnedMask'+Version)

elif Sensor == 1:
    ##print 'L8'
    Path='/media/gonzalo/ALMACEN/Landsat8/'

    PathPost=Path+'PostFire/'
    PathPostNIR=PathPost+'LC08_L1TP_204032_20180517_20180604_01_T1_B5_sur.tif'
    PathPostSMIR=PathPost+'LC08_L1TP_204032_20180517_20180604_01_T1_B6_sur.tif'
    PathPostSWIR=PathPost+'LC08_L1TP_204032_20180517_20180604_01_T1_B7_sur.tif'
    
    PathPre=Path+''
    PathPreNIR=PathPre+''
    PathPreSMIR=PathPre+''
    PathPreSWIR=PathPre+''

    TifNIR1=gdal.Open(PathPostNIR)
    nir1 = TifNIR1.GetRasterBand(1)
    NoData=nir1.GetNoDataValue()
    del(TifNIR1,nir1)
    ScaleFactor=0.0001
    Version='_1'
    PathIndex=Fold(Path+'RBR_BurnedMask'+Version)    
    
elif Sensor == 2:
    ##print 'L7'
    Path='/media/gonzalo/ALMACEN/Landsat7/'

    PathPost=Path+''
    PathPostNIR=PathPost+''
    PathPostSMIR=PathPost+''
    PathPostSWIR=PathPost+''
    
    PathPre=Path+''
    PathPreNIR=PathPre+''
    PathPreSMIR=PathPre+''
    PathPreSWIR=PathPre+''

    TifNIR1=gdal.Open(PathPostNIR)
    nir1 = TifNIR1.GetRasterBand(1)
    NoData=nir1.GetNoDataValue()
    del(TifNIR1,nir1)
    ScaleFactor=0.0001
    Version='_1'
    PathIndex=Fold(Path+''+Version)     
        
def calcNBR(swir,nir,comp_mask,SD,path,Year,Month,Day,gridColumnTot,gridLineTot,DataType,NoData):
    Band = 'NBR' 
    ##print 'Calculating: ', Band
    
    swir=np.where((swir == NoData), -1, swir)
    nir=np.where((nir == NoData), -1, nir)
    
    nir = nir * ScaleFactor
    swir = swir * ScaleFactor
    
    mask = np.where(((nir+swir)==0),False,True)
    nir *= mask
    swir = swir*mask + 0.2*np.invert(mask) #The factor (0.2) doesn't affect, is for Nodata values
    
    nbr = (nir-swir)/(nir+swir)

    comp_mask *= mask
    nbr = nbr * comp_mask + NoData * np.invert(comp_mask)

    nbr=nbr.astype(np.float32)
    #Name=str(Year)+str(Month)+str(Day)+'_'+Band+'.tif'
    #saveTIFnew(SD,nbr,path,Name,gridColumnTot,gridLineTot,DataType,NoData)
    return nbr

def CalcMIRBI(smir,swir,Mask,SD,path,Year,Month,Day,gridColumnTot,gridLineTot,DataType,NoData):
    Band = 'MIRBI' 
    #print 'Calculating: ', Band
    
    swir=np.where((swir == NoData), -1, swir)
    smir=np.where((smir == NoData), -1, smir)
    
    smir = smir * ScaleFactor
    swir = swir * ScaleFactor
    
    MIRBI=10*swir-9.8*smir+2
    MIRBI = MIRBI * Mask + NoData * np.invert(Mask)

    MIRBI=MIRBI.astype(np.float32)
    #Name=str(Year)+str(Month)+str(Day)+'_'+Band+'.tif'
    #saveTIFnew(SD,MIRBI,path,Name,gridColumnTot,gridLineTot,DataType,NoData)
    return MIRBI

def CalcNBR2(smir,swir,Mask,SD,path,Year,Month,Day,gridColumnTot,gridLineTot,DataType,NoData):
    Band = 'NBR2' 
    #print 'Calculating: ', Band
    
    swir=np.where((swir == NoData), -1, swir)
    smir=np.where((smir == NoData), -1, smir)
    
    smir = smir * ScaleFactor
    swir = swir * ScaleFactor

    mask2 = np.where(((smir+swir)==0),False,True)
    smir *= mask2
    swir = swir*mask2 + 0.2*np.invert(mask2) #The factor (0.2) doesn't affect, is for Nodata values
    
    NBR2=(smir-swir)/(smir+swir)
    
    Mask *= mask2
    NBR2 = NBR2 * Mask + NoData * np.invert(Mask)

    NBR2=NBR2.astype(np.float32)
    #Name=str(Year)+str(Month)+str(Day)+'_'+Band+'.tif'
    #saveTIFnew(SD,NBR2,path,Name,gridColumnTot,gridLineTot,DataType,NoData)
    return NBR2

def saveTIFnew(SD,array,path,name,gridColumnTot,gridLineTot,DataType,NoData):               
    RD=gdal.GetDriverByName("GTiff").Create(path + str(name), gridColumnTot, gridLineTot, 1, DataType)
    RD.SetGeoTransform(SD.GetGeoTransform())
    RD.SetProjection(SD.GetProjection())
    RD.GetRasterBand(1).WriteArray(array)
    RD.GetRasterBand(1).SetNoDataValue(NoData)
    RD=None
    
def mask_values(array,NoData):
    y = np.ma.masked_values(array, NoData)
    mean=y.mean()
    
    #print mean
    return mean

#print 'Open files...'
TifSWIR1=gdal.Open(PathPostSWIR)
swir1=TifSWIR1.ReadAsArray()
TifSMIR1=gdal.Open(PathPostSMIR)
smir1=TifSMIR1.ReadAsArray()

TifSWIR0=gdal.Open(PathPreSWIR)
swir0=TifSWIR0.ReadAsArray()  
TifSMIR0=gdal.Open(PathPreSMIR)
smir0=TifSMIR0.ReadAsArray()      

Year1=(PathPostSWIR.split("/")[-1]).split("_")[1][:4]
Month1=(PathPostSWIR.split("/")[-1]).split("_")[1][4:6]
Day1=(PathPostSWIR.split("/")[-1]).split("_")[1][6:8]   

Year0=(PathPreSWIR.split("/")[-1]).split("_")[1][:4]
Month0=(PathPreSWIR.split("/")[-1]).split("_")[1][4:6]
Day0=(PathPreSWIR.split("/")[-1]).split("_")[1][6:8]

gridLineTot=len(swir0) # Row
gridColumnTot=len(swir0[0]) #Columns
DataType=gdal.GDT_Float32

#print 'Calculating SWIR/SMIR Mask'  
SWIRMask = (swir1 != NoData) * (swir0 != NoData) 
SMIRMask = (smir1 != NoData) * (smir0 != NoData)
SMask=SWIRMask*SMIRMask

#print 'Calculating MIRBI'
MIRBI1=CalcMIRBI(smir1,swir1,SMask,TifSWIR1,PathIndex,Year1,Month1,Day1,gridColumnTot,gridLineTot,DataType,NoData)
MeanMIRBI1=mask_values(MIRBI1,NoData)
MIRBI0=CalcMIRBI(smir0,swir0,SMask,TifSWIR1,PathIndex,Year0,Month0,Day0,gridColumnTot,gridLineTot,DataType,NoData)

#print 'Calculating difMIRBI'  
difMIRBI = MIRBI1 - MIRBI0
difMIRBI = difMIRBI * SMask + NoData * np.invert(SMask)    
#FileNamedifMIRBI=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_difMIRBI.tif'
#saveTIFnew(TifSWIR1,difMIRBI,PathIndex,FileNamedifMIRBI,gridColumnTot,gridLineTot,DataType,NoData)    

#print 'Calculating NBR2'
NBR21=CalcNBR2(smir1,swir1,SMask,TifSWIR1,PathIndex,Year1,Month1,Day1,gridColumnTot,gridLineTot,DataType,NoData)
MeanNBR21=mask_values(NBR21,NoData)
NBR20=CalcNBR2(smir0,swir0,SMask,TifSWIR1,PathIndex,Year0,Month0,Day0,gridColumnTot,gridLineTot,DataType,NoData)

#print 'Calculating difNBR2'  
difNBR2 = NBR21 - NBR20
difNBR2 = difNBR2 * SMask + NoData * np.invert(SMask)    
#FileNamedifNBR2=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_difNBR2.tif'
#saveTIFnew(TifSWIR1,difNBR2,PathIndex,FileNamedifNBR2,gridColumnTot,gridLineTot,DataType,NoData)    

del(smir1,smir0,MIRBI0,NBR20)

#print 'Open files...'
TifNIR1=gdal.Open(PathPostNIR)
nir1=TifNIR1.ReadAsArray()
TifNIR0=gdal.Open(PathPreNIR)
nir0=TifNIR0.ReadAsArray()

#print 'Calculating NIR Mask'  
NIRMask = (nir1 != NoData) * (nir0 != NoData) 

#print 'Calculating NIR'  
MeanNIR1=mask_values(nir1,NoData)

#print 'Calculating difNIR'  
difNIR = nir1 - nir0
difNIR = difNIR * NIRMask + NoData * np.invert(NIRMask)    
#FileNamedifNIR=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_difNIR.tif'
#saveTIFnew(TifSWIR1,difNIR,PathIndex,FileNamedifNIR,gridColumnTot,gridLineTot,DataType,NoData) 

#print 'Calculating Burned Mask'  
SMask
#FileNameSMask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_SMask.tif'
#saveTIFnew(TifSWIR1,SMask,PathIndex,FileNameSMask,gridColumnTot,gridLineTot,DataType,NoData)  

NIRMask
#FileNameNIRMask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_NIRMask.tif'
#saveTIFnew(TifSWIR1,NIRMask,PathIndex,FileNameNIRMask,gridColumnTot,gridLineTot,DataType,NoData)  

MeanMIRBI1Mask=(MIRBI1>MeanMIRBI1)
#FileNameMeanMIRBI1Mask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_MeanMIRBI1Mask.tif'
#saveTIFnew(TifSWIR1,MeanMIRBI1Mask,PathIndex,FileNameMeanMIRBI1Mask,gridColumnTot,gridLineTot,DataType,NoData) 

DifMIRBIMask=(difMIRBI>0.25)
#FileNameDifMIRBIMask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_DifMIRBIMask.tif'
#saveTIFnew(TifSWIR1,DifMIRBIMask,PathIndex,FileNameDifMIRBIMask,gridColumnTot,gridLineTot,DataType,NoData)    

MeanNBR21Mask=(NBR21<MeanNBR21)
#FileNameMeanNBR21Mask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_MeanNBR21Mask.tif'
#saveTIFnew(TifSWIR1,MeanNBR21Mask,PathIndex,FileNameMeanNBR21Mask,gridColumnTot,gridLineTot,DataType,NoData)     

difNBR2Mask=(difNBR2<-0.05)
#FileNamedifNBR2Mask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_difNBR2Mask.tif'
#saveTIFnew(TifSWIR1,difNBR2Mask,PathIndex,FileNamedifNBR2Mask,gridColumnTot,gridLineTot,DataType,NoData)

MeanNIR1Mask=(nir1<MeanNIR1)
#FileNameMeanNIR1Mask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_MeanNIR1Mask.tif'
#saveTIFnew(TifSWIR1,MeanNIR1Mask,PathIndex,FileNameMeanNIR1Mask,gridColumnTot,gridLineTot,DataType,NoData)     

difNIRMask=(difNIR<-0.01)
#FileNamedifNIRMask=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_difNIRMask.tif'
#saveTIFnew(TifSWIR1,difNIRMask,PathIndex,FileNamedifNIRMask,gridColumnTot,gridLineTot,DataType,NoData)    

BurnedMask=SMask*NIRMask*MeanMIRBI1Mask*DifMIRBIMask*MeanNBR21Mask*difNBR2Mask*MeanNIR1Mask*difNIRMask
#FileNameMaskEkhi=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_BurnedMask.tif'
#saveTIFnew(TifSWIR1,BurnedMask,PathIndex,FileNameMaskEkhi,gridColumnTot,gridLineTot,DataType,NoData)

#### End of calculation of the mask ####
#__________________________________________________________________________________________________________#

## Calculation of RBR ##

#print 'Calculating NBR'  
NBR1 = calcNBR(swir1,nir1,BurnedMask,TifSWIR1,PathIndex,Year1,Month1,Day1,gridColumnTot,gridLineTot,DataType,NoData)
NBR0 = calcNBR(swir0,nir0,BurnedMask,TifSWIR1,PathIndex,Year0,Month0,Day0,gridColumnTot,gridLineTot,DataType,NoData)

#print 'Calculating difNBR'  
difNBR = NBR0 - NBR1
difNBR = difNBR * BurnedMask + NoData * np.invert(BurnedMask)
#Name=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_difNBR.tif'
#saveTIFnew(TifSWIR1,difNBR,PathIndex,Name,gridColumnTot,gridLineTot,DataType,NoData)    

#print 'Calculating RBR'  
mask = np.where((NBR0+1.001==0),False,True)
RBR = (difNBR)/(NBR0+1.001)
RBR = RBR * BurnedMask + NoData * np.invert(BurnedMask)
FileName=str(Year0)+str(Month0)+str(Day0)+'_'+str(Year1)+str(Month1)+str(Day1)+'_RBR.tif'
saveTIFnew(TifSWIR1,RBR,PathIndex,FileName,gridColumnTot,gridLineTot,DataType,NoData)
   