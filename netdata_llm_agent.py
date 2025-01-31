import json
import requests

from typing import Optional
from pydantic import BaseModel, Field

from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


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


class NetdataLLMAgent:
    """
    A wrapper class that creates a LangChain Agent with tools to interact
    with a Netdata node and retrieve system/metrics information.
    """

    def __init__(
        self,
        base_url: str = "https://london3.my-netdata.io",
        model_name: str = "gpt-4o",
    ):
        self.base_url = base_url
        self.model = ChatOpenAI(model=model_name)
        self.memory = MemorySaver()

        # -- Define the tools --
        self.get_netdata_info_tool = StructuredTool.from_function(
            name="get_netdata_info",
            func=self._get_netdata_info,
            description="Gets high-level system info from Netdata. No parameters required.",
            args_schema=GetNetdataInfoInput,
        )

        self.get_netdata_charts_tool = StructuredTool.from_function(
            name="get_netdata_charts",
            func=self._get_netdata_charts,
            description="Gets a list of available charts from Netdata. No parameters required.",
            args_schema=GetNetdataChartsInput,
        )

        self.get_netdata_chart_info_tool = StructuredTool.from_function(
            name="get_netdata_chart_info",
            func=self._get_netdata_chart_info,
            description=(
                "Gets detailed info (e.g. dimensions) for a specific chart from Netdata. "
                "Provide a chart name (e.g. 'cpu.cpu0')."
            ),
            args_schema=GetNetdataChartInfoInput,
        )

        self.get_netdata_chart_data_tool = StructuredTool.from_function(
            name="get_netdata_chart_data",
            func=self._get_netdata_chart_data,
            description=(
                "Gets data for a specific chart from Netdata. "
                "Provide a chart name (e.g. 'cpu.cpu0'), 'after', and 'before' timestamps."
            ),
            args_schema=GetNetdataChartDataInput,
        )

        # -- Create the agent prompt --
        prompt_text = (
            "You are a helpful AI bot that allows users to interact with their Netdata "
            "nodes and metrics to better understand their systems. You have the following tools:\n\n"
            " - get_netdata_info()\n"
            " - get_netdata_charts()\n"
            " - get_netdata_chart_info()\n"
            " - get_netdata_chart_data()\n\n"
            "You can provide system info using get_netdata_info, list available charts "
            "using get_netdata_charts, get individual chart info using get_netdata_chart_info, "
            "and get chart data using get_netdata_chart_data."
        )
        prompt = ChatPromptTemplate([("system", prompt_text)])

        # -- Create the agent executor --
        self.agent_executor: AgentExecutor = create_react_agent(
            model=self.model,
            tools=[
                self.get_netdata_info_tool,
                self.get_netdata_charts_tool,
                self.get_netdata_chart_info_tool,
                self.get_netdata_chart_data_tool,
            ],
            checkpointer=self.memory,
            prompt=prompt,
        )

    def _get_netdata_info(self, params: GetNetdataInfoInput) -> str:
        """
        Calls Netdata /api/v1/info to retrieve system info.
        No input params are needed, so we accept an empty Pydantic model.
        """
        url = f"{self.base_url}/api/v1/info"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        r_json = resp.json()

        info = (
            f"netdata version = {r_json['version']}\n"
            f"hostname = {r_json['mirrored_hosts'][0]}\n"
            f"operating system = {r_json['os_name']}\n"
            f"operating system version = {r_json['os_id']}\n"
            f"cores total = {r_json['cores_total']}\n"
            f"total disk space = {r_json['total_disk_space']}\n"
            f"ram total = {r_json['ram_total']}\n"
        )

        return info

    def _get_netdata_charts(self, params: GetNetdataChartsInput) -> str:
        """
        Calls Netdata /api/v1/charts to retrieve the list of available charts.
        No input params are needed, so we accept an empty Pydantic model.
        """
        url = f"{self.base_url}/api/v1/charts"
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

    def _get_netdata_chart_info(self, params: GetNetdataChartInfoInput) -> str:
        """
        Calls Netdata /api/v1/charts to retrieve info for a specific chart.
        The Pydantic model (GetNetdataChartInfoInput) provides:
          - params.chart (required)
        """
        url = f"{self.base_url}/api/v1/charts"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        chart_data = resp.json()["charts"][params.chart]

        chart_info = {
            "id": chart_data["id"],
            "title": chart_data["title"],
            "units": chart_data["units"],
            "family": chart_data["family"],
            "context": chart_data["context"],
            "dimensions": list(chart_data["dimensions"].keys()),
        }

        return json.dumps(chart_info, indent=2)

    def _get_netdata_chart_data(self, params: GetNetdataChartDataInput) -> str:
        """
        Calls Netdata /api/v1/data for a specific chart.

        The Pydantic model (GetNetdataChartDataInput) provides:
          - params.chart (required)
          - params.after (default: '-60')
          - params.before (default: 'now')
          - params.points (default: 60)
        """
        url = f"{self.base_url}/api/v1/data"
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

    def run(self, query: str) -> str:
        """
        A convenience method to send queries to the AgentExecutor.
        """
        return self.agent_executor.run(query)

