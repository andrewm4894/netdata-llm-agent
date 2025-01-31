from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from netdata_tools import (
    get_netdata_info,
    get_netdata_charts,
    get_netdata_chart_info,
    get_netdata_chart_data,
    get_netdata_alarms
)

SYSTEM_PROMPT = """
You are are helpful Netdata assistant. Users can ask you about Netdata charts, chart info, and chart data.

The following tools are available:
- get_netdata_info(netdata_host_url) : Get Netdata info.
- get_netdata_charts(netdata_host_url) : Get Netdata charts.
- get_netdata_chart_info(netdata_host_url, chart) : Get Netdata chart info for a specific chart.
- get_netdata_chart_data(netdata_host_url, chart, after, before, points) : Get Netdata chart data for a specific chart.
- get_netdata_alarms(netdata_host_url) : Get Netdata alarms.

General Notes:
- When pulling data from get_netdata_chart_data() you can leverage the points param to aggregate data points given the specific after and before time range.
- When there are multiple mirrored hosts you can adapt the base url to reflect the specific host you want to pull data from if the user asks about one of the mirrored hosts.
- Charts with breakouts per user typically live at user.* eg. user.cpu_utilization, user.mem_usage etc. as per get_netdata_charts().
- Charts with breakouts per application typically live at app.* eg. app.cpu_utilization, app.mem_usage etc. as per get_netdata_charts().
"""


class NetdataLLMAgent:
    """
    NetdataLLMAgent is a language model agent that can interact with Netdata API to provide information about Netdata charts, chart info, and chart data.

    Args:
        netdata_host_urls: List of Netdata host urls to interact with.
        model: Language model to use. Default is 'gpt-4o'.
        system_prompt: System prompt to use. Default is SYSTEM_PROMPT.
        platform: Platform to use. Default is 'openai'.
    """
    def __init__(
            self,
            netdata_host_urls: list,
            model: str = "gpt-4o",
            system_prompt: str = SYSTEM_PROMPT,
            platform: str = "openai",
        ):
        self.netdata_host_urls = netdata_host_urls
        self.system_prompt = f'{system_prompt}\n\nSpecific Notes: \n- The netdata_host_urls available are {netdata_host_urls}'
        self.messages = {"messages": []}
        self.platform = platform
        self.llm = ChatOpenAI(model=model) if platform == "openai" else ValueError("Only openai platform is supported.")
        self.tools = [
            tool(get_netdata_info, parse_docstring=True),
            tool(get_netdata_charts, parse_docstring=True),
            tool(get_netdata_chart_info, parse_docstring=True),
            tool(get_netdata_chart_data, parse_docstring=True),
            tool(get_netdata_alarms, parse_docstring=True),
        ]

        self.agent = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=SystemMessage(content=self.system_prompt)
            )

    def chat(
            self,
            message: str,
            verbose: bool = False,
            continue_chat: bool = False,
            no_print: bool = True,
            return_last: bool = False
        ):
        """
        Chat with the NetdataLLMAgent.

        Args:
            message: Message to send to the agent.
            verbose: If True, print all messages in the conversation. Default is False.
            continue_chat: If True, continue the chat from the last message. Default is False.
            no_print: If True, do not print the messages. Default is True.
            return_last: If True, return the last message content. Default is False.

        Returns:
            If return_last is True, return the last message content.
        """
        if continue_chat:
            self.messages['messages'].append(HumanMessage(content=message))
        else:
            self.messages = {"messages": [HumanMessage(content=message)]}
        self.messages = self.agent.invoke(self.messages)
        if not no_print:
            if verbose:
                for m in self.messages["messages"]:
                    m.pretty_print()
                else:
                    self.messages["messages"][-1].pretty_print()
        if return_last:
            return self.messages["messages"][-1].content
