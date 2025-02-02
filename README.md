# Netdata LLM Agent

An LLM agent for chatting with your netdata server's.

See [example notebook](./example.ipynb) for more updated examples.

Tools the [agent](./netdata_llm_agent.py) has access to ([source](./netdata_llm_tools.py)):
- `get_info(netdata_host_url)` : Get Netdata info about a node.
- `get_charts(netdata_host_url, search_term)` : Get Netdata charts, optionally filter by search_term.
- `get_chart_info(netdata_host_url, chart)` : Get Netdata chart info for a specific chart.
- `get_chart_data(netdata_host_url, chart, after, before, points, options, df_freq)` : Get Netdata chart data for a specific chart. Optionally filter by after, before, points, options, and df_freq. options can be used to add optional flags for example 'anomaly-bit' will return anomaly rates rather than raw metric values.
- `get_alarms(netdata_host_url, all, active)` : Get Netdata alarms. all=True to get all alarms, active=True to get active alarms (warning or critical).
- `get_current_metrics(netdata_host_url, search_term)` : Get current metrics values for all charts, no time range, just the current values for all dimensions on all charts. Optionally filter by search_term on chart name.
- `get_anomaly_rates(netdata_host_url, after, before, search_term)` : Get anomaly rates for a specific time frame for all charts or optionally filter by search_term on chart name.
- `get_netdata_docs_sitemap(search_term)` : Get Netdata docs sitemap to list available Netdata documentation pages. Use search_term to filter by a specific term.
- `get_netdata_docs_page(url)` : Get Netdata docs page content for a specific docs page url on learn.netdata.cloud.

## TODO

Some things i'd like to do:

- [ ] make pip installable.
- [ ] probably optimize langchain implementation more.
- [ ] add more advanced langchain functionality around memory etc.
- [x] make cli tool for chatting with agent.
- [ ] dockerize it all.
- [ ] iterate and polish streamlit app.
- [x] add anthropic support.
- [ ] optimize and expand custom netdata tool usage and structure etc.
- [ ] add more examples.
- [x] add ability to use local models using ollama.
- [ ] add deeper context and knowledge of netdata and its tools.

## App Example

A little streamlit app that uses the agent to chat with your netdata server's ([source](./netdata_llm_app.py)).

```bash
make app
```

or

```python
streamlit run app.py
```

![App Example](./static/app.png)

## CLI Example

A very simplistic cli tool that uses the agent to chat with your netdata server's on command line ([source](./netdata_llm_cli.py)).

```base
make cli
```

