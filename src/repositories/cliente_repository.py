from src.database.conexao import Conexao
from src.entities.cliente import Cliente


class ClienteRepository:
    def __init__(self, conexao: Conexao):
        self.conexao = conexao

    def buscar_por_id(self, id_cliente: int) -> Cliente:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_cliente, 
                    nome, cpf, telefone, endereco 
                    FROM clientes 
                    WHERE id_cliente = %s
                    """,
                    (id_cliente,),
                )
                row = cursor.fetchone()
            if row:
                return Cliente(
                    id_cliente=row[0],
                    nome=row[1],
                    cpf=row[2],
                    telefone=row[3],
                    endereco=row[4],
                )
            return None
        except Exception:
            conn.rollback()
            raise

    def buscar_por_cpf(self, cpf: str) -> Cliente:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_cliente,
                    nome,cpf,telefone,endereco
                    FROM clientes
                    WHERE cpf = %s
                    """,
                    (cpf,),
                )
                row = cursor.fetchone()
            if row:
                return Cliente(
                    id_cliente=row[0],
                    nome=row[1],
                    cpf=row[2],
                    telefone=row[3],
                    endereco=row[4],
                )
            return None
        except Exception:
            conn.rollback()
            raise

    def criar(self, cliente: Cliente) -> Cliente:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO clientes
                    (nome,cpf,telefone,endereco)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_cliente
                    """,
                    (cliente.nome, cliente.cpf, cliente.telefone, cliente.endereco),
                )
                cliente.id_cliente = cursor.fetchone()[0]
            conn.commit()
            return cliente
        except Exception:
            conn.rollback()
            raise

    def atualizar(self, cliente: Cliente) -> Cliente:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE clientes 
                    SET nome = %s, cpf = %s, telefone = %s, endereco = %s 
                    WHERE id_cliente = %s
                    """,
                    (
                        cliente.nome,
                        cliente.cpf,
                        cliente.telefone,
                        cliente.endereco,
                        cliente.id_cliente,
                    ),
                )
                linhas_afetadas = cursor.rowcount
            conn.commit()
            if linhas_afetadas == 0:
                raise ValueError(f"Cliente com id {cliente.id_cliente} não encontrado.")
            return cliente
        except Exception:
            conn.rollback()
            raise
