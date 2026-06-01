# RESE+ — Sistema de Rastreamento e Controle de Equipamentos

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)
![Flutter](https://img.shields.io/badge/Flutter-Web-02569B?logo=flutter)
![License](https://img.shields.io/badge/licença-Uso%20Restrito-red)

> Sistema desenvolvido de forma independente por **Jaqueline Batista** para digitalizar e automatizar o controle de entrada e saída de equipamentos na **Mineração Taboca** (Presidente Figueiredo, AM).

---

## 📋 Sobre o Projeto

O RESE+ substituiu um processo 100% manual (planilhas e papel) por um sistema web completo com rastreamento via QR Code, painel de portaria em tempo real e trilha de auditoria completa — atendendo à Política de Segurança da Informação CRP-TIN-TIN-POL-016.

### O problema que resolve

- ❌ Controle manual de notebooks, celulares e tablets entrando e saindo da mineração
- ❌ Sem rastreabilidade de quem levou o quê e quando
- ❌ Sem histórico auditável para conformidade

### A solução

- ✅ QR Codes únicos por dispositivo (impressão via Niimbot D11)
- ✅ Painel de portaria com leitor USB — registra entrada/saída automaticamente
- ✅ Audit log completo de todas as operações
- ✅ Exportação Excel para relatórios gerenciais

---

## 🚀 Funcionalidades

### Painel da Portaria (Telão)
- Leitor USB de QR Code integrado
- Auto-decisão CHECK-IN / CHECK-OUT baseada no último registro
- Feed em tempo real das últimas 10 leituras
- Interface de tela cheia para monitor dedicado na portaria

### Gestão de Equipamentos
- Cadastro completo (empregado + dispositivo + QR em uma operação)
- Vinculação/desvinculação de QR Codes
- Histórico de movimentações com filtros
- Exportação Excel com dados completos

### Segurança
- Autenticação JWT com modelo de usuário customizado
- Rate limiting no login (bloqueio após 5 tentativas)
- Política de expiração de senha configurável
- Trilha de auditoria de todos os CRUDs (quem fez, o quê, quando)
- Aviso de expiração de senha na interface (7 e 3 dias)

### Administração
- 3 perfis de acesso: Master, Admin, Operador
- Reset de senha com senha temporária forte
- Logs de auditoria filtráveis e exportáveis
- Gerenciamento completo de usuários

---

## 🛠️ Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 6.0 + Django REST Framework |
| Autenticação | JWT customizado (SimpleJWT) |
| Frontend | Flutter Web |
| Banco de dados | SQLite (dev) / PostgreSQL (prod) |
| Documentação API | drf-spectacular (OpenAPI 3.0 / Swagger) |
| Impressão de etiquetas | Niimbot D11 via ZIP de PNGs |
| Controle de versão | Git + GitHub |

---

## 📡 Documentação da API

A API é documentada automaticamente via Swagger UI:

```
GET /api/docs/     → Interface Swagger interativa
GET /api/schema/   → Schema OpenAPI 3.0 (JSON)
```

Principais endpoints:

```
POST /api/v1/login-auto/          → Autenticação JWT
POST /api/v1/scan/                → Scan QR (auto CHECK-IN / CHECK-OUT)
GET  /api/v1/ultimos-registros/   → Feed do painel de portaria
GET  /api/v1/meu-perfil/          → Perfil + dias até expirar senha
GET  /api/v1/logs-auditoria/      → Trilha de auditoria
POST /api/v1/resetar-senha/       → Reset de senha pelo Master
GET  /api/v1/exportar-excel/      → Exportação de dados
```

---

## 🏗️ Arquitetura

```
rese-plus/
├── rese_plus_api/          # Configurações Django
│   ├── settings.py
│   └── urls.py
└── dispositivos/           # App principal
    ├── models.py           # Usuario, Dispositivo, Empregado,
    │                       # Registro, QrCode, LogAuditoria
    ├── views.py            # Toda a lógica de negócio
    ├── serializers.py
    ├── authentication.py   # JWT customizado p/ modelo Usuario
    └── migrations/
```

```
flutter-app/
└── lib/
    ├── modules/
    │   ├── auth/           # Login, TrocarSenha
    │   └── rese/
    │       ├── pages/      # Painel, Scanner, Histórico,
    │       │               # Dispositivos, QrCodes, Exportação,
    │       │               # Logs, MeuPerfil, Gerenciar Usuários
    │       └── rese_home_page.dart
    └── services/
        ├── api_service.dart    # Comunicação com o backend
        └── auth_service.dart   # Gestão de tokens JWT
```

---

## ⚙️ Como rodar localmente

### Backend

```bash
# Clonar e entrar na pasta
git clone https://github.com/rjaqueline/rese-plus.git
cd rese-plus

# Ambiente virtual
python -m venv venv
venv\Scripts\Activate      # Windows
source venv/bin/activate   # Linux/Mac

# Dependências
pip install -r requirements.txt

# Banco de dados
python manage.py migrate

# Criar superusuário
python manage.py shell -c "
from dispositivos.models import Usuario
from django.contrib.auth.hashers import make_password
Usuario.objects.create(
    username='admin',
    nome='Administrador',
    perfil='master',
    senha=make_password('Admin@2026'),
    ativo=True
)
"

# Rodar
python manage.py runserver
```

### Frontend (Flutter)

```bash
cd flutter-app
flutter pub get
flutter run -d chrome --web-port=3000
```

---

## 🔒 Segurança & Conformidade

| Requisito | Implementação |
|-----------|--------------|
| Rastreabilidade | Log de auditoria em 100% das operações |
| Controle de acesso | 3 perfis com permissões distintas |
| Proteção de credenciais | JWT + expiração + rate limiting |
| Política de senha | Expiração configurável + troca obrigatória |
| Proteção contra força bruta | Bloqueio após 5 tentativas (HTTP 423) |

---

## 📊 Contexto de Desenvolvimento

- **Desenvolvido por:** Jaqueline Batista
- **Início:** Novembro 2025
- **Contexto:** Projeto independente, desenvolvido em paralelo à função administrativa na Mineração Taboca
- **Status:** Em fase de testes com implantação prevista para 2026

---

## 📄 Licença

Este sistema foi desenvolvido por **Jaqueline Batista** e cedido para uso pela Mineração Taboca sob Termo de Cessão Limitada de Uso. A propriedade intelectual permanece com a autora.

---

*Desenvolvido com 🖤 e muito café em Manaus, AM.*
