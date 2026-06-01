from django.db import models
from django.utils import timezone
from datetime import timedelta

class Empregado(models.Model):
    TIPOS_PESSOA = [('proprio', 'Proprio'), ('terceiro', 'Terceiro'), ('visitante', 'Visitante')]

    nome = models.CharField(max_length=200)
    tipo_pessoa = models.CharField(max_length=20, choices=TIPOS_PESSOA, default='proprio')
    matricula = models.CharField(max_length=50, blank=True, null=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    empresa = models.CharField(max_length=200, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    setor = models.CharField(max_length=100, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    foto_url = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        identificador = self.matricula or self.documento or ''
        return self.nome + ' - ' + identificador

    class Meta:
        ordering = ['nome']

class Dispositivo(models.Model):
    TIPOS = [('notebook', 'Notebook'), ('celular', 'Celular'), ('tablet', 'Tablet'), ('outro', 'Outro')]
    CATEGORIAS = [('taboca', 'Taboca'), ('terceira', 'Terceira'), ('pessoal', 'Pessoal')]
    STATUS = [('disponivel', 'Disponivel'), ('em_uso', 'Em uso'), ('manutencao', 'Manutencao')]

    tipo = models.CharField(max_length=50, choices=TIPOS, default='notebook')
    tipo_descricao = models.CharField(max_length=200, blank=True, null=True)
    patrimonio = models.CharField(max_length=50, blank=True, null=True)
    serial = models.CharField(max_length=100)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='taboca')
    terceira_nome = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='em_uso')
    empregado = models.ForeignKey(Empregado, on_delete=models.SET_NULL, null=True, related_name='dispositivos')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.serial + ' - ' + self.tipo

    class Meta:
        ordering = ['-criado_em']

class Registro(models.Model):
    TIPOS = [('CHECK-IN', 'Check-in'), ('CHECK-OUT', 'Check-out')]

    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='registros')
    empregado = models.ForeignKey(Empregado, on_delete=models.CASCADE, related_name='registros')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    operador_nome = models.CharField(max_length=200, blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tipo + ' - ' + self.dispositivo.serial

    class Meta:
        ordering = ['-data_hora']

class Baixa(models.Model):
    MOTIVOS = [('devolucao', 'Devolucao'), ('demissao', 'Demissao'), ('troca', 'Troca'), ('transferencia', 'Transferencia'), ('furto_perda', 'Furto/Perda')]

    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='baixas')
    empregado = models.ForeignKey(Empregado, on_delete=models.SET_NULL, null=True)
    motivo = models.CharField(max_length=20, choices=MOTIVOS)
    observacao = models.TextField(blank=True, null=True)
    usuario_nome = models.CharField(max_length=200, blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.motivo + ' - ' + self.dispositivo.serial

    class Meta:
        ordering = ['-data_hora']





class Usuario(models.Model):
    PERFIS = [('master', 'Admin Master'), ('usuario', 'Usuario'), ('operador', 'Operador')]

    nome = models.CharField(max_length=200)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)  # Opcional agora
    senha = models.CharField(max_length=255)
    perfil = models.CharField(max_length=20, choices=PERFIS, default='usuario')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    senha_atualizada_em = models.DateTimeField(auto_now=True)

    # CAMPOS DE SEGURANCA
    precisa_trocar_senha = models.BooleanField(
        default=True,
        help_text='True no primeiro login ou quando admin resetou a senha'
    )
    @property
    def is_authenticated(self):
        return True
    senha_expira_em = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Data em que a senha expira e o usuario sera forcado a trocar'
    )
    dias_validade_senha = models.IntegerField(
        default=90,
        help_text='Quantos dias a senha e valida (padrao corporativo: 90)'
    )
    tentativas_login_falhas = models.IntegerField(default=0)
    ultimo_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nome + ' - ' + self.perfil

    def atualizar_expiracao_senha(self):
        """Atualiza a data de expiracao com base em dias_validade_senha."""
        self.senha_expira_em = timezone.now() + timedelta(days=self.dias_validade_senha)

    def senha_esta_expirada(self):
        """Verifica se a senha esta expirada."""
        if not self.senha_expira_em:
            return False
        return timezone.now() > self.senha_expira_em

    class Meta:
        ordering = ['nome']


