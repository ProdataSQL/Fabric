from io import BytesIO
import requests
import pandas
import fnmatch
from pandas import ExcelFile, DataFrame
try:
    from notebookutils import mssparkutils
    USE_MSSPARKUTILS = True
except ModuleNotFoundError:
    USE_MSSPARKUTILS = False
# while this can be in the except statement - importing modules in an except
# confuses linters -_-
if not USE_MSSPARKUTILS:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
class AuthToken:
    """Class to retrieve token from tenant id, client id, seceret and scope.

    :param str token_url: https://login.microsoftonline.com/
    :param str tenant_id:
    :param str app_client_id: The id or keyvault secret name (if keyvault URL provided).
    :param str app_client_secret: The id or keyvault secret name (if keyvault URL provided).
    :param str scope: https://graph.microsoft.com/
    :param str keyvault_url: https://{key-vault-name}.vault.azure.net/ or {key-vault-name}.
    """

    def __init__(
        self,
        tenant_id,
        app_client_id,
        app_client_secret,
        scope="https://graph.microsoft.com/",
        keyvault: str or None = None,
        token_url: str or None = "https://login.microsoftonline.com/",
        **args
    ):
        self.access_token = None
        # Set the Token URL for Azure AD Endpoint
        if token_url is not None:
            self.token_url = f"{token_url}{tenant_id}/oauth2/token"
        else:
            self.token_url = (
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
            )
        if keyvault:
            if not keyvault.startswith("https://"):
                keyvault = f"https://{keyvault}.vault.azure.net/"
            if USE_MSSPARKUTILS:
                app_client_id = mssparkutils.credentials.getSecret(
                    keyvault, app_client_id
                )
                app_client_secret = mssparkutils.credentials.getSecret(
                    keyvault, app_client_secret
                )
            else:
                secret_client = SecretClient(
                    vault_url=keyvault, credential=DefaultAzureCredential()
                )
                app_client_id = secret_client.get_secret(app_client_id).value
                app_client_secret = secret_client.get_secret(app_client_secret).value

        self.set_token(app_client_id, app_client_secret, scope)

    def set_token(self, client_id, client_secret, scope):
        """Sets the classes token value.
        :param str client_id:
        :param str client_secret:
        :param str scope:
        :return: None
        """
        
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": scope,
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
class Sharepoint():
    def __init__(self, auth_token : AuthToken, sharepoint_url = None, site=None, library=None, folder=None, file=None,**args):
        self.sharepoint_url = sharepoint_url
        self.site = site
        self.library = library
        self.folder = folder
        self.file = file
        self.headers = {"Authorization": f"Bearer {auth_token.access_token}"}
    def get_site_id_by_name(self, sharepoint_url= None, site_name = None):
        sharepoint_url = sharepoint_url or self.sharepoint_url
        site_name = site_name or self.site
        if not sharepoint_url:
            raise ValueError("sharepoint_url cannot be None or blank.")
        if not site_name:
            raise ValueError("site_name cannot be None or blank.")

        url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_url}:/sites/{site_name}?$select=id"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            **self.headers
        }

        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()

        return response.json()["id"]


    def get_drive_id_by_name(self, site_id, library_name=None):
        library_name = library_name or self.library
        if (not site_id):
            raise ValueError("site_id cannot be None or blank.")
        if (not library_name):
            raise ValueError("library_name cannot be None or blank.")
            
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            **self.headers
        }

        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()

        drives = response.json()["value"]
        for drive in drives:
            if drive["name"] == library_name:
                return drive["id"]    
        raise Exception("Drive name was not found.")

    def get_folder_id_by_name(self,site_id, drive_id, folder_name=None):
        folder_name = folder_name or self.folder
        if (not site_id):
            raise ValueError("site_id cannot be None or blank.")
        if (not drive_id):
            raise ValueError("drive_id cannot be None or blank.")
        if (not folder_name):
            raise ValueError("folder_name cannot be None or blank.")
        url = f"http://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root:/{folder_name}"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            **self.headers
        }

        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()
        
        return response.json()["id"]

    def get_file_url_by_name(self, site_id, drive_id, folder_id, file_name=None):
        file_name = file_name or self.file
        if not site_id or not drive_id or not folder_id or not file_name:
            raise ValueError("site_id, drive_id, folder_id, and file_name cannot be None or blank.")

        url = f"http://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{folder_id}/children"
        headers = {
            **self.headers
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            print(f"File not found: {file_name}")
            return {}  # Return an empty dictionary if no matching files are found
        response.raise_for_status()

        files_returned = {}
        files = response.json()["value"]

        for file in files:
            if fnmatch.fnmatch(file["name"], file_name):
                files_returned[file["name"]] = file["@microsoft.graph.downloadUrl"]

        return files_returned
        
    def get_file_bytes(self, sharepoint_url:str | None =None, site_name:str | None=None,\
                             library_name:str | None=None, folder_name:str | None=None, file_name:str | None=None) -> dict[str,BytesIO]:
        sharepoint_url = sharepoint_url or self.sharepoint_url
        site_name = site_name or self.site
        library_name = library_name or self.library
        folder_name = folder_name or self.folder
        file_name = file_name or self.file
        
        site_id = self.get_site_id_by_name(sharepoint_url, site_name)
        drive_id = self.get_drive_id_by_name(site_id, library_name)
        folder_id = self.get_folder_id_by_name(site_id, drive_id, folder_name)
        file_url = self.get_file_url_by_name(site_id,drive_id,folder_id, file_name)
        
        file_return = {}
        for file, url in file_url.items():
            response = requests.request("GET", url=file_url[file])
            if response.status_code == 404:
                print(f"File not found: {file}")
                continue  # Skip this file if it's not found
            response.raise_for_status()
            
            file_return[file] = BytesIO(response.content)
        return file_return
        
    def get_excel_file(self, sharepoint_url:str | None =None, site_name:str | None=None,\
                             library_name:str | None=None, folder_name:str | None=None, file_name: str | None = None) -> ExcelFile:
        sharepoint_url = sharepoint_url or self.sharepoint_url
        site_name = site_name or self.site
        library_name = library_name or self.library
        folder_name = folder_name or self.folder
        file_name = file_name or self.file
        if not file_name: raise Exception("Filename cannot be none.")
        if  '*' in file_name  or "%" in file_name:
            raise Exception("Wildcard name not supported for excel files.")
        file = self.get_file_bytes(sharepoint_url,site_name,library_name,folder_name, file_name)

        return ExcelFile(file[file_name])
def df_from_excel(excel_file : ExcelFile, sheet_name):
    if not sheet_name: # checks if empty or None
        yield (excel_file.sheet_names[0],pandas.read_excel(excel_file))
    elif sheet_name == "*":
        for sheet in excel_file.sheet_names:
            yield (sheet,pandas.read_excel(excel_file, sheet_name=sheet))
    else:
        for sheet in sheet_name.split(","):
            yield (sheet,pandas.read_excel(excel_file, sheet_name=sheet))

if __name__ == "__main__":
    import pandas
    import json
    from os.path import join
    from pathlib import Path

    # Environment parameters
    SourceConnectionSettings='{"tenant_id":"d8ca992a-5fbe-40b2-9b8b-844e198c4c94","app_client_id":"app-fabricdw-dev-clientid", "app_client_secret":"app-fabricdw-dev-clientsecret","keyvault":"kv-fabric-dev" ,"sharepoint_url":"prodata365.sharepoint.com","site" : "Fabric"}'
    # Source Settings
    SourceSettings = '{"library":"Unittest","sharepoint_url":"prodata365.sharepoint.com","site":"Fabric"}'
    # Pipeline Parameters
    SourceDirectory = "EmptyFolder"
    SourceObject = "*"
    TargetDirectory = "landing/erp"
    TargetFileName = ""

    source_connection_options = json.loads(SourceConnectionSettings)

    source_options = json.loads(SourceSettings)

    auth_token = AuthToken(**source_connection_options)
    sharepoint = Sharepoint(auth_token, folder=SourceDirectory, file=SourceObject, **source_options)

    files = sharepoint.get_file_bytes()

    for file_name, file_bytes in files.items():
        Path(join("/lakehouse/default/Files/",TargetDirectory)).mkdir(parents=True, exist_ok=True)

        with open(join("/lakehouse/default/Files/",TargetDirectory,file_name), "wb") as f:
            f.write(file_bytes.getbuffer())
