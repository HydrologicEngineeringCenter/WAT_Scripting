from __future__ import with_statement

PRIMARY_FORECASTS = [
"/TDA/VOLUME[APR-AUG] FCST",
"/DWR/VOLUME[APR-JUL] FCST",
"/BRN/VOLUME[APR-JUL] FCST",
"/LIB/VOLUME[APR-AUG] FCST",
"/HGH/VOLUME[MAY-SEP] FCST",
"/ARDB/VOLUME[APR-AUG] FCST",
"/MCDB/VOLUME[APR-AUG] FCST",
"/DCDB/VOLUME[APR-AUG] FCST"
]

# set basic fPart for SDI run to read forecasts from
SDI_F_PART = "STOCHHYDRO-CLIMCHANGE" # "STOCHHYDRO-CC_%PERIOD%_W1DAYFCSTS" # 

from hec2.wat import WAT
from hec.heclib.dss import HecDss
from hec.heclib.util import HecTime
from hec.script import Constants
from hec.io import TimeSeriesContainer
from hec.heclib.util import Heclib;

from csv import DictReader
import shutil
import os.path

# this is the entry point for the script from the WAT scripting plugin
def computeAlternative(currentAlt, options):
    # An example sending a message box to the user - don't turn this on!
    #WAT.getWAT().postError("Computing", "LC#%d" % lcNumber)
    # get watershed directory
    runDirectory = options.getRunDirectory()
    watershedDirectory = runDirectory.split("runs")[0]
    # Set output type to DSS v6 in case file doesn't exist
    Heclib.zset("DssVersion", "", 6)
    # currentAlt is the scripting alt.  Use this to access data locations
    # options is the WAT compute options that contains timewindow and event ID information
    # check if this is an FRA compute, get lifecycle number and size of compute
    if options.isFrmCompute():
        lcNumber = options.getCurrentLifecycleNumber()
        eventNumber = options.getCurrentEventNumber()
        maxLifecycle = options.getNumberLifecycles()
        # get the GCM/projection name from the index file
        gcmFileName = os.path.join(watershedDirectory, "climate_change", "GCM_List_%d.txt" % (maxLifecycle))
        gcmName = getGCMNameFromFile(lcNumber, gcmFileName)
        #WAT.getWAT().postError("LC#%d/%d: GCM %s" % (lcNumber, maxLifecycle, gcmName), "ClimChangePreProc Script")
    # build fpart, get alternative and analysis period names
    simName = options.getSimulationName()
    altName, apName = simName.split("-")
    period = apName.replace("SDI_", "")
    sdiFPart =  "%s:%s:%s" % (altName, apName, SDI_F_PART) # not used .replace("%PERIOD%", period)
    # open dss file
    twString = computeOptions.getSimulationTimeWindow().getTimeWindowString()
    dssFilename = options.getDssFilename()
    dssFile = HecDss.open(dssFilename) #, twString)
    # run data logistics tasks
    #if options.isFrmCompute(): # only do these if FRA/SDI compute?
    # format FPart with event ID
    sdiFPart = "C:%06d|%s" % (eventNumber, sdiFPart)
    # fixForecasts still needed with new SDI plugin
    # run fixForecast for converting 1DAY to IR-CENTURY data
    fixForecasts(dssFile, PRIMARY_FORECASTS, sdiFPart)
    # run CVSE file creator - DON'T DO THIS, just specify file name in hydro config file
    #moveCVSEFiles(watershedDirectory, gcmName, period)
    csvFilename = "climate_change/cvse_files/%s_%s.csv" % (gcmName, period)
    # run URC statistics file creator
    moveURCFiles(watershedDirectory, gcmName, period.replace("s", ""))
    # run other pre-processing stuff here...
    
    # close the DSS File
    dssFile.done()
    
    # get forecast normal volumes:
    fcstNormalsFile = open(os.path.join(watershedDirectory, "climate_change", "FcstAvgVolumes.csv"), 'r')
    fcstNormalsReader = DictReader(fcstNormalsFile)
    fcstNormals = dict()
    locationsDict = {"LIB": "Libby", "HGH": "Hungry Horse"}
    for row in fcstNormalsReader:
        if row["Dataset"] == gcmName and row["Simulation"] == period:
            if fcstNormals.has_key(row["Location"]):
                raise Exception("row already exists, duplicate data?")
            fcstNormals[locationsDict[row["Location"]]] = row["Fcst_Avg"]
    
    # create hydro config file
    hydroConfigFile = open(os.path.join(watershedDirectory, "shared", "alt_config", "hydrology.txt"), 'w')
    hydroConfigDict = {
        "period": period, 
        "gcmName": gcmName, 
        "fcstNormalDict": fcstNormals, 
        "cvseFilename": csvFilename}
    for k,v in hydroConfigDict.items():
        hydroConfigFile.write("%s: \"%s\"\n" % (k, v))
    return 1


