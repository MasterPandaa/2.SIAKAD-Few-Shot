from marshmallow import Schema, fields, validate


class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    nis = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^\d{10}$", error="NIS harus 10 digit angka"),
    )
    name = fields.Str(required=True, validate=validate.Length(min=3))
    birth_date = fields.Date(required=True)
    address = fields.Str(required=False, allow_none=True)
    gender = fields.Str(required=True, validate=validate.OneOf(["L", "P"]))
    parent_phone = fields.Str(
        required=False, allow_none=True, validate=validate.Regexp(r"^\d{8,15}$")
    )
    class_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=20))
