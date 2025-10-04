# 📖 Documentação Técnica - Ávila DevOps SaaS

Guia completo para desenvolvedores, DevOps e contribuidores da plataforma Ávila DevOps SaaS.

## 📋 Índice

- [🏗️ Arquitetura](./architecture.md)
- [🚀 Deploy](./deployment.md)
- [📊 Monitoramento](./monitoring.md)
- [🔒 Segurança](./security.md)
- [🧪 Testes](./testing.md)
- [🤝 Contribuição](./contributing.md)
- [🔧 Desenvolvimento Local](./local-development.md)

## 🚀 Início Rápido para Desenvolvedores

### **Pré-requisitos**
```bash
# Verificar versões
python --version     # 3.11+
node --version       # 18+
docker --version     # 20+
docker-compose --version  # 2.0+

# Instalar ferramentas (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
sudo apt install nodejs npm
sudo apt install postgresql postgresql-contrib
sudo apt install redis-server
```

### **Setup de Desenvolvimento**
```bash
# 1. Clone o repositório
git clone https://github.com/avila-devops/saas.git
cd saas

# 2. Configure ambiente virtual Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações locais

# 4. Instale dependências
make install

# 5. Configure banco de dados
make migrate
make superuser

# 6. Execute ambiente de desenvolvimento
make dev

# 7. Execute testes
make test
```

## 🏗️ Arquitetura Detalhada

### **Multi-tenant Architecture**

Cada tenant (cliente) possui:
- Banco de dados isolado
- Domínio personalizado (`cliente.aviladevops.com.br`)
- Configurações específicas
- Usuários e permissões próprios

### **Microsserviços**

#### **Landing Page** (`/LANDING-PAGE/`)
- **Framework**: Django 4.2+
- **Banco**: PostgreSQL (schema público)
- **Cache**: Redis
- **Responsabilidades**:
  - Site institucional
  - Formulários de contato
  - SEO otimizado

#### **Sistema de Reciclagem** (`/sistema/`)
- **Framework**: Django 4.2+
- **Banco**: PostgreSQL (schema dedicado)
- **ML**: Integração com bibliotecas de análise
- **Responsabilidades**:
  - Gestão de materiais recicláveis
  - Controle de estoque
  - Relatórios financeiros

#### **Sistema Fiscal** (`/fiscal/`)
- **Framework**: Django 4.2+
- **Banco**: PostgreSQL (schema dedicado)
- **Analytics**: Pandas + scikit-learn
- **Responsabilidades**:
  - Processamento de XMLs fiscais (NFe/CTe)
  - Dashboards de analytics
  - Relatórios automatizados

#### **Clínica Management** (`/clinica/`)
- **Framework**: Next.js 14+
- **Linguagem**: TypeScript 5+
- **Banco**: PostgreSQL (via API)
- **Responsabilidades**:
  - Agendamento de consultas
  - Gestão de pacientes
  - Relatórios médicos

#### **Admin Dashboard** (`/app-aviladevops/`)
- **Framework**: Django 4.2+
- **Frontend**: Django Admin + React (opcional)
- **Banco**: PostgreSQL (multi-tenant)
- **Responsabilidades**:
  - Gestão de tenants
  - Monitoramento geral
  - Configurações do sistema

## 🔧 Desenvolvimento Local

### **Estrutura de Desenvolvimento**

```
saas/
├── services/           # Serviços individuais
│   ├── landing-page/   # Django app
│   ├── sistema/        # Django app
│   ├── fiscal/         # Django app
│   ├── clinica/        # Next.js app
│   └── admin/          # Django app
├── shared/             # Recursos compartilhados
│   ├── docker/         # Configurações Docker
│   ├── k8s/           # Kubernetes manifests
│   └── scripts/        # Scripts utilitários
├── docs/              # Esta documentação
└── .github/           # CI/CD workflows
```

### **Padrões de Código**

#### **Python (Django)**
```python
# settings.py - Configurações específicas
DJANGO_SETTINGS_MODULE=core.settings

# requirements.txt - Versões fixadas
Django>=4.2,<5.0
djangorestframework>=3.14.0
psycopg2-binary>=2.9.7

# Código - Padrões PEP 8 + extensões
class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet para serviços com documentação completa."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar por tenant do usuário."""
        return super().get_queryset().filter(tenant=self.request.user.tenant)
```

#### **JavaScript/TypeScript (Next.js)**
```typescript
// pages/api/services.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { method } = req

  switch (method) {
    case 'GET':
      // Implementação
      break
    default:
      res.setHeader('Allow', ['GET'])
      res.status(405).end(`Method ${method} Not Allowed`)
  }
}
```

## 🚀 Deploy

### **Ambientes**

#### **Desenvolvimento**
```bash
# Local com Docker
make dev

# Serviços disponíveis:
# - Landing Page: http://localhost:8000
# - Sistema: http://localhost:8001
# - Fiscal: http://localhost:8002
# - Clínica: http://localhost:3000
# - Admin: http://localhost:8003
```

#### **Staging**
```bash
# Deploy automatizado via GitHub Actions
# Trigger: Push para branch develop

# Manual
make deploy-staging
```

