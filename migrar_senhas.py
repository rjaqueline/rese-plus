"""
Script de MIGRACAO DE SENHAS — roda UMA VEZ.

Converte todas as senhas em texto puro do banco pra hash bcrypt/pbkdf2.
Marca todos os usuarios com precisa_trocar_senha=True pra forcar troca no proximo login.

Como rodar:
1. No PowerShell do Django, com venv ativado:
   cd C:\\Users\\Jaqueline\\django_projects
   .\\venv\\Scripts\\Activate
   python manage.py shell < migrar_senhas.py

OU:
2. python manage.py shell
   (dentro do shell, cole o conteudo deste arquivo)

APOS RODAR:
- O admin master (admin@taboca.com) ainda pode logar com a senha '12345678'
- Mas sera forcado a trocar no primeiro login
- Depois da troca, precisa atender a politica forte (8+ chars, maiuscula, minuscula, numero, especial)
"""

from dispositivos.models import Usuario
from django.contrib.auth.hashers import make_password, identify_hasher
from django.utils import timezone
from datetime import timedelta

print('')
print('═══════════════════════════════════════════════════════')
print('  MIGRACAO DE SENHAS — RESE+')
print('═══════════════════════════════════════════════════════')

usuarios = Usuario.objects.all()
total = usuarios.count()
migrados = 0
ja_hasheados = 0

print(f'\nTotal de usuarios no banco: {total}\n')

for u in usuarios:
    # Verifica se a senha ja esta hasheada (Django hashers tem prefixo tipo 'pbkdf2_sha256$...')
    senha_atual = u.senha or ''

    try:
        identify_hasher(senha_atual)
        # Se chegou aqui, ja e hash — nao mexe
        print(f'  [JA HASHEADO] {u.email}')
        ja_hasheados += 1
        continue
    except Exception:
        # Nao e hash — precisa migrar
        pass

    # Hasheia a senha atual
    senha_pura = senha_atual
    u.senha = make_password(senha_pura)
    u.precisa_trocar_senha = True
    u.senha_expira_em = timezone.now() + timedelta(days=u.dias_validade_senha or 90)
    u.save()
    migrados += 1
    print(f'  [MIGRADO] {u.email} — senha hasheada, precisa_trocar=True')

print('')
print('═══════════════════════════════════════════════════════')
print(f'  Migrados: {migrados}')
print(f'  Ja hasheados: {ja_hasheados}')
print(f'  Total: {total}')
print('═══════════════════════════════════════════════════════')
print('')
print('Pronto! Os usuarios podem logar com a senha atual,')
print('mas serao forcados a trocar no primeiro login.')
print('')
