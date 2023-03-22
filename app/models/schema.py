from marshmallow import fields, Schema


class ModelSchema(Schema):
    """Model schema"""

    id = fields.String(attribute="id")
    project_id = fields.String(attribute="project_id")