
using System.Data.SqlClient;
using Azure.Identity;
using Azure.Core;
using System.Data;

var  DefaultAzureCredentialOptions  =  new DefaultAzureCredentialOptions 
    {
        ExcludeAzureCliCredential = true,
        ExcludeManagedIdentityCredential = true,
        ExcludeSharedTokenCacheCredential = true,
        ExcludeVisualStudioCredential = false,
        ExcludeAzurePowerShellCredential = true,
        ExcludeEnvironmentCredential = true,
        ExcludeVisualStudioCodeCredential = true,
        ExcludeInteractiveBrowserCredential = true
    };

    var accessToken = new DefaultAzureCredential(DefaultAzureCredentialOptions).GetToken(new TokenRequestContext(new string[] { "https://database.windows.net//.default" }));
    var sqlServer = "fkm4vwf6l6zebg4lqrhbtdcmsq-absyvg6llsuutcc3wwyid37nou.datawarehouse.pbidedicated.windows.net";
    var sqlDatabase = "";
    var connectionString = $"Server={sqlServer};Database={sqlDatabase}";

    //Set AAD Access Token, Open Conneciton, Run Queries and Disconnect
    using var con = new SqlConnection(connectionString);
    con.AccessToken = accessToken.Token;
    con.Open();
    using var cmd = new SqlCommand();
    cmd.Connection = con;
    cmd.CommandType = CommandType.Text;
    cmd.CommandText = "SELECT @@Version";
    var res =cmd.ExecuteScalar();

    con.Close();


    Console.WriteLine(res);
    Console.ReadLine();

 