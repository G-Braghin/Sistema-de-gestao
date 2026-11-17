# Sistema de Gestão Empresarial

Sistema de gestão empresarial desenvolvido em Python, com API REST utilizando FastAPI, banco de dados PostgreSQL e arquitetura em camadas.

## Objetivo

Projeto desenvolvido para aplicar e aprimorar conhecimentos em desenvolvimento de software, utilizando práticas e ferramentas presentes no desenvolvimento de aplicações.

Principais objetivos de aprendizado:

- Python e programação orientada a objetos.
- Modelagem e gerenciamento de bancos de dados.
- SQL e ORM.
- Arquitetura em camadas.
- Desenvolvimento de APIs REST.
- Testes automatizados.
- Controle de versão com Git e GitHub.
- Desenvolvimento de aplicações web.

## Tecnologias

- **Linguagem:** Python 3.14.
- **Framework:** FastAPI.
- **Banco de dados:** PostgreSQL.
- **ORM:** SQLAlchemy.
- **Migrações:** Alembic.
- **Validação de dados:** Pydantic.
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
- API REST para disponibilização das funcionalidades do sistema.

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

### 2. Clonar o repositório e configurar o ambiente

Clone o repositório:

```bash
git clone https://github.com/G-Braghin/Sistema-de-Gestao.git
```

Acesse a pasta do projeto:

```bash
cd Sistema-de-Gestao
```

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
| `SENHA_PADRAO_FABRICA` | Senha utilizada na criação do administrador inicial. |
| `SECRET_KEY` | Chave secreta utilizada para assinar e validar os tokens de autenticação. |
| `ALGORITHM` | Algoritmo criptográfico utilizado na assinatura dos tokens. |
| `TEMPO_DE_EXPIRACAO_TOKEN` | Tempo de validade dos tokens, em minutos. |

Exemplo de configuração:

```env
# Banco de dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sistema_gestao
DB_USER=postgres
DB_PASSWORD=defina_a_senha_do_banco

DATABASE_URL=postgresql+psycopg://postgres:defina_a_senha_do_banco@localhost:5432/sistema_gestao

# Administrador inicial
SENHA_PADRAO_FABRICA=defina_a_senha_do_administrador

# Autenticação
SECRET_KEY=gere_uma_chave_secreta_segura
ALGORITHM=HS256
TEMPO_DE_EXPIRACAO_TOKEN=60
```

Ajuste os valores conforme sua configuração.

A senha do banco de dados e a senha inicial do administrador são configurações independentes.

A `SECRET_KEY` deve ser gerada aleatoriamente e mantida em segredo. O algoritmo e o tempo de expiração devem corresponder às configurações utilizadas pela aplicação.

Para gerar uma chave secreta segura para a autenticação, execute o seguinte comando:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o valor gerado e utilize-o na variável `SECRET_KEY` do arquivo `.env`.

**Importante:** não compartilhe essa chave nem a envie ao GitHub. Cada instalação deve utilizar sua própria chave secreta.

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

### 6. Criar o administrador inicial

Antes de utilizar o sistema, crie o primeiro administrador:

```bash
poetry run python scripts/criar_admin.py
```

O script verifica se já existe um administrador cadastrado e, caso não exista, cria o usuário inicial utilizando a senha definida em `SENHA_PADRAO_FABRICA`.

A senha configurada é utilizada somente na criação inicial do administrador. Alterá-la posteriormente não modifica a senha de um usuário já existente.

### 7. Iniciar a API

Execute a aplicação utilizando o Uvicorn:

```bash
poetry run uvicorn src.api.app:app --reload
```

Por padrão, a aplicação ficará disponível em:

- **API:** <http://127.0.0.1:8000>
- **Documentação interativa (Swagger UI):** <http://127.0.0.1:8000/docs>
- **Documentação alternativa (ReDoc):** <http://127.0.0.1:8000/redoc>

O parâmetro `--reload` habilita o recarregamento automático da aplicação durante o desenvolvimento.

## Próximos passos

O projeto continua em desenvolvimento, com foco na evolução da arquitetura e na disponibilização das funcionalidades por meio de uma aplicação web.

- [ ] **Interface web:** implementar uma interface para interação com as funcionalidades por meio do navegador.
- [ ] **Autenticação e autorização:** adaptar o sistema de autenticação e controle de permissões para o ambiente web.
- [ ] **Testes automatizados:** ampliar a cobertura de testes unitários e de integração, incluindo os endpoints da API.
- [ ] **Segurança:** aprimorar a proteção de dados, o gerenciamento de sessões e a validação de entradas.
- [ ] **Documentação:** documentar a arquitetura do sistema e os endpoints da API.
- [ ] **Deploy:** preparar a aplicação para execução em um ambiente de produção.
