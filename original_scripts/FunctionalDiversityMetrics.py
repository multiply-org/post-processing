# -*- coding: utf-8 -*-
# /usr/bin/env python

__author__ = "L.T.Hauser"
__copyright__ = "Copyright 2017 L. Hauser"
__version__ = "0.1 (06.11.2017)"
__license__ = "GPLv3"
__email__ = "L.T.Hauser@cml.leidenuniv.nl"


    ## LOAD LIBRARIES ## 

from osgeo import gdal
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy import stats 
from scipy import spatial
from scipy.spatial.distance import squareform, pdist
from sklearn.neighbors import NearestNeighbors
import sklearn.preprocessing as sk

class CalcFuncDiv():
    def __init__(self, configfile = None):        
        
#        if configfile==None:
#            configfile = 'config.yml'
#        parameters = yml.load(configfile)#        
#        self.laipath     = parameters['Postprocessing']['lai']

        self.metrics     = {'CVH', 'MNND', 'FE', 'FDIV'}
        
        self.laipath     = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/ASCIIs/Analytics/lai5.txt'
        self.cabpath     = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/ASCIIs/Analytics/cab5.txt'
        self.cwpath      = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/ASCIIs/Analytics/cw5.txt'
        self.maskpath    = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/Flagsby5/flagsbyfiveall.txt' 
                                
    def ReadData(self, laipath=None, cabpath=None, cwpath=None, maskpath=None):        
        if laipath==None:
            laipath=self.laipath
        if cabpath==None:
            cabpath=self.cabpath
        if cwpath==None:
            cwpath=self.cwpath
        if maskpath==None:
            maskpath=self.maskpath
        
            ## READ ASCIIs to GDAL RASTERS ## 
        lai             = gdal.Open(laipath).ReadAsArray()
        cab             = gdal.Open(cabpath).ReadAsArray()
        cwc             = gdal.Open(cwpath).ReadAsArray()
        fmsk            = gdal.Open(maskpath).ReadAsArray()
        
        cols  = gdal.Open(laipath).RasterXSize
        rows  = gdal.Open(laipath).RasterYSize
        
        return lai, cab, cwc, fmsk, cols, rows    
    
    def PreProcessData(self, lai, cab, cwc, fmsk):
    
                    ## SET ALL MISSING VALUES / NaNs TO - 9999 ## 
        lai[lai==0]=-9999
        cwc[cwc==0]=-9999
        cab[cab==0]=-9999
        
            ## PASS TRAITS THROUGH THE MASK ## 
        flagpasser = (fmsk == 0)    
        lai[flagpasser] = -9999
        cwc[flagpasser] = -9999
        cab[flagpasser] = -9999
        
            ## STANDARDIZE ALL TRAIT VALUES ##
        traitz = [lai, cwc, cab]
        for t, trait in enumerate(traitz):
            zeropasser = (trait == -9999)
            scalall = []
            scalall = sk.StandardScaler()            
            scalall.fit(trait[~zeropasser])
            stdtrait = scalall.transform(trait)
            traitz[t][~zeropasser] = stdtrait[~zeropasser]    
         
        a_lai, a_cwc, a_cab = traitz
       
        return a_lai, a_cwc, a_cab
        
    def Processdata(self, lai, a_lai, a_cwc, a_cab, plotsize, cols, rows, metrics):        
        xsize = int(np.sqrt(plotsize))
        ysize = int(np.sqrt(plotsize))
        xoff  = np.round(xsize/2)
        yoff  = np.round(ysize/2)
        
        ## SELECT THE FUNCTIONAL DIVERSITY METRICS YOU WANT TO CALCULATE ## 
        if 'CVH' in self.metrics:  
            cvh_out   =  np.zeros(((rows/xsize)+1,(cols/ysize)+1), dtype=float, order='C')
        else:
            cvh_out      =   None
        
        if 'MNND' in self.metrics: 
            mnnd_out =  np.zeros(((rows/xsize)+1,(cols/ysize)+1), dtype=float, order='C')
        else: 
            mnnd_out      =   None
        
        if 'FE' in self.metrics:         
            fe_out    =  np.zeros(((rows/xsize)+1,(cols/ysize)+1), dtype=float, order='C')
        else: 
            fe_out      =   None

        if 'FDIV' in self.metrics: 
            fdiv_out  =  np.zeros(((rows/xsize)+1,(cols/ysize)+1), dtype=float, order='C')          
        else: 
            fdiv_out      =   None

        for ir,row in enumerate(np.arange(0,rows,10)):
            for ic,column in enumerate(np.arange(0,cols,10)): 
            
                #read data in moving window
                r_lai                 = a_lai[(row - xoff):(row + xoff),(column - yoff):(column + yoff)]
        #        r_cab                 = cab.ReadAsArray(xoff=ix_center, yoff=iy_center, xsize=xsize, ysize=ysize)
        #        r_cwc                 = cwc.ReadAsArray(xoff=ix_center, yoff=iy_center, xsize=xsize, ysize=ysize)              
                
                if (np.sum(r_lai != -9999)) >= 95:
                    r_cab                 = a_cab[(row - xoff):(row + xoff),(column - yoff):(column + yoff)]
                    r_cwc                 = a_cwc[(row - xoff):(row + xoff),(column - yoff):(column + yoff)]
        
                    #arrange data#
                    traitslist = np.array([np.concatenate(r_cab), np.concatenate(r_cwc), np.concatenate(r_lai)])
                    
                    # EXCLUDE MISSING VALUES / NaN FROM ANALYSIS ##
                    abu = (traitslist[0:,0:625,] == -9999)
                    est = traitslist[~abu]
                    lengthr = (len(est)/3)
                    est = np.reshape(est, (3, lengthr))
                    
                    #kernel density estimates to define outliers
                    kde = stats.gaussian_kde(est)
                    density = kde(est)
                    lower_quartile = np.percentile(density, 05)
                    noutliers = (density > lower_quartile)
                    estd = est.T[noutliers]
                    
                    cvh = self.FuncRich(estd, metrics)
                    cvh_out[ir, ic] = cvh.volume
                    
                    mnnd = self.FuncDivAiba(estd, metrics)
                    mnnd_out[ir, ic] = mnnd
                    
                    fe = self.FuncEvenness(estd, metrics)
                    fe_out[ir, ic] = np.mean(fe)
                    
                    fdiv = self.FuncDivVill(estd, metrics)
                    fdiv_out[ir, ic] = fdiv
                
        print "CALCULATIONS DONE"
                              
        return cvh_out, mnnd_out, fe_out, fdiv_out
        

    def FuncRich(self, estd, metrics):
        if 'CVH' in self.metrics:
            cvh = spatial.ConvexHull(estd)
            
        else: 
            cvh      =   None
            
        return cvh

    def FuncDivAiba(self, estd, metrics):
        if 'MNND' in self.metrics:
            scaler = []
            scaler = sk.StandardScaler()            
            scaler.fit(estd)
            nestd = scaler.transform(estd)
            nnbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(nestd)
            ndistances, nindices = nnbrs.kneighbors(nestd)
            mnnd = np.mean(ndistances[:,1])
                        
        else: 
            mnnd      =   None

        return mnnd        
            
    def FuncEvenness(self, estd, metrics):
        if 'FE' in self.metrics: 
            
            #calculate FunctEveness (Villeger et al., 2008)
            undgraph    = squareform(pdist(estd, 'euclidean'))
            mintree     = minimum_spanning_tree(undgraph)
            mstmat      = mintree.toarray().astype(float) 
            mstpasser   = mstmat == 0
            mst         = mstmat[~mstpasser]
            ss          = np.zeros(np.shape(mst))
            ss          = (1/(ss+len(mst)))
            PEW         = (mst/np.sum(mst))
            fe          = (np.sum(np.minimum(PEW,ss))-ss[0])/(1-ss[0])
                        
        else: 
            fe      =   None
            
        return fe

    def FuncDivVill(self, estd, metrics):
        if 'FDIV' in self.metrics: 
            cvh = spatial.ConvexHull(estd)
            centroid    = np.mean(estd[cvh.simplices,0]),np.mean(estd[cvh.simplices,1]), np.mean(estd[cvh.simplices,2])
            eucdist = np.zeros(len(estd))
            for i in xrange(len(estd)):
                eucdist[i] = spatial.distance.euclidean(estd[i], centroid) 
            fdiv = np.mean(eucdist)
            
        else: 
            fdiv      =   None
        
        return fdiv


    def OutputData(self, cvh_out, mnnd_out, fe_out, fdiv_out, laipath, outpath, metrics):
        myfile = open(laipath)    
        head = [next(myfile) for x in xrange(6)]
        head2 = head*1
        head_cellsize=  head[4]
        head_rows = head2[1]
        head_cols = head2[0]
        head_rows_new = head_rows[0:14] + str(np.shape(cvh_out)[0]) + head_rows[-2:] 
        head_cols_new = head_cols[0:14] + str(np.shape(cvh_out)[1]) + head_rows[-2:] 
        head_cellsize_new=head_cellsize[0:16]+'0'+head_cellsize[16:]
        head2[0] = head_cols_new
        head2[1] = head_rows_new
        head2[4] = head_cellsize_new
        headerw = '\n'.join([head2[0][0:-2], head2[1][0:-2], head2[2][0:-2], head2[3][0:-2], head2[4][0:-2], 'NODATA_value  0'])

        ## OUTPUT FUNCTIONAL DIVERSITY RASTERS TO ASCII ## \
        #export Convex Hull Map (Functional Richness)
        if 'CVH' in self.metrics:
             outname = outpath + 'cvh_nameofmap.txt'
             np.savetxt(outname, cvh_out, fmt='%.5f', header = headerw, comments='')

        #export MNND Map (Aiba's Functional Divergence)
        if 'MNND' in self.metrics:
            outname = outpath + 'mnnd_nameofmap.txt'
            np.savetxt(outname, mnnd_out, fmt='%.5f', header = headerw, comments='')
      
        #export FE Map (Functional Evenness)
        if 'FE' in self.metrics:            
            outname = outpath + 'fe_nameofmap.txt'
            np.savetxt(outname, fe_out, fmt='%.5f', header = headerw, comments='')

        #export Villegers FDiv Map (Functional Divergence)
        if 'FDIV' in self.metrics:            
            outname = outpath + 'fdiv_nameofmap.txt'
            np.savetxt(outname, fdiv_out, fmt='%.5f', header = headerw, comments='')

        # STORE TABLE OF FUNCTIONAL DIVERSITY METRICS - EXCLUDING MISSING VALUES /NaNs #
        cvhopasser = (cvh_out>0)
        cvh_e  = cvh_out[cvhopasser]
        mnnd_e = mnnd_out[cvhopasser]
        fe_e   = fe_out[cvhopasser]
        fdiv_e = fdiv_out[cvhopasser]
        dbf = cvh_e, mnnd_e, fe_e, fdiv_e
        dbft = np.transpose(dbf)
        tablefile = outpath + 'name_of_outputtable.txt'
        np.savetxt(tablefile, dbft, fmt='%.5f', header= metrics, comments='')

            
    def PostProcess(self,laipath = None,cabpath=None, cwpath=None, maskpath=None, plotsize = 100, traitsin = ['lai', 'cab', 'cw'], metrics     = {'CVH', 'MNND', 'FE', 'FDIV'}):            
