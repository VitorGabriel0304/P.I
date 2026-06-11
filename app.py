from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import execute_one, iniciar_bd, execute_query
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Inicia o aplicativo Flask
app = Flask(__name__)
app.secret_key = 'biblio_secret_key_v2' # Chave para segurança da sessão

# Cria o banco e as tabelas ao rodar o projeto
iniciar_bd()

# Função que cria o usuário Administrador padrão se o banco estiver vazio
def garantir_admin():
    try:
        total = execute_one('SELECT COUNT(*) AS total FROM usuarios')
        if total and total['total'] == 0:
            funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',))
            if not funcao:
                execute_query(
                    "INSERT INTO funcoes (nome, status, descricao, gerenciar_livros, gerenciar_usuarios, gerenciar_emprestimos) VALUES (%s, 'Ativo', %s, 1, 1, 1)",
                    ('Administrador', 'Acesso total ao sistema')
                )
                funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',))
            
            execute_query(
                "INSERT INTO usuarios (nome, cpf, email, celular, estado, senha, status, funcao_id) VALUES (%s, %s, %s, %s, %s, %s, 'Ativo', %s)",
                ('Administrador', '000.000.000-00', 'admin@bibliocommunity.com', '(00) 00000-0000', 'SP', generate_password_hash('admin123'), funcao['id_funcao'])
            )
    except Exception as e:
        print(f'Erro ao garantir admin: {e}')

garantir_admin()

# Decorador para proteger rotas que precisam de login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('usuario'):
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# Disponibiliza os dados do usuário logado para todos os templates HTML
@app.context_processor
def injetar_usuario():
    return dict(usuario_logado=session.get('usuario'))

# --- Módulo de Funções/Cargos ---

@app.route('/funcoes/listar')
@login_required
def funcoes_listar():
    # Busca todas as funções cadastradas no banco
    dados = execute_query("SELECT * FROM funcoes ORDER BY nome", fetch=True)
    return render_template('dashboard/funcoes/listar.html', dados=dados)

@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
@login_required
def funcoes_cadastrar():
    if request.method == 'POST':
        # Pega os dados enviados pelo formulário
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        gerenciar_livros = request.form.get('gerenciar_livros') == 'on'
        gerenciar_usuarios = request.form.get('gerenciar_usuarios') == 'on'
        gerenciar_emprestimos = request.form.get('gerenciar_emprestimos') == 'on'
        
        if not nome:
            flash('Nome da função é obrigatório!', 'danger')
            return redirect(url_for('funcoes_cadastrar'))
        
        try:
            # Insere a nova função no banco de dados
            execute_query(
                "INSERT INTO funcoes (nome, descricao, gerenciar_livros, gerenciar_usuarios, gerenciar_emprestimos) VALUES (%s, %s, %s, %s, %s)",
                (nome, descricao, gerenciar_livros, gerenciar_usuarios, gerenciar_emprestimos)
            )
            flash('Função cadastrada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar função: {str(e)}', 'danger')
    
    return render_template('dashboard/funcoes/form.html', modo='cadastrar')

