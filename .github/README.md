# Configuração dos Secrets do GitHub Actions

Para que os workflows funcionem corretamente, você precisa configurar os seguintes secrets no seu repositório do GitHub:

## Secrets Necessários

### Para projetos Django (Landing Page, Sistema, Fiscal):

1. **`GCP_SA_KEY`** - Chave JSON da Service Account do Google Cloud Platform
   - Vá para [Google Cloud Console](https://console.cloud.google.com/)
   - IAM & Admin > Service Accounts
   - Crie uma nova chave JSON para uma service account com as seguintes permissões:
     - App Engine Admin
     - Cloud Run Admin
     - Storage Admin
     - Cloud SQL Admin

2. **`GCP_PROJECT_ID`** - ID do seu projeto no Google Cloud
   - Encontrado no Google Cloud Console

3. **`DJANGO_DEBUG`** - Configuração de debug (geralmente "False" para produção)

4. **`DJANGO_SECRET_KEY`** - Chave secreta do Django (gere uma nova para produção)

5. **`DATABASE_URL`** - URL de conexão com o banco de dados
   - Formato: `mysql://user:password@host:port/database`

### Para projeto Next.js (Clínica):

1. **`VERCEL_TOKEN`** - Token de acesso da Vercel
   - Vá para [Vercel Dashboard](https://vercel.com/dashboard)
   - Settings > Tokens > Criar Token

## Como configurar os secrets:

1. Vá para o seu repositório no GitHub
2. Settings > Secrets and variables > Actions
3. Clique em "New repository secret"
4. Adicione cada secret com o nome e valor correspondente

## Funcionalidades dos Workflows

### Deploy Individual:
- Cada projeto tem seu próprio workflow de deploy
- Executa automaticamente em push para main/master
- Roda testes antes do deploy
- Deploy condicional baseado na branch

### Deploy All:
- Workflow para deploy de todos os projetos simultaneamente
- Trigger por tags (v*) ou manualmente
- Útil para releases de produção

### Quality Checks:
- Verificação de formatação (Black)
- Linting (Flake8)
- Verificação de tipos (MyPy)
- Análise de segurança (Bandit)
- Verificação de dependências vulneráveis (Safety)

### Dependabot:
- Atualizações automáticas de dependências
- PRs semanais com atualizações de segurança
- Configurado para Python (pip) e Node.js (npm)

## Troubleshooting

Se os workflows falharem, verifique:
1. Se todos os secrets estão configurados
2. Se as permissões da service account estão corretas
3. Se o projeto está conectado ao repositório correto
4. Logs detalhados no GitHub Actions
