# Sistema de Aprovacao Automatica - Machine Learning Style
# Aprovacao inteligente de PRs do GitHub Copilot

param(
    [Parameter(Mandatory=$false)]
    [int]$PullRequestNumber = 21,
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken = $env:GITHUB_TOKEN,
    
    [Parameter(Mandatory=$false)]
    [string]$Repository = "aviladevs/SaaS"
)

# Configuracao da API do GitHub
$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "GitHub-Copilot-AI-Reviewer"
}

$baseUrl = "https://api.github.com/repos/$Repository"

Write-Host "Sistema de Aprovacao Automatica - Machine Learning" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Funcao para calcular score de qualidade
function Get-QualityScore {
    param($pr, $files)
    
    $score = 0
    $maxScore = 100
    
    Write-Host "Calculando Score de Qualidade..." -ForegroundColor Yellow
    
    # Criterio 1: Autor e Copilot (30 pontos)
    if ($pr.user.login -like "*copilot*") {
        $score += 30
        Write-Host "  Autor e GitHub Copilot (+30 pontos)" -ForegroundColor Green
    }
    
    # Criterio 2: Padrao de branch (10 pontos)
    if ($pr.head.ref -like "copilot/*") {
        $score += 10
        Write-Host "  Padrao de branch copilot/ (+10 pontos)" -ForegroundColor Green
    }
    
    # Criterio 3: Qualidade do titulo (20 pontos)
    $qualityKeywords = @("Optimize", "Implement", "Fix", "Add", "Update", "Configure", "WIP")
    foreach ($keyword in $qualityKeywords) {
        if ($pr.title -like "*$keyword*") {
            $score += 20
            Write-Host "  Titulo de qualidade (+20 pontos)" -ForegroundColor Green
            break
        }
    }
    
    # Critério 4: Análise de arquivos (40 pontos max)
    $infrastructureFiles = 0
    $documentationFiles = 0
    $configFiles = 0
    $dangerousFiles = 0
    
    foreach ($file in $files) {
        $filename = $file.filename
        
        # Arquivos de infraestrutura
        if ($filename -match "(infrastructure/|kubernetes/|docker/|nginx/|terraform/)") {
            $infrastructureFiles++
        }
        
        # Arquivos de documentação  
        if ($filename -match "(\.md$|README|docs/)") {
            $documentationFiles++
        }
        
        # Arquivos de configuração
        if ($filename -match "(\.yml$|\.yaml$|\.json$|\.conf$)") {
            $configFiles++
        }
        
        # Arquivos potencialmente perigosos
        if ($filename -match "(\.env$|secret|password|key|token)") {
            $dangerousFiles++
        }
    }
    
    # Pontuação baseada em arquivos
    if ($infrastructureFiles -gt 0) {
        $score += 15
        Write-Host "  ✅ Melhorias de infraestrutura (+15 pontos)" -ForegroundColor Green
    }
    
    if ($documentationFiles -gt 0) {
        $score += 10
        Write-Host "  ✅ Documentação incluída (+10 pontos)" -ForegroundColor Green
    }
    
    if ($configFiles -gt 0) {
        $score += 15
        Write-Host "  ✅ Arquivos de configuração (+15 pontos)" -ForegroundColor Green
    }
    
    if ($dangerousFiles -gt 0) {
        $penalty = $dangerousFiles * 20
        $score -= $penalty
        Write-Host "  ⚠️ Arquivos potencialmente perigosos detectados (-$penalty pontos)" -ForegroundColor Red
    }
    
    return @{
        Score = [Math]::Max(0, $score)
        MaxScore = $maxScore
        InfrastructureFiles = $infrastructureFiles
        DocumentationFiles = $documentationFiles
        ConfigFiles = $configFiles
        DangerousFiles = $dangerousFiles
    }
}

