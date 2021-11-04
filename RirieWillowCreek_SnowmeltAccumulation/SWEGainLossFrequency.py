# Imports
from hec.heclib.dss import HecDss
import sys

# Get required paths from main sequence
def computeAlternative(currentAlternative, computeOptions):
    # Add shared variables
    modulePath = currentAlternative.getAbsolutePath("scripts")
    sys.path.append(modulePath)
    import pathAndNameManager # This was created seperately/custom

    # Get alternative and analysis period names, & start building fPart
    simName = computeOptions.getSimulationName()
    altName, apName = simName.split("-")
    fPart =  "%#.10s:%s:HMS-(MCA)Full Uncertainty" % (altName, apName)
    
    # Get event number 
    eventNumber = computeOptions.getCurrentEventNumber()
    
    # Format fPart with event ID
    fPart = "C:%06d|%s" % (eventNumber, fPart)
    
    # Create and store shared variables
    # pathAndNameManager.graysLake = "//GRAYS LAKE/SWE//1DAY/%s/" % (fPart) 
    pathAndNameManager.ririeLocal = "//RIRIE LOCAL/SWE//1DAY/%s/" % (fPart)
    pathAndNameManager.ririeUpstream = "//RIRIE UPSTREAM/SWE//1DAY/%s/" % (fPart)
    pathAndNameManager.dssFileName = computeOptions.getDssFilename() 
    
    # Prevent this path from accumulating every run
    sys.path.remove(modulePath)

    return True

# Output variable sequence
def computeOutputVariable(currentAlternative, currentVariable):
    # Add shared variables
    modulePath = currentAlternative.getAbsolutePath("scripts")
    sys.path.append(modulePath)
    import pathAndNameManager # This was created seperately/custom
    
    # Open dss file
    dssFile = HecDss.open(pathAndNameManager.dssFileName)

    # Check variable
        # Open SWE, calculate delta SWE, and store result
    
    # Storm only calc
    # if currentVariable.getName() == "GraysLakeDeltaSWEStorm":
        # myTSC = dssFile.get(pathAndNameManager.graysLake, True)
        # GraysLakeDeltaSWE = myTSC.values[4] - myTSC.values[2]
        # currentVariable.setValue(GraysLakeDeltaSWE)
        
    if currentVariable.getName() == "RirieLocalDeltaSWEStorm":
        myTSC = dssFile.get(pathAndNameManager.ririeLocal, True)
        RirieLocalDeltaSWE = myTSC.values[4] - myTSC.values[2] 
        currentVariable.setValue(RirieLocalDeltaSWE)
        
    elif currentVariable.getName() == "RirieUpstreamDeltaSWEStorm":
        myTSC = dssFile.get(pathAndNameManager.ririeUpstream, True)
        RirieUpstreamDeltaSWE = myTSC.values[4] - myTSC.values[2] 
        currentVariable.setValue(RirieUpstreamDeltaSWE)
    
    # One week centered on storm
    # elif currentVariable.getName() == "GraysLakeDeltaSWECenteredWeek":
        # myTSC = dssFile.get(pathAndNameManager.graysLake, True)
        # GraysLakeDeltaSWE = myTSC.values[6] - myTSC.values[0]
        # currentVariable.setValue(GraysLakeDeltaSWE)
        
    # elif currentVariable.getName() == "RirieLocalDeltaSWECenteredWeek":
        # myTSC = dssFile.get(pathAndNameManager.ririeLocal, True)
        # RirieLocalDeltaSWE = myTSC.values[6] - myTSC.values[0] 
        # currentVariable.setValue(RirieLocalDeltaSWE)
        
    # elif currentVariable.getName() == "RirieUpstreamDeltaSWECenteredWeek":
        # myTSC = dssFile.get(pathAndNameManager.ririeUpstream, True)
        # RirieUpstreamDeltaSWE = myTSC.values[6] - myTSC.values[0] 
        # currentVariable.setValue(RirieUpstreamDeltaSWE)
        
    # First 10 days
    # elif currentVariable.getName() == "GraysLakeDeltaSWEFirstTen":
        # myTSC = dssFile.get(pathAndNameManager.graysLake, True)
        # GraysLakeDeltaSWE = myTSC.values[9] - myTSC.values[0]
        # currentVariable.setValue(GraysLakeDeltaSWE)
        
    # elif currentVariable.getName() == "RirieLocalDeltaSWEFirstTen":
        # myTSC = dssFile.get(pathAndNameManager.ririeLocal, True)
        # RirieLocalDeltaSWE = myTSC.values[9] - myTSC.values[0] 
        # currentVariable.setValue(RirieLocalDeltaSWE)
        
    # elif currentVariable.getName() == "RirieUpstreamDeltaSWEFirstTen":
        # myTSC = dssFile.get(pathAndNameManager.ririeUpstream, True)
        # RirieUpstreamDeltaSWE = myTSC.values[9] - myTSC.values[0] 
        # currentVariable.setValue(RirieUpstreamDeltaSWE)
    
    # Full sequence
    # elif currentVariable.getName() == "GraysLakeDeltaSWEAll":
        # myTSC = dssFile.get(pathAndNameManager.graysLake, True)
        # GraysLakeDeltaSWE = myTSC.values[14] - myTSC.values[0]
        # currentVariable.setValue(GraysLakeDeltaSWE)
        
    elif currentVariable.getName() == "RirieLocalDeltaSWEAll":
        myTSC = dssFile.get(pathAndNameManager.ririeLocal, True)
        RirieLocalDeltaSWE = myTSC.values[14] - myTSC.values[0] 
        currentVariable.setValue(RirieLocalDeltaSWE)
        
    elif currentVariable.getName() == "RirieUpstreamDeltaSWEAll":
        myTSC = dssFile.get(pathAndNameManager.ririeUpstream, True)
        RirieUpstreamDeltaSWE = myTSC.values[14] - myTSC.values[0] 
        currentVariable.setValue(RirieUpstreamDeltaSWE)
        
        # Prevent this path from accumulating every run - Located here to only run once
        sys.path.remove(modulePath)
        
    # Close the DSS file
    dssFile.done()
    
    return True