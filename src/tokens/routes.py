API_ROUTE_METHOD = {
    "Get": "GET",
    "Post": "POST",
    "Put": "PUT",
    "Patch": "PATCH",
    "Delete": "DELETE",
}

health_live_contract = {
    "method": API_ROUTE_METHOD["Get"],
    "path": "/health/live",
    "response": {"data": {"status": "ok"}},
}

health_ready_contract = {
    "method": API_ROUTE_METHOD["Get"],
    "path": "/health/ready",
    "response": {"data": {"status": "ok|unready"}},
}

health_routes = {
    "live": health_live_contract,
    "ready": health_ready_contract,
}

metrics_contract = {
    "method": API_ROUTE_METHOD["Get"],
    "path": "/metrics",
    "response": "text/plain",
}

metrics_routes = {
    "collect": metrics_contract,
}
