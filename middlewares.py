import time
import requests
import threading
from django.conf import settings

class HeliosMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Retrieve Helios configurations from Django settings
        self.api_key = 'dw_e75b8134f65c370a2a4ba1701fa889dbb0ba3ddc6705b3ba'
        self.helios_url = 

    def __call__(self, request):B
        # 1. Start high-precision timer
        start_time = time.perf_counter()

        # 2. Process the request
        response = self.get_response(request)

        # 3. Calculate execution time in milliseconds
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # 4. Upload metric using a daemon thread to prevent blocking client responses
        if self.api_key:
            threading.Thread(
                target=self._upload_metric,
                args=(latency_ms,),
                daemon=True
            ).start()

        return response

    def _upload_metric(self, latency):
        try:
            requests.post(
                f"{self.helios_url}/metrics",
                headers={"x-api-key": self.api_key},
                json={"type": "latency", "value": round(latency, 2)},
                timeout=2.0  # Safe timeout limit
            )
        except Exception:
            # Silently pass telemetry failures to keep production resilient
            pass