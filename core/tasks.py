import requests
import psutil

def collect_and_send_metrics():
    """
    Collect system metrics (CPU, RAM) and send to Helios API.
    Called by cron job every 5 minutes.
    """
    api_key = 'dw_314ec0c492d6b9a6a9920af845548d229b04fa94636af81a'
    helios_url = 'https://deploywatchapi.onrender.com/api'
    
    try:
        # 1. Report system CPU utilization
        cpu_usage = psutil.cpu_percent()
        requests.post(
            f"{helios_url}/metrics",
            headers={"x-api-key": api_key},
            json={"type": "cpu", "value": round(cpu_usage, 2)},
            timeout=2.0
        )
        
        # 2. Report system RAM utilization
        ram_usage = psutil.virtual_memory().percent
        requests.post(
            f"{helios_url}/metrics",
            headers={"x-api-key": api_key},
            json={"type": "ram", "value": round(ram_usage, 2)},
            timeout=2.0
        )
        
        return f"Metrics sent successfully: CPU={cpu_usage}%, RAM={ram_usage}%"
    except Exception as e:
        return f"Error sending metrics: {str(e)}"
