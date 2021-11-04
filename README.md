# WAT_Scripting
Example Jython scripts for the Scripting Plugin and Time Window Modifier Plugin for HEC-WAT

## Scripting Plugin Scripts
A list of the example scripts with brief explanations:
### RMJOCII_ClimateChange
A script developed to pre-process data in a HEC-WAT Stochastic Data Importer compute, performing the following for a model:
 - Moving input files used by the HEC-ResSim model in the compute, using the lifecycle number to match data to a particular climate change projection.
 - Assembling another input file calculated from a recent 30-year window of hydrology, using the lifecycle number to match the projection.
 - Fix the timestamps on an input timeseries of forecasts for input to the `URC` plugin that calculates draft requirements.

 This script was developed by Evan Heisman (Walla Walla District) in support of the RMJOC-II Climate Change study.  Required input files are not provided.

### Ririe/Willow Creek Snow Accumulation
This script computes additional output variables from the snowmelt portion of the HEC-HMS model to help answer questions about snow accumulation versus snowmelt during rain-on-snow events.

The script was written by Eric Gabel (NWW) in support of the Ririe Dam Winter Inflow Volume Frequency study.

## Time Window Modifier Scripts

### Columbia Datum Shift
This script converts ResSim pool elevation and pool elevation targets from the modeled NAVD88 datum to NGVD29 datum that is more familiar to stakeholders.  Since the Scripting Plugin was not an option at the time, this script was initially developed as a TimeWindowModifier script (it does not modify the compute time window).  The script was written by Heather Baxter (NWD).

### Columbia Spring Season
This script computes a fixed time window for the April 1st through July 31st season which overrides any peak-based time window computed by the standard Time Window Modifier logic.  This script was used to set a shorter time window for HEC-FIA to compute damages resulting from a spring flood versus winter or annual flood damages.

### Event Peak / Breach
This script computes a timewindow based on the combination of a peak at a downstream location in the HEC-ResSim model and a state variable that indicates if any reserviors were modeled as breached due to a failure.  This was used to generate a combined time window for HEC-RAS that reduces the overall compute time to only include the combination of those two events.  Contact Evan Heisman (NWW) for the corresponding ResSim state variables.

