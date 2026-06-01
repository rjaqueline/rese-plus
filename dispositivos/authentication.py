"""
Autenticacao JWT customizada para o RESE+.
Usa nosso modelo Usuario (em vez do auth.User padrao do Django).

Fica em arquivo separado pra evitar circular imports com o DRF
quando registrado em DEFAULT_AUTHENTICATION_CLASSES.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import Usuario


class UsuarioJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if user_id is None:
            raise InvalidToken('Token sem user_id')
        try:
            return Usuario.objects.get(id=user_id, ativo=True)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Usuario nao encontrado', code='user_not_found')