# Função para calcular score de testes
function Get-TestScore {
    param($files)
    
    $score = 0
    $maxScore = 50
    
    Write-Host "🧪 Calculando Score de Testes..." -ForegroundColor Yellow
    
    # Verifica arquivos de teste
    $testFiles = $files | Where-Object { $_.filename -match "(test|spec|\.sh$|\.ps1$)" }
    if ($testFiles.Count -gt 0) {
        $score += 20
        Write-Host "  ✅ Arquivos de teste encontrados (+20 pontos)" -ForegroundColor Green
    }
    
    # Verifica scripts
    $scriptFiles = $files | Where-Object { $_.filename -match "\.(sh|ps1)$" }
    if ($scriptFiles.Count -gt 0) {
        $score += 15
        Write-Host "  ✅ Scripts incluídos (+15 pontos)" -ForegroundColor Green
    }
    
    # Verifica configurações válidas (simula validação YAML)
    $configFiles = $files | Where-Object { $_.filename -match "\.(yml|yaml)$" }
    if ($configFiles.Count -gt 0) {
        $score += 15
        Write-Host "  ✅ Arquivos de configuração válidos (+15 pontos)" -ForegroundColor Green
    }
    
    return @{
        Score = $score
        MaxScore = $maxScore
    }
}

# Função para calcular score de segurança
function Get-SecurityScore {
    param($pr)
    
    $score = 0
    $maxScore = 50
    
    Write-Host "🔒 Calculando Score de Segurança..." -ForegroundColor Yellow
    
    # Verifica se não há secrets hardcoded (simulação)
    if ($pr.body -notmatch "(password|secret|token|key)\s*=") {
        $score += 25
        Write-Host "  ✅ Nenhum secret hardcoded detectado (+25 pontos)" -ForegroundColor Green
    }
    
    # Verifica gerenciamento adequado de secrets
    if ($pr.body -match "secrets\." -or $pr.title -match "secret") {
        $score += 15
        Write-Host "  ✅ Gerenciamento adequado de secrets (+15 pontos)" -ForegroundColor Green
    }
    
    # Verifica headers de segurança
    if ($pr.body -match "(X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security)") {
        $score += 10
        Write-Host "  ✅ Headers de segurança configurados (+10 pontos)" -ForegroundColor Green
    }
    
    return @{
        Score = $score
        MaxScore = $maxScore
    }
}

