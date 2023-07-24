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