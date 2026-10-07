# Sistema de Gestão

Sistema de gestão empresarial desenvolvido em Python.

## Objetivo

Projeto desenvolvido para praticar:

- Python
- Programação orientada a objetos
- Banco de dados
- SQL
- Arquitetura em camadas
- Testes automatizados
- Git e GitHub

## Tecnologias

- Python
- PostgreSQL
- Pytest
- Git
- GitHub

## Como executar

Os comandos abaixo usam PowerShell e devem ser executados na raiz do projeto.

### 1. Preparar o ambiente

Instale Python e PostgreSQL e mantenha o serviço do PostgreSQL em execução.
O ambiente de desenvolvimento utiliza Python 3.14.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual, sem precisar ativá-lo.

### 2. Criar o banco de dados

No pgAdmin, crie um banco vazio chamado `sistema_gestao`. Abra o Query Tool
desse banco, carregue o arquivo `sql/schema.sql` e execute seu conteúdo.

O script cria as seis tabelas do sistema. Ele deve ser executado uma vez em um
banco vazio e não atualiza tabelas existentes.

### 3. Configurar o ambiente

Copie o arquivo de exemplo, caso ainda não tenha um `.env`:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` com os dados da sua instalação:

| Variável | Finalidade |
| --- | --- |
| `DB_HOST` | Endereço do PostgreSQL; use `localhost` para instalação local. |
| `DB_PORT` | Porta do PostgreSQL, normalmente `5432`. |
| `DB_NAME` | Nome do banco criado na etapa anterior. |
| `DB_USER` | Usuário do PostgreSQL. |
| `DB_PASSWORD` | Senha desse usuário do PostgreSQL. |
| `SENHA_PADRAO_FABRICA` | Senha do administrador inicial do sistema. |

Substitua os valores de exemplo antes de iniciar. A senha do banco e a senha
do administrador do sistema são configurações diferentes.

O `.env` contém suas configurações locais e já está ignorado pelo Git.
Compartilhe somente o `.env.example`, sem credenciais reais.

### 4. Iniciar o sistema

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Quando não existe nenhum usuário cadastrado, o sistema cria o usuário `admin`
com o papel de administrador e mostra seu ID de acesso. Entre com esse ID e
com a senha definida em `SENHA_PADRAO_FABRICA`.

Essa variável é usada somente na criação inicial. Alterá-la depois não muda
a senha de um usuário já cadastrado. Para mudar sua senha, use a opção
**Perfil > Trocar senha**.

Na implementação atual, se a variável estiver ausente, a senha inicial será
`admin123`. Configure uma senha própria no `.env` antes da primeira execução.

### Conferência da instalação

Em um banco separado para testes, confira o fluxo inicial:

1. Iniciar o sistema e entrar com o administrador criado.
2. Cadastrar um cliente e um produto.
3. Registrar uma entrada de estoque.
4. Realizar uma venda e conferir o saldo do produto.
5. Cancelar a venda e conferir a devolução das unidades ao estoque.
6. Consultar os relatórios e exportar um CSV.

Faça essa conferência sem usar dados reais. Os CSVs são salvos na pasta em que
o programa foi iniciado e não precisam ser incluídos nos commits.
