from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint for Google App Engine
    """
    return Response({
        'status': 'healthy',
        'message': 'API is running'
    })