#        "-laipath =  ..."
#        "-cabpath=..."
#        "-cwpath=..."
#        "-maskpath=..."
#        "-plotsize = ..."
#        "-traitsin = ['lai', 'cab', 'cw']"
#        "-metrics = ['CVH', 'MNND', 'FE', 'FDIV'] "
        
        outpath = '.'
        lai, cab, cwc, fmsk, cols, rows     = self.ReadData(laipath = laipath,cabpath=cabpath, cwpath=cwpath, maskpath=maskpath)
        a_lai, a_cwc, a_cab                 =  self.PreProcessData(lai, cab, cwc, fmsk)
        cvh_out, mnnd_out, fe_out, fdiv_out = self.Processdata(lai, a_lai, a_cwc, a_cab, plotsize, cols, rows, metrics)
        self.OutputData(cvh_out, mnnd_out, fe_out, fdiv_out, laipath, outpath, metrics)
                    
if __name__ =='main':
    #from FunctionalDiversityMetrics import CalcFuncDiv
    
    laipath     = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/ASCIIs/Analytics/lai5.txt'
    cabpath     = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/ASCIIs/Analytics/cab5.txt'
    cwpath      = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/ASCIIs/Analytics/cw5.txt'
    maskpath    = '/media/leon/FREECOM HDD/Data/Borneo/Sentinel/NORTH/More_Sabah/GISworks/Flagsby5/flagsbyfiveall.txt' 
    metrics     = {'CVH', 'MNND', 'FE', 'FDIV'}
    
    print(laipath)
    
    CFD = CalcFuncDiv()
    CFD.PostProcess(laipath = laipath,cabpath=cabpath, cwpath=cwpath, maskpath=maskpath)    
    
    #lai, cab, cwc, fmsk     = CalcFuncDiv.ReadData(laipath = laipath,cabpath=cabpath, cwpath=cwpath, maskpath=maskpath)
    #a_lai, a_cwc, a_cab    =  CalcFuncDiv.PreProcessData(lai, cab, cwc, fmsk)
    #cvh_out, mnnd_out, fe_out, fdiv_out = CalcFuncDiv.Processdata(lai, a_lai, a_cwc, a_cab, plotsize, metrics)
    #CalcFuncDiv.OutputData(cvh_out, mnnd_out, fe_out, fdiv_out, laipath, outpath, metrics)