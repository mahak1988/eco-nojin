"""Build satellite router with EO stack attached."""
from apps.satellite.router import router
from apps.satellite.eo_routes_attach import attach_eo_routes

attach_eo_routes(router)
