-- Schema para armazenar dados de NFe e CTe no Google Cloud SQL (MySQL)

-- Tabela para armazenar NFe (Notas Fiscais Eletrônicas)
CREATE TABLE IF NOT EXISTS nfe (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    chave_acesso VARCHAR(44) UNIQUE NOT NULL,
    numero_nf VARCHAR(20),
    serie VARCHAR(10),
    data_emissao DATETIME,
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Emitente
    emit_cnpj VARCHAR(14),
    emit_nome VARCHAR(255),
    emit_fantasia VARCHAR(255),
    emit_ie VARCHAR(20),
    emit_endereco TEXT,
    emit_municipio VARCHAR(100),
    emit_uf VARCHAR(2),
    emit_cep VARCHAR(8),
    
    -- Destinatário
    dest_cnpj_cpf VARCHAR(14),
    dest_nome VARCHAR(255),
    dest_ie VARCHAR(20),
    dest_endereco TEXT,
    dest_municipio VARCHAR(100),
    dest_uf VARCHAR(2),
    dest_cep VARCHAR(8),
    
    -- Totais
    valor_total DECIMAL(15,2),
    valor_produtos DECIMAL(15,2),
    valor_icms DECIMAL(15,2),
    valor_ipi DECIMAL(15,2),
    valor_pis DECIMAL(15,2),
    valor_cofins DECIMAL(15,2),
    valor_tributos DECIMAL(15,2),
    
    -- Status e Protocolo
    status_nfe VARCHAR(20),
    protocolo VARCHAR(50),
    motivo TEXT,
    
    -- XML completo
    xml_content LONGTEXT,
    arquivo_nome VARCHAR(255),
    
    INDEX idx_chave (chave_acesso),
    INDEX idx_emit_cnpj (emit_cnpj),
    INDEX idx_dest_cnpj (dest_cnpj_cpf),
    INDEX idx_data_emissao (data_emissao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para armazenar itens da NFe
CREATE TABLE IF NOT EXISTS nfe_itens (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nfe_id BIGINT NOT NULL,
    chave_acesso VARCHAR(44) NOT NULL,
    numero_item INT,
    
    -- Produto
    codigo_produto VARCHAR(60),
    descricao TEXT,
    ncm VARCHAR(8),
    cfop VARCHAR(4),
    cest VARCHAR(7),
    unidade VARCHAR(6),
    quantidade DECIMAL(15,4),
    valor_unitario DECIMAL(15,10),
    valor_total DECIMAL(15,2),
    ean VARCHAR(14),
    
    -- Impostos
    valor_icms DECIMAL(15,2),
    valor_ipi DECIMAL(15,2),
    valor_pis DECIMAL(15,2),
    valor_cofins DECIMAL(15,2),
    
    FOREIGN KEY (nfe_id) REFERENCES nfe(id) ON DELETE CASCADE,
    INDEX idx_nfe_id (nfe_id),
    INDEX idx_chave (chave_acesso),
    INDEX idx_produto (codigo_produto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para armazenar CTe (Conhecimento de Transporte Eletrônico)
CREATE TABLE IF NOT EXISTS cte (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    chave_acesso VARCHAR(44) UNIQUE NOT NULL,
    numero_ct VARCHAR(20),
    serie VARCHAR(10),
    data_emissao DATETIME,
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Emitente
    emit_cnpj VARCHAR(14),
    emit_nome VARCHAR(255),
    emit_fantasia VARCHAR(255),
    emit_ie VARCHAR(20),
    emit_endereco TEXT,
    emit_municipio VARCHAR(100),
    emit_uf VARCHAR(2),
    
    -- Remetente
    rem_cnpj VARCHAR(14),
    rem_nome VARCHAR(255),
    rem_ie VARCHAR(20),
    rem_municipio VARCHAR(100),
    rem_uf VARCHAR(2),
    
    -- Destinatário
    dest_cnpj VARCHAR(14),
    dest_nome VARCHAR(255),
    dest_ie VARCHAR(20),
    dest_municipio VARCHAR(100),
    dest_uf VARCHAR(2),
    
    -- Dados do transporte
    modal VARCHAR(2),
    tipo_servico VARCHAR(1),
    cfop VARCHAR(4),
    natureza_operacao VARCHAR(255),
    municipio_inicio VARCHAR(100),
    uf_inicio VARCHAR(2),
    municipio_fim VARCHAR(100),
    uf_fim VARCHAR(2),
    
    -- Valores
    valor_total DECIMAL(15,2),
    valor_receber DECIMAL(15,2),
    valor_carga DECIMAL(15,2),
    valor_icms DECIMAL(15,2),
    
    -- Status e Protocolo
    status_cte VARCHAR(20),
    protocolo VARCHAR(50),
    motivo TEXT,
    
    -- XML completo
    xml_content LONGTEXT,
    arquivo_nome VARCHAR(255),
    
    INDEX idx_chave (chave_acesso),
    INDEX idx_emit_cnpj (emit_cnpj),
    INDEX idx_rem_cnpj (rem_cnpj),
    INDEX idx_dest_cnpj (dest_cnpj),
    INDEX idx_data_emissao (data_emissao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para armazenar documentos relacionados ao CTe
CREATE TABLE IF NOT EXISTS cte_documentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cte_id BIGINT NOT NULL,
    chave_acesso_cte VARCHAR(44) NOT NULL,
    tipo_documento VARCHAR(20),
    chave_documento VARCHAR(44),
    
    FOREIGN KEY (cte_id) REFERENCES cte(id) ON DELETE CASCADE,
    INDEX idx_cte_id (cte_id),
    INDEX idx_chave_cte (chave_acesso_cte)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de log de importação
CREATE TABLE IF NOT EXISTS import_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_documento VARCHAR(10),
    arquivo_nome VARCHAR(255),
    status VARCHAR(20),
    mensagem TEXT,
    chave_acesso VARCHAR(44),
    
    INDEX idx_data (data_importacao),
    INDEX idx_tipo (tipo_documento),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
