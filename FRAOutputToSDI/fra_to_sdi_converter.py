# FRA to SDI converter
# takes f parts, merges events into lifecycles per file, consolidates into one big file.
# catches if file not found, records not found

import os, logging, sys, warnings

from hec import DssDataStore, TimeSeries
from hecdss import DssPath

# mutes warnings from the hec library
warnings.filterwarnings("ignore", category=UserWarning)

pathSet = """//J_GRN_AUB/FLOW//1Hour/C:000001|Space1S1:FRA50S:HydroSampl-HHD_Auburn/
//RES_GRN_HHD_in/FLOW//1Hour/C:000001|Space1S1:FRA50S:HydroSampl-HHD_Auburn/
//J_GRN_AUB/Flow-UNREG//1Hour/C:000001|Space1S1:FRA50S:ResSim-SFO_Space1/
//J_GRN_AUB/Flow-Local//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//J_GRN_AUB:FMA=2 VOL=/Flow-Local//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//J_GRN_AUB:FMA=3 VOL=/Flow-Local//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//J_GRN_AUB:FMA=4 VOL=/Flow-Local//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//J_GRN_AUB:FMA=5 VOL=/Flow-Local//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//RES_GRN_HHD_in/Flow//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//RES_GRN_HHD_in:FMA=2 VOL=/Flow//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//RES_GRN_HHD_in:FMA=3 VOL=/Flow//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//RES_GRN_HHD_in:FMA=4 VOL=/Flow//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//RES_GRN_HHD_in:FMA=5 VOL=/Flow//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
//RES_GRN_HHD_in:VOL=/Flow//1Day/C:000001|Space1S1:FRA50S:Scripting-SynFcstPreProcessor/
"""
fcstPaths = """
//CUMULATIVE(1.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/"""

def pathnameFormatter(pathname, collectionID):
    pathParts = pathname.split("/")
    fPart = pathParts[-2]
    lastPart = fPart.split("|")[-1]
    newFPart = "C:%06d|%s" % (collectionID, lastPart)
    pathParts[-2] = newFPart
    return "/".join(pathParts)

def perRecordCopy(inputFile, outputFile, pathname, lcNum):
    outTS = None
    missedEvents = set()
    for eventNum in range(1, nEventsPerLC+1):
        readPathname = pathnameFormatter(pathname, eventNum)
        inpath = DssPath(readPathname)
        # from input file, copy to output file
        try:
            ts = None
            # special logic to deal with f parts that are blank, plugin issue in WAT to fix.
            if inpath.C.strip() == "":
                ts = inputFile._hecdss.get(readPathname)
                inpath.C = "FLOW" # we assume?  deals with bad EFP output pathnames :(
                ts.id = str(inpath)
                ts = TimeSeries.from_native(inputFile, ts)
            else:
                ts = inputFile.retrieve(readPathname)
            # hec TimeSeries object seems to be happier with this, may not always be true.
            ts.ilabel_as_time_zone("UTC")
        except Exception as e:
            # note when a record could not be read, write to a log.
            logger.warning("Unable to read %s from %s [%s]" % (readPathname, inputFile._hecdss._filename, str(e)))
            missedEvents.add(eventNum)
            continue
        sdiFPart = readPathname.split(":")[-1].replace("/","")
        ts.version = "C:%06d|%s" % (lcNum, sdiFPart)
        tsMergeNeeded = "IR-" in readPathname
        if not tsMergeNeeded:
            # trying this naive write
            outputFile._hecdss.put(ts.to_native(outputFile))
        else:
            #ts.isnap_to_regular("1Day")
            #ts = ts.ito_irregular("IR-Year")
            if outTS is None:
                outTS = ts
            else:
                # merge record onto outRecord
                outTS.imerge(ts)
    if not outTS is None:
        outputFile.store(outTS)
    return missedEvents


def perFileCopy(inputFile, outputFile, pathSet, lcNum):
    for pathname in pathSet:
        if len(pathname.strip()) == 0:
            continue
        missedEvents = perRecordCopy(inputFile, outputFile, pathname, lcNum)
        if len(missedEvents) > 0:
            missedEventList = list(missedEvents)
            missedEventList.sort()
            missedEventString  = ",".join([str(e) for e in missedEventList])
            # summary information about missing records.
            logger.info("LC %d missing one or more records for events %s" % (lcNum, missedEventString))


def inputFilenameFormatter(inputDir, alt, ap, r, lc):
    # wat folder structure within a compute
    return os.path.join(inputDir, "Realization %d" % r, "Lifecycle %d" % lc, "%s-%s.dss" % (alt, ap))

def lifecycleNumbers(r, nLCsPerR):
    # generate lifecycle #s for a given realization
    return range((r-1)*nLCsPerR+1, r*nLCsPerR+1)

def allCopy(inputDirectory, outputFilename, pathSet):
    with DssDataStore.open(outputFilename, read_only=False) as outFile:
        # supress DSS messages to console by setting this to 1.  4 is default.
        outFile.set_message_level(1)
        for realization in range(1, nRealizations+1):
            for lifecycle in lifecycleNumbers(realization, nLCsPerRealization):
                inputFilename = inputFilenameFormatter(inputDirectory, alternative, analysisPeriod, realization, lifecycle)
                if not os.path.exists(inputFilename):
                    logger.error("File does not exist: %s" % inputFilename)
                    continue
                print(inputFilename)
                with DssDataStore.open(inputFilename, read_only=True) as inFile:
                    inFile.set_message_level(1)
                    perFileCopy(inFile, outFile, pathSet, lifecycle)

# config section
logFilename = "sdi_consolidator.log"
outputFilename = "sdi_consolidated.dss"
inputDirectory = r"C:\Watersheds\FRA50S_FcstsOnly"

# globals
nEventsPerLC = 50
nLCsPerRealization = 30
nRealizations = 20
alternative = "Space1S1"
analysisPeriod = "FRA50S"


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(filename=logFilename, level=logging.INFO)
    paths = pathSet.split("\n")
    # print(paths)
    allCopy(inputDirectory, outputFilename, paths)
