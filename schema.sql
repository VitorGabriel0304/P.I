-- Cria o banco de dados se ele ainda não existir
CREATE DATABASE IF NOT EXISTS bibliocommunity CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bibliocommunity;

-- Tabela para armazenar os cargos e o que cada um pode acessar
CREATE TABLE IF NOT EXISTS funcoes (
    id_funcao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(20) NOT NULL UNIQUE, -- Nome do cargo (ex: Admin)
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    descricao VARCHAR(255),
    -- Permissões de acesso (0 = Não, 1 = Sim)
    gerenciar_livros BOOLEAN DEFAULT 0,
    gerenciar_usuarios BOOLEAN DEFAULT 0,
    gerenciar_emprestimos BOOLEAN DEFAULT 0,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela para cadastrar os usuários do sistema (Admin, Alunos, etc)
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    celular VARCHAR(20) NOT NULL,
    estado CHAR(2) NOT NULL, -- UF do estado (ex: SP)
    senha VARCHAR(255) NOT NULL, -- Senha criptografada
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    funcao_id BIGINT UNSIGNED NOT NULL, -- FK ligando ao cargo do usuário
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_funcao FOREIGN KEY (funcao_id) REFERENCES funcoes (id_funcao)
);

-- Tabela de Livros (Desenvolvido por Vitor)
CREATE TABLE IF NOT EXISTS livros (
    id_livro BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    categoria VARCHAR(100),
    status ENUM('Disponível', 'Emprestado', 'Indisponível') DEFAULT 'Disponível',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Empréstimos (Desenvolvido por Rhian)
CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    livro_id BIGINT UNSIGNED NOT NULL, -- FK do livro emprestado
    usuario_id BIGINT UNSIGNED NOT NULL, -- FK do usuário que pegou o livro
    data_retirada DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_prevista_devolucao DATETIME NOT NULL,
    data_devolucao_real DATETIME NULL, -- Preenchido quando o livro é devolvido
    status ENUM('Ativo', 'Devolvido', 'Atrasado') DEFAULT 'Ativo',
    CONSTRAINT fk_emprestimo_livro FOREIGN KEY (livro_id) REFERENCES livros (id_livro),
    CONSTRAINT fk_emprestimo_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id_usuario)
);
