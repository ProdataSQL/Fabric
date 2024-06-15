## 09_sp_WhoIsActive
Monitoring TSQL Script for Fabric DW with similar output to the world famous sp_WhoIsActive by Adam Machanic
https://whoisactive.com/

So far it just shows exec requests, sessions and SQL Statements. When coming from SqlDbEngine this adds some familiarity to monitoring.

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
- No XML or ring buffer support in Fabric
- The following DMVS we use on SqlDBEngine are not supported on Fabric
  - sys.dm_os_sys_info
  - sys.dm_os_workers
  - sys.dm_os_threads
  - sys.dm_os_waiting_tasks
  - sys.dm_db_task_space_usage
  - sys.dm_tran_active_transactions
  - sys.dm_tran_database_transactions
  - sys.dm_tran_session_transactions
  - sys.dm_exec_query_statistics_xml
  - sys.dm_exec_text_query_plan
  - sys.dm_broker_activated_tasks
  - sys.dm_os_tasks
  - sys.dm_os_waiting_tasks
  - sys.dm_db_session_space_usage



Sample call below showing a logn running query causing blocking
  ![image](https://github.com/ProdataSQL/Fabric/assets/19823837/fda392ae-1766-4617-95da-4ba71ecf292c)

