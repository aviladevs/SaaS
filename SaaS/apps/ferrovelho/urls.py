from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse

def ferrovelho_streamlit(request):
    """Redirecionar para aplicação Streamlit integrada"""
    # Em produção, isso seria servido por um serviço separado
    # Por enquanto, redirecionar para localhost:8501 (porta padrão do Streamlit)
    return redirect('http://localhost:8501')

def ferrovelho_api(request):
    """API para integração com frontend"""
    from apps.ferrovelho.models import SucataEntry, SucataMaterial

    # Obter dados básicos
    materiais = list(SucataMaterial.objects.filter(is_active=True).values('id', 'nome', 'categoria', 'preco_atual'))

    entradas_recentes = list(SucataEntry.objects.all()[:10].values(
        'id', 'cliente', 'data', 'hora', 'observacoes', 'is_processed'
    ))

    return JsonResponse({
        'materiais': materiais,
        'entradas_recentes': entradas_recentes,
        'total_materiais': len(materiais),
        'total_entradas': SucataEntry.objects.count()
    })

urlpatterns = [
    path('streamlit/', ferrovelho_streamlit, name='streamlit'),
    path('api/data/', ferrovelho_api, name='api_data'),
]
