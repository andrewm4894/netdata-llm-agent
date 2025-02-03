#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tools for Netdata LLM Agent.
"""

import json
import requests
import pandas as pd
from markdownify import markdownify as md


def get_info(netdata_host_url: str) -> str:
    """
    Calls Netdata /api/v1/info to retrieve system info and some metadata.

    Args:
        netdata_host_url: Netdata host url to call.

    Returns:
        JSON string with system info.
    """
    url = f"{netdata_host_url}/api/v1/info"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()

    info = {
        "netdata_version": r_json["version"],
        "hostname": r_json["mirrored_hosts"][0],
        "operating_system": r_json["os_name"],
        "operating_system_version": r_json["os_id"],
        "cores_total": r_json["cores_total"],
        "total_disk_space": r_json["total_disk_space"],
        "ram_total": r_json["ram_total"],
        "mirrored_hosts": [
            {k: h[k] for k in ["hostname", "hops", "reachable"]}
            for h in r_json["mirrored_hosts_status"]
        ],
        "alarms": r_json["alarms"],
        "buildinfo": r_json["buildinfo"],
        "charts-count": r_json["charts-count"],
        "metrics-count": r_json["metrics-count"],
        "collectors": r_json["collectors"],
    }

    return json.dumps(info, indent=2)


def get_charts(
    netdata_host_url: str, search_term: str = None, include_dimensions: bool = False
) -> str:
    """
    Calls Netdata /api/v1/charts to retrieve the list of available charts and some metadata about each chart. Use the search_term to filter the charts if needed.

    Args:
        netdata_host_url: Netdata host url to call.
        search_term: Optional search term to filter the charts returned based on chart name, title, or dimensions.
        include_dimensions: If True, include the dimensions for each chart in the returned JSON.

    Returns:
        JSON string with chart metadata. List of tuples with chart id and title and dimensions if include_dimensions is True.
    """
    url = f"{netdata_host_url}/api/v1/charts"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()

    charts = []
    for chart in r_json["charts"]:
        if (
            search_term
            and search_term not in r_json["charts"][chart]["name"]
            and search_term not in r_json["charts"][chart]["title"]
            and not any(search_term in dim for dim in r_json["charts"][chart]["dimensions"].keys())
        ):
            continue
        chart_info = (r_json["charts"][chart]["name"], r_json["charts"][chart]["title"])
        if include_dimensions:
            chart_info = (
                *chart_info,
                list(r_json["charts"][chart]["dimensions"].keys()),
            )
        charts.append(chart_info)

    return json.dumps(charts, indent=2)


def get_chart_info(netdata_host_url: str, chart: str = "system.cpu") -> str:
    """
    Calls Netdata /api/v1/chart?chart={chart} to retrieve info for a specific chart.

    Args:
        netdata_host_url: Netdata host url.
        chart: Chart id.

    Returns:
        Chart info.
    """
    url = f"{netdata_host_url}/api/v1/chart?chart={chart}"
    resp = requests.get(url, timeout=5)
    chart_data = resp.json()
    chart_info = {
        "id": chart_data["id"],
        "title": chart_data["title"],
        "units": chart_data["units"],
        "family": chart_data["family"],
        "context": chart_data["context"],
        "dimensions": list(chart_data["dimensions"].keys()),
        "data_url": chart_data["data_url"],
        "alarms": chart_data["alarms"],
    }

    return json.dumps(chart_info, indent=2)


def get_chart_data(
    netdata_host_url: str,
    chart: str = "system.cpu",
    after: int = -60,
    before: int = 0,
    points: int = 60,
    options: str = None,
    df_freq: str = "5s",
) -> str:
    """
    Calls Netdata /api/v1/data?chart=chart for a specific chart over a specific time range.

    Args:
        netdata_host_url: Netdata host url.
        chart: Chart id.
        after: Seconds before now or timestamp in seconds.
        before: Seconds after now or timestamp in seconds.
        points: Number of points to retrieve. Can be used to aggregate data.
        options: Additional options to pass to the API. 'anomaly-bit' for anomaly rate instead of raw metric values.
        df_freq: Frequency for the pandas DataFrame. Can be used to resample and aggregate data for larger time ranges.

    Returns:
        Pandas DataFrame as a string with the chart data.
    """
    url = f"{netdata_host_url}/api/v1/data"
    query_params = {
        "chart": chart,
        "after": after,
        "before": before,
        "format": "json",
        "points": points,
    }
    if options:
        query_params["options"] = options
    resp = requests.get(url, params=query_params, timeout=5)
    resp_json = resp.json()
    df = pd.DataFrame(resp_json["data"], columns=resp_json["labels"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.set_index("time")
    df = df.asfreq(df_freq)

    return df.to_string(index=False)


def get_alarms(netdata_host_url: str, all: bool = False, active: bool = False) -> str:
    """
    Calls Netdata /api/v1/alarms to retrieve information about alarms.

    Args:
        netdata_host_url: Netdata host url.
        all: Get all enabled alarms regardless of status.
        active: Get only raised alarms in WARNING or CRITICAL status.

    Returns:
        JSON string with alarm information.
    """
    url = f"{netdata_host_url}/api/v1/alarms?{'all' if all else ''}&{'active' if active else ''}"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()

    alarms = {}
    for alarm in r_json["alarms"]:
        alarms[alarm] = {
            "name": r_json["alarms"][alarm].get("name", ""),
            "status": r_json["alarms"][alarm].get("status", ""),
            "value": r_json["alarms"][alarm].get("value", ""),
            "units": r_json["alarms"][alarm].get("units", ""),
            "info": r_json["alarms"][alarm].get("info", ""),
            "summary": r_json["alarms"][alarm].get("summary", ""),
            "chart": r_json["alarms"][alarm].get("chart", ""),
            "class": r_json["alarms"][alarm].get("class", ""),
            "component": r_json["alarms"][alarm].get("component", ""),
            "workload": r_json["alarms"][alarm].get("workload", ""),
            "type": r_json["alarms"][alarm].get("type", ""),
            "active": r_json["alarms"][alarm].get("active", ""),
            "silenced": r_json["alarms"][alarm].get("silenced", ""),
            "disabled": r_json["alarms"][alarm].get("disabled", ""),
            "lookup_dimensions": r_json["alarms"][alarm].get("lookup_dimensions", ""),
            "calc": r_json["alarms"][alarm].get("calc", ""),
            "warn": r_json["alarms"][alarm].get("warn", ""),
            "crit": r_json["alarms"][alarm].get("crit", ""),
        }

    return json.dumps(alarms, indent=2)


def get_current_metrics(netdata_host_url: str, search_term: str = None) -> str:
    """
    Calls Netdata /api/v1/allmetrics to retrieve current values for all metrics. Optionally filter by search_term on he chart name.

    Args:
        netdata_host_url: Netdata host url.
        search_term: Optional search term to filter the metrics by chart name.

    Returns:
        JSON string with all metrics and their current values.
    """
    url = f"{netdata_host_url}/api/v1/allmetrics?format=json"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()
    all_metrics = {
        c: {
            "units": r_json[c]["units"],
            "dimensions": {
                d: r_json[c]["dimensions"][d]["value"] for d in r_json[c]["dimensions"]
            },
        }
        for c in r_json
        if not search_term or search_term in c
    }

    return json.dumps(all_metrics, indent=2)


def get_anomaly_rates(
    netdata_host_url: str, after: int = -60, before: int = 0, search_term: str = None
) -> str:
    """
    Calls Netdata /api/v1/weights?method=anomaly-rate to retrieve anomaly rates for all charts for a given time range or optionally filter by search_term on chart name.

    Args:
        netdata_host_url: Netdata host url.
        after: Seconds before now or timestamp in seconds.
        before: Seconds after now or timestamp in seconds.
        search_term: Optional search term to filter the anomaly rates by chart name.

    Returns:
        JSON string with anomaly rates for all charts.
    """
    url = f"{netdata_host_url}/api/v1/weights?method=anomaly-rate&after={after}&before={before}"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()
    contexts = r_json["contexts"]
    anomaly_rates = []
    for context in contexts:
        for c in contexts[context]["charts"]:
            if search_term and search_term not in c:
                continue
            anomaly_rates.append({f"{c}": contexts[context]["charts"][c]["dimensions"]})

    return json.dumps(anomaly_rates, indent=2)


def get_netdata_docs_sitemap(search_term: str = None) -> str:
    """
    Calls Netdata Learn (docs site) /sitemap.xml to retrieve the sitemap for the Netdata documentation.

    Args:
        search_term: Optional search term to filter the sitemap by URL.

    Returns:
        JSON string with the sitemap URLs.
    """
    url = "https://learn.netdata.cloud/sitemap.xml"
    resp = requests.get(url, timeout=5)
    sitemap = resp.text
    sitemap = [
        s.split("<loc>")[1].split("</loc>")[0] for s in sitemap.split("<url>")[1:]
    ]
    if search_term:
        sitemap = [s for s in sitemap if search_term in s]

    return json.dumps(sitemap, indent=2)


def get_netdata_docs_page(url: str) -> str:
    """
    Calls Netdata Learn (docs site) to retrieve the content of a specific documentation page.

    Args:
        url: URL of the documentation page.

    Returns:
        Markdown rendering of the HTML content of the documentation page.
    """
    resp = requests.get(url, timeout=5)

    return md(resp.text)
