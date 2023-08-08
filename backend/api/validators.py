import re
from django.core.exceptions import ValidationError


def model_validate_username(value):
    if value == 'me':
        raise ValidationError(f'{value} служебное имя!')
    bad_symbol = ''.join(
        set(''.join(re.sub(r'[\w.@+-]+', '', value)))
    )
    if bad_symbol != '':
        raise ValidationError(
            f'в username используются недопустимые '
            f'символы: {bad_symbol}'
        )
    return value


def model_validate_minutes(value):
    if value <= 0:
        raise ValidationError(
            f'Время приготовления рецепта "{value}" неправильное!')
    return value


def model_validate_qty(value):
    if value <= 0:
        raise ValidationError(
            f'Количество указано неверно - "{value}"')
    return value


def model_validate_slug(value):
    if value is not None:
        # pattern: ^[-a-zA-Z0-9_]+$
        bad_symbol = ''.join(
            set(
                ''.join(
                    re.sub(r'[-a-zA-Z0-9_]+', '', value)
                )
            )
        )
        if bad_symbol != '':
            raise ValidationError(
                f'в slug используются недопустимые '
                f'символы: {bad_symbol}'
            )
    return value
