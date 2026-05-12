from rest_framework import serializers
from .models import Empregado, Dispositivo, Registro, Baixa, Usuario, QrCode, LogAuditoria

class EmpregadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empregado
        fields = '__all__'

class DispositivoSerializer(serializers.ModelSerializer):
    empregado_nome = serializers.CharField(source='empregado.nome', read_only=True, default='')
    empregado_matricula = serializers.CharField(source='empregado.matricula', read_only=True, default='')
    empregado_setor = serializers.CharField(source='empregado.setor', read_only=True, default='')
    empregado_cargo = serializers.CharField(source='empregado.cargo', read_only=True, default='')
    empregado_tipo_pessoa = serializers.CharField(source='empregado.tipo_pessoa', read_only=True, default='proprio')
    class Meta:
        model = Dispositivo
        fields = '__all__'

class RegistroSerializer(serializers.ModelSerializer):
    empregado_nome = serializers.CharField(source='empregado.nome', read_only=True, default='')
    empregado_matricula = serializers.CharField(source='empregado.matricula', read_only=True, default='')
    dispositivo_serial = serializers.CharField(source='dispositivo.serial', read_only=True, default='')
    dispositivo_tipo = serializers.CharField(source='dispositivo.tipo', read_only=True, default='')
    dispositivo_patrimonio = serializers.CharField(source='dispositivo.patrimonio', read_only=True, default='')
    dispositivo_categoria = serializers.CharField(source='dispositivo.categoria', read_only=True, default='')
    class Meta:
        model = Registro
        fields = '__all__'

class BaixaSerializer(serializers.ModelSerializer):
    empregado_nome = serializers.CharField(source='empregado.nome', read_only=True, default='')
    dispositivo_serial = serializers.CharField(source='dispositivo.serial', read_only=True, default='')
    dispositivo_tipo = serializers.CharField(source='dispositivo.tipo', read_only=True, default='')
    class Meta:
        model = Baixa
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {'senha': {'write_only': True}}

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    senha = serializers.CharField()
    perfil = serializers.CharField()

class CadastroCompletoSerializer(serializers.Serializer):
    tipo_pessoa = serializers.CharField(default='proprio')
    nome = serializers.CharField()
    matricula = serializers.CharField(required=False, allow_blank=True)
    setor = serializers.CharField(required=False, allow_blank=True)
    cargo = serializers.CharField(required=False, allow_blank=True)
    empresa = serializers.CharField(required=False, allow_blank=True)
    documento = serializers.CharField(required=False, allow_blank=True)
    telefone = serializers.CharField(required=False, allow_blank=True)
    tipo = serializers.CharField(default='notebook')
    tipo_descricao = serializers.CharField(required=False, allow_blank=True)
    serial = serializers.CharField()
    patrimonio = serializers.CharField(required=False, allow_blank=True)
    marca = serializers.CharField(required=False, allow_blank=True)
    modelo = serializers.CharField(required=False, allow_blank=True)
    categoria = serializers.CharField(default='taboca')
    terceira_nome = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(default='em_uso')

class QrCodeSerializer(serializers.ModelSerializer):
    dispositivo_serial = serializers.CharField(source='dispositivo.serial', read_only=True, default='')
    empregado_nome = serializers.SerializerMethodField()

    class Meta:
        model = QrCode
        fields = '__all__'

    def get_empregado_nome(self, obj):
        if obj.dispositivo and obj.dispositivo.empregado:
            return obj.dispositivo.empregado.nome
        return ''
        
        # ═══════════════════════════════════════════════════════════
#  LOG DE AUDITORIA — Serializer
#  Atende: Politica CRP-TIN-TIN-POL-016 (Taboca)
# ═══════════════════════════════════════════════════════════
class LogAuditoriaSerializer(serializers.ModelSerializer):
    """Serializa logs de auditoria pra exibicao no Flutter."""
    
    # Versao "humana" da acao: "Login realizado" em vez de "LOGIN"
    acao_label = serializers.CharField(source='get_acao_display', read_only=True)
    
    class Meta:
        model = LogAuditoria
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'usuario_username',
            'acao',
            'acao_label',
            'descricao',
            'objeto_tipo',
            'objeto_id',
            'objeto_descricao',
            'ip',
            'sucesso',
            'timestamp',
        ]
        # TODOS os campos sao READONLY (log e imutavel!)
        read_only_fields = fields