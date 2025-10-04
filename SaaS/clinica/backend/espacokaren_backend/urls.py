from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from agendamentos.views import ClienteViewSet, ServicoViewSet, AgendamentoViewSet
from agendamentos.monitoring import health_check, health_detailed, metrics, performance_metrics

# Router para API REST
router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'servicos', ServicoViewSet)
router.register(r'agendamentos', AgendamentoViewSet)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API principal
    path('api/', include(router.urls)),
    
    # Autenticação DRF
    path('api-auth/', include('rest_framework.urls')),
    
    # Health checks e monitoramento
    path('health/', health_check, name='health_check'),
    path('health/detailed/', health_detailed, name='health_detailed'),
    path('metrics/', metrics, name='metrics'),
    path('metrics/performance/', performance_metrics, name='performance_metrics'),
    
    # Endpoints específicos (já incluídos via router actions)
    # /api/agendamentos/dashboard/
    # /api/agendamentos/calendario/
    # /api/agendamentos/relatorio/
    # /api/agendamentos/{id}/cancelar/
    # /api/agendamentos/{id}/concluir/
    # /api/clientes/{id}/agendamentos/
    # /api/clientes/{id}/historico/
    # /api/servicos/estatisticas/
]
