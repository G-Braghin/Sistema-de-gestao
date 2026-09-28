from src.database.conexao import Conexao
from src.entities.enums.tipo_movimentacao import TipoMovimentacao
from src.entities.movimentacao_estoque import MovimentacaoEstoque


class MovimentacaoRepository:
    def __init__(self, conexao: Conexao):
        self.conexao = conexao

    def criar(self, movimentacao: MovimentacaoEstoque):
        conn = self.conexao.get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO movimentacoes_estoque
            (id_produto,id_usuario,tipo,quantidade,data_hora)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id_movimentacao
            """,
                (
                    movimentacao.id_produto,
                    movimentacao.id_usuario,
                    movimentacao.tipo.value,
                    movimentacao.quantidade,
                    movimentacao.data_hora,
                ),
            )
            movimentacao.id_movimentacao = cursor.fetchone()[0]

        return movimentacao

    def buscar_por_id(self, id_movimentacao):
        conn = self.conexao.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_movimentacao,
            id_produto,id_usuario,tipo,quantidade,data_hora
            FROM movimentacoes_estoque
            where id_movimentacao = %s
            """,
                (id_movimentacao,),
            )
            row = cursor.fetchone()
        if row:
            return MovimentacaoEstoque(
                id_movimentacao=row[0],
                id_produto=row[1],
                id_usuario=row[2],
                tipo=TipoMovimentacao(row[3]),
                quantidade=row[4],
                data_hora=row[5],
            )
        return None

    def listar(self) -> list[MovimentacaoEstoque]:
        conn = self.conexao.get_connection()

        with conn.cursor() as cursor:
            cursor.execute("""   
                SELECT id_movimentacao,
                id_produto,id_usuario,tipo,quantidade,data_hora
                FROM movimentacoes_estoque
                ORDER by data_hora     
                """)
            rows = cursor.fetchall()

        return [
            MovimentacaoEstoque(
                id_movimentacao=row[0],
                id_produto=row[1],
                id_usuario=row[2],
                tipo=TipoMovimentacao(row[3]),
                quantidade=row[4],
                data_hora=row[5],
            )
            for row in rows
        ]
