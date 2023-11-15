## 07_SharePoint
Example Fabric Notebook with SharePoint Integration an AAD Service Principle and Graph API.
This allows Notebooks to seamlessly download file and folders from SharePoint.

What you will need 
- ClientID and Secret for Service Principle (details below). Our sample assumes that the Secret is in Keyvault.
- TenantID for AAD where the app regsistration has been added.
- A Sharepoint Site, Library, optional Folder and some sample files
- A Fabric Workspace with Notebooks

**Pre-Requisite
You will need to create the service principle and assign Sharepoint permissions to the service principle for the target site.
This process is very well documented in the blog here
https://sposcripts.com/download-files-from-sharepoint-using-graph/

Sample Code below to download files, including wildard support
<pre><code class='python'>
ConnectionSettings = '{"library": "Unittest", "tenant_id":"xxxxxxxx-xxxx--xxxx-xxxxxxxxxxxx","app_client_id":"app-fabricdw-dev-clientid","app_client_secret":"app-fabricdw-dev-clientsecret","keyvault":"kv-fabric-dev","sharepoint_url":"prodata365.sharepoint.com","site":"Fabric"}'
SourceSettings = '{}'
SourceDirectory = 'tst'
TargetDirectory = 'unittest/AW/tst'
SourceObject = '*.xlsx'
TargetFileName = ''
TargetSettings = ''   

from builtin.sharepoint import Sharepoint,AuthToken
import pandas
import json
from os.path import join
from pathlib import Path

SourceSettings = SourceSettings or '{}'
ConnectionSettings = ConnectionSettings or '{}'
source_connection_options = json.loads(ConnectionSettings)
source_options = json.loads(SourceSettings)

auth_token = AuthToken(**source_connection_options)
sharepoint = Sharepoint(auth_token, folder=SourceDirectory, file=SourceObject, **source_options, **source_connection_options)

files = sharepoint.get_file_bytes()

for file_name, file_bytes in files.items():
    Path(join("/lakehouse/default/Files/",TargetDirectory)).mkdir(parents=True, exist_ok=True)

    with open(join("/lakehouse/default/Files/",TargetDirectory,file_name), "wb") as f:
        f.write(file_bytes.getbuffer())
</code></pre>
  
