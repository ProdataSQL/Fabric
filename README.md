# Fabric

This contains random examples of code snippets for Microsoft Fabric. Particulary stuff we couldn't find documented.
All of these examples can use various auth methods such as Managed Identity, Visual Studio and VS Code.
## [01_SqlClientAAD](01_SqlClientAAD/)
Example of using Azure.Identity with SqlClient to authenticate to a Fabric SQL EndPoint.


## [02_PipelineExecute](02_PipelineExecute/)
Example of using Azure.Identity with HttpClient to authenticate to a Fabric Pipeline and execute it. 
This interacts with the api the same way the web client would when requesting a pipeline execution.

## [03_CopyBlobOneLake](03_CopyBlobOneLake/)
Example of using Azure.Identity with HttpClient to copy a Blob across the OneLake.
This is a basic example of a rest call to copy a file on a onelake.

## [04_PauseFabricCapacity](04_PauseFabricCapacity/)
Example of using Azure.Identity with HttpClient to authenticate to a Fabric Capcity and Suspend it.
This is the same management api as used in a web browser. Will fail if capacity is already paused

## [05_ResumeFabricCapacity](05_ResumeFabricCapicty/)
Example of using Azure.Identity with HttpClient to authenticate to a Fabric Capcity and Resume it.
This is the same management api as used in a web browser. Will fail if capacity is already running.

## [06_RefreshPowerBIDataset](06_RefreshPowerBIDataset/)
Example of using Python API to refresh PowerBI datasets within workspaces.

## [07_SharePoint](07_SharePoint/)
Sample Fabric Notebooks and builtin python class to Integrate Sharepoint and Fabric using Graph API.

## [09_sp_WhoIsActive](09_sp_WhoIsActive/)
Monitoring script for Fabric DW to show requests, sessions and blocking. This has moved to https://github.com/ProdataSQL/FabricWhoIsActive
