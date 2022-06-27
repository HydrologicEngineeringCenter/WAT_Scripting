import os
import json
from csv import DictWriter
import subprocess
from hec.script import Constants
from hec.heclib.util import HecTime
from hec.hecmath import TimeSeriesMath


scriptConfigFilename = "synForecasts/forecastConfig.json"

def callR(scriptFile, opts, args=[], relativeScript=True, relativeR=False, shell=False):
	watershedDir = opts.getRunDirectory().split("runs")[0]

	# load config file to find R
	with open(os.path.join(watershedDir, scriptConfigFilename), 'r') as configFile:
		scriptConfig = json.load(configFile)
	RScriptExe = scriptConfig["r_config"]["RScriptExe"]
	# RScript.exe gets used because the --vanilla option allows us to have a clean environment

	# if script file isn't provided, load the one from the config file
	if scriptFile is None:
		scriptFile = scriptConfig["r_config"]["RScriptFile"]

	if relativeR: # use R in the watershed
		RScriptExe = os.path.join(watershedDir, "R_install", RScriptExe)	
	if relativeScript:  # use scripts in the watershed
		scriptFile = os.path.join(watershedDir, scriptFile)
	# assemble command
	#cmdLine = RScriptExe + " --vanilla " + stringWrap(scriptFile) + " " + " ".join(args)
	#if shell:
	#	cmdLine = "cmd /c " + "'%s'" % cmdLine
	
	
	cmdLine = []
	cmdLine += [RScriptExe, "--vanilla", stringWrap(scriptFile)] + args
	# I need to clean this up, I cannot make it launch a separate shell to monitor the process
	# this appears to not work with spaces in the arguments
	if shell: cmdLine = ["start", "cmd", "/k ^\n", " ".join(cmdLine)] #+ cmdLine
	# quotations around the program being called can make a big difference here.
	subprocess.call(" ".join(cmdLine), shell=shell) # This works if shell=False
	# TODO: use Popen class to facilitate communication back to WAT.
	#p = subprocess.Popen(cmdLine, shell=True) 
	#p.wait()
	return " ".join(cmdLine)

#def getLocationFilename(locationName):
#	for c in [' ', '..', '.', '/', '\\', ':', ',']:
#		locationName = locationName.replace(c, "_")
#	return locationName	

def getOutputDir(opts):
	d = os.path.dirname(opts.getRunDirectory())
	d = d.replace("Scripting", "")
	if not os.path.exists(d):
		os.mkdir(d)
	return d

def stringWrap(s, force=False):
	#quotes = ["'", "\"",]
	#if not force and (s[0] in quotes) and (s[-1] in quotes):
	#	return s
	#else:
	return "\"%s\"" % s

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
		# not technically seeds, but these can be used to generate a seed for the R script
		randomDict = dict()
		randomDict["Event Random"] = opts.getEventRandom()
		randomDict["Realization Random"] = opts.getRealizationRandom()
		randomDict["Lifecycle Random"] = opts.getLifeCycleRandom()
		config["Randoms"] = randomDict
		indexDict = dict()
		indexDict["Event Number"] = opts.getCurrentEventNumber()
		indexDict["Lifecycle Number"] = opts.getCurrentLifecycleNumber()
		indexDict["Realization Number"] = opts.getCurrentRealizationNumber()
		config["Indices"] = indexDict

	# get DSS output data:
	outputDict = dict()
	outputDict["Run Directory"] = opts.getRunDirectory()
	watershedDir = opts.getRunDirectory().split("runs")[0]
	outputDict["Watershed Directory"] = watershedDir
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
		#alt.addComputeWarningMessage(loc.getName())
		#alt.addComputeMessage(loc.getParameter())
		config["locations"].append(locDict)

	# write to file
	d = getOutputDir(opts)
	configFilename = os.path.join(d, "rScriptConfig.json") 
	with open(configFilename, 'w') as out:
		out.write(json.dumps(config))
	
	return stringWrap(configFilename)

def getValueAtTime(tsc, timestamp):
	# returns a value from tsc for the time that matches t; passing through once, no interpolation
	# set nearest to True to receive the previous valid value instead of undefined
	for t,v in zip(tsc.times, tsc.values):
		if t == timestamp:
			return v, True
	return Constants.UNDEFINED, False

# TODO: use Python's datetime or simular to handle this with a format string for flexibility
def formatTime(t):
	# format expected by R script
	return "%d/%d/%d %02d:%02d" % (t.month(), t.day(), t.year(), t.hour(), t.minute())
	
def writeTsCSV(alt, opts, outTimestep=None, timestampColumnName="timestamp"):
	if outTimestep is None: outTimestep = alt.getTimeStep()
	
	# stash timeseries
	timeseries = dict()
	locationNames = list()
	for loc in alt.getInputDataLocations():
		locationNames.append(loc.getName())
		tsc = alt.loadTimeSeries(loc)
		hm = TimeSeriesMath(tsc).transformTimeSeries(outTimestep, "0M", "AVE")
		timeseries[loc.getName()] = hm.getData() # back to TSC
		#for t,v in zip(timeseries[loc.getName()].times, timeseries[loc.getName()].values):
		#	#ts = HecTime()
		#	#ts.set(t)
		#	#alt.addComputeMessage("\t" + ts.toString(104) + " : "  + str(v))
		
	d = os.path.dirname(opts.getRunDirectory())
	d = d.replace("Scripting", "")
	csvFilename = os.path.join(d, "obsTimeseries.csv")
	# CSV Format is as follows 
	#              GMT,Loc1,Loc2,Loc3
	#              10/1/1948 12:00,,,-8.087059,8.087059,-999
	# this doesn't have to be GMT, but this works for the script I am going to be running.
	header = [timestampColumnName] + locationNames
	with open(csvFilename, 'wb') as out:
		outCSV = DictWriter(out, header)
		outCSV.writeheader()
		# simply loop through timestamps and output values
		rtw = opts.getRunTimeWindow()	
		#rtw.setTimeStep(alt.getTimeStep())
		#alt.addComputeMessage(str(rtw.getNumSteps())) # getNumSteps returns negative number?
		#alt.addComputeMessage("rtw is valid: " + str(rtw.isValid()))
		#alt.addComputeMessage("start: " + str(rtw.getStartTime()))
		#alt.addComputeMessage("end: " + str(rtw.getEndTime()))
		#alt.addComputeMessage("lookback: " + str(rtw.getLookbackTime()))
		i = 0
		timestep = rtw.getTimeAtStep(i)
		while timestep < rtw.getEndTime():
			row = dict()
			row[timestampColumnName] = formatTime(timestep)
			# use valid row to only write data that exists - hack for mixing up timesteps
			validRow = False
			for loc in locationNames:
				row[loc], validValue = getValueAtTime(timeseries[loc], timestep.value())
				validRow = validRow or validValue
			if validRow:
				#alt.addComputeMessage(str(row))
				outCSV.writerow(row)
			i += 1
			timestep = rtw.getTimeAtStep(i)
	return stringWrap(csvFilename)
	
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
	configFile = writeScriptConfig(currentAlternative, computeOptions)

	# write timeseries
	dataFile = writeTsCSV(currentAlternative, computeOptions, outTimestep="1DAY", timestampColumnName="GMT")
	
	# run R compute function here 
	rScriptFile = None #r"synForecasts\wat_launcher.R"
	currentAlternative.addComputeMessage(callR(rScriptFile, computeOptions, [configFile, dataFile], relativeScript=True))
	
	return True
