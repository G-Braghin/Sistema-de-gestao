from src.entities.usuario import Usuario
from src.entities.enums.papel_usuario import PapelUsuario

class UsuarioRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    def buscar_por_id(self, id_usuario):
        conn = self.conexao.get_connection()
        try: 
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_usuario, 
                    nome, senha_hash, papel, ativo 
                    FROM usuarios 
                    WHERE id_usuario = %s
                    """, 
                    (id_usuario,)
                )
                row = cursor.fetchone()
            if row:
                return Usuario(
                    id_usuario=row[0], 
                    nome=row[1], 
                    senha_hash=row[2], 
                    papel=PapelUsuario(row[3]), 
                    ativo=row[4]
                )         
            return None
        except Exception:
            conn.rollback()
            raise

    def criar(self, usuario: Usuario):
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios
                    (nome, senha_hash, papel, ativo)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_usuario
                    """,
                    (
                        usuario.nome,
                        usuario.senha_hash,
                        usuario.papel.value,
                        usuario.ativo
                    )
                )
                usuario.id_usuario = cursor.fetchone()[0]
            conn.commit()
            return usuario
        except Exception:
            conn.rollback()
            raise

    def atualizar(self, usuario: Usuario):
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE usuarios 
                    SET nome = %s, senha_hash = %s, papel = %s, ativo = %s 
                    WHERE id_usuario = %s
                    """,
                    (
                        usuario.nome,
                        usuario.senha_hash,
                        usuario.papel.value,
                        usuario.ativo,
                        usuario.id_usuario
                    )
                )
                linhas_afetadas = cursor.rowcount
            conn.commit()
            if linhas_afetadas == 0:
                raise ValueError(f"Usuário com id {usuario.id_usuario} não encontrado.")
            return usuario
        except Exception:
            conn.rollback()
            raise
