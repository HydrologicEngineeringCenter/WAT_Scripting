# if any breach occurs, use breach window (first to last value > 0)
# if no breach occurs, use +/- N-days
from hec.hecmath import TimeSeriesMath
from hec.hecmath import DSS
from hec.heclib.util import HecTime


# script entry point for TimeWindow modification.
# arguments:
# runTimeWindow - the runtime window after all the other time window modifications have been applied
# alternative - the TimeWindowAlternative
# computeOptions - the ComputeOptions passed to the TimeWindowMod plugin
#
# Return:
#  the new runtime window.  If nil is returned a compute error is raised
#
# buffer time window around breach for RAS
RAS_START_BUFFER = 3 # days
RAS_END_BUFFER = 1 # days

def timeWindowMod(runtimeWindow, alternative, computeOptions):
	originalRTW = computeOptions.getRunTimeWindow()
	
	dssFile = DSS.open(computeOptions.getDssFilename(), originalRTW.getTimeWindowString())
	# pathname for breaches
	twmTSM = TimeSeriesMath(alternative.getTimeSeries()) # assumes this is the mapped input to TWM
	twmPath = twmTSM.getPath().split("/") # use this for e/f parts
	breachPath = "/".join(["", "","BREACHTRACKER-TIMESTEPS REMAINING","TIMESTEPS REMAINING","",twmPath[5], twmPath[6], ""])

	# find start and end of breach timeseries
	breaches = dssFile.read(breachPath)
	dssFile.done()
	breachTSC = breaches.getData()
	
	start, end = None, None
	rtwStart = runtimeWindow.getStartTime().value()
	newStart = HecTime() # keep track of start time that is a valid ResSim timestep
	for t,v in zip(breachTSC.times, breachTSC.values):
		if v > 0:
			if start is None: # first non-zero
				start = t
			end = t
		# update until original start time occurs, make sure this is prev. timestep in ResSim
		# avoids interpolated input on start timestep in RAS
		if t <= rtwStart:
			newStart.set(t)

	# no breach
	if start is None: 
		runtimeWindow.setStartTime(newStart)
		return runtimeWindow

	# compare and adjust if needed
	startTime = HecTime()
	startTime.set(start)
	startTime.subtractDays(RAS_START_BUFFER) # add days to give RAS a little spin up time
	if startTime <= runtimeWindow.getStartTime():
		runtimeWindow.setStartTime(startTime)
		
	endTime = HecTime()
	endTime.set(end)
	endTime.addDays(RAS_END_BUFFER) # buffer at end
	if endTime >= runtimeWindow.getEndTime():
		runtimeWindow.setEndTime(endTime)

	alternative.addComputeMessage("New time window set: %s" % runtimeWindow.getTimeWindowString())
	
	return runtimeWindow