# RESE+

**Sistema de Gestão Patrimonial com Controle de Entrada e Saída de Equipamentos**

Sistema full-stack desenvolvido para rastreamento e controle de dispositivos (notebooks, celulares, tablets) em ambiente corporativo, com suporte a QR Codes, leitor de câmera/Bluetooth e controle de acesso por perfil.

---

## ✨ Funcionalidades

### Gestão de Patrimônio
- Cadastro de dispositivos (notebook, celular, tablet, outros)
- Suporte a 3 categorias: próprios, terceiros e visitantes
- Vinculação dispositivo ↔ empregado
- Histórico completo de check-in/check-out
- Baixa de dispositivos com 8 motivos rastreáveis

### QR Codes
- Geração em lote (prefixo + numeração automática)
- Impressão em etiquetas Niimbot D11 (15x50mm a 300 DPI)
- Download de ZIP com PNGs prontos para impressão
- Vinculação automática QR ↔ dispositivo
- Leitor integrado (câmera do celular + Bluetooth)

### Controle de Acesso
- 3 perfis: Admin Master, Usuário, Operador
- Interface dedicada para vigilância/portaria
- Autenticação com hash PBKDF2-SHA256 (1.2M iterações)
- Política de senha forte (8+ caracteres, maiúscula, minúscula, número, especial)
- Troca obrigatória no primeiro login
- Expiração periódica de senha (90 dias)
- Indicador visual de força em tempo real

### Segurança
- Variáveis sensíveis em `.env` (fora do repositório)
- CORS restrito a origens autorizadas
- Headers de segurança HTTP em produção (HSTS, XSS, Clickjacking)
- Contagem de tentativas de login falhas
- Auditoria com registro de último login

---

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.12**
- **Django 5** + Django REST Framework
- **SQLite** (em produção: PostgreSQL recomendado)
- **Pillow** + **qrcode** para geração de etiquetas
- **python-dotenv** para gerenciamento de variáveis

### Frontend
- **Flutter 3.9+**
- **mobile_scanner** para leitura de QR via câmera
- **printing** para geração e compartilhamento de arquivos
- **http** para integração com API REST

### Infraestrutura
- Suporte a execução local e deploy em nuvem
- Estrutura modular preparada para PostgreSQL + Redis

---

## 📐 Arquitetura

```
rese_plus/
├── rese_plus_api/          # Configuração Django
│   ├── settings.py         # Configurações + .env
│   └── urls.py             # Rotas da API
├── dispositivos/           # App principal
│   ├── models.py           # Empregado, Dispositivo, Registro, Baixa, Usuario, QrCode
│   ├── views.py            # Endpoints REST
│   ├── serializers.py      # Serialização de dados
│   └── migrations/
├── .env                    # Variáveis sensíveis (não versionado)
├── .gitignore
└── requirements.txt

flutter_projects/rese_plus/
├── lib/
│   ├── modules/
│   │   ├── auth/           # Login, troca de senha
│   │   ├── rese/           # Páginas do sistema
│   │   └── vigilante/      # Interface do operador
│   └── services/
│       └── api_service.dart
└── pubspec.yaml
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.12+
- Flutter 3.9+
- Git

### Backend (Django)

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd django_projects

# 2. Crie e ative o ambiente virtual
python -m venv venv
# Windows:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o .env (copie o .env.example e ajuste)
cp .env.example .env
# Edite o .env com suas configurações

# 5. Rode as migrations
python manage.py makemigrations
python manage.py migrate

# 6. Crie um usuário admin master
python manage.py shell
# Dentro do shell:
from dispositivos.models import Usuario
from django.contrib.auth.hashers import make_password
Usuario.objects.create(
    nome='Admin',
    email='admin@exemplo.com',
    senha=make_password('SenhaForte@2026'),
    perfil='master',
)
exit()

# 7. Inicie o servidor
python manage.py runserver
```

### Frontend (Flutter)

```bash
cd flutter_projects/rese_plus

# Instale as dependências
flutter pub get

# Rode no navegador
flutter run -d chrome

# Ou em dispositivo Android
flutter run
```

---

## 🗺️ Roadmap

### ✅ Concluído
- [x] CRUD completo de dispositivos, empregados, registros
- [x] 3 perfis de acesso com interfaces dedicadas
- [x] Geração em lote e impressão de QR Codes
- [x] Leitor de câmera e Bluetooth no mobile
- [x] Segurança de senha (hash + política + expiração)
- [x] Variáveis em `.env` + CORS restrito

### 🔄 Em desenvolvimento
- [ ] JWT com refresh token
- [ ] Permissões `IsAuthenticated` nas views
- [ ] Hospedagem em nuvem (Azure / Railway)

### 💡 Futuro
- [ ] Integração com RFID UHF para inventário rápido
- [ ] Dashboard analítico com gráficos
- [ ] Exportação de relatórios em Excel/PDF
- [ ] Integração com sistemas corporativos (Senior)
- [ ] App mobile nativo (iOS/Android)

---

## 👩‍💻 Desenvolvimento

Desenvolvido por Jaqueline Santos como projeto de evolução técnica e portfólio profissional, com foco em boas práticas de:

- Arquitetura modular (separação clara entre backend e frontend)
- Segurança (OWASP Top 10, políticas corporativas)
- UX (feedback em tempo real, dark mode, interface limpa)
- Código limpo (separação de responsabilidades, nomenclatura clara)

---

## 📄 Licença

Projeto privado — todos os direitos reservados.

---

*Última atualização: abril de 2026*
