from hec.hecmath import TimeSeriesMath
from com.rma.io import DssFileManagerImpl

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
	#write_example_dl(currentAlternative)
	for odl in currentAlternative.getOutputDataLocations():
		locName = odl.getName()
		paramName = odl.getParameter()

		# if there are commands, process them into a dictionary
		# use anything after a colon as the commands
		# e.g. "location1-unreg:FMA=72" will compute the 72hr unreg flow forward moving average.
		settings = dict()
		if ":" in locName:
			locName, commands = locName.split(":")
			for cmd in commands.split(" "):
				if "=" in cmd:
					k,v = cmd.split("=")
					# store as upper case, don't do anything with the value, as it could be anything.
					settings[k.upper()] = v
	
		# read timeseries
		#idl = currentAlternative.getInputDataLocation(locName, paramName)
		tsm = TimeSeriesMath(currentAlternative.getTimeSeriesForInputDataLocation(locName,paramName))
	
		# compute forward moving average on N timesteps
		if "FMA" in settings.keys():
			nAvg = int(settings["FMA"])
			tsm = tsm.forwardMovingAverage(nAvg)
		tsm.setLocation(odl.getName())
  		tsm.setParameterPart(odl.getParameter())  #NEW!  This is important for the OutputVariables to work correctly.
		currentAlternative.writeTimeSeries(tsm.getData())
		currentAlternative.addComputeMessage("\tsuccesfully computed for output %s:%s" % (odl.getName(), odl.getParameter()))
	return True
