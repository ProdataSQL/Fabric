## 09_sp_WhoIsActive
This is a rough tool for Fabric DW with similar  output to the world famous sp_WhoIsActive by Adam Machanic
https://whoisactive.com/

This is very much WIP. SO far it just shows exec requests, sessions and SQL Statements

Limitations:
- We dont yet have query plans in Fabric DW
- Wait stats are pretty generic
- We dont get CPU in DMVs



Sample call below
<pre><code class='SQL'
sp_WhoIsActive
</code></pre>
  
