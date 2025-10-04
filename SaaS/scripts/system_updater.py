#!/usr/bin/env python3
"""
Script de Atualização Automática do Sistema
Atualiza dependências, executa migrações e faz deploy seguro
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemUpdater:
    """Atualizador automático do sistema"""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.backup_service = None

    def update_dependencies(self):
        """Atualizar dependências Python"""
        logger.info("🔄 Atualizando dependências Python...")
        
        try:
            # Backup antes da atualização
            self._create_backup_if_available()
            
            # Atualizar pip
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True)
            
            # Instalar dependências atualizadas
            requirements_file = self.project_root / 'app-aviladevops' / 'requirements.txt'
            if requirements_file.exists():
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 
                              str(requirements_file), '--upgrade'], check=True)
            
            logger.info("✅ Dependências Python atualizadas com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao atualizar dependências: {e}")
            return False

    def update_frontend_dependencies(self):
        """Atualizar dependências do frontend (Node.js)"""
        logger.info("🔄 Atualizando dependências do frontend...")
        
        try:
            clinica_dir = self.project_root / 'clinica'
            if clinica_dir.exists() and (clinica_dir / 'package.json').exists():
                # Mudar para diretório da clínica
                original_cwd = os.getcwd()
                os.chdir(clinica_dir)
                
                try:
                    # Atualizar dependências
                    subprocess.run(['npm', 'update'], check=True)
                    subprocess.run(['npm', 'audit', 'fix'], check=False)  # Não falhar se não houver correções
                    
                    logger.info("✅ Dependências do frontend atualizadas")
                    return True
                    
                finally:
                    os.chdir(original_cwd)
            else:
                logger.info("ℹ️ Projeto frontend não encontrado, pulando atualização")
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao atualizar frontend: {e}")
            return False

    def run_migrations(self):
        """Executar migrações do banco de dados"""
        logger.info("🗄️ Executando migrações do banco...")
        
        try:
            # Verificar migrações pendentes
            result = subprocess.run([
                sys.executable, 'manage.py', 'showmigrations', '--plan'
            ], capture_output=True, text=True, cwd=self.project_root / 'app-aviladevops')
            
            if '[ ]' in result.stdout:  # Há migrações pendentes
                logger.info("📝 Migrações pendentes encontradas, executando...")
                
                # Fazer migrations
                subprocess.run([
                    sys.executable, 'manage.py', 'makemigrations'
                ], check=True, cwd=self.project_root / 'app-aviladevops')
                
                # Executar migrations
                subprocess.run([
                    sys.executable, 'manage.py', 'migrate'
                ], check=True, cwd=self.project_root / 'app-aviladevops')
                
                logger.info("✅ Migrações executadas com sucesso")
            else:
                logger.info("ℹ️ Nenhuma migração pendente")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao executar migrações: {e}")
            return False

    def collect_static_files(self):
        """Coletar arquivos estáticos"""
        logger.info("📁 Coletando arquivos estáticos...")
        
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'collectstatic', '--noinput'
            ], check=True, cwd=self.project_root / 'app-aviladevops')
            
            logger.info("✅ Arquivos estáticos coletados")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao coletar estáticos: {e}")
            return False

    def run_tests(self):
        """Executar testes automatizados"""
        logger.info("🧪 Executando testes...")
        
        try:
            # Testes do backend
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', '--verbosity=2'
            ], capture_output=True, text=True, cwd=self.project_root / 'app-aviladevops')
            
            if result.returncode == 0:
                logger.info("✅ Todos os testes passaram")
                return True
            else:
                logger.error(f"❌ Testes falharam:\n{result.stdout}\n{result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao executar testes: {e}")
            return False

    def check_security(self):
        """Verificar vulnerabilidades de segurança"""
        logger.info("🔒 Verificando segurança...")
        
        try:
            # Verificar vulnerabilidades Python
            try:
                subprocess.run(['safety', 'check'], check=True)
                logger.info("✅ Verificação de segurança Python OK")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("⚠️ Safety não instalado ou vulnerabilidades encontradas")
            
            # Verificar vulnerabilidades Node.js
            clinica_dir = self.project_root / 'clinica'
            if clinica_dir.exists():
                original_cwd = os.getcwd()
                os.chdir(clinica_dir)
                
                try:
                    result = subprocess.run(['npm', 'audit'], capture_output=True, text=True)
                    if 'found 0 vulnerabilities' in result.stdout:
                        logger.info("✅ Verificação de segurança Node.js OK")
                    else:
                        logger.warning("⚠️ Vulnerabilidades encontradas no Node.js")
                finally:
                    os.chdir(original_cwd)
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na verificação de segurança: {e}")
            return True  # Não falhar o update por isso

    def restart_services(self):
        """Reiniciar serviços (se usando systemd ou docker)"""
        logger.info("🔄 Reiniciando serviços...")
        
        try:
            # Verificar se está rodando em Docker
            if os.path.exists('/.dockerenv'):
                logger.info("🐳 Ambiente Docker detectado - restart automático")
                return True
            
            # Verificar se há serviços systemd
            service_files = [
                'aviladevops-saas.service',
                'aviladevops-worker.service',
                'aviladevops-beat.service'
            ]
            
            for service in service_files:
                try:
                    subprocess.run(['systemctl', 'restart', service], 
                                 check=True, capture_output=True)
                    logger.info(f"✅ Serviço {service} reiniciado")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.info(f"ℹ️ Serviço {service} não encontrado")
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao reiniciar serviços: {e}")
            return True  # Não falhar por isso

    def _create_backup_if_available(self):
        """Criar backup se o serviço estiver disponível"""
        try:
            backup_script = self.project_root / 'scripts' / 'backup_manager.py'
            if backup_script.exists():
                logger.info("💾 Criando backup antes da atualização...")
                subprocess.run([
                    sys.executable, str(backup_script), '--action', 'backup', '--type', 'db'
                ], check=True)
                logger.info("✅ Backup criado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar backup: {e}")

    def health_check(self):
        """Verificar saúde do sistema após atualização"""
        logger.info("🏥 Verificando saúde do sistema...")
        
        try:
            # Verificar se o Django está funcionando
            result = subprocess.run([
                sys.executable, 'manage.py', 'check'
            ], capture_output=True, text=True, cwd=self.project_root / 'app-aviladevops')
            
            if result.returncode == 0:
                logger.info("✅ Sistema Django OK")
            else:
                logger.error(f"❌ Problemas no Django: {result.stdout}")
                return False
            
            # Verificar health endpoint se disponível
            try:
                import requests
                response = requests.get('http://localhost:8000/health/', timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Health endpoint OK")
                else:
                    logger.warning(f"⚠️ Health endpoint retornou {response.status_code}")
            except Exception:
                logger.info("ℹ️ Health endpoint não disponível")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de saúde: {e}")
            return False

    def full_update(self):
        """Executar atualização completa do sistema"""
        logger.info("🚀 Iniciando atualização completa do sistema...")
        start_time = datetime.now()
        
        steps = [
            ("Atualizar dependências Python", self.update_dependencies),
            ("Atualizar dependências Frontend", self.update_frontend_dependencies),
            ("Executar migrações", self.run_migrations),
            ("Coletar arquivos estáticos", self.collect_static_files),
            ("Executar testes", self.run_tests),
            ("Verificar segurança", self.check_security),
            ("Reiniciar serviços", self.restart_services),
            ("Verificar saúde", self.health_check),
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            
            if not step_func():
                failed_steps.append(step_name)
                logger.error(f"❌ Falha em: {step_name}")
                
                # Parar em falhas críticas
                if step_name in ["Executar migrações", "Executar testes"]:
                    logger.error("🛑 Falha crítica detectada, interrompendo atualização")
                    break
        
        duration = datetime.now() - start_time
        
        if not failed_steps:
            logger.info(f"🎉 Atualização completa bem-sucedida! Duração: {duration}")
            return True
        else:
            logger.error(f"⚠️ Atualização concluída com falhas: {failed_steps}")
            logger.error(f"Duração: {duration}")
            return False


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Atualizador automático do sistema')
    parser.add_argument('--step', choices=[
        'deps', 'frontend', 'migrations', 'static', 'tests', 'security', 'restart', 'health'
    ], help='Executar apenas um passo específico')
    parser.add_argument('--project-root', help='Caminho raiz do projeto')
    
    args = parser.parse_args()
    
    updater = SystemUpdater(args.project_root)
    
    if args.step:
        step_functions = {
            'deps': updater.update_dependencies,
            'frontend': updater.update_frontend_dependencies,
            'migrations': updater.run_migrations,
            'static': updater.collect_static_files,
            'tests': updater.run_tests,
            'security': updater.check_security,
            'restart': updater.restart_services,
            'health': updater.health_check,
        }
        
        success = step_functions[args.step]()
        sys.exit(0 if success else 1)
    else:
        # Atualização completa
        success = updater.full_update()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()