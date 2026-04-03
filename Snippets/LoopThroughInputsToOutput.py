# This is a snippet to include in another script that loops through input data locations does a transform, and writes to an output data location with the same name.  The Scripting Alternative must be configured with these data locations having identical names.

from hec.hecmath import TimeSeriesMath

def createDailyAverageForForecasts(alt, opts):
	"""
	"""
	for inputLoc in alt.getInputDataLocations():
		inputTSM = TimeSeriesMath(alt.loadTimeSeries(inputLoc))
		# see https://www.hec.usace.army.mil/confluence/dssdocs/dssvueum/scripting/math-functions
		# Computes daily average anchored at midnight end-of-day.  offsetString can be used to shift the calculation, but leaving blank.
		offsetString = ""
		dailyTSM = inputTSM.transformTimeSeries(alt.getTimeStep(), offsetString, "AVE")
		# this ensures the output data location is used.
		outputLoc = currentAlternative.getOutputDataLocation(inputLoc.getName(), inputLoc.getParameter())
		dailyTSM.setPathname(outputLoc.getDssPath())
		alt.writeTimeSeries(dailyTSM.getData())
