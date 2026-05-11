from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from .models import Empregado, Dispositivo, Registro, Baixa, Usuario, QrCode
from .serializers import (
    EmpregadoSerializer, DispositivoSerializer, RegistroSerializer,
    BaixaSerializer, UsuarioSerializer, LoginSerializer,
    CadastroCompletoSerializer, QrCodeSerializer
)
import re


def validar_politica_senha(senha):
    if len(senha) < 8:
        return False, 'A senha deve ter pelo menos 8 caracteres'
    if not re.search(r'[A-Z]', senha):
        return False, 'A senha deve ter pelo menos 1 letra maiuscula'
    if not re.search(r'[a-z]', senha):
        return False, 'A senha deve ter pelo menos 1 letra minuscula'
    if not re.search(r'[0-9]', senha):
        return False, 'A senha deve ter pelo menos 1 numero'
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', senha):
        return False, 'A senha deve ter pelo menos 1 caractere especial (!@#$%...)'
    return True, ''


def gerar_tokens_para_usuario(usuario):
    refresh = RefreshToken()
    refresh['user_id'] = usuario.id
    refresh['username'] = usuario.username
    refresh['perfil'] = usuario.perfil

    access = refresh.access_token
    access['user_id'] = usuario.id
    access['username'] = usuario.username
    access['perfil'] = usuario.perfil

    return {
        'refresh': str(refresh),
        'access': str(access),
    }


# ===============================================================
#  VIEWSETS
# ===============================================================
class EmpregadoViewSet(viewsets.ModelViewSet):
    queryset = Empregado.objects.filter(ativo=True)
    serializer_class = EmpregadoSerializer


