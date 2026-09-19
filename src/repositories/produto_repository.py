from src.database.conexao import Conexao
from src.entities.produto import Produto


class ProdutoRepository:
    def __init__(self, conexao: Conexao):
        self.conexao = conexao

    def criar(self, produto: Produto) -> Produto:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO produtos
                    (nome,marca,preco,quantidade_estoque)
                    VALUES (%s,%s,%s,%s)
                    RETURNING id_produto
                    """,
                    (
                        produto.nome,
                        produto.marca,
                        produto.preco,
                        produto.quantidade_estoque,
                    ),
                )
                produto.id_produto = cursor.fetchone()[0]
            conn.commit()
            return produto
        except Exception:
            conn.rollback()
            raise

    def buscar_por_id(self, id_produto: int) -> Produto:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_produto,
                    nome, marca, preco, quantidade_estoque
                    FROM produtos
                    WHERE id_produto = %s
                    """,
                    (id_produto,),
                )
                row = cursor.fetchone()
            if row:
                return Produto(
                    id_produto=row[0],
                    nome=row[1],
                    marca=row[2],
                    preco=row[3],
                    quantidade_estoque=row[4],
                )
            return None
        except Exception:
            conn.rollback()
            raise

    def listar(self) -> list[Produto]:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(""" 
                    SELECT id_produto,
                    nome, marca, preco, quantidade_estoque
                    FROM produtos
                    ORDER BY nome
                    """)
                rows = cursor.fetchall()

            return [
                Produto(
                    id_produto=row[0],
                    nome=row[1],
                    marca=row[2],
                    preco=row[3],
                    quantidade_estoque=row[4],
                )
                for row in rows
            ]
        except Exception:
            conn.rollback()
            raise

    def atualizar(self, produto: Produto) -> Produto:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE produtos
                    SET nome = %s, marca = %s, preco = %s, quantidade_estoque = %s
                    WHERE id_produto = %s
                    """,
                    (
                        produto.nome,
                        produto.marca,
                        produto.preco,
                        produto.quantidade_estoque,
                        produto.id_produto,
                    ),
                )
                linhas_afetadas = cursor.rowcount
            conn.commit()
            if linhas_afetadas == 0:
                raise ValueError(f"Produto com id {produto.id_produto} nao encontrado.")
            return produto
        except Exception:
            conn.rollback()
            raise
