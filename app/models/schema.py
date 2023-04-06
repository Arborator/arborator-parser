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
    train_task_id = fields.String(attribute="train_task_id", required=True)


class ParsingSettingsSchema(Schema):
    """ParsingSettings schema"""
    keep_upos = fields.String(attribute="keep_upos", default="NONE")
    keep_xpos = fields.String(attribute="keep_xpos", default="NONE")
    keep_lemmas = fields.String(attribute="keep_lemmas", default="NONE")
    keep_deprels = fields.String(attribute="keep_deprels", default="NONE")
    keep_heads = fields.String(attribute="keep_heads", default="NONE")
    keep_feats = fields.String(attribute="keep_feats", default="NONE")

class ModelParseStartPostSchema(Schema):
    "ModelParseStartPost Schema"
    model_info = fields.Nested(ModelInfoSchema, attribute="model_info", required=True)
    parsing_settings = fields.Nested(ParsingSettingsSchema, attribute="parsing_settings", required=True)
    to_parse_samples = fields.Dict(keys=fields.String(), values=ConllSampleField, attribute="to_parse_samples", required=True)

class ModelParseStatusPostSchema(Schema):
    "ModelParseStatusPost Schema"
    parse_task_id = fields.String(attribute="parse_task_id", required=True)