# name=DatumShift
# displayinmenu=true
# displaytouser=true
# displayinselector=true
#Datum Shift any DSS file
#Opens a dss file and then shifts the data if it's not already in NGVD29
# KAW, 16 May 2018
# Time window modifications by Heather Baxter
from hec.script import *
from hec.heclib.dss import *
from hec.heclib.dss import HecDss
import java
from hec.io import TimeSeriesContainer
from hec.heclib.util import HecTime
from hec.hecmath import TimeSeriesMath
from hec.lang import DSSPathString
import os
import sys
import time
from java.lang import String
from hec2.plugin.timewindow.modifier import ThresholdModifier
from hec2.plugin.timewindow.calc import PeakFinder
from com.rma.io import DssFileManagerImpl
from hec.io import DSSIdentifier
from hec2.plugin.timewindow.modifier import CroppingTimeWindowModifier
from hec.heclib.util import HecTime
from hec2.plugin.timewindow.calc import DateTimeHolder
from hec.model import RunTimeWindow

def timeWindowMod(runtimeWindow, alternative, computeOptions):
	t = time.time()
	# Load the active paths: 
	
	# Replace file names and imports with:
	dssFileName = computeOptions.getDssFilename()
	dssFileObj = HecDss.open(dssFileName)
	
	paths = dssFileObj.getCatalogedPathnames()
	
	print "\nStarting Script..."
	
	# Read the datum shifts. NOTE THAT THESE NEED UPDATED HERE AND IN THE STATE VARIABLE EDITOR.
	datumShiftDict = {"ALBENI FALLS" : 3.9, \
		"AMERICAN FALLS" : 3.3, "ANDERSON RANCH" : 3.4, "ARROW LAKES" : 4.3, \
		"ARROWROCK" : 3.4, "BONNEVILLE" : 3.3, "BOUNDARY" : 4, \
		"BOX CANYON" : 4., "BRILLIANT" : 4.2, "BROWNLEE" : 3.3, \
		"BUMPING LAKE" : 3.9,	"CABINET GORGE" : 3.9, "CASCADE" : 3.6, \
		"CHELAN" : 3.9, "CHIEF JOSEPH" : 4.,	"CLE ELUM" : 3.9, \
		"CORRA LINN" : 4.3, "DEADWOOD" : 4.,	"DUNCAN" : 4.3, \
		"DWORSHAK" : 3.3,	"GRAND COULEE" : 3.9,	"HELLS CANYON" : 3.6, \
		"HUNGRY HORSE" : 3.9, "ICE HARBOR" : 3.4,	"JACKSON LAKE" : 4.3, \
		"JOHN DAY" : 3.2,	"KACHESS" : 3.9, "KEECHELUS" : 4., \
		"SKQ" : 3.6,	"LIBBY" : 3.9, "LITTLE FALLS" : 3.8, "LITTLE GOOSE" : 3.2,	\
		"LONG LAKE" : 3.8,	"LOWER BONNINGTON" : 4.2,	"LOWER GRANITE" : 3.4, \
		"LOWER MONUMENTAL" : 3.3,	"LUCKY PEAK" : 3.3, "MCNARY" : 3.3, \
		"MICA" : 4.7,	"MONROE STREET" : 3.8,	"NINE MILE" : 3.8, \
		"NOXON RAPIDS" : 3.9,	"OWYHEE" : 3.3, "OXBOW" : 3.4, \
		"PALISADES" : 4., "PELTON" : 3.6, "PELTON REREG" : 3.5, \
		"POST FALLS" : 3.8, "PRIEST LAKE" : 4., "PRIEST RAPIDS" : 3.5, \
		"REVELSTOKE" : 4.5, "ROCK ISLAND" : 3.7, "ROCKY REACH" : 3.8, \
		"ROUND BUTTE" : 3.6, "SEVEN MILE" : 4.1, "SLOCAN" : 4.2, \
		"THE DALLES" : 3.3, "THOMPSON FALLS" : 3.8, "TIETON" : 3.8, \
		"UPPER BONNINGTON" : 4.2,	"UPPER FALLS" : 3.8, "WANAPUM" : 3.5, \
		"WANETA" : 4.,	"WELLS" : 4.}
	
	# Add NGVD29 elevations
	for path in paths:
		pathParts = path.split("/")# Split path name to separate out A through F parts.
		# This split has the following format: [u'', u'A part', u'B part', u'C part', u'Start time', u'E part', u'F part', u'']
		aPart = pathParts[1]
		bPart = pathParts[2]
		cPart = pathParts[3]
		dPart = pathParts[4]
		ePart = pathParts[5]
		fPart = pathParts[6]
		# Skip lots of paths if this is an FRA run:
		if computeOptions.isFrmCompute():
			CurrentEvent = computeOptions.getCurrentEventNumber()
			fPartCurrentEventText = "C:"+"%06d" % CurrentEvent+"|"
			if fPartCurrentEventText not in fPart:
				continue # Don't run unless it's the current event.
		if "ELEV" in cPart and  "NGVD29" not in cPart: # Skip any records that have the "NGVD29" string
			tsCont = dssFileObj.get(path)
			# Create the time series container. Make sure its properties are defined correctly.
			tsContNewFile = tsCont
			tsContNewFile.watershed = aPart
			tsContNewFile.location = bPart
			tsContNewFile.version = fPart
			for key in datumShiftDict.keys(): # Loop for all locations for which datum shifts defined
				if key in bPart: # Check to see if the BPart matches a datum shift location
					cPartNew = cPart+"-NGVD29" # Append a -NGVD29 to make it obvious
					# Test if FRA run
					if hasattr(tsContNewFile, 'yOrdinates'): # yOrdinates are present in paired data container objects, which are created in CRSO FRA post processing.
						for j in range(len(tsCont.yOrdinates)):
							try:
								for k in range(len(tsContNewFile.yOrdinates[j])):
									tsContNewFile.yOrdinates[j][k] = tsContNewFile.yOrdinates[j][k] - (datumShiftDict[key]) # Convert to NGVD29
									tsContNewFile.yparameter = cPartNew
									tsContNewFile.fullName = "/%s/%s/%s/%s/%s/%s/" % (aPart, bPart, cPartNew, dPart, ePart, fPart)
							except:
								alternative.addComputeMessage("Problem applying datum shift to "+path) # Note paths that couldn't process. Don't stop script.
								continue
					# Otherwise:
					else:
						try:
							for j in range(len(tsCont.values)):
								tsContNewFile.values[j] = tsContNewFile.values[j] - datumShiftDict[key]
								tsContNewFile.parameter = cPartNew
								tsContNewFile.fullName = "/%s/%s/%s//%s/%s/" % (aPart, bPart, cPartNew, ePart, fPart)
						except:
							alternative.addComputeMessage("Problem applying datum shift to "+path) # Note paths that couldn't process. Don't stop script.
							continue
							
					tsMathNewFile = TimeSeriesMath.createInstance(tsContNewFile)	 # This will work for time series containers or paired data containers.	
					dssFileObj.write(tsMathNewFile) # This will work for time series containers or paired data containers.		
	dssFileObj.done()
	
	elapsed = time.time() - t
	alternative.addComputeMessage("TIME WINDOW MODIFIER FINISHED RUNNING. COMPUTE TIME IS "+str(elapsed))
	
	print "\nComplete..."
	return runtimeWindow # Return and do not change runtimeWindow
	