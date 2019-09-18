# WAT_Scripting
A repo to help store and share information about the scripting plugin in WAT

## Example Scripts
A list of the example scripts with brief explanations:
### ClimateChange-ScriptingPluginScript
A script developed to pre-process a HEC-WAT Stochastic Data Importer compute, performing the following for a model:
 - Moving input files used by the HEC-ResSim model in the compute, dependent on the lifecycle number to match with a particular climate change projection.
 - Assembling another input file calculated from a recent 30-year window of hydrology, dependent on the lifecycle number to match to the projection.
 - Performing some minor fixes to the timestamps on an input timeseries of forecasts for input to the `URC` program.

 This script was developed by Evan Heisman (Walla Walla District) in support of the RMJOC-II Climate Change study.  Required input files are not provided.

