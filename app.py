from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import execute_one, iniciar_bd, execute_query
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'biblio_secret_key_v2'

iniciar_bd()

# --- Lógica de Segurança (Padrão Professor) ---
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

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('usuario'):
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.context_processor
def injetar_usuario():
    return dict(usuario_logado=session.get('usuario'))

# --- Módulo Funções (Padrão Professor) ---
@app.route('/funcoes/listar')
@login_required
def funcoes_listar():
    dados = execute_query("SELECT * FROM funcoes ORDER BY nome", fetch=True)
    return render_template('dashboard/funcoes/listar.html', dados=dados)

@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
@login_required
def funcoes_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        gerenciar_livros = request.form.get('gerenciar_livros') == 'on'
        gerenciar_usuarios = request.form.get('gerenciar_usuarios') == 'on'
        gerenciar_emprestimos = request.form.get('gerenciar_emprestimos') == 'on'
        
        if not nome:
            flash('Nome da função é obrigatório!', 'danger')
            return redirect(url_for('funcoes_cadastrar'))
        
        try:
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
        
        if not nome:
            flash('Nome da função é obrigatório!', 'danger')
            return redirect(url_for('funcoes_editar', id=id))
        
        try:
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
        execute_query("DELETE FROM funcoes WHERE id_funcao = %s", (id,))
        flash('Função removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover função: {str(e)}', 'danger')
    return redirect(url_for('funcoes_listar'))

# --- Módulo Usuários (Padrão Professor) ---
@app.route('/usuarios/listar')
@login_required
def usuarios_listar():
    sql = "SELECT u.*, f.nome as funcao_nome FROM usuarios u INNER JOIN funcoes f ON u.funcao_id = f.id_funcao ORDER BY u.nome"
    dados = execute_query(sql, fetch=True)
    return render_template('dashboard/usuarios/listar.html', dados=dados)

