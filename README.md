# RESE+ — Sistema de Rastreamento e Controle de Equipamentos

Sistema web para rastreamento e controle da entrada e saída de equipamentos por meio de QR Code.

O RESE+ foi desenvolvido para substituir controles manuais baseados em planilhas e registros em papel, oferecendo rastreabilidade das movimentações, controle de acesso por perfil e trilha de auditoria.

> Projeto desenvolvido de forma independente por **Jaqueline Batista**, a partir de uma necessidade real identificada em ambiente corporativo.

---

## Sobre o projeto

O controle de entrada e saída de equipamentos como notebooks, celulares e tablets exigia registros manuais e consultas em diferentes fontes de informação.

O RESE+ centraliza esse processo em uma aplicação web integrada a uma API REST.

Cada equipamento pode ser identificado por QR Code e suas movimentações ficam registradas, permitindo consultar o histórico e identificar quando cada dispositivo entrou ou saiu.

---

## Principais funcionalidades

### Rastreamento por QR Code

- QR Code individual por dispositivo
- Leitura por scanner USB
- Registro de entrada e saída
- Identificação automática do tipo de movimentação com base no último registro
- Histórico das movimentações

### Painel operacional

- Interface dedicada para monitor de portaria
- Exibição das últimas leituras
- Atualização das movimentações
- Identificação visual do equipamento processado

### Gestão de equipamentos

- Cadastro de equipamentos
- Associação entre equipamento, colaborador e QR Code
- Vinculação e desvinculação de QR Codes
- Consulta do histórico de movimentações
- Filtros de pesquisa
- Exportação de dados para Excel

### Usuários e permissões

O sistema possui três perfis de acesso:

- **Master**
- **Admin**
- **Operador**

Cada perfil possui permissões específicas de acordo com sua função dentro do sistema.

### Auditoria

Operações relevantes são registradas para permitir rastreabilidade das alterações realizadas no sistema.

Os registros permitem identificar informações como:

- usuário responsável;
- operação executada;
- data e horário;
- objeto afetado.

Os logs podem ser consultados e filtrados pela interface.

---

## Tecnologias

### Back-end

- Python
- Django
- Django REST Framework
- SimpleJWT
- PostgreSQL
- SQLite

### Front-end

- Flutter Web
- Dart

### API e documentação

- REST
- OpenAPI 3.0
- drf-spectacular
- Swagger UI

### Desenvolvimento e versionamento

- Git
- GitHub

---

## Arquitetura

O RESE+ utiliza uma arquitetura cliente-servidor:

```text
Flutter Web
     │
     │ HTTP / REST
     ▼
Django REST Framework
     │
     ├── autenticação
     ├── regras de negócio
     ├── controle de acesso
     ├── auditoria
     └── movimentações
     │
     ▼
PostgreSQL
```

O front-end Flutter consome a API REST desenvolvida com Django REST Framework.

Em desenvolvimento, o projeto pode utilizar SQLite. O ambiente de produção utiliza PostgreSQL.

---

## Estrutura do back-end

```text
rese-plus/
├── rese_plus_api/
│   ├── settings.py
│   └── urls.py
│
└── dispositivos/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── authentication.py
    └── migrations/
```

Entre as principais entidades da aplicação estão:

```text
Usuario
Dispositivo
Empregado
Registro
QrCode
LogAuditoria
```

---

## Estrutura do front-end

```text
flutter-app/
└── lib/
    ├── modules/
    │   ├── auth/
    │   └── rese/
    │       ├── pages/
    │       └── rese_home_page.dart
    │
    └── services/
        ├── api_service.dart
        └── auth_service.dart
```

Os serviços centralizam a comunicação com a API e o gerenciamento da autenticação.

---

## API REST

A API possui documentação automática utilizando OpenAPI 3.0 e Swagger UI.

### Documentação

```text
GET /api/docs/
GET /api/schema/
```

### Alguns endpoints

