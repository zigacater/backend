from marshmallow import Schema, fields, validate

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True, load_default=None)
    due_date = fields.Str(allow_none=True, load_default=None)
    priority = fields.Int(required=False, load_default=0,validate=validate.Range(min=0, max=5))
    created_at = fields.DateTime(dump_only=True)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
