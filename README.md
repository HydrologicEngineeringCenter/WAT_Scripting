# WAT_Scripting
Example Jython scripts for the Scripting Plugin and Time Window Modifier Plugin for HEC-WAT.

These scripts are organized by folder and include the HEC-WAT Scripting Plugin or Time Window Modifier alternative and supporting files where available.  Authors have been identified to help place scripts in context, but cannot garantee any support in their use.

## Scripting Plugin Scripts
A list of the example scripts with brief explanations:

### RMJOC-II ClimateChange Pre-Processor
A script developed to pre-process data in a HEC-WAT Stochastic Data Importer compute, performing the following for a model:
 - Moving input files used by the HEC-ResSim model in the compute, using the lifecycle number to match data to a particular climate change projection.
 - Assembling another input file calculated from a recent 30-year window of hydrology, using the lifecycle number to match the projection.
 - Fix the timestamps on an input timeseries of forecasts for input to the `URC` plugin that calculates draft requirements.

 This script was developed by Evan Heisman in support of the RMJOC-II Climate Change study.  Required input files are not provided.

### Ririe/Willow Creek Snow Accumulation
This script computes additional output variables from the snowmelt portion of the HEC-HMS model to help answer questions about snow accumulation versus snowmelt during rain-on-snow events.  The identified output variables are computed as the difference in cumulative precipitation and snowpack between the begining and end of the event or over a shorter period.  The script was written by Eric Gabel (NWW) in support of the Ririe Dam Winter Inflow Volume Frequency study.

### RunRCmd
Relatively generic WAT compute script to launch an R command via a system call to `RScript` on Windows.  Only tested with a single input location and does not return an output data location.  Tested and used for a project to generate synthetic ensemble forecasts in support of Forecast Informed Reservoir Operations using the scripts from ![HEC-WAT Synthetic Forecast Ensembles](https://github.com/eheisman/hec-wat_syn-fcst-ensemble)

### Hydrograph Unscaler
Allows for merging several hydrographs sampled by Hydrologic Sampler into one, as a work around for generating short-duration flood events within the context of a longer duration season.  This script "unscales" hydrographs indicated by "-UNSCALED" in the location name, returning them to their initial magnitude (adjusted by Hydrologic Sampler) and then adds them together to create one output hydrograph.

### Hydrograph Saver
On a non-distributed HEC-WAT compute, this script saves any timeseries that are linked into it as an input data location  to a single .DSS file, collapsing the f-part to have a collection ID for each lifecycle.  Currently only works for continuous event lifecycles which have a single collection ID per lifecycle, as merging DSS record functionality needs to be added.  _TO USE:_ Add this script at the end of the program order in a simulation, adding Input Data Locations for each record to be saved, and then use the model linking editor to identify which model outputs need to be saved.  When the compute runs, a DSS file in the simulation's output directory will be created (parallel to the output variable file) that saves the timeseries data for later analysis.

## Time Window Modifier Scripts

### Columbia Datum Shift
This script converts ResSim pool elevation and pool elevation targets from the modeled NAVD88 datum to NGVD29 datum that is more familiar to stakeholders.  Since the Scripting Plugin was not an option at the time, this script was initially developed as a TimeWindowModifier script (it does not modify the compute time window).

### Columbia Spring Season
This script computes a fixed time window for the April 1st through July 31st season which overrides any peak-based time window computed by the standard Time Window Modifier logic.  This script was used to set a shorter time window for HEC-FIA to compute damages resulting from a spring flood versus winter or annual flood damages.

### Event Peak / Breach
This script computes a timewindow based on the combination of a peak at a downstream location in the HEC-ResSim model and a state variable that indicates if any reserviors were modeled as breached due to a failure.  This was used to generate a combined time window for HEC-RAS that reduces the overall compute time to only include the combination of those two events.  Contact Evan Heisman (@eheisman) for the corresponding HEC-ResSim state variables.
