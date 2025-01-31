import json
import requests
import pandas as pd


def get_netdata_info(base_url: str) -> str:
    """
    Calls Netdata /api/v1/info to retrieve system info.

    Args:
        base_url: Netdata base url.

    Returns:
        System info.
    """
    url = f"{base_url}/api/v1/info"
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


def get_netdata_info(base_url: str) -> str:
    """
    Calls Netdata /api/v1/info to retrieve system info.

    Args:
        base_url: Netdata base url.

    Returns:
        System info.
    """
    url = f"{base_url}/api/v1/info"
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


def get_netdata_info(base_url: str) -> str:
    """
    Calls Netdata /api/v1/info to retrieve system info.

    Args:
        base_url: Netdata base url.

    Returns:
        System info.
    """
    url = f"{base_url}/api/v1/info"
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


def get_netdata_charts(base_url: str) -> str:
    """
    Calls Netdata /api/v1/charts to retrieve the list of available charts.
    """
    url = f"{base_url}/api/v1/charts"
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


def get_netdata_chart_info(base_url: str, chart: str = 'system.cpu') -> str:
    """
    Calls Netdata /api/v1/charts to retrieve info for a specific chart.

    Args:
        base_url: Netdata base url.
        chart: Chart id.

    Returns:
        Chart info.
    """
    url = f"{base_url}/api/v1/charts"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    chart_data = resp.json()["charts"][chart]

    chart_info = {
        "id": chart_data["id"],
        "title": chart_data["title"],
        "units": chart_data["units"],
        "family": chart_data["family"],
        "context": chart_data["context"],
        "dimensions": list(chart_data["dimensions"].keys()),
    }

    return json.dumps(chart_info, indent=2)


def get_netdata_chart_data(base_url: str, chart: str = 'system.cpu', after: int = -60, before: int = 0, points: int = 60) -> str:
    """
    Calls Netdata /api/v1/data?chart=chart for a specific chart.
    """
    url = f"{base_url}/api/v1/data"
    query_params = {
        "chart": chart,
        "after": after,
        "before": before,
        "format": "json",
        "points": points,
    }

    resp = requests.get(url, params=query_params, timeout=5)
    resp.raise_for_status()
    resp_json = resp.json()
    df = pd.DataFrame(resp_json["data"], columns=resp_json["labels"])

    return df.to_string(index=False)