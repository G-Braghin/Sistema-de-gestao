-- Estrutura inicial para um banco vazio.
-- Este script nao atualiza tabelas existentes.

CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    papel VARCHAR(20) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(200),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT clientes_cpf_unico UNIQUE (cpf)
);

CREATE TABLE produtos (
    id_produto SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    marca VARCHAR(100) NOT NULL,
    preco NUMERIC(10, 2) NOT NULL,
    quantidade_estoque INTEGER NOT NULL,
    CONSTRAINT produtos_estoque_nao_negativo CHECK (quantidade_estoque >= 0),
    CONSTRAINT produtos_preco_positivo CHECK (preco > 0)
);

CREATE TABLE vendas (
    id_venda SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    preco_total NUMERIC(10, 2) NOT NULL,
    data_hora TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'Concluido',
    data_cancelamento TIMESTAMPTZ,
    id_usuario_cancelamento INTEGER REFERENCES usuarios(id_usuario)
);

CREATE TABLE venda_itens (
    id_venda_item SERIAL PRIMARY KEY,
    id_venda INTEGER NOT NULL REFERENCES vendas(id_venda),
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto),
    nome_produto VARCHAR(100) NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario NUMERIC(10, 2) NOT NULL,
    CONSTRAINT venda_itens_quantidade_positiva CHECK (quantidade > 0),
    CONSTRAINT venda_itens_preco_positivo CHECK (preco_unitario > 0)
);

CREATE TABLE movimentacoes_estoque (
    id_movimentacao SERIAL PRIMARY KEY,
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto),
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    tipo VARCHAR(10) NOT NULL,
    quantidade INTEGER NOT NULL,
    data_hora TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    motivo VARCHAR(20) NOT NULL,
    id_venda INTEGER REFERENCES vendas(id_venda),
    CONSTRAINT movimentacoes_quantidade_positiva CHECK (quantidade > 0)
);
