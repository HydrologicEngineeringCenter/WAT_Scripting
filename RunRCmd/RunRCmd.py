"""
Example Script for writing a timeseries CSV and launching an external R script via a system call.  Could be adapted to many other models.
"""

import os
import json
from csv import DictWriter
from hec.script import Constants
from hec.heclib.util import HecTime
from hec.hecmath import TimeSeriesMath

def callR(scriptFile, args=[]):
	args = " " + " ".join(args)
	os.system(RScriptExe + " " + scriptFile + args)

def getOutputDir(opts):
	d = os.path.dirname(opts.getRunDirectory())
	d = d.replace("Scripting", "")
	if not os.path.exists(d):
		os.mkdir(d)
	return d

def writeScriptConfig(alt, opts):
	## Writes out a configuration file for R script to reference
	config = dict()

	# create run time window details
	rtw = opts.getRunTimeWindow()
	rtwDict = dict()
	rtwDict["Start Time"] = rtw.getStartTimeString()
	rtwDict["End Time"] = rtw.getEndTimeString()
	config["TimeWindow"] = rtwDict

	## Save realization and event seeds
	if opts.isFrmCompute():
		seedDict = dict()
    #  technically these aren't seeds as the dictionary name implies
		seedDict["Event Random"] = opts.getEventRandom()
		seedDict["Realization Random"] = opts.getRealizationRandom()
		seedDict["Lifecycle Random"] = opts.getLifeCycleRandom()
		config["Seeds"] = seedDict
		indexDict = dict()
		indexDict["Event Number"] = opts.getCurrentEventNumber()
		indexDict["Lifecycle Number"] = opts.getCurrentLifecycleNumber()
		indexDict["Realization Number"] = opts.getCurrentRealizationNumber()
		config["Indices"] = indexDict

	# get DSS output data:
	outputDict = dict()
	outputDict["Run Directory"] = opts.getRunDirectory()
	outputDict["Simulation Name"] = opts.getSimulationName()
	outputDict["DSS File"] = opts.getDssFilename()
	outputDict["F Part"] = opts.getFpart()
	config["Outputs"] = outputDict

	# create list of locations mapped in
	locations = alt.getInputDataLocations()
	config["locations"] = list()
	for loc in locations:
		locDict = dict()
		locDict["name"] = loc.getName()
		locDict["param"] = loc.getParameter()
		#locDict["type"] = loc.getType()
		#locDict["dssPath"] = loc.getDssPath()
		alt.addComputeWarningMessage(loc.getName())
		alt.addComputeMessage(loc.getParameter())
		config["locations"].append(locDict)

	# write to file
	d = getOutputDir(opts)
	configFilename = os.path.join(d, "rScriptConfig.json") 
	with open(configFilename, 'w') as out:
		out.write(json.dumps(config))
	
	return configFilename

def getValueAtTime(tsc, timestamp):
	# returns a value from tsc for the time that matches t; passing through once, no interpolation
	# set nearest to True to receive the previous valid value instead of undefined
	for t,v in zip(tsc.times, tsc.values):
		if t == timestamp:
			return v, True
	return Constants.UNDEFINED, False

def formatTime(t):
	# format expected by R script
	return "%d/%d/%d %02d:%02d" % (t.month(), t.day(), t.year(), t.hour(), t.minute())
	
def writeTsCSV(alt, opts, outTimestep=None, timestepColumn="GMT"):
	if outTimestep is None: outTimestep = alt.getTimeStep()
	
	# stash timeseries
	timeseries = dict()
	locationNames = list()
	for loc in alt.getInputDataLocations():
		locationNames.append(loc.getName())
		tsc = alt.loadTimeSeries(loc)
		hm = TimeSeriesMath(tsc).transformTimeSeries(outTimestep, "0M", "AVE")
		timeseries[loc.getName()] = hm.getData() # back to TSC
		for t,v in zip(timeseries[loc.getName()].times, timeseries[loc.getName()].values):
			ts = HecTime()
			ts.set(t)
			alt.addComputeMessage("\t" + ts.toString(104) + " : "  + str(v))
		
	d = os.path.dirname(opts.getRunDirectory())
	d = d.replace("Scripting", "")
	csvFilename = os.path.join(d, "obsTimeseries.csv")
	# CSV Format is as follows 
	#              GMT,Loc1,Loc2,Loc3
	#              10/1/1948 12:00,-8.087059,8.087059,-999
  # header column named GMT could be changed with timestepColumn arg, but GMT required for my purpose
	header = [timestepColumn] + locationNames
	with open(csvFilename, 'wb') as out:
		outCSV = DictWriter(out, header)
		outCSV.writeheader()
		# simply loop through timestamps and output values
		rtw = opts.getRunTimeWindow()	
    # optionally set the timestep for output not the alternative's predefined timestep (not required for WAT 1.1.0.682 and greater)
		#rtw.setTimeStep(alt.getTimeStep())
		i = 0
		timestep = rtw.getTimeAtStep(i)
		while timestep < rtw.getEndTime():
			row = dict()
			row[timestepColumn] = formatTime(timestep)
			# use valid row to only write data that exists - hack for mixing up timesteps
			validRow = False
			for loc in locationNames:
				row[loc], validValue = getValueAtTime(timeseries[loc], timestep.value())
				validRow = validRow or validValue
			if validRow:
				alt.addComputeMessage(str(row))
				outCSV.writerow(row)
			i += 1
			timestep = rtw.getTimeAtStep(i)
	return csvFilename
	
	
## Scripts to run
# initRScript gets run when this script initializes; not clear if this runs more than once.
initRScript = r"C:\Projects\WAT_R_Test\testInit.R"
# runRScript runs with access to computeOptions and currentAlternative objects
runRScript = r"C:\Projects\WAT_R_Test\testRun.R"

# R executable
RScriptExe = "\"C:\\Program Files\\R\\R-4.1.2\\bin\\Rscript.exe\""

## Init R Script (optional)
#callR(initRScript) 

##
#
# computeAlternative function is called when the ScriptingAlternative is computed.
# Arguments:
#   currentAlternative - the ScriptingAlternative. hec2.wat.plugin.java.impl.scripting.model.ScriptPluginAlt
#   computeOptions     - the compute options.  hec.wat.model.ComputeOptions
#
# return True if the script was successful, False if not.
# no explicit return will be treated as a successful return
#
##
def computeAlternative(currentAlternative, computeOptions):
	currentAlternative.addComputeMessage("Computing ScriptingAlternative:" + currentAlternative.getName())
	# write configuration for script - tells it compute timewindow and locations
  # script should be expected to find this.
	configFilename = writeScriptConfig(currentAlternative, computeOptions)

	# write timeseries - any mapped input DataLocations will be written to CSV.
	csvFilename = writeTsCSV(currentAlternative, computeOptions, outTimestep="1DAY")
	
	# run R script 
  # should pass in config and csv files as args, not currently done
	callR(runRScript, [configFilename, csvFilename])
	
	return True
