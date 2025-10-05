from marshmallow import Schema, fields, validate


class TeacherSchema(Schema):
    id = fields.Int(dump_only=True)
    nip = fields.Str(required=True, validate=validate.Regexp(r"^\d{8,18}$"))
    name = fields.Str(required=True, validate=validate.Length(min=3))
    phone = fields.Str(
        required=False, allow_none=True, validate=validate.Regexp(r"^\d{8,15}$")
    )
    address = fields.Str(required=False, allow_none=True)
