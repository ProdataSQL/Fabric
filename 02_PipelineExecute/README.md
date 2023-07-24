## 02_PipelineExecute
Example of using Azure.Identity with HttpClient to execute a Fabric Pipeline.
Currently tested mechanisms of authentication are AzurePowerShellCredential, Visual Studio authentication hasn't been shown to work.

The root of the url (wabi-north-europe-redirect) may need to be changed depending on your region

Some Warnings:
1. You need to ensure that  ExcludeManagedIdentityCredential is set to True if you aer not using Managed Identity.
Ths avoids timeouts as Azure.Identity alwasy tries Managed Identity First.

2. If doing frequent connections you need to consider caching the AccessToken. By default is valid for an hour, but re-caling the 
TokenRequest on each connection request can be a second or so of wasted time.


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
  