from django.urls import path, include
from rest_framework import routers
from . import views

# Router básico - ViewSets serão adicionados conforme necessário
router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health_check'),
]
