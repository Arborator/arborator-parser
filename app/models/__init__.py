from flask_restx import Api


NAMESPACE_AFFIXE = "models"


def register_routes(api: Api, base_url):
    from .controller import namespace as models_namespace

    api.add_namespace(models_namespace, path=f"/{base_url}/{NAMESPACE_AFFIXE}")
