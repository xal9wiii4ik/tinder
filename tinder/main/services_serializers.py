from rest_framework import serializers


def verification_password(value: str) -> str:
    """Проверка пароля"""

    if len(value) >= 8:
        if any((c in set('QAZWSXEDCRFVTGBYHNUJMIKOLP')) for c in value):
            if any((f in set('1234567890') for f in value)):
                return value
            else:
                raise serializers.ValidationError('Password must contain at least 1 number')
        else:
            raise serializers.ValidationError('Password must contain at least 1 uppercase letter')
    else:
        raise serializers.ValidationError('Password must have to have at least 8 characters')
