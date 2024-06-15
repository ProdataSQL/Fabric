/****** Object:  StoredProcedure [dbo].[sp_WhoIsActive]    Script Date: 15/06/2024 09:20:07 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
/*********************************************************************************************
Fabric sp_WhoIsActive by Bob Duffy. bob@prodata.ie

This is based on the SqlDbEngine sp_WhoIsActive 
(C) 2007-2018, Adam Machanic
http://whoisactive.com

*********************************************************************************************/
CREATE OR ALTER PROCEDURE [dbo].[sp_WhoIsActive]
AS
BEGIN
    SET NOCOUNT ON

	SELECT RIGHT('0' + CAST(r.total_elapsed_time / (1000 * 60 * 60 * 24) AS VARCHAR(10)),2) + ' ' + -- Days
    RIGHT('0' + CAST((r.total_elapsed_time / (1000 * 60 * 60)) % 24 AS VARCHAR(2)), 2) + ':' + -- Hours
    RIGHT('0' + CAST((r.total_elapsed_time / (1000 * 60)) % 60 AS VARCHAR(2)), 2) + ':' + -- Minutes
    RIGHT('0' + CAST((r.total_elapsed_time / 1000) % 60 AS VARCHAR(2)), 2) + '.' + -- Seconds
    RIGHT('00' + CAST(r.total_elapsed_time % 1000 AS VARCHAR(3)), 3) AS [dd hh:mm:ss.mss]
	, r.session_id
	, SUBSTRING(st.text, (r.statement_start_offset / 2)+1, ((CASE statement_end_offset WHEN -1 THEN DATALENGTH(st.text)ELSE r.statement_end_offset END-r.statement_start_offset)/ 2)+1)  AS sql_text
	, s.login_name
	, r.wait_type + ':' + CONVERT(varchar, r.wait_time) as wait_info
	, r.cpu_time as cpu
	, r.blocking_session_id
	, r.logical_reads as reads
	, r.writes
	, r.reads as physical_reads
	, r.status
	, r.open_transaction_count as open_tran_count
	, r.percent_complete, s.host_name
	, db_name(s.database_id) as database_name
	, s.program_name
	, r.start_time
	, s.login_time
	, r.request_id
	, GETDATE() as collection_time

	FROM sys.dm_exec_requests r
	CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
	INNER JOIN sys.dm_exec_sessions s on s.session_id =r.session_id

	WHERE r.session_id <> @@SPID
	AND s.program_name <> 'QueryInsights'

END
GO