@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
@login_required
def usuarios_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        email = request.form.get('email', '').strip()
        celular = request.form.get('celular', '').strip()
        estado = request.form.get('estado', '').strip()
        funcao_id = request.form.get('funcao_id')
        senha = request.form.get('senha', '').strip()
        confirma_senha = request.form.get('confirma_senha', '').strip()
        
        # Validações
        if not all([nome, cpf, email, celular, estado, funcao_id, senha]):
            flash('Todos os campos são obrigatórios!', 'danger')
            funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
            return render_template('dashboard/usuarios/form.html', modo='cadastrar', funcoes=funcoes)
        
        if senha != confirma_senha:
            flash('As senhas não conferem!', 'danger')
            funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
            return render_template('dashboard/usuarios/form.html', modo='cadastrar', funcoes=funcoes)
        
        if len(senha) < 6:
            flash('Senha deve ter no mínimo 6 caracteres!', 'danger')
            funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
            return render_template('dashboard/usuarios/form.html', modo='cadastrar', funcoes=funcoes)
        
        try:
            execute_query(
                "INSERT INTO usuarios (nome, cpf, email, celular, estado, senha, funcao_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (nome, cpf, email, celular, estado, generate_password_hash(senha), funcao_id)
            )
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('usuarios_listar'))
        except Exception as e:
            if 'Duplicate entry' in str(e):
                flash('E-mail ou CPF já cadastrado no sistema!', 'danger')
            else:
                flash(f'Erro ao cadastrar usuário: {str(e)}', 'danger')
            funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
            return render_template('dashboard/usuarios/form.html', modo='cadastrar', funcoes=funcoes)
    
    funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
    return render_template('dashboard/usuarios/form.html', modo='cadastrar', funcoes=funcoes)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def usuarios_editar(id):
    item = execute_one("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    if not item:
        flash('Usuário não encontrado!', 'warning')
        return redirect(url_for('usuarios_listar'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        email = request.form.get('email', '').strip()
        celular = request.form.get('celular', '').strip()
        estado = request.form.get('estado', '').strip()
        funcao_id = request.form.get('funcao_id')
        senha = request.form.get('senha', '').strip()
        
        if not all([nome, cpf, email, celular, estado, funcao_id]):
            flash('Todos os campos são obrigatórios!', 'danger')
            funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
            return render_template('dashboard/usuarios/form.html', modo='editar', item=item, funcoes=funcoes)
        
        try:
            if senha:
                if len(senha) < 6:
                    flash('Senha deve ter no mínimo 6 caracteres!', 'danger')
                    funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
                    return render_template('dashboard/usuarios/form.html', modo='editar', item=item, funcoes=funcoes)
                
                execute_query(
                    "UPDATE usuarios SET nome=%s, cpf=%s, email=%s, celular=%s, estado=%s, funcao_id=%s, senha=%s WHERE id_usuario=%s",
                    (nome, cpf, email, celular, estado, funcao_id, generate_password_hash(senha), id)
                )
            else:
                execute_query(
                    "UPDATE usuarios SET nome=%s, cpf=%s, email=%s, celular=%s, estado=%s, funcao_id=%s WHERE id_usuario=%s",
                    (nome, cpf, email, celular, estado, funcao_id, id)
                )
            
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('usuarios_listar'))
        except Exception as e:
            if 'Duplicate entry' in str(e):
                flash('E-mail ou CPF já cadastrado no sistema!', 'danger')
            else:
                flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
            funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
            return render_template('dashboard/usuarios/form.html', modo='editar', item=item, funcoes=funcoes)
    
    funcoes = execute_query("SELECT * FROM funcoes WHERE status = 'Ativo' ORDER BY nome", fetch=True)
    return render_template('dashboard/usuarios/form.html', modo='editar', item=item, funcoes=funcoes)

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def usuarios_excluir(id):
    try:
        execute_query("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        flash('Usuário removido com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover usuário: {str(e)}', 'danger')
    return redirect(url_for('usuarios_listar'))

# --- Rotas Públicas ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        usuario = execute_one(
            "SELECT u.*, f.nome AS funcao_nome, f.gerenciar_livros, f.gerenciar_usuarios, f.gerenciar_emprestimos FROM usuarios u INNER JOIN funcoes f ON u.funcao_id = f.id_funcao WHERE u.email = %s",
            (email,)
        )
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
    session.clear()
    return redirect(url_for('login'))

# --- Dashboard ---
@app.route('/home')
@login_required
def home(): return render_template('dashboard/home.html')

# --- Módulo Livros (Vitor - Lógica mesclada do Trabalho-Ronan) ---
@app.route('/livros/listar')
@login_required
def livros_listar():
    # Filtro por categoria (Lógica que estava no seu app.py original)
    categoria_filtro = request.args.get('categoria')
    if categoria_filtro:
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
        execute_query("UPDATE livros SET titulo=%s, autor=%s, isbn=%s, categoria=%s WHERE id_livro=%s", (titulo, autor, isbn, categoria, id))
        flash('Livro atualizado!', 'success')
        return redirect(url_for('livros_listar'))
    return render_template('dashboard/livros/form.html', modo='editar', item=item)

@app.route('/livros/excluir/<int:id>')
@login_required
def livros_excluir(id):
    execute_query("DELETE FROM livros WHERE id_livro = %s", (id,))
    flash('Livro removido do acervo.', 'success')
    return redirect(url_for('livros_listar'))

# --- Módulo Empréstimos (Rhian) ---
@app.route('/emprestimos/listar')
@login_required
def emprestimos_listar():
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
        
        execute_query("INSERT INTO emprestimos (livro_id, usuario_id, data_prevista_devolucao) VALUES (%s, %s, %s)", (livro_id, usuario_id, data_prevista))
        execute_query("UPDATE livros SET status = 'Emprestado' WHERE id_livro = %s", (livro_id,))
        flash('Empréstimo registrado com sucesso!', 'success')
        return redirect(url_for('emprestimos_listar'))
    
    livros = execute_query("SELECT * FROM livros WHERE status = 'Disponível'", fetch=True)
    usuarios = execute_query("SELECT * FROM usuarios WHERE status = 'Ativo'", fetch=True)
    return render_template('dashboard/emprestimos/form.html', livros=livros, usuarios=usuarios)

@app.route('/emprestimos/devolver/<int:id>')
@login_required
def emprestimos_devolver(id):
    emp = execute_one("SELECT * FROM emprestimos WHERE id_emprestimo = %s", (id,))
    if emp:
        execute_query("UPDATE emprestimos SET data_devolucao_real = %s, status = 'Devolvido' WHERE id_emprestimo = %s", (datetime.now(), id))
        execute_query("UPDATE livros SET status = 'Disponível' WHERE id_livro = %s", (emp['livro_id'],))
        flash('Devolução realizada!', 'success')
    return redirect(url_for('emprestimos_listar'))

if __name__ == "__main__":
    app.run(debug=True)
