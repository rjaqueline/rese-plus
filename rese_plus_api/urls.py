from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from dispositivos.views import (
    EmpregadoViewSet, DispositivoViewSet, RegistroViewSet, BaixaViewSet,
    UsuarioViewSet, QrCodeViewSet,
    login, login_auto, cadastro_completo, dar_baixa, gerar_qrcodes_lote,
    vincular_qrcode, desvincular_qrcode, scan_qrcode,
    gerar_etiquetas_png, gerar_etiqueta_unica, baixa_qrcode,
    trocar_senha, validar_senha,
)

router = DefaultRouter()
router.register('empregados', EmpregadoViewSet)
router.register('dispositivos', DispositivoViewSet)
router.register('registros', RegistroViewSet)
router.register('baixas', BaixaViewSet)
router.register('qrcodes', QrCodeViewSet)
router.register('usuarios', UsuarioViewSet)

urlpatterns = [
    # Viewsets
    path('api/', include(router.urls)),

    # JWT — Token refresh (nao precisa de auth)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Auth (nao precisa de auth)
    path('api/login/', login),
    path('api/login-auto/', login_auto),

    # Endpoints autenticados
    path('api/cadastro-completo/', cadastro_completo),
    path('api/dar-baixa/<int:pk>/', dar_baixa),
    path('api/gerar-qrcodes/', gerar_qrcodes_lote),
    path('api/vincular-qrcode/', vincular_qrcode),
    path('api/desvincular-qrcode/<int:pk>/', desvincular_qrcode),
    path('api/scan/', scan_qrcode),
    path('api/etiquetas/', gerar_etiquetas_png),
    path('api/etiqueta/<str:codigo>/', gerar_etiqueta_unica),
    path('api/baixa-qrcode/', baixa_qrcode),

    # Senha
    path('api/trocar-senha/', trocar_senha),
    path('api/validar-senha/', validar_senha),
]
