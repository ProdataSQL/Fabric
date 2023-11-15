"""Tools used to get workspace, dataset names and refresh datasets.

Power BI tools to refresh a dataset using client secret authentication.

Sample use (client id and secret values directly):
tenant_id = "xxxxxxxx-5fbe-40b2-xxxx-xxxx198c4c94" # replace with your azure tenant id
app_client_id = "XXXXXXXX-b37a-41ed-xxxx-xxxx558e66b3"
app_client_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
app_scope = "https://analysis.windows.net/powerbi/api"
auth_token = AuthToken(tenant_id, app_client_id, app_app_client_secret, app_scope)

workspace_name = "FabricDWUnitTests" # choose whichever workspace is applicable
pbi_refresh = PowerBIRefresh(workspace_name, auth_token)

dataset_name = "SampleDataset"
pbi_refresh.refresh(dataset_name)

Sample use (keyvault):
tenant_id = "xxxxxxxx-5fbe-40b2-xxxx-xxxx198c4c94" # replace with your azure tenant id
app_client_id_secretname = "fabricDW-app-client-id"
app_client_secret_secretname = "fabricDW-app-client-secret"
auth_token = AuthToken(tenant_id, app_client_id_secretname, app_client_secret_secretname)

workspace_name = "FabricDWUnitTests" # choose whichever workspace is applicable
pbi_refresh = PowerBIRefresh(workspace_name, auth_token)

dataset_name = "SampleDataset"
pbi_refresh.refresh(dataset_name)
"""
import time
from os.path import join
import requests

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
READ_STATUS_TIMER = 5
REST_TIMEOUT = 10


class AuthToken:
    """Class to retrieve token from tenant id, client id, seceret and scope.

    :param str token_url: https://login.microsoftonline.com/
    :param str tenant_id:
    :param str app_client_id: The id or keyvault secret name (if keyvault URL provided).
    :param str app_client_secret: The id or keyvault secret name (if keyvault URL provided).
    :param str scope: https://analysis.windows.net/powerbi/api
    :param str keyvault_url: https://{key-vault-name}.vault.azure.net/ or {key-vault-name}.
    """

    def __init__(
        self,
        tenant_id,
        app_client_id,
        app_client_secret,
        scope="https://analysis.windows.net/powerbi/api",
        keyvault: str or None = None,
        token_url: str or None = "https://login.microsoftonline.com/",
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

        # Send POS request to obtain access token
        response = requests.post(self.token_url, data=data, timeout=REST_TIMEOUT)

        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]


