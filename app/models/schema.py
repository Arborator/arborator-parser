from marshmallow import fields, Schema, ValidationError
from conllup.conllup import sentenceConllToJson



class ModelInfoSchema(Schema):
    """ModelInfo schema"""
    model_id = fields.String(attribute="model_id")
    project_name = fields.String(attribute="project_name")



class ConllSampleField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if type(value) != str:
            raise ValidationError(f'Not a string : {value}')
        for sentence_conll in value.strip().rstrip().split("\n\n"):
            try: 
                sentenceConllToJson(sentence_conll)
            except:
                print("ConllValidationError : ", sentence_conll)
                raise ValidationError(f'Invalid sentence conll found:\n{sentence_conll}')
        return value


class ModelTrainStartPostSchema(Schema):
    "ModelTrainStartPost Schema"
    project_name = fields.String(attribute="project_name", required=True)
    train_samples = fields.Dict(keys=fields.String(), values=ConllSampleField, attribute="train_samples", required=True)
    max_epoch = fields.Integer(attribute="max_epoch", load_default=10)
    base_model = fields.Nested(ModelInfoSchema, attribute="base_model", allow_none=True)


class ModelTrainStatusPostSchema(Schema):
    model_info = fields.Nested(ModelInfoSchema, attribute="model_info", required=True)
    parse_train_id = fields.String(attribute="parse_train_id", required=True)


class ModelParseStartPostSchema(Schema):
    "ModelParseStartPost Schema"
    model_info = fields.Nested(ModelInfoSchema, attribute="model_info", required=True)
    to_parse_samples = fields.Dict(keys=fields.String(), values=ConllSampleField, attribute="to_parse_samples", required=True)

class ModelParseStatusPostSchema(Schema):
    "ModelParseStatusPost Schema"
    parse_task_id = fields.String(attribute="parse_task_id", required=True)