class DispositivoViewSet(viewsets.ModelViewSet):
    queryset = Dispositivo.objects.filter(ativo=True).select_related('empregado')
    serializer_class = DispositivoSerializer

    @action(detail=False, methods=['get'], url_path='buscar/(?P<serial>[^/.]+)')
    def buscar_por_serial(self, request, serial=None):
        try:
            disp = Dispositivo.objects.select_related('empregado').get(
                serial__iexact=serial, ativo=True
            )
            return Response(DispositivoSerializer(disp).data)
        except Dispositivo.DoesNotExist:
            return Response(
                {'erro': 'Dispositivo nao encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all().select_related('empregado', 'dispositivo')
    serializer_class = RegistroSerializer


class BaixaViewSet(viewsets.ModelViewSet):
    queryset = Baixa.objects.all().select_related('empregado', 'dispositivo')
    serializer_class = BaixaSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        senha_pura = request.data.get('senha', '')
        if senha_pura:
            valido, erro = validar_politica_senha(senha_pura)
            if not valido:
                return Response({'erro': erro}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.save()
        usuario.senha = make_password(senha_pura)
        usuario.precisa_trocar_senha = True
        usuario.atualizar_expiracao_senha()
        usuario.save()

        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        usuario = self.get_object()
        senha_pura = request.data.get('senha', '')

        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        if senha_pura:
            valido, erro = validar_politica_senha(senha_pura)
            if not valido:
                return Response({'erro': erro}, status=status.HTTP_400_BAD_REQUEST)
            usuario.senha = make_password(senha_pura)
            usuario.precisa_trocar_senha = True
            usuario.atualizar_expiracao_senha()
            usuario.save()

        return Response(UsuarioSerializer(usuario).data)


class QrCodeViewSet(viewsets.ModelViewSet):
    queryset = QrCode.objects.all()
    serializer_class = QrCodeSerializer


# ===============================================================
#  LOGIN — por username + senha (PUBLICO)
# ===============================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    username = serializer.validated_data['username']
    senha = serializer.validated_data['senha']
    perfil = serializer.validated_data['perfil']

    try:
        usuario = Usuario.objects.get(username=username, ativo=True)
    except Usuario.DoesNotExist:
        return Response({'erro': 'Usuario ou senha incorretos'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(senha, usuario.senha):
        usuario.tentativas_login_falhas += 1
        usuario.save()
        return Response({'erro': 'Usuario ou senha incorretos'}, status=status.HTTP_401_UNAUTHORIZED)

    if usuario.perfil != perfil:
        return Response({'erro': 'Perfil incorreto para este usuario'}, status=status.HTTP_403_FORBIDDEN)

    usuario.tentativas_login_falhas = 0
    usuario.ultimo_login = timezone.now()
    usuario.save()

    tokens = gerar_tokens_para_usuario(usuario)
    data = UsuarioSerializer(usuario).data
    data['precisa_trocar_senha'] = usuario.precisa_trocar_senha or usuario.senha_esta_expirada()
    data['senha_expirada'] = usuario.senha_esta_expirada()
    data['access'] = tokens['access']
    data['refresh'] = tokens['refresh']
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_auto(request):
    username = request.data.get('username', '')
    senha = request.data.get('senha', '')
    if not username or not senha:
        return Response({'erro': 'Preencha usuario e senha'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(username=username, ativo=True)
    except Usuario.DoesNotExist:
        return Response({'erro': 'Usuario ou senha incorretos'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(senha, usuario.senha):
        usuario.tentativas_login_falhas += 1
        usuario.save()
        return Response({'erro': 'Usuario ou senha incorretos'}, status=status.HTTP_401_UNAUTHORIZED)

    usuario.tentativas_login_falhas = 0
    usuario.ultimo_login = timezone.now()
    usuario.save()

    tokens = gerar_tokens_para_usuario(usuario)
    data = UsuarioSerializer(usuario).data
    data['precisa_trocar_senha'] = usuario.precisa_trocar_senha or usuario.senha_esta_expirada()
    data['senha_expirada'] = usuario.senha_esta_expirada()
    data['access'] = tokens['access']
    data['refresh'] = tokens['refresh']
    return Response(data)


# ===============================================================
#  TROCAR SENHA
# ===============================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def trocar_senha(request):
    usuario_id = request.data.get('usuario_id')
    senha_atual = request.data.get('senha_atual', '')
    senha_nova = request.data.get('senha_nova', '')

    if not usuario_id:
        return Response({'erro': 'ID do usuario obrigatorio'}, status=status.HTTP_400_BAD_REQUEST)
    if not senha_atual or not senha_nova:
        return Response({'erro': 'Preencha a senha atual e a nova'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(pk=usuario_id, ativo=True)
    except Usuario.DoesNotExist:
        return Response({'erro': 'Usuario nao encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if not check_password(senha_atual, usuario.senha):
        return Response({'erro': 'Senha atual incorreta'}, status=status.HTTP_401_UNAUTHORIZED)

    valido, erro = validar_politica_senha(senha_nova)
    if not valido:
        return Response({'erro': erro}, status=status.HTTP_400_BAD_REQUEST)

    if check_password(senha_nova, usuario.senha):
        return Response({'erro': 'A nova senha deve ser diferente da atual'}, status=status.HTTP_400_BAD_REQUEST)

    usuario.senha = make_password(senha_nova)
    usuario.precisa_trocar_senha = False
    usuario.atualizar_expiracao_senha()
    usuario.save()

    tokens = gerar_tokens_para_usuario(usuario)

    return Response({
        'mensagem': 'Senha atualizada com sucesso',
        'senha_expira_em': usuario.senha_expira_em.isoformat() if usuario.senha_expira_em else None,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def validar_senha(request):
    senha = request.data.get('senha', '')
    valido, erro = validar_politica_senha(senha)
    return Response({'valido': valido, 'erro': erro})


# ===============================================================
#  ENDPOINTS AUTENTICADOS
# ===============================================================
@api_view(['POST'])
def cadastro_completo(request):
    serializer = CadastroCompletoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    d = serializer.validated_data
    tipo_pessoa = d.get('tipo_pessoa', 'proprio')

    empregado = Empregado.objects.create(
        nome=d['nome'],
        tipo_pessoa=tipo_pessoa,
        matricula=d.get('matricula', '') or '',
        documento=d.get('documento', '') or '',
        empresa=d.get('empresa', '') or '',
        telefone=d.get('telefone', '') or '',
        setor=d.get('setor', '') or '',
        cargo=d.get('cargo', '') or '',
    )

    categoria = d.get('categoria', 'taboca')
    if tipo_pessoa == 'terceiro':
        categoria = 'terceira'
    elif tipo_pessoa == 'visitante':
        categoria = 'pessoal'

    dispositivo = Dispositivo.objects.create(
        tipo=d['tipo'],
        tipo_descricao=d.get('tipo_descricao', ''),
        serial=d['serial'],
        patrimonio=d.get('patrimonio', ''),
        marca=d.get('marca', ''),
        modelo=d.get('modelo', ''),
        categoria=categoria,
        terceira_nome=d.get('empresa', '') if tipo_pessoa == 'terceiro' else d.get('terceira_nome', ''),
        status=d['status'],
        empregado=empregado,
    )
    return Response({
        'empregado': EmpregadoSerializer(empregado).data,
        'dispositivo': DispositivoSerializer(dispositivo).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def dar_baixa(request, pk):
    try:
        disp = Dispositivo.objects.get(pk=pk, ativo=True)
        disp.ativo = False
        disp.save()
        qr = QrCode.objects.filter(dispositivo=disp).first()
        if qr:
            qr.dispositivo = None
            qr.status = 'inutilizado'
            qr.save()
        Baixa.objects.create(
            dispositivo=disp,
            empregado=disp.empregado,
            motivo=request.data.get('motivo', 'devolucao'),
            observacao=request.data.get('observacao', ''),
            usuario_nome=request.data.get('usuario_nome', '')
        )
        return Response({'mensagem': 'Baixa registrada com sucesso'})
    except Dispositivo.DoesNotExist:
        return Response({'erro': 'Dispositivo nao encontrado'}, status=404)


@api_view(['POST'])
def gerar_qrcodes_lote(request):
    prefixo = request.data.get('prefixo', 'TAB')
    inicio = int(request.data.get('inicio', 1))
    quantidade = int(request.data.get('quantidade', 50))
    criados = []
    for i in range(quantidade):
        codigo = prefixo + '-' + str(inicio + i).zfill(4)
        qr, created = QrCode.objects.get_or_create(codigo=codigo)
        if created:
            criados.append(codigo)
    return Response({'criados': len(criados), 'codigos': criados}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def vincular_qrcode(request):
    codigo = request.data.get('codigo', '')
    dispositivo_id = request.data.get('dispositivo_id', None)
    try:
        qr = QrCode.objects.get(codigo=codigo)
        if qr.status == 'em_uso':
            return Response({'erro': 'QR Code ja esta em uso'}, status=status.HTTP_400_BAD_REQUEST)
        if qr.status == 'danificado':
            return Response({'erro': 'QR Code danificado'}, status=status.HTTP_400_BAD_REQUEST)
        disp = Dispositivo.objects.get(pk=dispositivo_id)
        qr.dispositivo = disp
        qr.status = 'em_uso'
        qr.save()
        return Response({'mensagem': 'QR Code vinculado', 'qrcode': QrCodeSerializer(qr).data})
    except QrCode.DoesNotExist:
        return Response({'erro': 'QR Code nao encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Dispositivo.DoesNotExist:
        return Response({'erro': 'Dispositivo nao encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def desvincular_qrcode(request, pk):
    try:
        qr = QrCode.objects.get(pk=pk)
        qr.dispositivo = None
        qr.status = 'disponivel'
        qr.save()
        return Response({'mensagem': 'QR Code desvinculado'})
    except QrCode.DoesNotExist:
        return Response({'erro': 'QR Code nao encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def scan_qrcode(request):
    codigo = request.data.get('codigo', '')
    try:
        qr = QrCode.objects.select_related('dispositivo').get(codigo=codigo)
        if not qr.dispositivo:
            return Response({'status': 'nao_vinculado', 'mensagem': 'QR nao vinculado'})
        dispositivo = qr.dispositivo
        ultimo = Registro.objects.filter(dispositivo=dispositivo).order_by('-id').first()
        if not ultimo:
            novo_tipo = 'CHECK-IN'
        elif ultimo.tipo == 'CHECK-IN':
            novo_tipo = 'CHECK-OUT'
        else:
            novo_tipo = 'CHECK-IN'
        Registro.objects.create(dispositivo=dispositivo, empregado=dispositivo.empregado, tipo=novo_tipo)
        return Response({'status': 'ok', 'acao': novo_tipo, 'dispositivo': DispositivoSerializer(dispositivo).data})
    except QrCode.DoesNotExist:
        return Response({'status': 'nao_encontrado', 'mensagem': 'QR nao encontrado'}, status=404)


@api_view(['POST'])
def baixa_qrcode(request):
    qrcode_id = request.data.get('qrcode_id', None)
    motivo = request.data.get('motivo', '')

    if not qrcode_id:
        return Response({'erro': 'ID do QR Code obrigatorio'}, status=status.HTTP_400_BAD_REQUEST)
    if not motivo:
        return Response({'erro': 'Motivo da baixa obrigatorio'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        qr = QrCode.objects.get(pk=qrcode_id)
        if qr.status == 'inutilizado':
            return Response({'erro': 'QR Code ja esta inutilizado'}, status=status.HTTP_400_BAD_REQUEST)
        if qr.dispositivo:
            qr.dispositivo = None
        qr.status = 'inutilizado'
        qr.save()
        return Response({
            'mensagem': 'QR Code inutilizado com sucesso',
            'codigo': qr.codigo,
            'motivo': motivo,
        })
    except QrCode.DoesNotExist:
        return Response({'erro': 'QR Code nao encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ===============================================================
#  ETIQUETAS NIIMBOT
# ===============================================================
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from django.http import HttpResponse


@api_view(['GET'])
def gerar_etiquetas_png(request):
    todos = request.query_params.get('todos', 'false').lower() == 'true'
    if todos:
        qrcodes = QrCode.objects.all().order_by('codigo')
    else:
        qrcodes = QrCode.objects.filter(status='disponivel').order_by('codigo')

    if not qrcodes.exists():
        return Response({'erro': 'Nenhum QR Code encontrado'}, status=status.HTTP_404_NOT_FOUND)

    DPI = 300
    LARGURA = int(50 * DPI / 25.4)
    ALTURA = int(15 * DPI / 25.4)
    QR_SIZE = ALTURA - 20
    MARGEM = 10

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for qr_obj in qrcodes:
            codigo = qr_obj.codigo
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=1)
            qr.add_data(codigo)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
            qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.NEAREST)

            etiqueta = Image.new('RGB', (LARGURA, ALTURA), 'white')
            draw = ImageDraw.Draw(etiqueta)
            qr_y = (ALTURA - QR_SIZE) // 2
            etiqueta.paste(qr_img, (MARGEM, qr_y))
            texto_x = MARGEM + QR_SIZE + 15

            try:
                fonte_titulo = ImageFont.truetype("arial.ttf", 28)
                fonte_codigo = ImageFont.truetype("arial.ttf", 24)
            except (OSError, IOError):
                try:
                    fonte_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                    fonte_codigo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                except (OSError, IOError):
                    fonte_titulo = ImageFont.load_default()
                    fonte_codigo = ImageFont.load_default()

            draw.text((texto_x, ALTURA // 2 - 38), 'RESE+', fill='black', font=fonte_titulo)
            draw.line([(texto_x, ALTURA // 2 + 2), (LARGURA - MARGEM, ALTURA // 2 + 2)], fill='#CCCCCC', width=1)
            draw.text((texto_x, ALTURA // 2 + 10), codigo, fill='black', font=fonte_codigo)

            img_buffer = io.BytesIO()
            etiqueta.save(img_buffer, format='PNG', dpi=(DPI, DPI))
            img_buffer.seek(0)
            zip_file.writestr('etiqueta_' + codigo + '.png', img_buffer.getvalue())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="etiquetas_qrcodes_rese.zip"'
    return response


@api_view(['GET'])
def gerar_etiqueta_unica(request, codigo):
    try:
        qr_obj = QrCode.objects.get(codigo=codigo)
    except QrCode.DoesNotExist:
        return Response({'erro': 'QR Code nao encontrado'}, status=status.HTTP_404_NOT_FOUND)

    DPI = 300
    LARGURA = int(50 * DPI / 25.4)
    ALTURA = int(15 * DPI / 25.4)
    QR_SIZE = ALTURA - 20
    MARGEM = 10

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=1)
    qr.add_data(codigo)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.NEAREST)

    etiqueta = Image.new('RGB', (LARGURA, ALTURA), 'white')
    draw = ImageDraw.Draw(etiqueta)
    qr_y = (ALTURA - QR_SIZE) // 2
    etiqueta.paste(qr_img, (MARGEM, qr_y))
    texto_x = MARGEM + QR_SIZE + 15

    try:
        fonte_titulo = ImageFont.truetype("arial.ttf", 28)
        fonte_codigo = ImageFont.truetype("arial.ttf", 24)
    except (OSError, IOError):
        try:
            fonte_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            fonte_codigo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except (OSError, IOError):
            fonte_titulo = ImageFont.load_default()
            fonte_codigo = ImageFont.load_default()

    draw.text((texto_x, ALTURA // 2 - 38), 'RESE+', fill='black', font=fonte_titulo)
    draw.line([(texto_x, ALTURA // 2 + 2), (LARGURA - MARGEM, ALTURA // 2 + 2)], fill='#CCCCCC', width=1)
    draw.text((texto_x, ALTURA // 2 + 10), codigo, fill='black', font=fonte_codigo)

    img_buffer = io.BytesIO()
    etiqueta.save(img_buffer, format='PNG', dpi=(DPI, DPI))
    img_buffer.seek(0)

    response = HttpResponse(img_buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="etiqueta_' + codigo + '.png"'
    return response