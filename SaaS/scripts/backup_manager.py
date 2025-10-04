#!/usr/bin/env python3
"""
Sistema de Backup Automatizado
Backup inteligente com compressão, criptografia e armazenamento remoto
"""

import os
import sys
import json
import gzip
import tarfile
import logging
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import subprocess
import shutil

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class BackupService:
    """Serviço de backup automatizado"""

    def __init__(self):
        self.backup_dir = Path(settings.BASE_DIR) / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Chave de criptografia (deve ser armazenada de forma segura)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)

    def _get_or_create_encryption_key(self):
        """Obter ou criar chave de criptografia"""
        key_file = self.backup_dir / '.backup_key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Definir permissões restritas
            os.chmod(key_file, 0o600)
            return key

    def create_database_backup(self, backup_name=None):
        """Criar backup do banco de dados"""
        try:
            if not backup_name:
                backup_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_file = self.backup_dir / f"{backup_name}.sql"
            
            # Comando de backup baseado no banco configurado
            db_config = settings.DATABASES['default']
            engine = db_config['ENGINE']
            
            if 'postgresql' in engine:
                self._backup_postgresql(db_config, backup_file)
            elif 'mysql' in engine:
                self._backup_mysql(db_config, backup_file)
            elif 'sqlite' in engine:
                self._backup_sqlite(db_config, backup_file)
            else:
                raise ValueError(f"Banco não suportado: {engine}")
            
            # Comprimir backup
            compressed_file = self._compress_file(backup_file)
            
            # Criptografar backup
            encrypted_file = self._encrypt_file(compressed_file)
            
            # Limpar arquivos temporários
            backup_file.unlink(missing_ok=True)
            compressed_file.unlink(missing_ok=True)
            
            logger.info(f"Backup do banco criado: {encrypted_file}")
            return encrypted_file
            
        except Exception as e:
            logger.error(f"Erro ao criar backup do banco: {e}")
            raise

    def _backup_postgresql(self, db_config, backup_file):
        """Backup específico para PostgreSQL"""
        cmd = [
            'pg_dump',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--username={db_config['USER']}",
            f"--dbname={db_config['NAME']}",
            f"--file={backup_file}",
            '--verbose',
            '--clean',
            '--no-owner',
            '--no-privileges'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"pg_dump falhou: {result.stderr}")

    def _backup_mysql(self, db_config, backup_file):
        """Backup específico para MySQL"""
        cmd = [
            'mysqldump',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--user={db_config['USER']}",
            f"--password={db_config['PASSWORD']}",
            '--single-transaction',
            '--routines',
            '--triggers',
            db_config['NAME']
        ]
        
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise Exception(f"mysqldump falhou: {result.stderr}")

    def _backup_sqlite(self, db_config, backup_file):
        """Backup específico para SQLite"""
        db_path = db_config['NAME']
        shutil.copy2(db_path, backup_file)

    def create_media_backup(self, backup_name=None):
        """Criar backup dos arquivos de mídia"""
        try:
            if not backup_name:
                backup_name = f"media_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            media_root = Path(settings.MEDIA_ROOT)
            if not media_root.exists():
                logger.info("Diretório de mídia não existe, pulando backup")
                return None
            
            backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            
            # Criar arquivo tar comprimido
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(media_root, arcname='media')
            
            # Criptografar backup
            encrypted_file = self._encrypt_file(backup_file)
            backup_file.unlink()
            
            logger.info(f"Backup de mídia criado: {encrypted_file}")
            return encrypted_file
            
        except Exception as e:
            logger.error(f"Erro ao criar backup de mídia: {e}")
            raise

    def create_full_backup(self):
        """Criar backup completo (banco + mídia + código)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            backups = {
                'timestamp': timestamp,
                'database': None,
                'media': None,
                'code': None
            }
            
            # Backup do banco
            db_backup = self.create_database_backup(f"full_db_{timestamp}")
            backups['database'] = str(db_backup.name)
            
            # Backup de mídia
            media_backup = self.create_media_backup(f"full_media_{timestamp}")
            if media_backup:
                backups['media'] = str(media_backup.name)
            
            # Backup do código (opcional)
            code_backup = self._create_code_backup(f"full_code_{timestamp}")
            if code_backup:
                backups['code'] = str(code_backup.name)
            
            # Criar manifesto do backup
            manifest_file = self.backup_dir / f"backup_manifest_{timestamp}.json"
            with open(manifest_file, 'w') as f:
                json.dump(backups, f, indent=2)
            
            # Criptografar manifesto
            encrypted_manifest = self._encrypt_file(manifest_file)
            manifest_file.unlink()
            
            logger.info(f"Backup completo criado: {encrypted_manifest}")
            
            # Enviar notificação
            self._send_backup_notification(True, f"Backup completo criado: {timestamp}")
            
            return encrypted_manifest
            
        except Exception as e:
            logger.error(f"Erro ao criar backup completo: {e}")
            self._send_backup_notification(False, f"Erro no backup: {str(e)}")
            raise

    def _create_code_backup(self, backup_name):
        """Criar backup do código fonte"""
        try:
            # Backup apenas se estivermos em um repositório git
            if not (Path(settings.BASE_DIR) / '.git').exists():
                return None
            
            backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            
            # Criar arquivo tar excluindo arquivos desnecessários
            with tarfile.open(backup_file, 'w:gz') as tar:
                def exclude_filter(tarinfo):
                    # Excluir arquivos/diretórios desnecessários
                    exclude_patterns = [
                        '.git/', '__pycache__/', '.env', 'node_modules/',
                        '.venv/', 'venv/', '*.pyc', '*.log', 'backups/'
                    ]
                    
                    for pattern in exclude_patterns:
                        if pattern in tarinfo.name:
                            return None
                    return tarinfo
                
                tar.add(settings.BASE_DIR, arcname='code', filter=exclude_filter)
            
            # Criptografar backup
            encrypted_file = self._encrypt_file(backup_file)
            backup_file.unlink()
            
            return encrypted_file
            
        except Exception as e:
            logger.warning(f"Erro ao criar backup de código: {e}")
            return None

    def _compress_file(self, file_path):
        """Comprimir arquivo"""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path

    def _encrypt_file(self, file_path):
        """Criptografar arquivo"""
        encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
        
        with open(file_path, 'rb') as f_in:
            data = f_in.read()
            encrypted_data = self.cipher.encrypt(data)
            
            with open(encrypted_path, 'wb') as f_out:
                f_out.write(encrypted_data)
        
        return encrypted_path

    def decrypt_file(self, encrypted_file_path, output_path=None):
        """Descriptografar arquivo"""
        if not output_path:
            output_path = Path(str(encrypted_file_path).replace('.enc', ''))
        
        with open(encrypted_file_path, 'rb') as f_in:
            encrypted_data = f_in.read()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(decrypted_data)
        
        return output_path

    def list_backups(self):
        """Listar backups disponíveis"""
        backups = []
        
        for backup_file in self.backup_dir.glob('*.enc'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'type': self._get_backup_type(backup_file.name)
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)

    def _get_backup_type(self, filename):
        """Identificar tipo de backup pelo nome"""
        if 'db_' in filename:
            return 'database'
        elif 'media_' in filename:
            return 'media'
        elif 'code_' in filename:
            return 'code'
        elif 'manifest_' in filename:
            return 'manifest'
        else:
            return 'unknown'

    def cleanup_old_backups(self, keep_days=30):
        """Limpar backups antigos"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        
        for backup_file in self.backup_dir.glob('*.enc'):
            created_time = datetime.fromtimestamp(backup_file.stat().st_ctime)
            
            if created_time < cutoff_date:
                backup_file.unlink()
                removed_count += 1
                logger.info(f"Backup antigo removido: {backup_file.name}")
        
        logger.info(f"Limpeza concluída: {removed_count} backups removidos")
        return removed_count

    def _send_backup_notification(self, success, message):
        """Enviar notificação sobre status do backup"""
        try:
            subject = "✅ Backup realizado com sucesso" if success else "❌ Erro no backup"
            
            send_mail(
                subject=subject,
                message=f"Status do backup:\n\n{message}\n\nTimestamp: {datetime.now()}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.BACKUP_NOTIFICATION_EMAIL],
                fail_silently=True
            )
        except Exception as e:
            logger.warning(f"Erro ao enviar notificação de backup: {e}")

    def restore_database(self, backup_file):
        """Restaurar banco de dados a partir de backup"""
        try:
            # Descriptografar backup
            decrypted_file = self.decrypt_file(backup_file)
            
            # Descomprimir se necessário
            if decrypted_file.suffix == '.gz':
                with gzip.open(decrypted_file, 'rb') as f_in:
                    sql_content = f_in.read().decode('utf-8')
            else:
                with open(decrypted_file, 'r') as f:
                    sql_content = f.read()
            
            # Executar restore baseado no banco
            db_config = settings.DATABASES['default']
            engine = db_config['ENGINE']
            
            if 'postgresql' in engine:
                self._restore_postgresql(db_config, sql_content)
            elif 'mysql' in engine:
                self._restore_mysql(db_config, sql_content)
            elif 'sqlite' in engine:
                self._restore_sqlite(db_config, decrypted_file)
            
            # Limpar arquivo temporário
            decrypted_file.unlink(missing_ok=True)
            
            logger.info("Banco de dados restaurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao restaurar banco: {e}")
            raise

    def _restore_postgresql(self, db_config, sql_content):
        """Restaurar PostgreSQL"""
        cmd = [
            'psql',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--username={db_config['USER']}",
            f"--dbname={db_config['NAME']}"
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        stdout, stderr = process.communicate(input=sql_content)
        
        if process.returncode != 0:
            raise Exception(f"Restore PostgreSQL falhou: {stderr}")


def main():
    """Função principal para execução via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Backup Automatizado')
    parser.add_argument('--action', choices=['backup', 'list', 'cleanup'], 
                       default='backup', help='Ação a executar')
    parser.add_argument('--type', choices=['full', 'db', 'media'], 
                       default='full', help='Tipo de backup')
    parser.add_argument('--keep-days', type=int, default=30, 
                       help='Dias para manter backups na limpeza')
    
    args = parser.parse_args()
    
    backup_service = BackupService()
    
    if args.action == 'backup':
        if args.type == 'full':
            backup_service.create_full_backup()
        elif args.type == 'db':
            backup_service.create_database_backup()
        elif args.type == 'media':
            backup_service.create_media_backup()
    
    elif args.action == 'list':
        backups = backup_service.list_backups()
        print(f"{'Nome':<40} {'Tipo':<10} {'Tamanho':<10} {'Criado'}")
        print("-" * 80)
        for backup in backups:
            size_mb = backup['size'] / (1024 * 1024)
            print(f"{backup['name']:<40} {backup['type']:<10} {size_mb:.1f}MB {backup['created']}")
    
    elif args.action == 'cleanup':
        removed = backup_service.cleanup_old_backups(args.keep_days)
        print(f"Removidos {removed} backups antigos")


if __name__ == '__main__':
    main()