class PowerBIRefresh:
    """Class of tools to handle power BI refreshing.
    :param str base_url: https://api.powerbi.com/v1.0/myorg/
    :param AuthToken auth_token:
    :param workspace_name:
    """

    def __init__(
        self,
        workspace_name,
        auth_token: AuthToken or str,
        base_url: str or None = "https://api.powerbi.com/v1.0/myorg/",
    ):
        
        if isinstance(auth_token,str):
            self.headers = {"Authorization": f"Bearer {auth_token}"}
        elif isinstance(auth_token,AuthToken):
            self.headers = {"Authorization": f"Bearer {auth_token.access_token}"}

        self.base_url = base_url

        if isinstance(workspace_name, str):
            self.workspace_id = self.get_workspace_id(workspace_name)
        elif isinstance(workspace_name, list):
            self.workspace_id = self.get_workspace_id(workspace_name[0])

    def get_workspace_id(self, workspace_name) -> str:
        """Returns a workspace name.

        :param str workspace_name:
        :raises WorkspaceNameNotFoundException:
        :return: Id of workspace.
        :rtype: str
        """
        relative_url = join(self.base_url, "groups")

        response = requests.get(
            relative_url, headers=self.headers, timeout=REST_TIMEOUT
        )
        if not response.ok:
            response.raise_for_status()

        workspaces = response.json()["value"]

        for workspace in workspaces:
            if workspace["name"] == workspace_name:
                self.workspace_id = workspace["id"]
                return self.workspace_id

        raise WorkspaceNameNotFoundException(workspace_name)

    def get_dataset_ids(self, dataset_names, workspace_id=None) -> list:
        """Returns a list of dataset ids from a list of dataset names.

        :param list(str) dataset_names:
        :param workspace_id:
        :type workspace_id: str or None
        :raises DatasetNameNotFoundException:
        :return: list of dataset ids
        :rtype: list
        """
        workspace_id = self.workspace_id if workspace_id is None else workspace_id
        relative_url = join(self.base_url, f"groups/{workspace_id}/datasets")

        # Set the GET response using the relative URL
        response = requests.get(
            relative_url, headers=self.headers, timeout=REST_TIMEOUT
        )

        if not response.ok:
            response.raise_for_status()

        dataset_ids = []
        datasets = response.json()["value"]

        for dataset in datasets:
            for dataset_name in dataset_names:
                if dataset["name"] == dataset_name and dataset["isRefreshable"] is True:
                    dataset_ids.append(dataset["id"])
                    return dataset_ids

        raise DatasetNameNotFoundException(dataset_names)

    def get_dataset_name(self, dataset_id, workspace_id=None) -> str:
        """Returns a datasetname from its id.

        :param str dataset_id:
        :param workspace_id:
        :type workspace_id: str or None
        :raises DatasetNameNotFoundException:
        :return: dataset id
        :rtype: str
        """
        workspace_id = self.workspace_id if workspace_id is None else workspace_id
        relative_url = join(self.base_url, f"groups/{workspace_id}/datasets")
        response = requests.get(
            relative_url, headers=self.headers, timeout=REST_TIMEOUT
        )

        if not response.ok:
            response.raise_for_status()

        datasets = response.json()["value"]
        for dataset in datasets:
            if dataset["id"] != dataset_id:
                pass
            if dataset["isRefreshable"] is True:
                return dataset["name"]
        raise DatasetNameNotFoundException(dataset_id)

    def refresh_dataset(self, dataset_id, workspace_id=None):
        """Refreshes a dataset by id.

        :param str dataset_id:
        :param workspace_id:
        :type workspace_id: str or None
        :raises DatasetRefreshFailedException:
        :return: None
        :rtype: None
        """
        workspace_id = self.workspace_id if workspace_id is None else workspace_id
        relative_url = join(
            self.base_url, f"groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        )
        response = requests.post(
            relative_url, headers=self.headers, timeout=REST_TIMEOUT
        )

        if response.ok:
            error_counter = 0
            error_limit = 5
            status = None

            print(
                f"Dataset {self.get_dataset_name(dataset_id, workspace_id)} refresh has been triggered successfully."
            )

            while error_counter < error_limit or status == "Unknown":
                try:
                    status = self.get_dataset_refresh_status(dataset_id, workspace_id)
                except requests.HTTPError:
                    error_counter += 1
                    time.sleep(READ_STATUS_TIMER)
                    continue

                if status == "Failed":
                    raise DatasetRefreshFailedException(self, workspace_id, dataset_id)
                if status == "Completed":
                    error_counter = 0
                    break

            if error_counter > error_limit:
                raise FailedToGetStatusException(
                    workspace_id, dataset_id, error_counter
                )
        else:
            print(
                f"Failed to trigger dataset"
                f"{self.get_dataset_name(dataset_id, workspace_id)} refresh."
            )
            print("Response status code:", response.status_code)
            print("Response content:", response.content)
            response.raise_for_status()
            raise DatasetRefreshFailedException(self, workspace_id, dataset_id)

    def get_dataset_refresh_status(self, dataset_id, workspace_id=None) -> str:
        """Gets the refresh status of a dataset by its dataset id.

        :param str dataset_id:
        :param workspace_id:
        :type workspace_id: str or None
        :return: The status of dataset refresh (current or previous).
        :rtype: str
        """
        workspace_id = self.workspace_id if workspace_id is None else workspace_id
        relative_url = join(
            self.base_url,
            f"groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top=1",
        )
        response = requests.get(
            relative_url, headers=self.headers, timeout=REST_TIMEOUT
        )
        response.raise_for_status()
        refresh_status = response.json()["value"]
        status = refresh_status[0]["status"]
        return status

    def refresh(
        self,
        dataset_names: str or list(str),
        workspace_names: str or list(str) or None = None,
    ):
        """Invokes refresh of PowerBI Dataset, can be a list of workspaces and datasets or just one.

        :param workspace_names: List or comma seperated string of workspace names.
        :type workspace_names: str or list(str) or None
        :param dataset_names: List or comma seperated string of dataset names.
        :type dataset_names: str or list(str)
        :return: None.
        :rtype: None
        """
        if isinstance(workspace_names, list):
            workspace_list = workspace_names
        elif workspace_names is None:
            workspace_list = [self.workspace_id]
        else:
            workspace_list = workspace_names.split(",")

        if dataset_names is None:
            raise DatasetNameBlankException()
        else:
            if isinstance(dataset_names, list):
                dataset_list = dataset_names
            else:
                dataset_list = dataset_names.split(",")

        for workspace_name in workspace_list:
            workspace_id = (
                self.workspace_id
                if workspace_name == self.workspace_id
                else self.get_workspace_id(workspace_name)
            )
            dataset_ids = self.get_dataset_ids(dataset_list, workspace_id)
            for dataset_id in dataset_ids:
                self.refresh_dataset(dataset_id, workspace_id)


class WorkspaceNameNotFoundException(Exception):
    """Workspace name not found runtime exception."""

    def __init__(self, workspace_name):
        message = f"workspace {workspace_name} Not Found"
        super().__init__(message)


class DatasetNameNotFoundException(Exception):
    """Dataset name not found runtime exception."""

    def __init__(self, dataset_name):
        message = f"Dataset Name {dataset_name} Not Found"
        super().__init__(message)


class DatasetNameBlankException(Exception):
    """Dataset name was blank."""

    def __init__(self):
        message = "Dataset Name cannot be blank"
        super().__init__(message)


class DatasetRefreshFailedException(Exception):
    """Refresh of dataset was not successful"""

    def __init__(self, pbi_refr_tools, workspace_id, dataset_id):
        workspace_name = ""
        message = (
            f"Dataset {pbi_refr_tools.get_pbi_dataset_name(dataset_id)} ({dataset_id})"
            + f"in workspace {workspace_name} ({workspace_id}) failed to refresh."
        )
        super().__init__(message)


class FailedToGetStatusException(Exception):
    """Failed to get status during refresh"""

    def __init__(self, workspace, dataset, retries):
        message = f"Dataset {dataset} in {workspace} failed to get status, after {retries} retries."
        super().__init__(message)


if __name__ == "__main__":
    TENANT_ID = (
        "xxxxxxxx-5fbe-xxxx-xxxx-xxxxxxxxxxxxx"  # replace with your azure tenant id
    )
    APP_CLIENT_ID = "<ClientIDName>"
    APP_CLIENT_SECRET = "<ClientIDSecret>"
    AUTH_TOKEN = AuthToken(
        TENANT_ID, APP_CLIENT_ID, APP_CLIENT_SECRET, keyvault="<KeyVaultName>"
    )

    WORKSPACE_NAME = "<WorkspaceName>"  # choose whichever workspace is applicable
    PBI_REFRESH = PowerBIRefresh(WORKSPACE_NAME, AUTH_TOKEN)
    DATASET_NAME = "<DatasetName>"
    PBI_REFRESH.refresh(DATASET_NAME)