#### **Produção**
```bash
# Deploy automatizado via GitHub Actions
# Trigger: Push para branch main ou tags v*

# Manual
make deploy-prod

# Verificar saúde
make health
```

### **CI/CD Pipeline**

#### **GitHub Actions Workflows**
- **`saas-deploy.yml`**: Deploy multi-serviço
- **`tenant-management.yml`**: Gestão de tenants
- **`monitoring.yml`**: Monitoramento 24/7
- **`quality.yml`**: Code quality gates

#### **Dependabot**
- Atualizações semanais de dependências
- PRs automáticos com review obrigatório
- Configurado por serviço (`dependabot-saas.yml`)

## 📊 Monitoramento

### **Métricas Coletadas**

#### **Application Metrics**
```yaml
# Prometheus queries de exemplo
uptime_seconds = time() - process_start_time_seconds
error_rate = rate(errors_total[5m]) / rate(requests_total[5m])
response_time_p95 = histogram_quantile(0.95, rate(response_time_seconds_bucket[5m]))
```

#### **Business Metrics**
- Usuários ativos por tenant
- Taxa de conversão por serviço
- Revenue por período
- Churn rate

### **Dashboards**

#### **Grafana Dashboards**
- **Application Health**: Uptime, erros, performance
- **Business KPIs**: Métricas de negócio
- **Infrastructure**: Recursos de cloud
- **Security**: Tentativas de acesso, vulnerabilidades

#### **Alertas Configurados**
```yaml
# Exemplo de alerta
- name: High Error Rate
  expr: error_rate > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }}%"
```

## 🔒 Segurança

### **Práticas Implementadas**

#### **Autenticação**
- JWT com refresh tokens
- OAuth 2.0 para integrações
- 2FA opcional
- Rate limiting por endpoint

#### **Autorização**
- RBAC (Role-Based Access Control)
- Escopo por tenant
- Permissões granulares
- Auditoria completa

#### **Proteção de Dados**
- Criptografia AES-256 para dados sensíveis
- PII masking em logs
- Backup criptografado
- Data retention policies

### **Scans de Segurança**

#### **Automatizados**
- **Dependabot**: Vulnerabilidades em dependências
- **Snyk**: Scans de segurança em containers
- **Trivy**: Análise de imagens Docker
- **OWASP ZAP**: DAST (Dynamic Application Security Testing)

#### **Manuais**
- Penetration testing anual
- Code review de segurança
- Arquitetura review

## 🧪 Estratégia de Testes

### **Tipos de Testes**

#### **Unit Tests**
```python
# Exemplo Django
class ServiceModelTest(TestCase):
    def test_service_creation(self):
        service = Service.objects.create(
            name="Test Service",
            tenant=self.tenant
        )
        self.assertEqual(service.tenant, self.tenant)
```

#### **Integration Tests**
```python
# Exemplo API
def test_service_api_endpoint(client, service):
    response = client.get(f'/api/services/{service.id}/')
    assert response.status_code == 200
    assert 'name' in response.data
```

#### **E2E Tests**
```javascript
// Exemplo Playwright
test('user can create service', async ({ page }) => {
  await page.goto('/services/new')
  await page.fill('[name=name]', 'New Service')
  await page.click('button[type=submit]')
  await expect(page.locator('.success')).toBeVisible()
})
```

### **Coverage Targets**
- **Unit Tests**: > 80%
- **Integration Tests**: > 60%
- **E2E Tests**: > 40%

## 🤝 Contribuição

### **Processo de Contribuição**

#### **1. Preparação**
```bash
# Fork o repositório
# Clone seu fork
git clone https://github.com/seu-username/saas.git

# Configure upstream
git remote add upstream https://github.com/avila-devops/saas.git

# Crie ambiente de desenvolvimento
make setup
```

#### **2. Desenvolvimento**
```bash
# Crie branch para feature
git checkout -b feature/nova-funcionalidade

# Desenvolva com testes
# Execute testes frequentemente
make test

# Commit seguindo conventional commits
git add .
git commit -m "feat: adiciona nova funcionalidade"
```

#### **3. Pull Request**
```bash
# Push para seu fork
git push origin feature/nova-funcionalidade

# Abra PR no GitHub
# Preencha template
# Solicite review
```

### **Conventional Commits**
```bash
feat: adiciona nova funcionalidade
fix: corrige bug
docs: atualiza documentação
style: melhora formatação
refactor: refatora código
test: adiciona testes
chore: tarefas de manutenção
```

## 📚 Recursos Adicionais

### **Links Úteis**
- [📖 Django Documentation](https://docs.djangoproject.com/)
- [⚛️ React Documentation](https://react.dev/)
- [🐳 Docker Documentation](https://docs.docker.com/)
- [☸️ Kubernetes Documentation](https://kubernetes.io/docs/)
- [🔧 Terraform Documentation](https://developer.hashicorp.com/terraform/docs)

### **Comunidade**
- [💬 Discord Ávila DevOps](https://discord.gg/avila-devops)
- [🐦 Twitter @avila_devops](https://twitter.com/avila_devops)
- [📧 Newsletter](https://newsletter.aviladevops.com.br)

---

**🚀 Happy coding!** | **Ávila DevOps**
