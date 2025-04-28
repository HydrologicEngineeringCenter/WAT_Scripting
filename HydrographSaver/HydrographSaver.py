from hec.heclib.dss import HecDss
from hec.hecmath import TimeSeriesMath
import os.path


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
	currentAlternative.addComputeMessage("Computing ScriptingAlternative:" + currentAlternative.getName() )
	# get folder where realizations are stored - e.g. root runs folder for this simulation
	currentAlternative.addComputeMessage(computeOptions.getDssFilename())
	if computeOptions.isFrmCompute():
		# fra sim, use the folder with the OV file
		outputFolder = os.path.sep.join(computeOptions.getDssFilename().split(os.path.sep)[:-3])
	else:
		# deterministic sim, use the same folder
		outputFolder = os.path.basedir(computeOptions.getDssFilename())
	currentAlternative.addComputeMessage("directory: %s" % outputFolder)
	outputFilename = os.path.sep.join([outputFolder, "%s-collectedTimeSeriesRecords.dss" % computeOptions.getSimulationName()])
	currentAlternative.addComputeMessage("writing out to: %s" % outputFilename)
	outFile = HecDss.open(outputFilename)
	
	for odl in currentAlternative.getInputDataLocations():
		tsc = currentAlternative.getTimeSeriesForInputDataLocation(odl.getName(), odl.getParameter())
		if tsc is None:
			currentAlternative.addComputeErrorMessage("unable to read record for %s-%s, check model linking" % (odl.getName(), odl.getParameter()))
			continue
		tsc.fileName = outputFilename
		# rewrite f part appropriately
		path = tsc.fullName.split("/")
		if computeOptions.isFrmCompute():
			newFPart = tsc.version.split("|")[-1]
			collectionID = computeOptions.getCurrentLifecycleNumber()
			newFPart = "C:%06d|%s" % (collectionID, newFPart)
			tsc.version = newFPart
			path[-2] = newFPart
			tsc.fullName = "/".join(path)
		# TODO: merge if required
		# if HecDss . recordExists(tsc.fullName):
		# read as TSM, convert to TSM, merge, write
		currentAlternative.addComputeMessage("Event #%d: " % computeOptions.getCurrentEventNumber())
		if computeOptions.getCurrentEventNumber() == 1: # OR len(computeOptions.getEventList()) == 1
			outFile.put(tsc)
		else:
			# this is likely very inefficient to read and write with every TSC being added, but I am trying to keep this _simple!_
			# it also doesn't work great... use with caution.
			stw = computeOptions.getSimulationTimeWindow().toString()
			currentAlternative.addComputeMessage("reading previous data for %s" % stw)
			mergeToTSM = outFile.read(tsc.fullName, stw)
			mergedTSM = mergeToTSM.mergeTimeSeries(TimeSeriesMath(tsc))
			# this next step is to convert timeseries back when converted to irregular, I think this is an issue when gaps are added to the data)
			# Okay, it doesn't work well, so when the merge function results in irregular data, ¯\_(?)_/¯ 
			#mergedTSM = mergedTSM.transformTimeSeries("INT", "", path[5])
			mergedTSM.setVersion(tsc.version)
			outFile.write(mergedTSM)	
			
	outFile.done()
	return True
