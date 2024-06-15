## 09_sp_WhoIsActive
This is a rough tool for Fabric DW with similar  output to the world famous sp_WhoIsActive by Adam Machanic
https://whoisactive.com/

This is very much WIP. So far it just shows exec requests, sessions and SQL Statements.
When coming from SqlDbEngine this adds some familiarity to monitoring.

Maybe in the future we will use KQL and Log Analytics, but hopefully we gte more DMVs to epand this type of solution.

Features:
- long runing queries
- view query text
- reads and writes
- blocking chains
- some wait stat info

Limitations:
- We dont yet have query plans in Fabric DW
- Wait stats are pretty generic
- We dont get CPU in DMVs


Sample call below
  ![image](https://github.com/ProdataSQL/Fabric/assets/19823837/fda392ae-1766-4617-95da-4ba71ecf292c)