```markdown
Welcome to the Netdata LLM Agent CLI!
Type your query about Netdata (e.g., charts, alarms, metrics) and press Enter.
Type 'exit' or 'quit' to end the session.

You: how do the mysql metrics look on london?
Agent: In the London Netdata instance, there are numerous MySQL-related metrics available for monitoring. Here's a comprehensive list:

1. User Process Metrics:
   - `user.mysql_cpu_utilization`: CPU utilization.
   - `user.mysql_mem_private_usage`: Memory usage without shared.
   - `user.mysql_cpu_context_switches`: CPU context switches.
   - `user.mysql_mem_usage`: Memory RSS usage.
   - `user.mysql_vmem_usage`: Virtual memory size.
   - `user.mysql_mem_page_faults`: Memory page faults.
   - `user.mysql_swap_usage`: Swap usage.
   - `user.mysql_disk_physical_io`: Disk physical IO.
   - `user.mysql_disk_logical_io`: Disk logical IO.
   - `user.mysql_processes`: Number of processes.
   - `user.mysql_threads`: Number of threads.
   - `user.mysql_fds_open_limit`: Open file descriptors limit.
   - `user.mysql_fds_open`: Open files descriptors.
   - `user.mysql_uptime`: Uptime.

2. User Group Process Metrics (Similar metrics for group processes):
   - CPU, memory, IO, and process-related metrics.

3. General MySQL Metrics:
   - `mysql_local.net`: Bandwidth.
   - `mysql_local.queries`: Queries per second.
   - `mysql_local.queries_type`: Types of queries.
   - `mysql_local.handlers`: Handlers.
   - `mysql_local.table_locks`: Table locks.
   - `mysql_local.join_issues`: Join issues.
   - `mysql_local.sort_issues`: Sort issues.
   - `mysql_local.tmp`: Temporary operations.
   - `mysql_local.connections`: Total connections.
   - `mysql_local.connections_active`: Active connections.
   - `mysql_local.threads`: Number of threads.
   - `mysql_local.thread_cache_misses`: Thread cache misses.
   - `mysql_local.innodb_io`: InnoDB I/O bandwidth.
   - `mysql_local.innodb_io_ops`: InnoDB I/O operations.
   - `mysql_local.innodb_io_pending_ops`: InnoDB pending I/O operations.
   - `mysql_local.innodb_log`: InnoDB log operations.
   - `mysql_local.innodb_cur_row_lock`: InnoDB current row locks.
   - `mysql_local.innodb_rows`: InnoDB row operations.
   - Other InnoDB metrics related to buffer pool and page requests.
   - `mysql_local.files`: Open files.
   - `mysql_local.files_rate`: Opened files rate.
   - `mysql_local.connection_errors`: Connection errors.
   - `mysql_local.opened_tables`: Number of opened tables.
   - `mysql_local.process_list_queries_count`: Queries count.
   - `mysql_local.innodb_deadlocks`: InnoDB deadlocks.
   - QCache and MyISAM-related metrics.

These metrics provide a detailed view of MySQL performance and can be used to monitor the database server's status, resource usage, and performance trends. If you'd like more detailed info on any specific chart, feel free to ask!

You: how does performance generaly look?
Agent: The current performance metrics for MySQL on the London Netdata instance indicate relatively stable and low resource usage. Here's a summary of key metrics:

### CPU and Memory Utilization
- **CPU Utilization**: Very low at around 0.61% for system usage, with no user CPU usage.
- **Memory Usage**:
  - Private memory usage is about 226 MiB.
  - RSS memory usage is around 234.95 MiB.
  - Virtual memory usage is approximately 1174 MiB.

### Disk I/O
- **Physical I/O**: Minimal, with writes noted at around -24 KiB/s.
- **Logical I/O**: Slightly more activity with reads at 8.46 KiB/s and writes at -32.18 KiB/s.

### Network and Query Activity
- **Network Bandwidth**: Inbound traffic is around 4.76 kb/s, while outbound traffic is -179.86 kb/s.
- **Queries**:
  - Handling around 6 queries/second with a mix of select operations (1 query/second) and some sorting and joining activities.

### Processes and Threads
- **Processes**: Running 1 MySQL process with 9 threads active.
- **Connections**: 1 active connection with a limit of 151.

### Cache and Buffers
- **Buffer Pool**: Utilized pages are minor with a total of 8064 pages, suggesting ample buffer pool size compared to usage.
- **QCache**: Limited operation, with free memory at 0.98 MiB.

### Miscellaneous
- **Swap Usage**: Not utilizing any swap memory.
- **InnoDB Deadlocks**: No deadlocks detected.

Overall, the system exhibits nominal activity levels indicating a stable and lightly loaded MySQL server. If there's a need for deeper analysis on specific metrics or additional monitoring, feel free to ask for more details.

You: thats great thanks! love you x
Agent: You're welcome! I'm glad I could help. If you have any more questions or need assistance in the future, feel free to reach out. Have a fantastic day! 😊
```

## Code Example

```python
from netdata_llm_agent import NetdataLLMAgent

# create agent
agent = NetdataLLMAgent(base_url='https://london3.my-netdata.io/')

# chat with agent
agent.chat('How much disk space do i have?')
```

Response:

```text
================================[1m Human Message [0m=================================

How much disk space do i have?
==================================[1m Ai Message [0m==================================
Tool Calls:
  get_netdata_info (call_z3UdHeDcsWZgm2w3KTsSLJa3)
 Call ID: call_z3UdHeDcsWZgm2w3KTsSLJa3
  Args:
    base_url: https://london3.my-netdata.io/
=================================[1m Tool Message [0m=================================
Name: get_netdata_info

netdata version = v2.2.0-70-nightly
hostname = registry.my-netdata.io
operating system = Debian GNU/Linux
operating system version = debian
cores total = 4
total disk space = 171799128064
ram total = 8326430720

==================================[1m Ai Message [0m==================================

You have a total disk space of approximately 171.8 GB.
```
