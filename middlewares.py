import time
import requests
import threading
from django.conf import settings

class HeliosMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Retrieve Helios configurations from Django settings
        self.api_key = 'dw_0e744e8ea7dd0d2b121be71997600971efa9a1b534f02891'
        self.helios_url = 'https://deploywatchapi.onrender.com/api'

    def __call__(self, request):
        # 1. Start high-precision timer
        start_time = time.perf_counter()

        # 2. Process the request
        response = self.get_response(request)

        # 3. Calculate execution time in milliseconds
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # 4. Upload metrics using a daemon thread to prevent blocking client responses
        if self.api_key:
            threading.Thread(
                target=self._upload_metrics,
                args=(latency_ms,),
                daemon=True
            ).start()

        return response

    def _upload_metrics(self, latency):
        try:
            import psutil
            # 1. Report request latency
            requests.post(
                f"{self.helios_url}/metrics",
                headers={"x-api-key": self.api_key},
                json={"type": "latency", "value": round(latency, 2)},
                timeout=2.0
            )
            # 2. Report system CPU utilization
            cpu_usage = psutil.cpu_percent()
            requests.post(
                f"{self.helios_url}/metrics",
                headers={"x-api-key": self.api_key},
                json={"type": "cpu", "value": round(cpu_usage, 2)},
                timeout=2.0
            )
            # 3. Report system RAM utilization
            ram_usage = psutil.virtual_memory().percent
            requests.post(
                f"{self.helios_url}/metrics",
                headers={"x-api-key": self.api_key},
                json={"type": "ram", "value": round(ram_usage, 2)},
                timeout=2.0
            )
        except Exception:
            # Silently pass telemetry failures to keep production resilient
            pass