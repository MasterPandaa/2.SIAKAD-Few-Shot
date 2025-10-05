from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class RegisterUserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(
        required=True, validate=validate.OneOf(["ADMIN", "TEACHER", "STUDENT"])
    )
    student_id = fields.Int(required=False, allow_none=True)
    teacher_id = fields.Int(required=False, allow_none=True)

    @validates_schema
    def validate_links(self, data, **kwargs):
        role = data.get("role")
        if role == "STUDENT" and not data.get("student_id"):
            raise ValidationError("student_id wajib diisi untuk role STUDENT")
        if role == "TEACHER" and not data.get("teacher_id"):
            raise ValidationError("teacher_id wajib diisi untuk role TEACHER")
        if role == "ADMIN" and (data.get("student_id") or data.get("teacher_id")):
            raise ValidationError(
                "ADMIN tidak boleh memiliki student_id/teacher_id")
