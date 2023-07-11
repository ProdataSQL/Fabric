# Fabric

This contains random example and code synippits for Microsof Fabric

## 01_SqlClientAAD
Example of using Azure.Identity with SqlClient to authenticate to a Fabric SQL EndPoint.
This can use various auth methods such as Managed Identity, Visual Studio and VS Code.

Some Warnings:
1. You need to ensure that  ExcludeManagedIdentityCredential is set to True if you aer not using Managed Identity.
Ths avoids timeouts as Azure.Identity alwasy tries Managed Identity First.

2. If doing frequent connections you need to consider caching the AccessToken. By default is valid for an hour, but re-caling the 
TokenRequets on each connection request can be a second or so of wasted time.



