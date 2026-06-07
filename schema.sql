CREATE DATABASE IF NOT EXISTS bibliocommunity CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bibliocommunity;

CREATE TABLE IF NOT EXISTS funcoes (
    id_funcao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    descricao VARCHAR(255),
    gerenciar_livros BOOLEAN DEFAULT 0,
    gerenciar_usuarios BOOLEAN DEFAULT 0,
    gerenciar_emprestimos BOOLEAN DEFAULT 0,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    celular VARCHAR(20) NOT NULL,
    estado CHAR(2) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    funcao_id BIGINT UNSIGNED NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_funcao FOREIGN KEY (funcao_id) REFERENCES funcoes (id_funcao)
);

-- Tabela de Livros (Vitor)
CREATE TABLE IF NOT EXISTS livros (
    id_livro BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    categoria VARCHAR(100),
    status ENUM('Disponível', 'Emprestado', 'Indisponível') DEFAULT 'Disponível',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);
