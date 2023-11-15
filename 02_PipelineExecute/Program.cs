using Azure.Identity;
using Azure.Core;
using System.Net.Http.Headers;

var DefaultAzureCredentialOptions = new DefaultAzureCredentialOptions
{
    ExcludeAzureCliCredential = false,
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