from marshmallow import fields, Schema, ValidationError


class ModelSchema(Schema):
    """Model schema"""
    id = fields.String(attribute="id")
    project_name = fields.String(attribute="project_name")


from conllup.conllup import sentenceConllToJson

class ConllSampleField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if type(value) != str:
            raise ValidationError(f'Not a string : {value}')
        for sentence_conll in value.strip().rstrip().split("\n\n"):
            try: 
                sentenceConllToJson(sentence_conll)
            except:
                raise ValidationError(f'Invalid sentence conll found:\n{sentence_conll}')
        return value


class ModelTrainerPostSchema(Schema):
    "ModelTrainerPost Schema"
    project_name = fields.String(attribute="project_name", required=True)
    train_samples = fields.Dict(keys=fields.String(), values=ConllSampleField, attribute="train_samples", required=True)
    max_epoch = fields.Integer(attribute="max_epoch", load_default=10)


class ModelTrainStatusPostSchema(Schema):
    project_name = fields.String(attribute="project_name", required=True)
    model_id = fields.String(attribute="model_id", required=True)


class ModelParserStartPostSchema(Schema):
    "ModelParserStartPostSchema Schema"
    project_name = fields.String(attribute="project_name", required=True)
    model_id = fields.String(attribute="model_id", required=True)
    to_parse_samples = fields.Dict(keys=fields.String(), values=ConllSampleField, attribute="to_parse_samples", required=True)