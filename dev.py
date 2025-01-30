#%%

import os
import json
import requests

from pydantic import BaseModel, Field
from typing import Optional

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from langchain.callbacks import get_openai_callback

BASE_URL = "http://127.0.0.1:19999"

##%%

# define Pydantic models for the Netdata functions below

class GetNetdataInfoInput(BaseModel):
    """No input needed."""


class GetNetdataChartsInput(BaseModel):
    """No input needed."""

class GetNetdataChartDataInput(BaseModel):
    chart: str = Field('cpu.cpu0', description="Name of the chart, e.g. 'cpu.cpu0'.")
    after: Optional[str] = Field(
        "-60", description="Unix timestamp or relative time (e.g. '-60')."
    )
    before: Optional[str] = Field(
        "now", description="Unix timestamp or 'now' for the current time."
    )

#%%

# define netdata functions to retrieve system info, charts, and chart data

def get_netdata_info(params: GetNetdataInfoInput = GetNetdataInfoInput()) -> str:
    """
    Calls Netdata /api/v1/info to retrieve system info.
    No input params are needed, so we accept an empty Pydantic model.
    """
    url = f"{BASE_URL}/api/v1/info"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        r_json = resp.json()
        info = "Netdata Info:\n"
        info += f"netdata version = {r_json['version']}\n"
        info += f"hostname = {r_json['mirrored_hosts'][0]}\n"
        info += f"operating system = {r_json['os_name']}\n"
        info += f"operating system version = {r_json['os_id']}\n"
        info += f"cores total = {r_json['cores_total']}\n"
        info += f"total disk space = {r_json['total_disk_space']}\n"
        info += f"ram total = {r_json['ram_total']}\n"
        return info
    except Exception as e:
        return f"Error retrieving Netdata info: {e}"

print(get_netdata_info())

#%%


def get_netdata_charts(params: GetNetdataChartsInput = GetNetdataChartsInput()) -> str:
    """
    Calls Netdata /api/v1/charts to retrieve the list of available charts.
    No input params are needed, so we accept an empty Pydantic model.
    """
    url = f"{BASE_URL}/api/v1/charts"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)
    except Exception as e:
        return f"Error retrieving charts: {e}"


def get_netdata_chart_data(params: GetNetdataChartDataInput = GetNetdataChartDataInput()) -> str:
    """
    Calls Netdata /api/v1/data for a specific chart.

    The Pydantic model (GetNetdataChartDataInput) provides:
      - params.chart (required)
      - params.after (default: '-60')
      - params.before (default: 'now')
    """
    try:
        url = f"{BASE_URL}/api/v1/data"
        query_params = {
            "chart": params.chart,
            "after": params.after,
            "before": params.before,
            "format": "json",
            "points": 60,
            "options": "seconds",
        }

        resp = requests.get(url, params=query_params, timeout=5)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)
    except Exception as e:
        return f"Error retrieving chart data: {e}"

##%%

# define tools for the netdata functions

get_netdata_info_tool = StructuredTool.from_function(
    name="get_netdata_info",
    func=get_netdata_info,
    description="Gets high-level system info from Netdata. No parameters required.",
    args_schema=GetNetdataInfoInput,
)

get_netdata_charts_tool = StructuredTool.from_function(
    name="get_netdata_charts",
    func=get_netdata_charts,
    description="Gets a list of available charts from Netdata. No parameters required.",
    args_schema=GetNetdataChartsInput,
)

get_netdata_chart_data_tool = StructuredTool.from_function(
    name="get_netdata_chart_data",
    func=get_netdata_chart_data,
    description=(
        "Gets data for a specific chart from Netdata. "
        "Provide a chart name (e.g. 'cpu.cpu0'), 'after' and 'before' timestamps."
    ),
    args_schema=GetNetdataChartDataInput,
)

##%%

# create a LangChain agent with the Netdata tools and a ChatOpenAI model

def create_netdata_agent():
    """
    Creates a LangChain agent with three Netdata tools:
      - get_netdata_info_tool      (no input)
      - get_netdata_charts_tool    (no input)
      - get_netdata_chart_data_tool
    The agent uses a ChatOpenAI model (GPT-3.5 or GPT-4).
    """

    # create a ChatOpenAI model
    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4"
    )

    # define the tools to be used by the agent
    tools = [
        get_netdata_info_tool,
        get_netdata_charts_tool,
        get_netdata_chart_data_tool,
    ]

    # initialize the agent with the tools and the ChatOpenAI model
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    return agent

#%%

# create the Netdata agent and run some example queries

agent = create_netdata_agent()

#%%

response = agent.run("How much disk space do I have?")
print(response)

#%%

response = agent.run("How much ram do I have?")
print(response)

#%%

response = agent.run("List all the charts from Netdata.")
print(response)

print("\n=== Chart Data (CPU) ===")
response = agent.run("Retrieve data for chart cpu.cpu0 from the last 120 seconds.")
print(response)

#%%

#%%

get_netdata_info()

#%%
