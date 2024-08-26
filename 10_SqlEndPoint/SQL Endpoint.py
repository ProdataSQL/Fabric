#!/usr/bin/env python
# coding: utf-8

# ## SQL Endpoint
# 
# New notebook

# In[33]:


dw_name="FabricDW"   # Change this to your DW Name

import sempy.fabric as fabric
import struct
import sqlalchemy
import pyodbc
import pandas as pd
from notebookutils import mssparkutils

#Function to Return sqlalchemt ODBC Engine, given a connection string and using Integrated AAD Auth to Fabric
def create_engine(connection_string : str):
    token = mssparkutils.credentials.getToken('https://analysis.windows.net/powerbi/api').encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token)}s', len(token), token)
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    return sqlalchemy.create_engine("mssql+pyodbc://", creator=lambda: pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}))


# Get ODBC Connection String for Default LH ijn this Notebook
tenant_id=spark.conf.get("trident.tenant.id")
workspace_id=spark.conf.get("trident.workspace.id")
lakehouse_id=spark.conf.get("trident.lakehouse.id")
lakehouse_name=spark.conf.get("trident.lakehouse.name")
sql_end_point= fabric.FabricRestClient().get(f"/v1/workspaces/{workspace_id}/lakehouses/{lakehouse_id}").json()['properties']['sqlEndpointProperties']['connectionString']
connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={sql_end_point}"
print (f"connection_string={connection_string}")

engine = create_engine(connection_string)
with engine.connect() as alchemy_connection:
    #Run TSQL Query on a LH End Point
    query = f"exec {lakehouse_name}.[sys].[sp_server_info] 2"
    df = pd.read_sql_query(query, alchemy_connection)
    print (df)

    #Run TSQL Query on a DW End Point
    query = f"exec {dw_name}.[sys].[sp_server_info] 2"
    df = pd.read_sql_query(query, alchemy_connection)
    print (df)

    #Execute a TSQL Stored Procedure or DDL/DML on a Fabric DW
    connection = engine.raw_connection()
    cursor = connection.cursor()
    sql= f"USE {dw_name};CREATE TABLE tmpTable (Column1 INT NULL);DROP TABLE tmpTable"
    cursor.execute(sql)
    connection.commit()




