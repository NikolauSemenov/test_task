import marshmallow.validate
from marshmallow import Schema, fields, EXCLUDE


class UserSchema(Schema):
    """
    """
    id = fields.UUID(dump_only=True)

    name = fields.Str(
        required=True,
        validate=marshmallow.validate.Length(min=5)
    )

    last_name = fields.Str(
        required=True
    )

    password = fields.Str(
        required=True
    )

    birthday = fields.Date(
        required=True
    )

    login = fields.Str(
        required=True
    )
    admin_flag = fields.Bool(missing=False, default=False)

    class Meta:
        unknown = EXCLUDE


class UsersList(Schema):
    users = fields.List(fields.Str(), required=True)


class UpdateSchema(Schema):

    login = fields.Str(required=True)
    name = fields.Str(required=True)
    last_name = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE


class DeleteSchema(Schema):

    login = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE