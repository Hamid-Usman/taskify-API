import time
import requests
import threading
from django.conf import settings


class HeliosMetricsMiddleware:
    """Middleware that records request latency and uploads metrics no more
    than once every 5 minutes. Uploads run in a short-lived daemon thread so
    responses are not blocked. This keeps everything in-process (no cron,
    no background worker).
    """
    # Class-level state shared across requests/process worker
    _last_metrics_time = 0
    _metrics_lock = threading.Lock()
    _metrics_interval = 60  # 5 minutes in seconds

    def __init__(self, get_response):
        self.get_response = get_response
        # Allow overriding via settings; fall back to the embedded key/URL
        self.api_key = getattr(settings, 'HELIOS_API_KEY', 'dw_ec78830b1b41449dc4a04e1b326729e7a73b4cd41ee04224')
        self.helios_url = getattr(settings, 'HELIOS_URL', 'https://deploywatchapi.onrender.com/api')

    def __call__(self, request):
        # Start high-precision timer
        start_time = time.perf_counter()

        # Process the request
        response = self.get_response(request)

        # Calculate execution time in milliseconds
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Decide whether to upload (throttled)
        current_time = time.time()
        should_upload = False
        with HeliosMetricsMiddleware._metrics_lock:
            if current_time - HeliosMetricsMiddleware._last_metrics_time >= HeliosMetricsMiddleware._metrics_interval:
                HeliosMetricsMiddleware._last_metrics_time = current_time
                should_upload = True

        if self.api_key and should_upload:
            threading.Thread(
                target=self._upload_metrics,
                args=(latency_ms,),
                daemon=True,
            ).start()

        return response

    def _upload_metrics(self, latency):
        try:
            import psutil

            # 1. Report request latency
            try:
                requests.post(
                    f"{self.helios_url}/metrics",
                    headers={"x-api-key": self.api_key},
                    json={"type": "latency", "value": round(latency, 2)},
                    timeout=2.0,
                )
            except Exception:
                # swallow single-request errors and continue
                pass

            # 2. Report system CPU utilization
            try:
                cpu_usage = psutil.cpu_percent()
                requests.post(
                    f"{self.helios_url}/metrics",
                    headers={"x-api-key": self.api_key},
                    json={"type": "cpu", "value": round(cpu_usage, 2)},
                    timeout=2.0,
                )
            except Exception:
                pass

            # 3. Report system RAM utilization
            try:
                ram_usage = psutil.virtual_memory().percent
                requests.post(
                    f"{self.helios_url}/metrics",
                    headers={"x-api-key": self.api_key},
                    json={"type": "ram", "value": round(ram_usage, 2)},
                    timeout=2.0,
                )
            except Exception:
                pass

        except Exception:
            # Keep telemetry failures silent to avoid affecting app behavior
            pass