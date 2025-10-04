from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

# from . import views  # Placeholder views - actual views in apps.users

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'services', views.ServiceViewSet)
# router.register(r'projects', views.ProjectViewSet)
# router.register(r'articles', views.ArticleViewSet)
# router.register(r'contact', views.ContactMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('docs/', include_docs_urls(title='Ávila DevOps API')),  # Requires coreapi
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
]
