from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from dispositivos.views import (
    EmpregadoViewSet, DispositivoViewSet, RegistroViewSet, BaixaViewSet,
    UsuarioViewSet, QrCodeViewSet,
    login, login_auto, cadastro_completo, dar_baixa, gerar_qrcodes_lote,
    vincular_qrcode, desvincular_qrcode, scan_qrcode,
    gerar_etiquetas_png, gerar_etiqueta_unica, baixa_qrcode,
    trocar_senha, validar_senha,
    listar_logs_auditoria,
    resetar_senha,
    refresh_token,
    listar_ultimos_registros,
    meu_perfil,
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
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),

    # JWT — Token refresh (nao precisa de auth)
    path('api/v1/token/refresh/', refresh_token, name='token_refresh'),
    # Auth (nao precisa de auth)
    path('api/v1/login/', login),
    path('api/v1/login-auto/', login_auto),

    # Endpoints autenticados
    path('api/v1/cadastro-completo/', cadastro_completo),
    path('api/v1/dar-baixa/<int:pk>/', dar_baixa),
    path('api/v1/gerar-qrcodes/', gerar_qrcodes_lote),
    path('api/v1/vincular-qrcode/', vincular_qrcode),
    path('api/v1/desvincular-qrcode/<int:pk>/', desvincular_qrcode),
    path('api/v1/scan/', scan_qrcode),
    
    path('api/v1/etiquetas/', gerar_etiquetas_png),
    path('api/v1/etiqueta/<str:codigo>/', gerar_etiqueta_unica),
    path('api/v1/baixa-qrcode/', baixa_qrcode),

    # Senha
    path('api/v1/trocar-senha/', trocar_senha),
    path('api/v1/validar-senha/', validar_senha),
    path('api/v1/logs-auditoria/', listar_logs_auditoria),
    # Reset de senha (SO master)
    path('api/v1/resetar-senha/<int:usuario_id>/', resetar_senha),
    path('api/v1/scan/', scan_qrcode),
    path('api/v1/ultimos-registros/', listar_ultimos_registros),
 # Documentação Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),   
       
]