from django.db import migrations
from django.apps import apps

def populate_initial_materials(apps, schema_editor):
    """Popular materiais iniciais para tenants existentes"""

    Tenant = apps.get_model('users', 'Tenant')
    SucataMaterial = apps.get_model('ferrovelho', 'SucataMaterial')

    materiais_iniciais = [
        # Chaparia e metais básicos
        {'nome': 'Chaparia', 'categoria': 'Ferro', 'preco_base': 0.80, 'preco_atual': 0.80},
        {'nome': 'Miúda', 'categoria': 'Ferro', 'preco_base': 0.75, 'preco_atual': 0.75},
        {'nome': 'Estamparia', 'categoria': 'Ferro', 'preco_base': 0.85, 'preco_atual': 0.85},
        {'nome': 'Fundido', 'categoria': 'Ferro', 'preco_base': 0.90, 'preco_atual': 0.90},
        {'nome': 'Cavaco', 'categoria': 'Ferro', 'preco_base': 0.70, 'preco_atual': 0.70},

        # Mola
        {'nome': 'Mola escolha', 'categoria': 'Mola', 'preco_base': 1.20, 'preco_atual': 1.20},

        # Filtros
        {'nome': 'Filtro óleo', 'categoria': 'Filtros', 'preco_base': 0.50, 'preco_atual': 0.50},

        # Alumínio
        {'nome': 'Alumínio - Latinha', 'categoria': 'Alumínio', 'preco_base': 4.50, 'preco_atual': 4.50},
        {'nome': 'Alumínio - Chaparia', 'categoria': 'Alumínio', 'preco_base': 3.80, 'preco_atual': 3.80},
        {'nome': 'Alumínio - Bloco', 'categoria': 'Alumínio', 'preco_base': 4.20, 'preco_atual': 4.20},
        {'nome': 'Alumínio - Panela', 'categoria': 'Alumínio', 'preco_base': 3.50, 'preco_atual': 3.50},
        {'nome': 'Alumínio - Perfil Novo', 'categoria': 'Alumínio', 'preco_base': 5.00, 'preco_atual': 5.00},
        {'nome': 'Alumínio - Perfil Pintado', 'categoria': 'Alumínio', 'preco_base': 4.80, 'preco_atual': 4.80},
        {'nome': 'Alumínio - Radiador', 'categoria': 'Alumínio', 'preco_base': 4.00, 'preco_atual': 4.00},
        {'nome': 'Alumínio - Roda', 'categoria': 'Alumínio', 'preco_base': 6.00, 'preco_atual': 6.00},
        {'nome': 'Alumínio - Cavaco', 'categoria': 'Alumínio', 'preco_base': 3.00, 'preco_atual': 3.00},
        {'nome': 'Alumínio - Estamparia', 'categoria': 'Alumínio', 'preco_base': 3.50, 'preco_atual': 3.50},
        {'nome': 'Alumínio - Off-set', 'categoria': 'Alumínio', 'preco_base': 4.50, 'preco_atual': 4.50},

        # Baterias e metais especiais
        {'nome': 'Bateria', 'categoria': 'Baterias', 'preco_base': 2.50, 'preco_atual': 2.50},
        {'nome': 'Chumbo', 'categoria': 'Metais', 'preco_base': 3.20, 'preco_atual': 3.20},

        # Cobre
        {'nome': 'Cobre - Mel', 'categoria': 'Cobre', 'preco_base': 25.00, 'preco_atual': 25.00},
        {'nome': 'Cobre - Misto', 'categoria': 'Cobre', 'preco_base': 22.00, 'preco_atual': 22.00},
        {'nome': 'Radiador Alum. Cobre', 'categoria': 'Cobre', 'preco_base': 18.00, 'preco_atual': 18.00},
        {'nome': 'Cobre Encapado', 'categoria': 'Cobre', 'preco_base': 20.00, 'preco_atual': 20.00},

        # Latão e metais diversos
        {'nome': 'Metal Latão', 'categoria': 'Metais', 'preco_base': 12.00, 'preco_atual': 12.00},
        {'nome': 'Cavaco Metal', 'categoria': 'Metais', 'preco_base': 8.00, 'preco_atual': 8.00},
        {'nome': 'Radiador Metal', 'categoria': 'Metais', 'preco_base': 15.00, 'preco_atual': 15.00},

        # Bronze
        {'nome': 'Bronze', 'categoria': 'Bronze', 'preco_base': 14.00, 'preco_atual': 14.00},
        {'nome': 'Cavaco Bronze', 'categoria': 'Bronze', 'preco_base': 10.00, 'preco_atual': 10.00},

        # Inox
        {'nome': 'Inox 304', 'categoria': 'Inox', 'preco_base': 8.00, 'preco_atual': 8.00},
        {'nome': 'Inox 430', 'categoria': 'Inox', 'preco_base': 6.50, 'preco_atual': 6.50},

        # Materiais especiais
        {'nome': 'Material Sujo', 'categoria': 'Outros', 'preco_base': 0.30, 'preco_atual': 0.30},
        {'nome': 'Magnésio', 'categoria': 'Outros', 'preco_base': 5.00, 'preco_atual': 5.00},
        {'nome': 'Antimônio', 'categoria': 'Outros', 'preco_base': 8.00, 'preco_atual': 8.00},
    ]

    # Para cada tenant existente, criar materiais
    for tenant in Tenant.objects.all():
        for mat in materiais_iniciais:
            SucataMaterial.objects.get_or_create(
                tenant=tenant,
                nome=mat['nome'],
                defaults={
                    'categoria': mat['categoria'],
                    'preco_base': mat['preco_base'],
                    'preco_atual': mat['preco_atual'],
                    'unidade': 'kg'
                }
            )

class Migration(migrations.Migration):

    dependencies = [
        ('ferrovelho', '0001_initial'),
        ('users', '0001_initial'),  # Dependência do modelo Tenant
    ]

    operations = [
        migrations.RunPython(populate_initial_materials),
    ]
