class Produto:
    def __init__(self,nome,marca,preco,quantidade_estoque=0,id_produto=None):
        self.id_produto=id_produto
        self.nome = nome
        self.marca = marca
        self.preco=preco
        self.quantidade_estoque = quantidade_estoque

    def __str__(self):
        return f"Cliente(id_produto={self.id_produto}, nome={self.nome}, marca={self.marca}, preco={self.preco}, quantidade_estoque={self.quantidade_estoque})"
        