@app.route('/funcoes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def funcoes_editar(id):
    # Busca os dados da função que será editada
    item = execute_one("SELECT * FROM funcoes WHERE id_funcao = %s", (id,))
    if not item:
        flash('Função não encontrada!', 'warning')
        return redirect(url_for('funcoes_listar'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        gerenciar_livros = request.form.get('gerenciar_livros') == 'on'
        gerenciar_usuarios = request.form.get('gerenciar_usuarios') == 'on'
        gerenciar_emprestimos = request.form.get('gerenciar_emprestimos') == 'on'
        
        try:
            # Atualiza os dados da função no banco
            execute_query(
                "UPDATE funcoes SET nome=%s, descricao=%s, gerenciar_livros=%s, gerenciar_usuarios=%s, gerenciar_emprestimos=%s WHERE id_funcao=%s",
                (nome, descricao, gerenciar_livros, gerenciar_usuarios, gerenciar_emprestimos, id)
            )
            flash('Função atualizada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))
        except Exception as e:
            flash(f'Erro ao atualizar função: {str(e)}', 'danger')
    
    return render_template('dashboard/funcoes/form.html', modo='editar', item=item)

@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
@login_required
def funcoes_excluir(id):
    try:
        # Remove a função do banco de dados
        execute_query("DELETE FROM funcoes WHERE id_funcao = %s", (id,))
        flash('Função removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover função: {str(e)}', 'danger')
    return redirect(url_for('funcoes_listar'))

# --- Módulo de Usuários ---

@app.route('/usuarios/listar')
@login_required
def usuarios_listar():
    # Busca usuários e traz também o nome da função (cargo) de cada um
    sql = "SELECT u.*, f.nome as funcao_nome FROM usuarios u INNER JOIN funcoes f ON u.funcao_id = f.id_funcao ORDER BY u.nome"
    dados = execute_query(sql, fetch=True)
    return render_template('dashboard/usuarios/listar.html', dados=dados)

@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
@login_required
def usuarios_cadastrar():
    if request.method == 'POST':
        # Coleta dados do formulário
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        email = request.form.get('email', '').strip()
        celular = request.form.get('celular', '').strip()
        estado = request.form.get('estado', '').strip()
        funcao_id = request.form.get('funcao_id')
        senha = request.form.get('senha', '').strip()
        confirma_senha = request.form.get('confirma_senha', '').strip()
        
        # Valida se campos estão vazios ou se senhas não batem
        if not all([nome, cpf, email, celular, estado, funcao_id, senha]):
            flash('Todos os campos são obrigatórios!', 'danger')
        elif senha != confirma_senha:
            flash('As senhas não conferem!', 'danger')
        else:
            try:
                # Salva o novo usuário com a senha criptografada
                execute_query(
                    "INSERT INTO usuarios (nome, cpf, email, celular, estado, senha, funcao_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (nome, cpf, email, celular, estado, generate_password_hash(senha), funcao_id)
                )
                flash('Usuário cadastrado com sucesso!', 'success')
                return redirect(url_for('usuarios_listar'))
            except Exception as e:
                flash(f'Erro ao cadastrar: {str(e)}', 'danger')
    
    funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
    return render_template('dashboard/usuarios/form.html', modo='cadastrar', funcoes=funcoes)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def usuarios_editar(id):
    item = execute_one("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        email = request.form.get('email', '').strip()
        funcao_id = request.form.get('funcao_id')
        senha = request.form.get('senha', '').strip()
        
        try:
            if senha:
                # Se informou nova senha, atualiza com criptografia
                execute_query(
                    "UPDATE usuarios SET nome=%s, cpf=%s, email=%s, funcao_id=%s, senha=%s WHERE id_usuario=%s",
                    (nome, cpf, email, funcao_id, generate_password_hash(senha), id)
                )
            else:
                # Se não informou senha, mantém a atual
                execute_query(
                    "UPDATE usuarios SET nome=%s, cpf=%s, email=%s, funcao_id=%s WHERE id_usuario=%s",
                    (nome, cpf, email, funcao_id, id)
                )
            flash('Usuário atualizado!', 'success')
            return redirect(url_for('usuarios_listar'))
        except Exception as e:
            flash(f'Erro ao atualizar: {str(e)}', 'danger')
            
    funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
    return render_template('dashboard/usuarios/form.html', modo='editar', item=item, funcoes=funcoes)

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def usuarios_excluir(id):
    try:
        execute_query("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        flash('Usuário removido!', 'success')
    except Exception as e:
        flash(f'Erro ao remover: {str(e)}', 'danger')
    return redirect(url_for('usuarios_listar'))

# --- Rotas de Autenticação ---

@app.route('/')
def index(): 
    # Página inicial pública
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        # Busca usuário e suas permissões de acesso
        usuario = execute_one(
            "SELECT u.*, f.nome AS funcao_nome, f.gerenciar_livros, f.gerenciar_usuarios, f.gerenciar_emprestimos FROM usuarios u INNER JOIN funcoes f ON u.funcao_id = f.id_funcao WHERE u.email = %s",
            (email,)
        )
        # Valida se a senha bate com o que está no banco
        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario'] = {
                'id': usuario['id_usuario'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'funcao': usuario['funcao_nome'],
                'gerenciar_livros': usuario['gerenciar_livros'],
                'gerenciar_usuarios': usuario['gerenciar_usuarios'],
                'gerenciar_emprestimos': usuario['gerenciar_emprestimos']
            }
            return redirect(url_for('home'))
        flash('E-mail ou senha inválidos.', 'danger')
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    # Limpa a sessão para deslogar o usuário
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home(): 
    # Página inicial do painel logado
    return render_template('dashboard/home.html')

# --- Módulo de Livros (Desenvolvido por Vitor) ---

@app.route('/livros/listar')
@login_required
def livros_listar():
    categoria_filtro = request.args.get('categoria')
    if categoria_filtro:
        # Filtra os livros por categoria se o usuário selecionou uma
        dados = execute_query("SELECT * FROM livros WHERE categoria = %s ORDER BY titulo", (categoria_filtro,), fetch=True)
    else:
        dados = execute_query("SELECT * FROM livros ORDER BY titulo", fetch=True)
    
    categorias = execute_query("SELECT DISTINCT categoria FROM livros", fetch=True)
    return render_template('dashboard/livros/listar.html', dados=dados, categorias=categorias)

@app.route('/livros/cadastrar', methods=['GET', 'POST'])
@login_required
def livros_cadastrar():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        isbn = request.form.get('isbn')
        categoria = request.form.get('categoria')
        # Insere o novo livro no acervo
        execute_query("INSERT INTO livros (titulo, autor, isbn, categoria) VALUES (%s, %s, %s, %s)", (titulo, autor, isbn, categoria))
        flash('Livro cadastrado com sucesso!', 'success')
        return redirect(url_for('livros_listar'))
    return render_template('dashboard/livros/form.html', modo='cadastrar')

@app.route('/livros/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def livros_editar(id):
    item = execute_one("SELECT * FROM livros WHERE id_livro = %s", (id,))
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        isbn = request.form.get('isbn')
        categoria = request.form.get('categoria')
        # Atualiza os dados do livro selecionado
        execute_query("UPDATE livros SET titulo=%s, autor=%s, isbn=%s, categoria=%s WHERE id_livro=%s", (titulo, autor, isbn, categoria, id))
        flash('Livro atualizado!', 'success')
        return redirect(url_for('livros_listar'))
    return render_template('dashboard/livros/form.html', modo='editar', item=item)

@app.route('/livros/excluir/<int:id>')
@login_required
def livros_excluir(id):
    # Remove o livro do banco de dados
    execute_query("DELETE FROM livros WHERE id_livro = %s", (id,))
    flash('Livro removido do acervo.', 'success')
    return redirect(url_for('livros_listar'))

# --- Módulo de Empréstimos (Desenvolvido por Rhian) ---

@app.route('/emprestimos/listar')
@login_required
def emprestimos_listar():
    # Busca os empréstimos ligando as tabelas de livros e usuários para mostrar os nomes
    sql = """
        SELECT e.*, l.titulo as livro_titulo, u.nome as usuario_nome 
        FROM emprestimos e 
        JOIN livros l ON e.livro_id = l.id_livro 
        JOIN usuarios u ON e.usuario_id = u.id_usuario
        ORDER BY e.data_retirada DESC
    """
    dados = execute_query(sql, fetch=True)
    return render_template('dashboard/emprestimos/listar.html', dados=dados)

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
@login_required
def emprestimos_novo():
    if request.method == 'POST':
        livro_id = request.form.get('livro_id')
        usuario_id = request.form.get('usuario_id')
        dias = int(request.form.get('dias', 7))
        data_prevista = datetime.now() + timedelta(days=dias)
        
        # Registra o empréstimo e muda o status do livro para 'Emprestado'
        execute_query("INSERT INTO emprestimos (livro_id, usuario_id, data_prevista_devolucao) VALUES (%s, %s, %s)", (livro_id, usuario_id, data_prevista))
        execute_query("UPDATE livros SET status = 'Emprestado' WHERE id_livro = %s", (livro_id,))
        flash('Empréstimo registrado com sucesso!', 'success')
        return redirect(url_for('emprestimos_listar'))
    
    # Busca apenas livros disponíveis e usuários ativos para o formulário
    livros = execute_query("SELECT * FROM livros WHERE status = 'Disponível'", fetch=True)
    usuarios = execute_query("SELECT * FROM usuarios WHERE status = 'Ativo'", fetch=True)
    return render_template('dashboard/emprestimos/form.html', livros=livros, usuarios=usuarios)

@app.route('/emprestimos/devolver/<int:id>')
@login_required
def emprestimos_devolver(id):
    emp = execute_one("SELECT * FROM emprestimos WHERE id_emprestimo = %s", (id,))
    if emp:
        # Marca como devolvido e libera o livro para um novo empréstimo
        execute_query("UPDATE emprestimos SET data_devolucao_real = %s, status = 'Devolvido' WHERE id_emprestimo = %s", (datetime.now(), id))
        execute_query("UPDATE livros SET status = 'Disponível' WHERE id_livro = %s", (emp['livro_id'],))
        flash('Devolução realizada!', 'success')
    return redirect(url_for('emprestimos_listar'))

# Roda o servidor se o arquivo for executado diretamente
if __name__ == "__main__":
    app.run(debug=True)