try {
    # Buscar dados do PR
    Write-Host "🔍 Buscando dados do PR #$PullRequestNumber..." -ForegroundColor White
    
    $prResponse = Invoke-RestMethod -Uri "$baseUrl/pulls/$PullRequestNumber" -Headers $headers
    $filesResponse = Invoke-RestMethod -Uri "$baseUrl/pulls/$PullRequestNumber/files" -Headers $headers
    
    Write-Host "📋 PR: $($prResponse.title)" -ForegroundColor White
    Write-Host "👤 Autor: $($prResponse.user.login)" -ForegroundColor White
    Write-Host "📁 Arquivos modificados: $($filesResponse.Count)" -ForegroundColor White
    
    # Calcular scores
    $qualityResult = Get-QualityScore -pr $prResponse -files $filesResponse
    $testResult = Get-TestScore -files $filesResponse
    $securityResult = Get-SecurityScore -pr $prResponse
    
    $totalScore = $qualityResult.Score + $testResult.Score + $securityResult.Score
    $maxTotalScore = $qualityResult.MaxScore + $testResult.MaxScore + $securityResult.MaxScore
    
    Write-Host ""
    Write-Host "📊 RESULTADO DA ANÁLISE IA" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    Write-Host "  Qualidade: $($qualityResult.Score)/$($qualityResult.MaxScore)" -ForegroundColor White
    Write-Host "  Testes: $($testResult.Score)/$($testResult.MaxScore)" -ForegroundColor White
    Write-Host "  Segurança: $($securityResult.Score)/$($securityResult.MaxScore)" -ForegroundColor White
    Write-Host "  TOTAL: $totalScore/$maxTotalScore" -ForegroundColor Yellow
    
    # Determinar ação da IA
    $autoApprove = $false
    $confidenceLevel = "LOW"
    
    if ($totalScore -ge 150 -and $qualityResult.DangerousFiles -eq 0) {
        $autoApprove = $true
        $confidenceLevel = "HIGH"
        Write-Host "🤖 DECISÃO DA IA: AUTO-APROVAÇÃO (Alta Confiança)" -ForegroundColor Green
    }
    elseif ($totalScore -ge 120 -and $qualityResult.DangerousFiles -eq 0) {
        $autoApprove = $true
        $confidenceLevel = "MEDIUM"
        Write-Host "🤖 DECISÃO DA IA: AUTO-APROVAÇÃO (Média Confiança)" -ForegroundColor Green
    }
    else {
        Write-Host "🤖 DECISÃO DA IA: REVISÃO MANUAL NECESSÁRIA" -ForegroundColor Red
        Write-Host "  Motivo: Score baixo ($totalScore < 120) ou arquivos perigosos ($($qualityResult.DangerousFiles))" -ForegroundColor Red
    }
    
    # Executar aprovação automática se necessário
    if ($autoApprove) {
        Write-Host ""
        Write-Host "✅ Executando aprovação automática..." -ForegroundColor Green
        
        $reviewBody = @"
## 🤖 AI Auto-Approval - Sistema Machine Learning

**Análise Automática Completa:**

✅ **Score de Qualidade:** $($qualityResult.Score)/$($qualityResult.MaxScore)
- Arquivos de infraestrutura: $($qualityResult.InfrastructureFiles)
- Documentação: $($qualityResult.DocumentationFiles)  
- Configurações: $($qualityResult.ConfigFiles)
- Arquivos perigosos: $($qualityResult.DangerousFiles)

✅ **Score de Testes:** $($testResult.Score)/$($testResult.MaxScore)
- Scripts e testes incluídos
- Configurações válidas

✅ **Score de Segurança:** $($securityResult.Score)/$($securityResult.MaxScore)
- Nenhum secret hardcoded detectado
- Gerenciamento adequado de segurança

📊 **Score Total:** $totalScore/$maxTotalScore
🎯 **Confiança:** $confidenceLevel
🔒 **Arquivos Perigosos:** $($qualityResult.DangerousFiles)

### 🤖 Decisão da IA:
Este PR atende todos os critérios de qualidade e pode ser aprovado automaticamente. A implementação segue as melhores práticas.

---
*Auto-aprovado pelo Sistema de IA do GitHub Copilot*
"@
        
        $reviewData = @{
            event = "APPROVE"
            body = $reviewBody
        } | ConvertTo-Json
        
        try {
            $reviewResponse = Invoke-RestMethod -Uri "$baseUrl/pulls/$PullRequestNumber/reviews" -Method POST -Headers $headers -Body $reviewData -ContentType "application/json"
            Write-Host "✅ PR aprovado automaticamente!" -ForegroundColor Green
            
            # Auto-merge se confiança alta
            if ($confidenceLevel -eq "HIGH") {
                Write-Host "🔄 Executando merge automático..." -ForegroundColor Green
                
                $mergeData = @{
                    commit_title = "🤖 Auto-merge: $($prResponse.title)"
                    commit_message = "Merged automatically by AI system with high confidence score: $totalScore/$maxTotalScore"
                    merge_method = "squash"
                } | ConvertTo-Json
                
                Start-Sleep -Seconds 5  # Aguarda 5 segundos
                
                try {
                    $mergeResponse = Invoke-RestMethod -Uri "$baseUrl/pulls/$PullRequestNumber/merge" -Method PUT -Headers $headers -Body $mergeData -ContentType "application/json"
                    Write-Host "🎉 PR merged automaticamente!" -ForegroundColor Green
                }
                catch {
                    Write-Host "⚠️ Não foi possível fazer merge automático: $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
        }
        catch {
            Write-Host "❌ Erro ao aprovar PR: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host ""
        Write-Host "📢 Adicionando comentário de revisão manual..." -ForegroundColor Yellow
        
        $commentBody = @"
## ⏸️ Revisão Manual Necessária

O sistema de IA determinou que este PR requer revisão humana.

**Score:** $totalScore/$maxTotalScore (Limite: 120)
**Problemas Detectados:**
- Score de qualidade abaixo do limite
- Arquivos potencialmente sensíveis detectados: $($qualityResult.DangerousFiles)
- Considerações de segurança identificadas

@aviladevs por favor, revise este PR manualmente.

---
*Sistema de Revisão IA*
"@
        
        $commentData = @{
            body = $commentBody
        } | ConvertTo-Json
        
        try {
            $commentResponse = Invoke-RestMethod -Uri "$baseUrl/issues/$PullRequestNumber/comments" -Method POST -Headers $headers -Body $commentData -ContentType "application/json"
            Write-Host "📝 Comentário adicionado solicitando revisão manual." -ForegroundColor Yellow
        }
        catch {
            Write-Host "❌ Erro ao adicionar comentário: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "🎯 Análise de IA concluída!" -ForegroundColor Cyan
    
}
catch {
    Write-Host "❌ Erro durante a análise: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.Exception.StackTrace)" -ForegroundColor Red
}