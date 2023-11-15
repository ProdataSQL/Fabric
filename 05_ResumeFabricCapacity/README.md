## 05_ResumeFabricCapacity
Example of using Azure.Identity with HttpClient to copy a blob on OneLake.
Currently tested mechanisms of authentication are AzurePowerShellCredential, VisualStudioCredential only works so far on older versions of Visual Studio components in VS 20022.


Some Warnings:
1. You need to ensure that  ExcludeManagedIdentityCredential is set to True if you are not using Managed Identity.
Ths avoids timeouts as Azure.Identity alwasy tries Managed Identity First.

2. If doing frequent connections you need to consider caching the AccessToken. By default is valid for an hour, but re-caling the 
TokenRequest on each connection request can be a second or so of wasted time.

3. Make sure to change the SubscriptionId, ResourceGroupName and CapacityName to relevant values.

4. We are tracking a bug in the Visual Studio DLLs whereby VisualStudioCredential does not work for generating tokens on the latest version, but you can switch to AzureCliCredential and this does work.
We are triaging this and will work with Microsoft Support to confirm if this is a bug, or if VisualStudioCredenital has lost some support.


<pre><code class='language-cs'>
using Azure.Core;
using Azure.Identity;
using System.Net.Http.Headers;


DefaultAzureCredentialOptions DefaultAzureCredentialOptions = new()
{
    ExcludeAzureCliCredential = false,
    ExcludeVisualStudioCredential = false,
    ExcludeAzurePowerShellCredential = false
};
// Fill in specific information here:
string SubscriptionId = "";
string ResourceGroupName = "";
string CapacityName = "";

string CapacityUrl = $"https://management.azure.com/subscriptions/{SubscriptionId}/resourceGroups/{ResourceGroupName}/providers/Microsoft.Fabric/capacities/{CapacityName}";

var defaultAzureCredential = new DefaultAzureCredential(DefaultAzureCredentialOptions);
string bearerToken = defaultAzureCredential.GetToken(new TokenRequestContext(new[] { "https://management.azure.com" })).Token;

HttpClient client = new();

using (var request = new HttpRequestMessage(HttpMethod.Post, $"{CapacityUrl}/resume?api-version=2022-07-01-preview"))
{
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", bearerToken);

    var response = client.SendAsync(request);

    response.Wait();
    Console.WriteLine(response.Result);
}
</code></pre>
  