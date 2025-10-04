# 🚀 Guia de Uso Avançado do GitHub MCP

## 🎯 **Prompts Eficazes para GitHub MCP**

### **📊 Análise de Repositório**
```
@workspace Analise a estrutura completa deste projeto e identifique áreas de melhoria

@workspace Liste todos os arquivos Python ordenados por tamanho

@workspace Encontre arquivos com mais de 100 linhas que poderiam ser refatorados

@workspace Mostre estatísticas: número de arquivos, linhas de código, cobertura de testes
```

### **🔍 Busca Inteligente**
```
@workspace Procure por "TODO" ou "FIXME" em todos os arquivos

@workspace Encontre todas as funções que fazem consultas ao banco de dados

@workspace Liste arquivos que importam bibliotecas externas específicas

@workspace Busque padrões de código duplicado entre arquivos
```

### **📝 Gestão de Issues e PRs**
```
@workspace Liste as últimas 10 issues ordenadas por prioridade

@workspace Qual é o status atual do sprint/iteration?

@workspace Mostre PRs que estão aguardando review há mais de 2 dias

@workspace Crie um relatório das métricas de desenvolvimento desta semana
```

### **🔧 Desenvolvimento Assistido**
```
@workspace Baseado no padrão atual, sugira como implementar uma nova feature X

@workspace Analise este código e identifique possíveis bugs ou melhorias

@workspace Gere testes unitários para esta função baseada nos padrões do projeto

@workspace Refatore este código seguindo as melhores práticas identificadas no repositório
```

## ⚡ **Atalhos Rápidos**

### **Comandos Úteis**
```bash
# Ver servidores MCP ativos
MCP: List Servers

# Ver logs do MCP
MCP: Show Output Logs

# Adicionar novo servidor
MCP: Add Server

# Reiniciar servidor
MCP: Restart Server
```

### **Configuração de Segurança**
```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "trust": true,
      "enabled": true
    }
  }
}
```

## 🎨 **Exemplos Práticos**

### **Análise de Performance**
```
@workspace Analise o tempo de resposta das APIs neste projeto

@workspace Identifique consultas N+1 no código

@workspace Sugira otimizações de banco de dados baseadas nos modelos atuais
```

### **Documentação Automática**
```
@workspace Gere documentação para esta função baseada no seu código

@workspace Crie exemplos de uso para esta API

@workspace Atualize o README com as novas funcionalidades adicionadas
```

### **Debugging Inteligente**
```
@workspace Baseado nos logs de erro, identifique a causa raiz deste problema

@workspace Compare este arquivo com a versão do commit anterior

@workspace Encontre arquivos relacionados que podem estar afetando este bug
```

---

**🎯 Com essas técnicas, você maximiza o potencial do GitHub MCP para desenvolvimento eficiente!**
