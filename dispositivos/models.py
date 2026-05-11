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