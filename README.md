# Contbem CRM

Sistema de CRM (Customer Relationship Management) desenvolvido em Flask para gerenciamento de entidades, pessoas, eventos e ações de relacionamento.

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Uso](#uso)
- [Deploy](#deploy)

## Visão Geral

O Contbem CRM é uma aplicação web para gerenciar relacionamentos com clientes e parceiros. O sistema permite o cadastro de entidades (empresas/organizações), pessoas de contato, eventos de interação e ações de follow-up.

## Funcionalidades

### Autenticação e Usuários
- **Login seguro** com senha criptografada
- **Gerenciamento de usuários** (apenas para administradores)
- **Alteração de senha** para usuários autenticados
- **Controle de acesso** por sessão

### Gestão de Entidades
- **CRUD completo** de entidades (empresas/organizações)
- Campos: nome, descrição, endereço, telefone, email, URL
- **Visualização detalhada** de cada entidade com:
  - Eventos relacionados
  - Ações pendentes/concluídas
- **Filtros e busca** por nome

### Gestão de Pessoas
- **CRUD completo** de pessoas de contato
- Campos: nome, email, telefone, cargo, entidade vinculada
- **Filtros avançados**:
  - Por entidade
  - Busca por nome
- Relacionamento obrigatório com entidade

### Gestão de Eventos
- **CRUD completo** de eventos/interações
- Campos: título, descrição, data, tipo, entidade, pessoa (opcional)
- **Filtros**:
  - Por entidade
  - Busca por nome da entidade
- Ordenação por data (mais recentes primeiro)
- Vinculação opcional com pessoa de contato

### Gestão de Ações
- **CRUD completo** de ações de follow-up
- Campos: título, descrição, status, prioridade, data de vencimento, entidade
- Status: pendente, em andamento, concluído
- Prioridade: baixa, média, alta
- Ordenação por data de vencimento

### Interface
- Design responsivo com **Bootstrap 5.3.3**
- **Ícones SVG** para ações (editar, deletar, detalhes)
- Logo centralizado e navegação intuitiva
- Mensagens flash para feedback de operações
- Interface em **Português Brasileiro**

## Tecnologias

### Backend
- **Python 3.x**
- **Flask** - Framework web
- **Supabase** - Backend as a Service (PostgreSQL)
- **Werkzeug** - Utilitários WSGI e hash de senhas
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **Gunicorn** - WSGI HTTP Server (produção)

### Frontend
- **HTML5/CSS3**
- **Bootstrap 5.3.3** - Framework CSS
- **Jinja2** - Template engine

### Banco de Dados
- **PostgreSQL** via Supabase
- Relacionamentos com integridade referencial
- Triggers automáticos para timestamps

## Instalação

### Pré-requisitos
- Python 3.8+
- Conta no Supabase
- Git

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd contbem
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados**
- Acesse seu projeto no Supabase
- Execute o script `database.sql` no SQL Editor do Supabase
- Isso criará todas as tabelas, índices e triggers necessários

5. **Configure as variáveis de ambiente**
Crie um arquivo `.env` na raiz do projeto:
```env
SUPABASE_URL=sua-url-do-supabase
SUPABASE_KEY=sua-chave-do-supabase
ADMIN_EMAIL=seu-email@exemplo.com
```

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `SUPABASE_URL` | URL do projeto Supabase | Sim |
| `SUPABASE_KEY` | Chave de API do Supabase | Sim |
| `ADMIN_EMAIL` | Email do usuário administrador | Sim |

### Primeiro Acesso

1. Execute o aplicativo localmente:
```bash
python app.py
```

2. Acesse `http://localhost:5000`

3. **Importante**: Para criar o primeiro usuário administrador, você precisa inserir diretamente no banco de dados via Supabase:
```sql
INSERT INTO users (name, email, password)
VALUES ('Seu Nome', 'seu-email@exemplo.com', 'senha-hash');
```

Você pode gerar o hash da senha com Python:
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('sua-senha'))
```

4. Após criar o usuário administrador, defina o email dele na variável `ADMIN_EMAIL`

## Estrutura do Banco de Dados

### Tabelas

#### users
Usuários do sistema
- `id` - ID único
- `name` - Nome completo
- `email` - Email (único)
- `password` - Senha criptografada
- `created_at`, `updated_at` - Timestamps

#### entities
Entidades (empresas/organizações)
- `id` - ID único
- `name` - Nome da entidade
- `description` - Descrição
- `address` - Endereço
- `phone` - Telefone
- `email` - Email
- `url` - Website
- `created_at`, `updated_at` - Timestamps

#### persons
Pessoas de contato
- `id` - ID único
- `name` - Nome da pessoa
- `email` - Email
- `phone` - Telefone
- `position` - Cargo
- `entity_id` - FK para entities (CASCADE)
- `created_at`, `updated_at` - Timestamps

#### events
Eventos/interações
- `id` - ID único
- `title` - Título do evento
- `description` - Descrição
- `event_date` - Data/hora do evento
- `event_type` - Tipo de evento
- `entity_id` - FK para entities (CASCADE)
- `person_id` - FK para persons (SET NULL)
- `created_at`, `updated_at` - Timestamps

#### actions
Ações de follow-up
- `id` - ID único
- `title` - Título da ação
- `description` - Descrição
- `status` - Status (pending/in_progress/completed)
- `priority` - Prioridade (low/medium/high)
- `due_date` - Data de vencimento
- `entity_id` - FK para entities (CASCADE)
- `created_at`, `updated_at` - Timestamps

### Relacionamentos

- **persons → entities**: Uma pessoa pertence a uma entidade (CASCADE delete)
- **events → entities**: Um evento pertence a uma entidade (CASCADE delete)
- **events → persons**: Um evento pode estar associado a uma pessoa (SET NULL on delete)
- **actions → entities**: Uma ação pertence a uma entidade (CASCADE delete)

## Uso

### Fluxo de Trabalho Típico

1. **Login** no sistema com suas credenciais
2. **Cadastre entidades** (empresas/organizações)
3. **Adicione pessoas** de contato para cada entidade
4. **Registre eventos** de interação com entidades e pessoas
5. **Crie ações** de follow-up para entidades
6. **Acompanhe detalhes** de cada entidade com histórico completo

### Rotas Principais

| Rota | Descrição |
|------|-----------|
| `/` | Página inicial (lista de usuários para admin) |
| `/login` | Página de login |
| `/welcome` | Página de boas-vindas após login |
| `/entities` | Lista de entidades |
| `/entities/<id>/details` | Detalhes de uma entidade |
| `/persons` | Lista de pessoas |
| `/events` | Lista de eventos |
| `/actions` | Lista de ações |
| `/register` | Cadastro de novo usuário (admin only) |
| `/change_password` | Alterar senha |
| `/logout` | Sair do sistema |

### Permissões

- **Usuários comuns**: Acesso a todas as funcionalidades de CRM
- **Administrador**: Acesso ao cadastro de novos usuários e visualização da lista de usuários

O usuário administrador é definido pela variável de ambiente `ADMIN_EMAIL`.

## Deploy

### Render.com

1. **Crie um novo Web Service** no Render.com

2. **Configure as variáveis de ambiente**:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ADMIN_EMAIL`

3. **Build Command**:
```bash
pip install -r requirements.txt
```

4. **Start Command**:
```bash
gunicorn app:app
```

5. O Render detectará automaticamente o arquivo `requirements.txt` e instalará as dependências

### Outras Plataformas

O aplicativo pode ser deployado em qualquer plataforma que suporte Python/Flask:
- Heroku
- Google Cloud Run
- AWS Elastic Beanstalk
- DigitalOcean App Platform

## Estrutura de Arquivos

```
contbem/
├── app.py                 # Aplicação Flask principal
├── database.sql           # Schema completo do banco de dados
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (não commitar)
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Este arquivo
├── static/
│   ├── images/
│   │   └── contbem.png   # Logo da aplicação
│   └── svg/
│       ├── edit.svg      # Ícone de editar
│       ├── delete.svg    # Ícone de deletar
│       └── details.svg   # Ícone de detalhes
└── templates/
    ├── base.html         # Template base
    ├── login.html        # Página de login
    ├── welcome.html      # Página de boas-vindas
    ├── index.html        # Lista de usuários
    ├── register.html     # Cadastro de usuário
    ├── change_password.html  # Alteração de senha
    ├── entities.html     # Lista de entidades
    ├── entity_form.html  # Formulário de entidade
    ├── entity_details.html # Detalhes da entidade
    ├── persons.html      # Lista de pessoas
    ├── person_form.html  # Formulário de pessoa
    ├── events.html       # Lista de eventos
    ├── event_form.html   # Formulário de evento
    ├── actions.html      # Lista de ações
    └── action_form.html  # Formulário de ação
```

## Segurança

- Senhas armazenadas com hash usando Werkzeug
- Proteção de rotas com verificação de sessão
- Validação de permissões para rotas administrativas
- Variáveis sensíveis em arquivo .env (não versionado)
- Proteção contra SQL injection via ORM do Supabase

## Suporte

Para reportar problemas ou sugerir melhorias, entre em contato com a equipe de desenvolvimento.

## Licença

[Definir licença apropriada]
