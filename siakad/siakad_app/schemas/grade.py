from marshmallow import Schema, fields, validate


class GradeSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    subject_id = fields.Int(required=True)
    tugas = fields.Float(
        required=True, validate=validate.Range(min=0, max=100))
    uts = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    uas = fields.Float(required=True, validate=validate.Range(min=0, max=100))
