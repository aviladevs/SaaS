"""
Placeholder views for API app
The actual API views are in apps.users.views
"""
from rest_framework import viewsets

# Placeholder viewsets referenced in urls.py
# These should be implemented or removed from urls.py

class UserViewSet(viewsets.ModelViewSet):
    pass

class ServiceViewSet(viewsets.ModelViewSet):
    pass

class ProjectViewSet(viewsets.ModelViewSet):
    pass

class ArticleViewSet(viewsets.ModelViewSet):
    pass

class ContactMessageViewSet(viewsets.ModelViewSet):
    pass
