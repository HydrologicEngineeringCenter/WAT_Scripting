from hec.heclib.dss import HecDss
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
		if computeOptions.isFrmCompute():
			newFPart = tsc.version.split("|")[-1]
			collectionID = computeOptions.getCurrentLifecycleNumber()
			newFPart = "C:%06d|%s" % (collectionID, newFPart)
			tsc.version = newFPart
			path = tsc.fullName.split("/")
			path[-2] = newFPart
			tsc.fullName = "/".join(path)
		# TODO: merge if required
		# if HecDss . recordExists(tsc.fullName):
		# read as TSM, convert to TSM, merge, write
		outFile.put(tsc)

	outFile.done()
	return True
