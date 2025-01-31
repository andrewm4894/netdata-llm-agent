import json
import requests
import pandas as pd


def get_netdata_info(netdata_host_url: str) -> str:
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
        "netdata_version": r_json['version'],
        "hostname": r_json['mirrored_hosts'][0],
        "operating_system": r_json['os_name'],
        "operating_system_version": r_json['os_id'],
        "cores_total": r_json['cores_total'],
        "total_disk_space": r_json['total_disk_space'],
        "ram_total": r_json['ram_total'],
        "mirrored_hosts_status": r_json['mirrored_hosts_status'],
        "alarms": r_json['alarms'],
        "buildinfo": r_json['buildinfo'],
        "charts-count": r_json['charts-count'],
        "metrics-count": r_json['metrics-count'],
    }

    return json.dumps(info, indent=2)


def get_netdata_charts(netdata_host_url: str) -> str:
    """
    Calls Netdata /api/v1/charts to retrieve the list of available charts and some metadata about each chart.

    Args:
        netdata_host_url: Netdata host url to call.

    Returns:
        JSON string with chart metadata.
    """
    url = f"{netdata_host_url}/api/v1/charts"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()

    charts = {}
    for chart in r_json["charts"]:
        charts[chart] = {
            "name": r_json["charts"][chart]["name"],
            "title": r_json["charts"][chart]["title"],
        }

    return json.dumps(charts, indent=2)


def get_netdata_chart_info(netdata_host_url: str, chart: str = 'system.cpu') -> str:
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


def get_netdata_chart_data(
        netdata_host_url: str,
        chart: str = 'system.cpu',
        after: int = -60,
        before: int = 0,
        points: int = 60
    ) -> str:
    """
    Calls Netdata /api/v1/data?chart=chart for a specific chart.

    Args:
        netdata_host_url: Netdata host url.
        chart: Chart id.
        after: Seconds before now or timestamp in seconds.
        before: Seconds after now or timestamp in seconds.
        points: Number of points to retrieve. Can be used to aggregate data.

    Returns:
        JSON string with chart data.
    """
    url = f"{netdata_host_url}/api/v1/data"
    query_params = {
        "chart": chart,
        "after": after,
        "before": before,
        "format": "json",
        "points": points,
    }
    resp = requests.get(url, params=query_params, timeout=5)
    resp_json = resp.json()
    df = pd.DataFrame(resp_json["data"], columns=resp_json["labels"])

    return df.to_string(index=False)


def get_netdata_alarms(netdata_host_url: str) -> str:
    """
    Calls Netdata /api/v1/alarms to retrieve the list of active alarms.

    Args:
        netdata_host_url: Netdata host url.

    Returns:
        JSON string with active alarms.
    """
    url = f"{netdata_host_url}/api/v1/alarms"
    resp = requests.get(url, timeout=5)
    r_json = resp.json()

    alarms = {}
    for alarm in r_json["alarms"]:
        alarms[alarm] = {
            "name": r_json["alarms"][alarm]["name"],
            "status": r_json["alarms"][alarm]["status"],
            "value": r_json["alarms"][alarm]["value"],
            "info": r_json["alarms"][alarm]["info"],
        }

    return json.dumps(alarms, indent=2)
