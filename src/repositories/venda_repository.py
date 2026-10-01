from datetime import datetime

from src.database.conexao import Conexao
from src.entities.dtos.venda_resumo import VendaResumo
from src.entities.enums.status_venda import StatusVenda
from src.entities.venda import Venda
from src.entities.venda_item import VendaItem


class VendaRepository:
    def __init__(self, conexao: Conexao):
        self.conexao = conexao

    def criar(self, venda: Venda):
        conn = self.conexao.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vendas
                (id_cliente,id_usuario,preco_total,data_hora,status)
                VALUES (%s, %s, %s, %s , %s)
                RETURNING id_venda
                """,
                (
                    venda.id_cliente,
                    venda.id_usuario,
                    venda.preco_total,
                    venda.data_hora,
                    venda.status.value,
                ),
            )
            venda.id_venda = cursor.fetchone()[0]

            for item in venda.itens:
                cursor.execute(
                    """
                INSERT INTO venda_itens
                (id_venda,id_produto,nome_produto,quantidade,preco_unitario)
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id_venda_item
                """,
                    (
                        venda.id_venda,
                        item.id_produto,
                        item.nome_produto,
                        item.quantidade,
                        item.preco_unitario,
                    ),
                )
                item.id_venda_item = cursor.fetchone()[0]
                item.id_venda = venda.id_venda

        return venda

    def buscar_por_id(self, id_venda: int):
        conn = self.conexao.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_venda, id_cliente, id_usuario,preco_total,
            data_hora,status,data_cancelamento,id_usuario_cancelamento
            FROM vendas
            WHERE id_venda = %s    
            """,
                (id_venda,),
            )
            venda_data = cursor.fetchone()

            if venda_data is None:
                return None

            venda = Venda(
                id_venda=venda_data[0],
                id_cliente=venda_data[1],
                id_usuario=venda_data[2],
                preco_total=venda_data[3],
                data_hora=venda_data[4],
                status=StatusVenda(venda_data[5]),
                data_cancelamento=venda_data[6],
                id_usuario_cancelamento=venda_data[7],
                itens=[],
            )

            cursor.execute(
                """
                SELECT id_venda_item,id_venda,id_produto,
                nome_produto,quantidade,preco_unitario
                FROM venda_itens
                WHERE id_venda = %s
                """,
                (id_venda,),
            )
            itens = cursor.fetchall()

            venda.itens = [
                VendaItem(
                    id_venda_item=item[0],
                    id_venda=id_venda,
                    id_produto=item[2],
                    nome_produto=item[3],
                    quantidade=item[4],
                    preco_unitario=item[5],
                )
                for item in itens
            ]

            return venda

    def listar_resumo(
        self, venda_status: StatusVenda | None = None
    ) -> list[VendaResumo]:
        conn = self.conexao.get_connection()
        with conn.cursor() as cursor:
            sql = """ 
                SELECT vendas.id_venda, 
                clientes.nome AS nome_cliente,
                usuarios.nome AS nome_usuario,
                vendas.data_hora, 
                vendas.preco_total,
                vendas.status
                FROM vendas
                INNER JOIN clientes ON vendas.id_cliente = clientes.id_cliente
                INNER JOIN usuarios ON vendas.id_usuario = usuarios.id_usuario
            """
            params = []

            if venda_status is not None:
                sql += " WHERE vendas.status = %s"
                params.append(venda_status.value)

            sql += " ORDER BY vendas.data_hora DESC"

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

            return [
                VendaResumo(
                    id_venda=row[0],
                    nome_cliente=row[1],
                    nome_vendedor=row[2],
                    data_venda=row[3],
                    valor_total=row[4],
                    status=StatusVenda(row[5]),
                )
                for row in rows
            ]

    def cancelar_venda(
        self, id_venda: int, data_cancelamento: datetime, id_usuario_cancelamento: int
    ):
        conn = self.conexao.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
            UPDATE vendas
            SET status = %s, data_cancelamento = %s, id_usuario_cancelamento = %s
            WHERE id_venda = %s AND status = %s
            """,
                (
                    StatusVenda.CANCELADO.value,
                    data_cancelamento,
                    id_usuario_cancelamento,
                    id_venda,
                    StatusVenda.CONCLUIDO.value,  # vai verificar se a compra esta concluida.
                ),
            )
            linhas_afetadas = cursor.rowcount

        if linhas_afetadas == 0:
            raise ValueError(
                f"Venda com id {id_venda} nao encontrada ou ja esta Cancelada."
            )
