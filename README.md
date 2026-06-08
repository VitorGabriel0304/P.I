# BiblioCommuntiy 📚

Sistema web completo para gerenciamento de biblioteca desenvolvido com **Flask** e **MySQL**.

## 🎯 Funcionalidades

- ✅ CRUD de Usuários com autenticação
- ✅ CRUD de Funções com permissões
- ✅ CRUD de Livros com categorias
- ✅ CRUD de Empréstimos com devolução
- ✅ Sistema de Login/Logout seguro
- ✅ Pool de conexões MySQL otimizado
- ✅ Interface responsiva com Bootstrap

## ⚙️ Pré-requisitos

- Python 3.10+
- MySQL (via XAMPP)
- Git

## 🚀 Instalação e Execução

### 1️⃣ Preparar o banco de dados

```bash
# Certifique-se que o MySQL está rodando
# Abra XAMPP Control Panel e clique em "Start" no MySQL
```

### 2️⃣ Clonar/Preparar o projeto

```bash
cd c:\Users\glauc\Projetos\P.I
```

### 3️⃣ Criar ambiente virtual (primeira vez)

```bash
python -m venv venv
venv\Scripts\activate
```

### 4️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 5️⃣ Executar a aplicação

```bash
python app.py
```

### 6️⃣ Acessar no navegador

```
http://127.0.0.1:5000
```

## 🔐 Credenciais Padrão

Na primeira execução, um usuário administrador é criado automaticamente:

- **Email:** admin@bibliocommunity.com
- **Senha:** admin123

⚠️ **Recomendação:** Altere a senha após o primeiro login!

## 📁 Estrutura do Projeto

```
P.I/
├── app.py                 # Aplicação Flask principal
├── db.py                  # Configuração do banco de dados
├── schema.sql             # Script de criação das tabelas
├── requirements.txt       # Dependências do projeto
├── static/
│   ├── css/
│   │   └── style.css      # Estilos globais
│   └── js/
│       └── script.js      # Scripts JavaScript
└── templates/
    ├── auth/
    │   └── login.html     # Página de login
    ├── dashboard/
    │   ├── home.html
    │   ├── funcoes/       # Templates de funções
    │   ├── usuarios/      # Templates de usuários
    │   ├── livros/        # Templates de livros
    │   └── emprestimos/   # Templates de empréstimos
    └── base_dashboard.html # Layout base do dashboard
```

## 🔧 Troubleshooting

### Erro: "Não foi possível obter conexão do pool"

- ✓ Verifique se o MySQL está rodando no XAMPP
- ✓ Confirme que o banco `bibliocommunity` foi criado
- ✓ Verifique as credenciais em `db.py`

### Erro: "ModuleNotFoundError: No module named 'flask'"

- ✓ Execute: `pip install -r requirements.txt`

### Templates não encontrados

- ✓ Certifique-se de estar na pasta raiz do projeto
- ✓ Execute: `python app.py`

## 📚 Material do Professor

Este projeto segue exatamente as etapas de desenvolvimento fornecidas:

1. Criação do Projeto
2. Conexão com Banco de Dados
3. Base do Projeto (CSS/JS)
4. Rotas e Templates
   5-8. CRUD de Funções e Usuários
5. Login, Logout e Proteção

## ✨ Funcionalidades Extras Implementadas

- 🔄 Pool de conexões otimizado
- 🛡️ Hash de senhas seguro
- ⚡ Validações avançadas no servidor
- 💾 Transações de banco de dados
- 📱 Interface responsiva

## 👨‍💻 Desenvolvido para

Atividade avaliativa da disciplina de Desenvolvimento Web em Flask - FATEC Jahu 2026

---

**Última atualização:** Junho 2026
