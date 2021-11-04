# script entry point for TimeWindow modification.
# arguments:
# runTimeWindow - the runtime window after all the other time window modifications have been applied
# alternative - the TimeWindowAlternative
# computeOptions - the ComputeOptions passed to the TimeWindowMod plugin
#
# Return: 
#  the new runtime window.  If nil is returned a compute error is raised
#
from hec.model import RunTimeWindow

def timeWindowMod(runtimeWindow, alternative, computeOptions):
    start = runtimeWindow.getStartTime()
    end = runtimeWindow.getEndTime()
    wy = end.year()
    # use apr-jul to capture spring peak from knn
    start.setYearMonthDay(wy, 4, 1, 0000)
    end.setYearMonthDay(wy, 7, 31, 24*60)
    newTimeWindow = RunTimeWindow()
    newTimeWindow.setStartTime(start)
    newTimeWindow.setEndTime(end)
    #alternative.addComputeErrorMessage("Cropped TimeWindow is " + runtimeWindow.toString());
    return newTimeWindow