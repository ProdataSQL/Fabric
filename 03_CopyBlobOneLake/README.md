## 03_CopyBlobOneLake
Example of using Azure.Identity with HttpClient to copy a blob on OneLake.
Currently tested mechanisms of authentication are AzurePowerShellCredential, VisualStudioCredential only works so far on older versions of Visual Studio components in VS 20022.


Some Warnings:
1. You need to ensure that  ExcludeManagedIdentityCredential is set to True if you are not using Managed Identity.
Ths avoids timeouts as Azure.Identity alwasy tries Managed Identity First.

2. If doing frequent connections you need to consider caching the AccessToken. By default is valid for an hour, but re-caling the 
TokenRequest on each connection request can be a second or so of wasted time.

3. Make sure to change the default details in sourceUrl and sinkUrl as these are Workspace specific.

4. We are tracking a bug in the Visual Studio DLLs whereby VisualStudioCredential does not work for generating tokens on the latest version, but you can switch to AzureCliCredential and this does work.
We are triaging this and will work with Microsoft Support to confirm if this is a bug, or if VisualStudioCredenital has lost some support.


<pre><code class='language-cs'>
using Azure.Identity;
using Azure.Core;
using System.Net.Http.Headers;

DefaultAzureCredentialOptions DefaultAzureCredentialOptions = new()
{
    ExcludeAzureCliCredential = false,
    ExcludeVisualStudioCredential = false,
    ExcludeAzurePowerShellCredential = false
};
var defaultAzureCredential= new DefaultAzureCredential(DefaultAzureCredentialOptions);
string bearerToken = defaultAzureCredential.GetToken(new TokenRequestContext(new[] { "https://storage.azure.com/" })).Token;

HttpClient client = new();

string rootUrl = "https://onelake.blob.fabric.microsoft.com/";
// CHANGE THESE
string sourceUrl = $"{rootUrl}FabricDW [Dev]/FabricLH.Lakehouse/Files/unittest/AdventureWorks/erp/Account.csv";
string sinkUrl = $"{rootUrl}FabricDW [Dev]/FabricLH.Lakehouse/Files/landing/csv/Account.csv";

using (var request = new HttpRequestMessage(HttpMethod.Put, $"{sinkUrl}"))
{
    request.Headers.Add("X-Ms-Copy-Source", $"{sourceUrl}");
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", bearerToken);

    var response = client.SendAsync(request);

    response.Wait();
    Console.WriteLine(response.Result);
}
</code></pre>
  