def register_routes(api, base_url):
    from app.models import register_routes as attach_models

    # Add routes
    attach_models(api, base_url)
