from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from netdata_tools import (
    get_netdata_info, get_netdata_charts, get_netdata_chart_info, get_netdata_chart_data
)

SYSTEM_PROMPT = """
You are are helpful Netdata assistant. You can ask me about Netdata charts, chart info, and chart data.

The following tools are available:
- get_netdata_info(base_url) : Get Netdata info.
- get_netdata_charts(base_url) : Get Netdata charts.
- get_netdata_chart_info(base_url, chart) : Get Netdata chart info for a specific chart.
- get_netdata_chart_data(base_url, chart) : Get Netdata chart data for a specific chart.

General Notes:
- When pulling data from get_netdata_chart_data() you can leverage the points param to aggregate data points given the specific after and before time range.
"""


class NetdataLLMAgent:
    def __init__(self, base_url: str, model: str = "gpt-4o", system_prompt: str = SYSTEM_PROMPT):
        self.base_url = base_url
        self.system_prompt = f'{system_prompt}\n\nSpecific Notes: \n- The base_url is {base_url}'
        self.messages = {"messages": []}
        self.llm = ChatOpenAI(model=model)
        self.tools = [
            tool(get_netdata_info, parse_docstring=True),
            tool(get_netdata_charts, parse_docstring=True),
            tool(get_netdata_chart_info, parse_docstring=True),
            tool(get_netdata_chart_data, parse_docstring=True),
        ]

        self.agent = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=SystemMessage(content=self.system_prompt)
            )

    def chat(self, message: str, verbose: bool = False, continue_chat: bool = False):
        if continue_chat:
            self.messages['messages'].append(HumanMessage(content=message))
        else:
            self.messages = {"messages": [HumanMessage(content=message)]}
        self.messages = self.agent.invoke(self.messages)
        if verbose:
            for m in self.messages["messages"]:
                m.pretty_print()
        else:
            self.messages["messages"][-1].pretty_print()
