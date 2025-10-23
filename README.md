# Sistema de Gestão - Django

Aplicação desenvolvida em **[Django](https://docs.djangoproject.com/en/stable/)** para gerenciamento interno de usuarios, autentiação e registro de logs de ação no sistema, contando também com gerenciamento de estoque e modulo de entrada e saida de produtos.

O projeto foi construído seguindo boas práticas de arquitetura com **[Class-Based Views (CBV)](https://docs.djangoproject.com/en/5.2/topics/class-based-views/)**, **[tratamento de exceções](https://docs.djangoproject.com/en/5.2/ref/exceptions/)**, **[type hints](https://peps.python.org/pep-0484/)**, e **[documentação padrão Docstring](https://peps.python.org/pep-0257/)** nos métodos.


## Funcionalidades
* **Autenticação de usuários** – Login e logout com tratamento de erros.
* **CRUD de usuários** – com proteção ao superusuário mestre.
* **Proteção de rotas** - usando a classe `LoginRequiredMixin`.
* **Registro de logs** - Cada ação importante é armazenada no banco via `LogSystem`.
* **Organização em camadas** - Uso de **Class-Based Views** (`View`, `LoginRequiredMixin`).
Estrutura modular (`core`, `user`, `estoque`.).

## Stack e Dependências

| Categoria                 | Tecnologia / Lib                                                                     |
|---------------------------|---------------------------------------------------------------------------------------|
| Linguagem & Frameworks    | **[Python 3.13](https://docs.python.org/pt-br/3.13/contents.html)**, **[Django 5.2.7](https://docs.djangoproject.com/pt-br/5.2/)**                         |
| Banco de dados          | **[PostgreSQL](https://www.postgresql.org/docs/)** via      **[psycopg2 2.9.11](https://www.psycopg.org/docs/)**                                             |
| Manipulação de Imagens             | **[Pillow 12.0.0](https://pillow.readthedocs.io/en/stable/)**                                                                           |
| Configuração(variáveis de ambiente)              | **[python-decouple 3.8](https://pypi.org/project/python-decouple/)**, **[python-dotenv 1.1.1](https://pypi.org/project/python-dotenv/)**                                           |
| Ambiente replicável       | **[Docker](https://docs.docker.com/)**                                               |

## Visão geral da estrutura de diretórios

```
SISTEMA_DE_GESTAO/
├── .venv/                             # Ambiente virtual Python
│
├── core/                              # App principal - páginas e layout base do sistema
│   ├── migrations/                    # Arquivos de migração do banco de dados
│   ├── templates/core/                # Templates HTML principais
│   │   ├── home.html                  # Página inicial
│   │   ├── login.html                 # Página de login
│   │   ├── model-footer.html          # Rodapé padrão
│   │   ├── model-header.html          # Cabeçalho padrão
│   │   └── model-page.html            # Estrutura base de layout
│   ├── __init__.py
│   ├── admin.py                       # Registro de modelos no Django Admin
│   ├── apps.py                        # Configurações do app
│   ├── models.py                      # Modelos principais
│   ├── tests.py                       # Testes automatizados
│   ├── urls.py                        # Rotas e URLs do app
│   └── views.py                       # Lógica de controle (renderização das páginas)
│
├── estoque/                           # App responsável pela gestão de produtos e movimentações
│   ├── migrations/                    # Migrações do banco de dados
│   ├── templates/estoque/             # Templates HTML do módulo de estoque
│   │   ├── detalhe_produto.html       # Detalhes de um produto
│   │   ├── listar.html                # Lista todos os produtos
│   │   ├── produtos_form.html         # Formulário de cadastro/edição de produtos
│   │   └── movimentacoes/             # Subpasta para movimentações de estoque
│   │       ├── form.html              # Formulário de movimentação
│   │       └── listar_movimentacao.html# Listagem de movimentações
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                      # Modelos de Produto e Movimentação
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── project/                           # Pasta principal do projeto Django (configurações globais)
│   ├── __pycache__/                   # Cache interno do Python
│   ├── __init__.py
│   ├── asgi.py                        
│   ├── settings.py                    # Configurações principais do projeto
│   ├── urls.py                        # URLs globais do sistema
│   └── wsgi.py                        
│
├── user/                              # App responsável pela gestão de usuários
│   ├── migrations/
│   ├── templates/user/                # Templates HTML relacionados aos usuários
│   │   ├── confirmacao_reset_senha.html# Confirmação de redefinição de senha
│   │   ├── listar.html                # Listagem de usuários
│   │   ├── pedido_reset_senha.html    # Solicitação de redefinição de senha
│   │   └── usuarios_form.html         # Formulário de cadastro/edição de usuário
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                      # Modelos de usuário 
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore                         # Arquivos e pastas ignorados pelo Git
├── manage.py                          # Comando principal para gerenciar o projeto Django
└── README.md                          # Documentação do projeto
```

## Variáveis de Ambiente

Crie um arquivo `.env` segundo o arquivo `.env.example`:

| Variável          | Descrição                                                        | Exemplo            |
|-------------------|------------------------------------------------------------------|--------------------|
| `DEBUG`           | `True` em dev, `False` em produção                               | `True`             |
| `SECRET_KEY`      | Chave secreta do Django                                          | `SECRET_KEY` |
| `ALLOWED_HOSTS`   | Hosts permitidos                                                 | `'*' Todos` |
| `EMAIL_HOST_USER`       | E-mail usado no SMTP                                | `admin@admin.com`            |
| `EMAIL_HOST_PASSWORD`  | Senha do e-mail                                            | `senha do e-mail`       |
| `DB_NAME`         | Nome do banco                                                  | `estoque_db`         |
| `DB_USER`         | Usuário do banco                                               | `admin`         |
| `DB_PASSWORD`     | Senha do banco                                                 | `admin`         |
| `DB_HOST`         | Host/IP do banco                                               | `localhost`        |
| `DB_PORT`         | Porta (padrão 5432)                                          | `5432`             |

Observação: O nome do container **postgres** é o host interno dentro da rede Docker.
## Instalação e Execução

Certifique-se de ter as dependências do sistema instaladas, como **Python 3.11** e **PostgreSQL**.

```bash
$ sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip
```
Clone este repositório com o git **ou** baixe o `.zip` e extraia-o.

Em um terminal, navegue até a pasta do projeto e prossiga com uma das opções abaixo.

### Ambiente virtual

```bash
# Ambiente virtual
    $ python3.11 -m venv venv
    $ source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Dependências Python
    $ pip install --upgrade pip
    $ pip install -r requirements.txt

# Banco de dados & migrations
    $ python manage.py makemigrations /$ python manage.py migrate

# Run!
    $ python manage.py runserver
```



### Instalar e configurar Docker

```bash
# Instalação e configuração Docker
    $ sudo apt-get update
    $ sudo apt-get install ca-certificates curl
    $ sudo install -m 0755 -d /etc/apt/keyrings
    $ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc

# Adicionar repositorios do Docker
    $ echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu   $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    $ sudo apt-get update

# Instalar Docker e plugins necessários
    $ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Iniciar serviço
    $ sudo systemctl start docker
```
A aplicação estará disponível em `http://localhost:8080/`.
```
http://localhost:8080/
````

## Container PostgreSQL com PgAdmin
```
# Criar Rede e volumes 
    $ docker network create pg_net
    $ docker volume create pg_data
    $ docker volume create pgadmin_data

# Container PostgreSQL
    $ docker run -d --name postgres --network pg_net -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=estoque_db -v pg_data:/var/lib/postgresql/data -p 5432:5432 postgres:17

# Container PgAdmin
    $ docker run -d --name pgadmin --network pg_net -e PGADMIN_DEFAULT_EMAIL=admin@admin.com -e PGADMIN_DEFAULT_PASSWORD=admin -v pgadmin_data:/var/lib/pgadmin -p 5050:80 dpage/pgadmin4
```

