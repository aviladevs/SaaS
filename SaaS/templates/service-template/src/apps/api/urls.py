from django.urls import path, include
from rest_framework.routers import DefaultRouter

# TODO: Importe seus ViewSets aqui
# from .views import ExemploViewSet

router = DefaultRouter()
# TODO: Registre seus ViewSets aqui
# router.register(r'exemplo', ExemploViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
