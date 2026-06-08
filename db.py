import mysql.connector
from mysql.connector import Error, pooling
import os

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

_pool = None

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

def get_connection():
    try:
        if _pool is None:
            criar_pool()
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')

def execute_query(sql, params=None, fetch=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount
    except Error as e:
        conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        cursor.close()
        conn.close()

def execute_one(sql, params=None):
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None

def iniciar_bd():
    try:
        # Primeiro, conecta sem especificar banco para criar o banco
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            charset='utf8mb4',
            use_pure=True
        )
        cursor = conn.cursor()
        
        # Lê e executa o schema.sql
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
        
        # Agora cria o pool após o banco estar pronto
        criar_pool()
        
    except Exception as e:
        print(f"✗ Erro ao inicializar o banco de dados: {e}")
        raise
