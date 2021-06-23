from marshmallow import Schema, fields, EXCLUDE


class UserSchema(Schema):
    """
    """
    id = fields.UUID(dump_only=True)

    name = fields.Str(
        error_messages={'invalid': 'Поле name должно быть строкой'}
    )

    last_name = fields.Str(
        error_messages={'invalid': 'Поле last_name должно быть строкой'}
    )

    password = fields.Str(
        error_messages={'invalid': 'Поле password должно быть строкой'}
    )

    birthday = fields.Str(
        error_messages={'invalid': 'Поле birthday должно быть строкой'}
    )

    login = fields.Str(
        required=True,
        error_messages={'invalid': 'Поле login должно быть строкой'}
    )
    admin_flag = fields.Bool()

    class Meta:
        unknown = EXCLUDE