###
# Climate Change specific functions
###
def getGCMNameFromFile(gcmNumber, gcmFileName):
    with open(gcmFileName, 'r') as gcmFile:
        gcmDictionary = DictReader(gcmFile, dialect="excel-tab")
        for row in gcmDictionary:
            if gcmNumber == int(row["Index"]):
                return row["Projection"]
    return "NoProjectionFound"

def moveURCFiles(watershedDirectory, gcmName, period):
    urcFcstMetadataFileName = "%s_urc_%s.csv" % (gcmName, period)
    srcFile = os.path.join(watershedDirectory, "climate_change", "urc_files", urcFcstMetadataFileName)
    destFile = os.path.join(watershedDirectory, "urc", "Base_URCs88", "forecastMetadata_CC.csv") 
    try:
        shutil.copyfile(srcFile, destFile)
    except IOError, e:
        print e
        #raise e
    return None

def moveCVSEFiles(watershedDirectory, gcmName, period):
    fcstCVSEFileName = "%s_%s.csv" % (gcmName, period)
    srcFile = os.path.join(watershedDirectory, "climate_change", "cvse_files", fcstCVSEFileName)
    destFile = os.path.join(watershedDirectory, "shared", "forecast_cvses.csv") 
    try:
        shutil.copyfile(srcFile, destFile)
    except IOError, e:
        #print e
        raise e
    return None

###
# fix forecasts process
###
def fixForecasts(dssFile, fcstList, fPart):
    for fcstABC in fcstList:
        if "1DAY" in fPart.upper():
            fcstPath = "/%s//1DAY/%s/" % (fcstABC, fPart)
        else:
            fcstPath = "/%s//IR-CENTURY/%s/" % (fcstABC, fPart)
        #WAT.getWAT().postError(fcstPath, "Computing...")
        #print dssFile.getCatalogedPathnames(fcstPath.replace("//","/*/"))
        fcstTSC = dssFile.get(fcstPath, True) #.getData()
        dssFile.put(reformatForecast(fcstTSC))

def reformatForecast(fcstTSC):
    # converts dailies to forecast set;
    # converts irregular data with monthly 0s to standard CRT format.
    # iterate through values
    outTimes = []
    outVals = []
    firstPoint = True
    prevTime, prevVal = 0, Constants.UNDEFINED
    isIrregular = (fcstTSC.interval <= 0)
    for t,v in zip(fcstTSC.times, fcstTSC.values):
        # add end point from previous when this changes; then start with new value
        ht = HecTime()
        ht.set(t)
        prevHt = HecTime()
        prevHt.set(prevTime)
        # insert new point whenever it changes, month changes, or on the first point
        if firstPoint or v != prevVal or (ht.month() != prevHt.month() and v != 0):
            # output endtimestamp for previous value
            if not firstPoint:
                outTimes.append(prevTime)
                outVals.append(prevVal)
            if firstPoint:
                firstPoint = False
            # output start timestamp for this value
            offset = -(24*60) + 1 # default to one minute past 0000 this day.
            if isIrregular and ht.minute() != 0:
                offset = 0
            outTimes.append(t + offset)
            outVals.append(v)
        prevTime = t
        prevVal = v
    # add last value to finish out series.
    #outTimes.append(t)
    #outVals.append(v)
    # create output TSC
    fcstOutTSC = TimeSeriesContainer()
    fcstOutTSC.interval = -1
    newPathName = fcstTSC.fullName.split("/")
    if not isIrregular: 
        newPathName[5] = "IR-CENTURY"
    fcstOutTSC.fullName = "/".join(newPathName) 
    fcstOutTSC.times = outTimes
    fcstOutTSC.values = outVals
    print fcstOutTSC.fullName
    print(outVals)
    fcstOutTSC.numberValues = len(outVals)
    fcstOutTSC.startTime = outTimes[0]
    fcstOutTSC.units = fcstTSC.units
    fcstOutTSC.type = "INST-VAL"
    return fcstOutTSC