```text
POST /api/v1/login-auto/
POST /api/v1/scan/
GET  /api/v1/ultimos-registros/
GET  /api/v1/meu-perfil/
GET  /api/v1/logs-auditoria/
POST /api/v1/resetar-senha/
GET  /api/v1/exportar-excel/
```

O endpoint de scan concentra a lógica de movimentação por QR Code e determina o registro correspondente a partir do estado atual do equipamento.

---

## Autenticação e segurança

O RESE+ implementa mecanismos de autenticação e controle de acesso, incluindo:

- autenticação baseada em JWT;
- perfis com permissões distintas;
- expiração configurável de senha;
- troca obrigatória de senha quando aplicável;
- limitação de tentativas de autenticação;
- bloqueio após tentativas consecutivas;
- trilha de auditoria;
- avisos de proximidade da expiração da senha.

A interface informa ao usuário quando a senha está próxima do vencimento.

---

## Banco de dados

O projeto utiliza:

```text
SQLite      → desenvolvimento
PostgreSQL  → produção
```

A modelagem contempla usuários, empregados, dispositivos, QR Codes, movimentações e registros de auditoria.

---

## Fluxo de movimentação

De forma simplificada:

```text
QR Code lido
     │
     ▼
API recebe o identificador
     │
     ▼
Equipamento é localizado
     │
     ▼
Última movimentação é consultada
     │
     ▼
Sistema determina a nova movimentação
     │
     ├── CHECK-IN
     │
     └── CHECK-OUT
     │
     ▼
Registro é persistido
     │
     ▼
Movimentação aparece no histórico/painel
```

Essa lógica reduz a necessidade de o operador selecionar manualmente o tipo de movimentação a cada leitura.

---

## Como executar localmente

### Back-end

Clone o repositório:

```bash
git clone https://github.com/rjaqueline/rese-plus.git
cd rese-plus
```

Crie o ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente.

Windows:

```powershell
venv\Scripts\Activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute as migrações:

```bash
python manage.py migrate
```

Crie um usuário administrativo para o ambiente local:

```bash
python manage.py createsuperuser
```

Inicie o servidor:

```bash
python manage.py runserver
```

---

## Front-end

Entre no projeto Flutter:

```bash
cd flutter-app
```

Instale as dependências:

```bash
flutter pub get
```

Execute no navegador:

```bash
flutter run -d chrome --web-port=3000
```

---

## Decisões de projeto

### QR Code como identificador operacional

O QR Code reduz a necessidade de digitação manual durante as movimentações e permite que o registro seja realizado diretamente no ponto de controle.

### Determinação automática de entrada e saída

O operador não precisa escolher manualmente entre CHECK-IN e CHECK-OUT.

A aplicação consulta o último estado registrado e determina a próxima movimentação.

### Separação entre interface e regras de negócio

O Flutter é responsável pela interface e interação com o usuário, enquanto as regras de negócio e persistência ficam concentradas no back-end Django.

### PostgreSQL em produção

O SQLite facilita o desenvolvimento local, enquanto o PostgreSQL é utilizado no ambiente de produção.

### Auditoria integrada

A rastreabilidade foi considerada desde a modelagem do sistema, permitindo registrar operações relevantes e identificar quem realizou cada alteração.

---

## Status

O RESE+ foi desenvolvido como projeto independente em paralelo à minha atuação profissional na área administrativa e operacional.

O sistema surgiu da observação de um processo real e foi desenvolvido desde o levantamento da necessidade até a implementação da API, interface, banco de dados, autenticação, regras de negócio, testes e preparação para implantação.

---

## Autoria

Desenvolvido por **Jaqueline Batista**.

---

## Licença e uso

Projeto desenvolvido de forma independente.

O uso do sistema em ambiente corporativo está sujeito às condições acordadas com a organização onde a solução foi aplicada.

O código disponibilizado neste repositório tem finalidade de demonstração técnica e portfólio.
