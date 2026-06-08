"""Smoke tests for poke-services.

Each service is a stdlib-only HTTP server with an /api/health endpoint.
These tests verify:
  1. The server module imports cleanly.
  2. The module exposes a ``PORT`` constant and a ``Handler`` class.
  3. The /api/health endpoint returns HTTP 200 with ``{"ok": true}``.

Services are started in a background daemon thread on their default port
and shut down after the test via ``server.shutdown()``.
"""

import importlib
import json
import os
import sys
import threading
import time
from http.server import HTTPServer

import httpx
import pytest

# Project root on the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# All poke-services: (module_path, default_port)
# Excluded: email-validator (requires dnspython, not stdlib-only)
SERVICES = [
    ("poke-services.barcode-gen.server", 8782),
    ("poke-services.base64-tool.server", 8775),
    ("poke-services.color-palette.server", 8769),
    ("poke-services.dns-lookup.server", 8768),
    ("poke-services.hash-gen.server", 8779),
    ("poke-services.health-agg.server", 8791),
    ("poke-services.json-formatter.server", 8774),
    ("poke-services.keyword-extractor.server", 8766),
    ("poke-services.link-preview.server", 8765),
    ("poke-services.markdown-render.server", 8776),
    ("poke-services.password-generator.server", 8772),
    ("poke-services.qr-generator.server", 8767),
    ("poke-services.rate-limiter.server", 8780),
    ("poke-services.sentiment.server", 8777),
    ("poke-services.status-dashboard.server", 8790),
    ("poke-services.text-summary.server", 8770),
    ("poke-services.timestamp-converter.server", 8773),
    ("poke-services.timestamp-conv.server", 8781),
    ("poke-services.url-shortener.server", 8771),
    ("poke-services.uuid-gen.server", 8780),
    ("poke-services.webhook-relay.server", 8779),
]


@pytest.fixture(scope="module")
def running_service():
    """Start a service module in a background thread and yield (module, port, server).

    The server is shut down after the test module finishes.
    """

    def _start(module_path: str, port: int):
        mod = importlib.import_module(module_path)
        # Some services bind to 0.0.0.0 by default; override PORT via env
        # so we can use a deterministic port.
        os.environ["PORT"] = str(port)

        # Re-import to pick up the new PORT if module-level code reads it at import time.
        # Most services read PORT at module level, so we need to handle this.
        # We'll create the server manually using the Handler class.
        handler_cls = mod.Handler

        server = HTTPServer(("127.0.0.1", port), handler_cls)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        time.sleep(0.3)  # give the thread a moment to bind
        return mod, port, server

    started = []
    for module_path, port in SERVICES:
        # Offset ports by +1000 to avoid conflicts with any running services
        safe_port = port + 1000
        mod, actual_port, server = _start(module_path, safe_port)
        started.append((mod, actual_port, server))

    yield started

    for _, _, server in started:
        server.shutdown()


class TestServiceImport:
    """Verify each service module can be imported and has expected attributes."""

    @pytest.mark.parametrize("module_path,port", SERVICES)
    def test_import(self, module_path, port):
        mod = importlib.import_module(module_path)
        assert hasattr(mod, "PORT"), f"{module_path} missing PORT"
        # Services use either Handler or H for the HTTP handler class
        has_handler = hasattr(mod, "Handler") or hasattr(mod, "H")
        assert has_handler, f"{module_path} missing Handler/H class"

    @pytest.mark.parametrize("module_path,port", SERVICES)
    def test_handler_is_class(self, module_path, port):
        mod = importlib.import_module(module_path)
        cls = getattr(mod, "Handler", None) or getattr(mod, "H", None)
        assert isinstance(cls, type), f"{module_path} handler is not a class"


class TestServiceHealth:
    """Start each service and hit /api/health."""

    @pytest.mark.parametrize(
        "module_path,port",
        [(mp, p + 1000) for mp, p in SERVICES],
    )
    def test_health_endpoint(self, module_path, port):
        """Start the service on a safe port and verify /api/health returns 200."""
        mod = importlib.import_module(module_path)
        handler_cls = getattr(mod, "Handler", None) or getattr(mod, "H")

        server = HTTPServer(("127.0.0.1", port), handler_cls)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        try:
            # Retry up to 5 times (services are fast, but thread startup can vary)
            last_err = None
            for _ in range(5):
                try:
                    resp = httpx.get(f"http://127.0.0.1:{port}/api/health", timeout=2.0)
                    assert resp.status_code == 200, (
                        f"{module_path} /api/health returned {resp.status_code}"
                    )
                    data = resp.json()
                    assert data.get("ok") is True, (
                        f"{module_path} /api/health ok is not true: {data}"
                    )
                    break
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    last_err = e
                    time.sleep(0.2)
            else:
                pytest.fail(
                    f"{module_path} /api/health unreachable after retries: {last_err}"
                )
        finally:
            server.shutdown()