class QrCode(models.Model):
    STATUS = [('disponivel', 'Disponivel'), ('em_uso', 'Em uso'), ('danificado', 'Danificado'), ('inutilizado', 'Inutilizado')]

    codigo = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS, default='disponivel')
    dispositivo = models.OneToOneField(Dispositivo, on_delete=models.SET_NULL, null=True, blank=True, related_name='qrcode')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo + ' - ' + self.status

    class Meta:
        ordering = ['codigo']
        # ═══════════════════════════════════════════════════════════
#  LogAuditoria — Rastreabilidade de acoes sensiveis
#  Atende: Politica CRP-TIN-TIN-POL-016 (Taboca)
#  Retencao: 90 dias minimo
# ═══════════════════════════════════════════════════════════
class LogAuditoria(models.Model):
    """
    Registro imutavel de acoes realizadas no sistema.
    Cada acao sensivel cria uma linha aqui.
    """
    
    # Tipos de acoes categorizadas
    ACOES = [
        # Autenticacao
        ('LOGIN', 'Login realizado'),
        ('LOGOUT', 'Logout realizado'),
        ('LOGIN_FALHA', 'Tentativa de login falhada'),
        
        # Senhas
        ('SENHA_TROCADA', 'Senha alterada pelo proprio usuario'),
        ('SENHA_RESETADA', 'Senha resetada por administrador'),
        ('SENHA_EXPIRADA', 'Senha expirou'),
        
        # Usuarios (CRUD)
        ('USUARIO_CRIADO', 'Novo usuario criado'),
        ('USUARIO_EDITADO', 'Usuario editado'),
        ('USUARIO_DESATIVADO', 'Usuario desativado'),
        
        # Dispositivos (CRUD)
        ('DISPOSITIVO_CRIADO', 'Novo dispositivo cadastrado'),
        ('DISPOSITIVO_EDITADO', 'Dispositivo editado'),
        ('DISPOSITIVO_BAIXA', 'Dispositivo dado baixa'),
        
        # QR Codes
        ('QR_GERADO', 'QR Code gerado em lote'),
        ('QR_VINCULADO', 'QR Code vinculado a dispositivo'),
        ('QR_DESVINCULADO', 'QR Code desvinculado'),
        ('QR_INUTILIZADO', 'QR Code inutilizado'),
        
        # Movimentacoes
        ('SCAN_CHECKIN', 'Check-in via scan'),
        ('SCAN_CHECKOUT', 'Check-out via scan'),
        
        # Outros
        ('OUTRO', 'Outra acao'),
    ]
    
    # Quem fez a acao
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,  # Se usuario for deletado, mantem log
        null=True,
        blank=True,
        related_name='logs_auditoria',
        verbose_name='Usuario'
    )
    
    # Nome cacheado (pra caso usuario seja deletado)
    usuario_nome = models.CharField(max_length=200, blank=True)
    usuario_username = models.CharField(max_length=100, blank=True)
    
    # O que aconteceu
    acao = models.CharField(max_length=50, choices=ACOES)
    descricao = models.TextField(blank=True)
    
    # Em qual objeto (opcional)
    objeto_tipo = models.CharField(max_length=50, blank=True)  # Ex: "Dispositivo", "Usuario"
    objeto_id = models.IntegerField(null=True, blank=True)
    objeto_descricao = models.CharField(max_length=200, blank=True)  # Ex: "Notebook Dell SN12345"
    
    # Contexto de rede (forense)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Sucesso ou falha
    sucesso = models.BooleanField(default=True)
    
    # Timestamp (imutavel)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-timestamp']  # Mais recentes primeiro
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['acao', '-timestamp']),
        ]
    
    def __str__(self):
        nome = self.usuario_username or self.usuario_nome or 'Sistema'
        return f'[{self.timestamp:%d/%m/%Y %H:%M}] {nome} - {self.get_acao_display()}'