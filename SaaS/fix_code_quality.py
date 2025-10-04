#!/usr/bin/env python3
"""
Script para corrigir problemas de qualidade de código automaticamente.
Corrige:
- W293: Linhas em branco com espaços
- F541: f-strings sem placeholders
- Alguns erros E501: Linhas muito longas (simples)
"""

import os
import re
import sys

def fix_blank_lines_with_whitespace(content):
    """Remove espaços em branco de linhas vazias (W293)"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Se a linha contém apenas espaços, remover todos
        if line.strip() == '':
            fixed_lines.append('')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_f_strings_without_placeholders(content):
    """Converte f-strings sem placeholders para strings normais (F541)"""
    # Regex para encontrar f-strings sem placeholders
    pattern = r'f"([^"]*?)"'
    
    def replace_f_string(match):
        string_content = match.group(1)
        # Se não contém { }, converter para string normal
        if '{' not in string_content and '}' not in string_content:
            return f'"{string_content}"'
        return match.group(0)
    
    content = re.sub(pattern, replace_f_string, content)
    
    # Mesmo para aspas simples
    pattern = r"f'([^']*?)'"
    content = re.sub(pattern, lambda m: f"'{m.group(1)}'" if '{' not in m.group(1) and '}' not in m.group(1) else m.group(0), content)
    
    return content

def fix_trailing_whitespace(content):
    """Remove espaços em branco no final das linhas (W291)"""
    lines = content.split('\n')
    fixed_lines = [line.rstrip() for line in lines]
    return '\n'.join(fixed_lines)

def add_newline_at_end(content):
    """Adiciona nova linha no final do arquivo se não existir (W292)"""
    if content and not content.endswith('\n'):
        content += '\n'
    return content

def fix_python_file(file_path):
    """Corrige um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar correções
        content = fix_blank_lines_with_whitespace(content)
        content = fix_f_strings_without_placeholders(content)
        content = fix_trailing_whitespace(content)
        content = add_newline_at_end(content)
        
        # Só escrever se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigido: {file_path}")
            return True
        else:
            print(f"⏭️  Sem mudanças: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro em {file_path}: {e}")
        return False

def main():
    """Função principal"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Diretórios para processar
    directories_to_fix = [
        'app-aviladevops',
        'fiscal', 
        'sistema',
        'LANDING-PAGE',
        'clinica/backend'
    ]
    
    total_files = 0
    fixed_files = 0
    
    for directory in directories_to_fix:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            print(f"⚠️  Diretório não encontrado: {dir_path}")
            continue
            
        print(f"\n📂 Processando: {directory}")
        
        # Buscar arquivos Python
        for root, dirs, files in os.walk(dir_path):
            # Ignorar diretórios comuns que não precisam de correção
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    if fix_python_file(file_path):
                        fixed_files += 1
    
    print(f"\n📊 Resumo:")
    print(f"   Total de arquivos Python processados: {total_files}")
    print(f"   Arquivos corrigidos: {fixed_files}")
    print(f"   Arquivos sem mudanças: {total_files - fixed_files}")
    
    if fixed_files > 0:
        print(f"\n🎉 Correções aplicadas! Execute git add . && git commit -m 'fix: code quality improvements'")
    else:
        print(f"\n✨ Todos os arquivos já estão em conformidade!")

if __name__ == "__main__":
    main()