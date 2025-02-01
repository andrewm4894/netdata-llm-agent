# Netdata LLM Agent

An LLM agent for chatting with your netdata server's.

See [example notebook](./example.ipynb) for more updated examples.

## TODO

Some things i'd like to do:

- [ ] make pip installable.
- [ ] probably optimize langchain implementation more.
- [ ] add more advanced langchain functionality around memory etc.
- [ ] make cli tool for chatting with agent.
- [ ] dockerize it all.
- [ ] iterate and polish streamlit app.
- [ ] add anthropic support.
- [ ] optimize and expand custom netdata tool usage and structure etc.
- [ ] add more examples.
- [ ] add ability to use local models using ollama.
- [ ] add deeper context and knowledge of netdata and its tools.

## App Example

A little streamlit app that uses the agent to chat with your netdata server's.

```python
streamlit run app.py
```

![App Example](./static/app.png)

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
