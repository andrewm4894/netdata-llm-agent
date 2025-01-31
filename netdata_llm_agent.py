
import json
import requests

from pydantic import BaseModel, Field
from typing import Optional

from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


BASE_URL = "http://127.0.0.1:19999"


class GetNetdataInfoInput(BaseModel):
    """No input needed."""


class GetNetdataChartsInput(BaseModel):
    """No input needed."""


class GetNetdataChartInfoInput(BaseModel):
    chart: str = Field("cpu.cpu0", description="Name of the chart, e.g. 'cpu.cpu0'.")


class GetNetdataChartDataInput(BaseModel):
    chart: str = Field("cpu.cpu0", description="Name of the chart, e.g. 'cpu.cpu0'.")
    after: Optional[str] = Field(
        "-60", description="Unix timestamp or relative time (e.g. '-60')."
    )
    before: Optional[str] = Field(
        "now",
        description="Unix timestamp or relative time or 'now' for the current time.",
    )
    points: Optional[int] = Field(
        60, description="Number of data points to retrieve (default: 60)."
    )


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
        info = ""
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


def get_netdata_charts(params: GetNetdataChartsInput = GetNetdataChartsInput()) -> str:
    """
    Calls Netdata /api/v1/charts to retrieve the list of available charts.
    No input params are needed, so we accept an empty Pydantic model.
    """
    url = f"{BASE_URL}/api/v1/charts"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        r_json = resp.json()
        charts = {}
        for chart in r_json["charts"]:
            charts[chart] = {
                "name": r_json["charts"][chart]["name"],
                "title": r_json["charts"][chart]["title"],
            }
        return json.dumps(charts, indent=2)
    except Exception as e:
        return f"Error retrieving charts: {e}"


def get_netdata_chart_info(
    params: GetNetdataChartInfoInput = GetNetdataChartInfoInput(),
) -> str:
    """
    Calls Netdata /api/v1/charts/ to retrieve info for a specific chart.
    The Pydantic model (GetNetdataChartInfoInput) provides:
      - params.chart (required)
    """
    try:
        url = f"{BASE_URL}/api/v1/charts"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        chart_info = resp.json()["charts"][params.chart]
        chart_info = {
            "id": chart_info["id"],
            "title": chart_info["title"],
            "units": chart_info["units"],
            "family": chart_info["family"],
            "context": chart_info["context"],
            "dimensions": list(chart_info["dimensions"].keys()),
        }
        return json.dumps(chart_info, indent=2)
    except Exception as e:
        return f"Error retrieving chart info: {e}"


def get_netdata_chart_data(
    params: GetNetdataChartDataInput = GetNetdataChartDataInput(),
) -> str:
    """
    Calls Netdata /api/v1/data for a specific chart.

    The Pydantic model (GetNetdataChartDataInput) provides:
      - params.chart (required)
      - params.after (default: '-60')
      - params.before (default: 'now')
      - params.points (default: 60)
    """
    try:
        url = f"{BASE_URL}/api/v1/data"
        query_params = {
            "chart": params.chart,
            "after": params.after,
            "before": params.before,
            "format": "csv",
            "points": params.points,
        }

        resp = requests.get(url, params=query_params, timeout=5)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)
    except Exception as e:
        return f"Error retrieving chart data: {e}"


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

get_netdata_chart_info_tool = StructuredTool.from_function(
    name="get_netdata_chart_info",
    func=get_netdata_chart_info,
    description=(
        "Gets detailed info e.g. dimensions it has etc, for a specific chart from Netdata. "
        "Provide a chart name (e.g. 'cpu.cpu0')."
    ),
    args_schema=GetNetdataChartInfoInput,
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


def create_netdata_agent(base_url: str = BASE_URL):
    """
    Creates a LangChain agent with some Netdata tools:
      - get_netdata_info_tool
      - get_netdata_charts_tool
      - get_netdata_chart_info_tool
      - get_netdata_chart_data_tool
    The agent uses a ChatOpenAI model.
    """
    model = ChatOpenAI(model="gpt-4o")
    tools = [
        get_netdata_info_tool,
        get_netdata_charts_tool,
        get_netdata_chart_info_tool,
        get_netdata_chart_data_tool,
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant tasked with helping the user better understand their Netdata system.",
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    return agent_executor
