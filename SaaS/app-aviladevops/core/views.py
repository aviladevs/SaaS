from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json

def index(request):
    """Página inicial da Ávila DevOps"""
    context = {
        'title': 'Ávila DevOps - Transforme sua empresa com tecnologia',
        'description': 'Soluções em DevOps, desenvolvimento e transformação digital para impulsionar seu negócio.',
    }
    return render(request, 'index.html', context)

@csrf_exempt
def contact_form(request):
    """Processa formulário de contato via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Enviar email
            send_mail(
                subject=f"Contato via site: {data.get('subject', 'Sem assunto')}",
                message=f"""
Nome: {data.get('name')}
Email: {data.get('email')}
Telefone: {data.get('phone', 'Não informado')}
Empresa: {data.get('company', 'Não informado')}

Mensagem:
{data.get('message')}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': 'Mensagem enviada com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Erro ao enviar mensagem.'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

def services(request):
    """Página de serviços"""
    services_data = [
        {
            'icon': 'fas fa-code',
            'title': 'Desenvolvimento Web',
            'description': 'Criação de aplicações web modernas e responsivas utilizando as melhores tecnologias do mercado.',
        },
        {
            'icon': 'fas fa-cloud',
            'title': 'DevOps & Cloud',
            'description': 'Automação de infraestrutura, CI/CD, monitoramento e otimização de ambientes em nuvem.',
        },
        {
            'icon': 'fas fa-chart-line',
            'title': 'Consultoria em TI',
            'description': 'Análise e otimização de processos tecnológicos para maximizar eficiência e reduzir custos.',
        },
        {
            'icon': 'fas fa-mobile-alt',
            'title': 'Aplicativos Mobile',
            'description': 'Desenvolvimento de aplicativos nativos e híbridos para iOS e Android.',
        },
        {
            'icon': 'fas fa-database',
            'title': 'Banco de Dados',
            'description': 'Modelagem, otimização e administração de bancos de dados relacionais e NoSQL.',
        },
        {
            'icon': 'fas fa-shield-alt',
            'title': 'Segurança Cibernética',
            'description': 'Auditoria de segurança, implementação de firewalls e proteção contra ameaças digitais.',
        },
    ]

    context = {
        'services': services_data,
        'title': 'Nossos Serviços - Ávila DevOps',
    }
    return render(request, 'services.html', context)

def portfolio(request):
    """Página de portfólio"""
    projects = [
        {
            'title': 'Sistema de Gestão Empresarial',
            'category': 'Web Development',
            'image': '/static/images/projects/erp-system.jpg',
            'description': 'Sistema completo de gestão para empresas de médio porte.',
            'technologies': ['Django', 'PostgreSQL', 'React', 'Docker'],
            'url': '#',
        },
        {
            'title': 'Plataforma E-commerce',
            'category': 'E-commerce',
            'image': '/static/images/projects/ecommerce.jpg',
            'description': 'Loja virtual com integração de pagamentos e gestão de estoque.',
            'technologies': ['Next.js', 'Stripe', 'Prisma', 'Vercel'],
            'url': '#',
        },
        {
            'title': 'Aplicativo de Delivery',
            'category': 'Mobile App',
            'image': '/static/images/projects/delivery-app.jpg',
            'description': 'App para restaurantes com rastreamento em tempo real.',
            'technologies': ['React Native', 'Node.js', 'MongoDB', 'Socket.io'],
            'url': '#',
        },
    ]

    context = {
        'projects': projects,
        'title': 'Portfólio - Ávila DevOps',
    }
    return render(request, 'portfolio.html', context)

def about(request):
    """Página sobre nós"""
    team = [
        {
            'name': 'Carlos Ávila',
            'role': 'CEO & Founder',
            'image': '/static/images/team/carlos.jpg',
            'bio': 'Especialista em DevOps com mais de 10 anos de experiência em transformação digital.',
            'linkedin': '#',
            'github': '#',
        },
        {
            'name': 'Ana Silva',
            'role': 'Tech Lead',
            'image': '/static/images/team/ana.jpg',
            'bio': 'Desenvolvedora full-stack especializada em aplicações escaláveis.',
            'linkedin': '#',
            'github': '#',
        },
        {
            'name': 'Roberto Santos',
            'role': 'DevOps Engineer',
            'image': '/static/images/team/roberto.jpg',
            'bio': 'Especialista em infraestrutura cloud e automação de processos.',
            'linkedin': '#',
            'github': '#',
        },
    ]

    stats = [
        {'number': '50+', 'label': 'Projetos Entregues'},
        {'number': '10+', 'label': 'Anos de Experiência'},
        {'number': '100%', 'label': 'Clientes Satisfeitos'},
        {'number': '24/7', 'label': 'Suporte Técnico'},
    ]

    context = {
        'team': team,
        'stats': stats,
        'title': 'Sobre Nós - Ávila DevOps',
    }
    return render(request, 'about.html', context)
