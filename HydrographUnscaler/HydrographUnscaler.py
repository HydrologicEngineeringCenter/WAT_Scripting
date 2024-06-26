
from com.rma.io import DssFileManagerImpl
from hec.hecmath import TimeSeriesMath

## Hydrograph Unscaler script for HEC-WAT
# Amanda Walsh and Evan Heisman, USACE-IWR-HEC
#
# Merges several hydrographs, optionally "unscaling" if "unscaled" is in the location name for the input DataLocation
# useful for merging together several hydrographs generated by Hydrologic Sampler when trying to "insert" a flood into a longer duration hydrograph.
# longer duration hydrograph is typically not scaled, but as Hydrologic Sampler doesn't offer this option, it uses the first value to scale it back down.  This works when the first value of the hydrograph being unscaled is set to "1" in the source shape set.


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
	output = None
	currentAlternative.addComputeMessage("Computing ScriptingAlternative:" + currentAlternative.getName() )

	# for each data location
	for loc in currentAlternative.getInputDataLocations():
		currentAlternative.addComputeMessage(loc.getName())
		# 1. read time series
		tsc = currentAlternative.loadTimeSeries(loc)
	
		# 2. get first value
		firstVal = tsc.values[0]
		# 3. divide time series by first value
		hm = TimeSeriesMath(tsc)
		if "UNSCALED" in loc.getName().upper():
			#currentAlternative.addComputeMessage("unscaling")
			hm = hm.divide(firstVal)
		# 4. add to output
		if output is None:
			#currentAlternative.addComputeMessage("first hydrograph")
			output = hm
		else: 
			currentAlternative.addComputeMessage("adding hydrograph")
			output = output.add(hm)
	# write output
	dfm = DssFileManagerImpl.getDssFileManager()
	odl = currentAlternative.getOutputDataLocations()[0]
	# tsc = currentAlternative.createOutputTimeSeries(odl)
	output.setPathname(odl.getDssPath())
	# hm.setVersion(writeTimeSeries(hec.io.TimeSeriesContainer))
	# dfm.write(hm.getData())
	currentAlternative.writeTimeSeries(output.getData())
				

	return True
