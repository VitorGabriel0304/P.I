import mysql.connector
from mysql.connector import Error, pooling
import os

# Configurações de acesso ao banco de dados MySQL
_DB_PARAMS = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bibliocommunity',
    'charset': 'utf8mb4',
    'use_pure': True,
    'connection_timeout': 10,
    'autocommit': False,
}

# Variável para guardar o pool de conexões (melhora a performance)
_pool = None

# Função para criar o pool de conexões com o banco
def criar_pool():
    global _pool
    try:
        if _pool is None:
            _pool = pooling.MySQLConnectionPool(
                pool_name='webapp_pool',
                pool_size=5,
                pool_reset_session=True,
                **_DB_PARAMS
            )
            print('✓ Pool de conexões criado com sucesso!')
    except Error as e:
        print(f'✗ Erro ao criar pool: {e}')
        raise Exception(f'Não foi possível criar o pool de conexões: {e}')

# Função para pegar uma conexão livre do pool
def get_connection():
    try:
        if _pool is None:
            criar_pool()
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')

# Função genérica para executar comandos SQL (Insert, Update, Delete, Select)
def execute_query(sql, params=None, fetch=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True) # Retorna os dados como dicionário
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall() # Retorna todos os registros se for um SELECT
        else:
            conn.commit() # Salva as alterações se for INSERT/UPDATE/DELETE
            return cursor.rowcount
    except Error as e:
        conn.rollback() # Cancela as alterações em caso de erro
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        cursor.close()
        conn.close()

# Função para buscar apenas um único registro no banco
def execute_one(sql, params=None):
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None

# Função que cria o banco e as tabelas ao iniciar o sistema
def iniciar_bd():
    try:
        # Conecta no MySQL sem banco definido para poder criá-lo
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            charset='utf8mb4',
            use_pure=True
        )
        cursor = conn.cursor()
        
        # Abre o arquivo schema.sql e executa os comandos para criar as tabelas
        arquivo_sql = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()
            for stmt in script_sql.split(';'):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
        
        conn.commit()
        cursor.close()
        conn.close()
        print('✓ Banco de dados e tabelas inicializados com sucesso!')
        
        # Cria o pool de conexões agora que o banco já existe
        criar_pool()
        
    except Exception as e:
        print(f"✗ Erro ao inicializar o banco de dados: {e}")
        raise
