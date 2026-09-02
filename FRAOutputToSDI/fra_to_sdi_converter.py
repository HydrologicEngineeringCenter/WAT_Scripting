# FRA to SDI converter
# takes f parts, merges events into lifecycles per file, consolidates into one big file.
# catches if file not found, records not found

import os, logging, sys, warnings

from hec import DssDataStore

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
fcst_rest = """
//CUMULATIVE(1.0DAY),AVERAGE///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.05)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.25)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.75)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(1.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),AVERAGE///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.05)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.25)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.75)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(2.0DAY),PERCENTILES(0.95)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),AVERAGE///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.05)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.25)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.75)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(3.0DAY),PERCENTILES(0.95)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),AVERAGE///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.05)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.25)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.75)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(4.0DAY),PERCENTILES(0.95)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),AVERAGE///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.05)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.1)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.25)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.5)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.75)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.9)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/
//CUMULATIVE(5.0DAY),PERCENTILES(0.95)///IR-Year/C:000001|Space1S1:FRA50S:FIRO_WFP-SFO_HHD/"""

def pathnameFormatter(pathname, collectionID):
    pathParts = pathname.split("/")
    fPart = pathParts[-2]
    lastPart = fPart.split("|")[-1]
    newFPart = "C:%06d|%s" % (collectionID, lastPart)
    pathParts[-2] = newFPart
    return "/".join(pathParts)

def perRecordCopy(inputFile, outputFile, pathname, lcNum):
    outTS = None
    for eventNum in range(1, nEventsPerLC+1):
        readPathname = pathnameFormatter(pathname, eventNum)
        # from input file, copy to output file
        try:
            ts = inputFile.retrieve(readPathname).label_as_time_zone("UTC")
        except:
            logger.warning("Unable to read %s from %s" % (readPathname, inputFile._hecdss._filename))
            break
        sdiFPart = readPathname.split(":")[-1].replace("/","")
        ts.version = "C:%06d|%s" % (lcNum, sdiFPart)
        tsMergeNeeded = "IR-" in readPathname
        if not tsMergeNeeded:
            # trying this naive write
            outputFile._hecdss.put(ts.to_native(outputFile))
        else:
            ts = ts.ito_irregular("IR-Year")
            if outTS is None:
                outTS = ts
            else:
                # merge record onto outRecord
                outTS.imerge(ts)
    if not outTS is None:
        outputFile.store(outTS)


def perFileCopy(inputFile, outputFile, pathSet, lcNum):
    for pathname in pathSet:
        if len(pathname.strip()) == 0:
            continue
        perRecordCopy(inputFile, outputFile, pathname, lcNum)

def inputFilenameFormatter(inputDir, alt, ap, r, lc):
    return os.path.join(inputDir, "Realization %d" % r, "Lifecycle %d" % lc, "%s-%s.dss" % (alt, ap))

def lifecycleNumbers(r, nLCsPerR):
    return range((r-1)*nLCsPerR+1, r*nLCsPerR)

def allCopy(inputDirectory, outputFilename, pathSet):
    with DssDataStore.open(outputFilename, read_only=False) as outFile:
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
                    # force catalog for record types
                    # catalog = inFile._hecdss.get_catalog()
                    perFileCopy(inFile, outFile, pathSet, lifecycle)

# config section
logFilename = "sdi_consolidator.log"
inputDirectory = r"C:\Watersheds\FRA50S_FcstsOnly"
outputFilename = "sdi_consolidated.dss"

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
