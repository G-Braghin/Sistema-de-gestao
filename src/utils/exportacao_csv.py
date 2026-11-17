import csv
from io import StringIO


def exportar_resumo_vendas_csv(relatorio):
    arquivo = StringIO()
    escritor = csv.writer(arquivo, delimiter=';')

    escritor.writerow([
        'Data inicial',
        'Data final',
        'Vendas concluidas',
        'Valor total',
        'Ticket medio',
    ])

    escritor.writerow([
        relatorio.data_inicial.strftime('%d/%m/%Y'),
        relatorio.data_final.strftime('%d/%m/%Y'),
        relatorio.vendas_concluidas,
        f'{relatorio.total_periodo:.2f}'.replace('.', ','),
        f'{relatorio.ticket_medio:.2f}'.replace('.', ','),
    ])

    return arquivo.getvalue()


def exportar_produtos_vendidos_csv(produtos):
    arquivo = StringIO()
    escritor = csv.writer(arquivo, delimiter=';')

    escritor.writerow([
        'ID do produto',
        'Nome',
        'Quantidade vendida',
        'Valor total',
    ])

    for produto in produtos:
        escritor.writerow([
            produto.id_produto,
            produto.nome_produto,
            produto.quantidade_vendida,
            f'{produto.valor_total:.2f}'.replace('.', ','),
        ])

    return arquivo.getvalue()


def exportar_estoque_csv(relatorio):
    arquivo = StringIO()
    escritor = csv.writer(arquivo, delimiter=';')

    escritor.writerow([
        'ID do produto',
        'Nome',
        'Quantidade em estoque',
    ])

    for produto in relatorio.produtos:
        escritor.writerow([
            produto.id,
            produto.nome,
            produto.quantidade,
        ])

    return arquivo.getvalue()
