## 02_PipelineExecute
Example of using Azure.Identity with HttpClient to execute a Fabric Pipeline.
Currently tested mechanisms of authentication are AzurePowerShellCredential, VisualStudioCredential only works so far on older versions of Visual Studio components in VS 20022.

The root of the url (wabi-north-europe-redirect) may need to be changed depending on your region

Some Warnings:
1. You need to ensure that  ExcludeManagedIdentityCredential is set to True if you are not using Managed Identity.
Ths avoids timeouts as Azure.Identity alwasy tries Managed Identity First.

2. If doing frequent connections you need to consider caching the AccessToken. By default is valid for an hour, but re-caling the 
TokenRequest on each connection request can be a second or so of wasted time.

3. We are tracking a bug in the Visual Studio DLLs whereby VisualStudioCredential does not work for generating tokens on the latest version, but you can switch to AzureCliCredential and this does work.
We are triaging this and will work with Microsoft Support to confirm if this is a bug, or if VisualStudioCredenital has lost some support.

<pre><code class='language-cs'>
using Azure.Identity;
using Azure.Core;
using System.Net.Http.Headers;

var DefaultAzureCredentialOptions = new DefaultAzureCredentialOptions
{
    ExcludeAzureCliCredential = true,
    ExcludeManagedIdentityCredential = true,
    ExcludeSharedTokenCacheCredential = true,
    ExcludeVisualStudioCredential = false,
    ExcludeAzurePowerShellCredential = false,
    ExcludeEnvironmentCredential = true,
    ExcludeVisualStudioCodeCredential = true,
    ExcludeInteractiveBrowserCredential = true
};

var accessToken = new DefaultAzureCredential(DefaultAzureCredentialOptions).GetToken(new TokenRequestContext(new[] { "https://analysis.windows.net/powerbi/api/.default" }));
string Token = accessToken.Token.ToString();

// constructs pipeline url
string pipelineId = "0987f3e1-4f93-46f9-b43b-c53dbbc13c33";
string pipelineUrl = $"https://wabi-north-europe-redirect.analysis.windows.net/metadata/artifacts/{pipelineId}/jobs/Pipeline";

HttpClient client = new();
using (var request = new HttpRequestMessage(HttpMethod.Post, pipelineUrl))
{
    // attaches headers
    request.Headers.Add("Accept", "application/json, text/plain, */*");
    request.Headers.Add("Accept-Encoding", "gzip, deflate, br");
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", Token);

    var response = client.SendAsync(request);

    response.Wait();
    Console.WriteLine(response.Result.ToString());
}
</code></pre>
  
