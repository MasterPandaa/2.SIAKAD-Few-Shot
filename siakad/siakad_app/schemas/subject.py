from marshmallow import Schema, fields, validate


class SubjectSchema(Schema):
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True, validate=validate.Regexp(r'^[A-Z0-9_\-]{2,12}$'))
    name = fields.Str(required=True, validate=validate.Length(min=2))
    sks = fields.Int(required=True, validate=validate.Range(min=1, max=6))
    teacher_id = fields.Int(required=False, allow_none=True)
