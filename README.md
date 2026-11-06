# Sistema de Gestão Empresarial

Sistema de gestão empresarial desenvolvido em Python, com banco de dados PostgreSQL e arquitetura em camadas.

## Objetivo

Projeto desenvolvido para aplicar e aprimorar conhecimentos em desenvolvimento de software, utilizando práticas e ferramentas presentes no desenvolvimento de aplicações.

Principais objetivos de aprendizado:

- Python e programação orientada a objetos.
- Modelagem e gerenciamento de bancos de dados.
- SQL e ORM.
- Arquitetura em camadas.
- Testes automatizados.
- Controle de versão com Git e GitHub.
- Desenvolvimento de APIs e aplicações web.

## Tecnologias

- **Linguagem:** Python 3.14.
- **Banco de dados:** PostgreSQL.
- **ORM:** SQLAlchemy.
- **Migrações:** Alembic.
- **Testes:** Pytest.
- **Gerenciamento de dependências:** Poetry.
- **Containerização:** Docker e Docker Compose.
- **Versionamento:** Git e GitHub.

## Funcionalidades

- Gerenciamento de usuários e controle de permissões.
- Cadastro e gerenciamento de clientes.
- Cadastro e gerenciamento de produtos.
- Controle de estoque e movimentações.
- Registro e cancelamento de vendas.
- Relatórios de vendas e produtos mais vendidos.
- Exportação de relatórios em CSV.

## Como executar

Os comandos abaixo devem ser executados na raiz do projeto.

### 1. Pré-requisitos

Antes de executar o projeto, instale as seguintes ferramentas:

| Ferramenta | Finalidade | Instalação |
| --- | --- | --- |
| Python 3.14 | Interpretador da aplicação. | [Download](https://www.python.org/downloads/) |
| Poetry | Gerenciamento de dependências e ambiente virtual. | [Instalação](https://python-poetry.org/docs/#installation) |
| Docker | Execução do PostgreSQL em container. | [Instalação](https://docs.docker.com/get-docker/) |
| Docker Compose | Gerenciamento dos containers. | [Documentação](https://docs.docker.com/compose/install/) |

**Observações:**

- O Docker Compose já está incluído no Docker Desktop. No Linux, ele pode ser instalado como plugin do Docker Engine.
- No Linux, o Docker precisa estar instalado e em execução, com permissões adequadas para executar os comandos sem `sudo`, caso essa seja sua configuração.

### 2. Configurar o ambiente

Clone o repositório e acesse a pasta do projeto.

Instale as dependências:

```bash
poetry install
```

### 3. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Configure as variáveis no arquivo `.env`:

| Variável | Finalidade |
| --- | --- |
| `DB_HOST` | Endereço do PostgreSQL. |
| `DB_PORT` | Porta de conexão do PostgreSQL. |
| `DB_NAME` | Nome do banco de dados. |
| `DB_USER` | Usuário do PostgreSQL. |
| `DB_PASSWORD` | Senha do usuário do PostgreSQL. |
| `DATABASE_URL` | URL de conexão utilizada pelo SQLAlchemy. |
| `SENHA_PADRAO_FABRICA` | Senha do administrador inicial do sistema. |

Exemplo de configuração:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sistema_gestao
DB_USER=postgres
DB_PASSWORD=defina_a_senha_do_banco

DATABASE_URL=postgresql+psycopg://postgres:defina_a_senha_do_banco@localhost:5432/sistema_gestao

SENHA_PADRAO_FABRICA=defina_a_senha_do_administrador
```

Ajuste os valores conforme sua configuração.

A senha do banco de dados e a senha inicial do administrador são configurações independentes.

**Importante:** o arquivo `.env` contém configurações locais e não deve ser compartilhado ou enviado ao GitHub. Utilize apenas o `.env.example` para documentar as variáveis necessárias.

### 4. Iniciar o banco de dados

Com o Docker em execução, utilize o Docker Compose para iniciar o container do PostgreSQL:

```bash
docker compose up -d
```

Para verificar se o container está em execução:

```bash
docker compose ps
```

### 5. Executar as migrações

Com o banco de dados disponível, execute as migrações do Alembic para criar e atualizar a estrutura do banco:

```bash
poetry run alembic upgrade head
```

As migrações são responsáveis por manter a estrutura do banco de dados sincronizada com os modelos da aplicação.

Não é necessário criar as tabelas manualmente.

### 6. Iniciar o sistema

Execute a aplicação:

```bash
poetry run python -m src.main
```

Na primeira execução, caso ainda não exista nenhum usuário cadastrado, o sistema cria automaticamente um administrador inicial.

O acesso é realizado utilizando o ID apresentado pelo sistema e a senha definida em `SENHA_PADRAO_FABRICA`.

Caso essa variável não esteja configurada, a implementação atual utiliza `admin123` como senha padrão.

Essa configuração é utilizada somente na criação inicial do administrador. Alterá-la posteriormente não modifica a senha de um usuário já existente.

## Próximos passos

O projeto continua em desenvolvimento, com foco na evolução da arquitetura e na disponibilização das funcionalidades por meio de uma aplicação web.

- [ ] **API REST:** desenvolver uma API utilizando FastAPI.
- [ ] **Interface web:** implementar uma interface para interação com as funcionalidades por meio do navegador.
- [ ] **Autenticação e autorização:** adaptar o sistema de autenticação e controle de permissões para o ambiente web.
- [ ] **Testes automatizados:** ampliar a cobertura de testes unitários e de integração, incluindo os endpoints da API.
- [ ] **Segurança:** aprimorar a proteção de dados, o gerenciamento de sessões e a validação de entradas.
- [ ] **Documentação:** documentar a arquitetura do sistema e os endpoints da API.
- [ ] **Deploy:** preparar a aplicação para execução em um ambiente de produção.
