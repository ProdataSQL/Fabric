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