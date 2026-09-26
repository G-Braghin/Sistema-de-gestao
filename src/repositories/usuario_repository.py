from src.database.conexao import Conexao
from src.entities.dtos.usuario_resumo import UsuarioResumo
from src.entities.enums.papel_usuario import PapelUsuario
from src.entities.usuario import Usuario


class UsuarioRepository:
    def __init__(self, conexao: Conexao):
        self.conexao = conexao

    # Sugestão: indicar Usuario | None no retorno, pois a busca pode não encontrar um usuário.
    def buscar_por_id(self, id_usuario: int) -> Usuario:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_usuario, nome, senha_hash, papel, ativo 
                    FROM usuarios 
                    WHERE id_usuario = %s
                    """,
                    (id_usuario,),
                )
                row = cursor.fetchone()
            if row:
                return Usuario(
                    id_usuario=row[0],
                    nome=row[1],
                    senha_hash=row[2],
                    papel=PapelUsuario(row[3]),
                    ativo=row[4],
                )
            return None
        except Exception:
            conn.rollback()
            raise

    def criar(self, usuario: Usuario) -> Usuario:
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
                        usuario.ativo,
                    ),
                )
                usuario.id_usuario = cursor.fetchone()[0]
            conn.commit()
            return usuario
        except Exception:
            conn.rollback()
            raise

    def atualizar(self, usuario: Usuario) -> Usuario:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE usuarios 
                    SET nome = %s, 
                        senha_hash = %s, 
                        papel = %s, 
                        ativo = %s 
                    WHERE id_usuario = %s
                    """,
                    (
                        usuario.nome,
                        usuario.senha_hash,
                        usuario.papel.value,
                        usuario.ativo,
                        usuario.id_usuario,
                    ),
                )
                linhas_afetadas = cursor.rowcount
            conn.commit()
            if linhas_afetadas == 0:
                raise ValueError(f"Usuário com id {usuario.id_usuario} não encontrado.")
            return usuario
        except Exception:
            conn.rollback()
            raise

    def existe_usuario(self):
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT EXISTS (SELECT 1 FROM usuarios)")
                (existe,) = cursor.fetchone()
            return existe
        except Exception:
            conn.rollback()
            raise

    def listar(self, status_ativo: bool = True) -> list[UsuarioResumo]:
        conn = self.conexao.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                SELECT id_usuario, nome, papel, ativo
                FROM usuarios
                WHERE ativo = %s
                ORDER BY 
                    CASE papel
                        WHEN 'Administrador' THEN 1
                        WHEN 'Gerente' THEN 2
                        WHEN 'Funcionario' THEN 3
                        ELSE 4
                    END,
                    nome ASC 
                """,
                    (status_ativo,),
                )
                rows = cursor.fetchall()

            return [
                UsuarioResumo(
                    id_usuario=row[0],
                    nome=row[1],
                    papel=PapelUsuario(row[2]),
                    ativo=row[3],
                )
                for row in rows
            ]
        except Exception:
            conn.rollback()
            raise
