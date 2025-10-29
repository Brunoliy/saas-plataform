# Checagem de Qualidade do Código

## Visão Geral

Este projeto tem verificações de qualidade obrigatórias antes de fazer commits e criar PRs.

## Script Automático

Use o script `check-quality.sh` para rodar todas as verificações de uma vez:

```bash
./check-quality.sh
```

Este script verifica:
- ✅ **Backend**: Ruff, Black, MyPy, Imports
- ✅ **Frontend**: ESLint, TypeScript, Build

## Verificações Manuais

### Backend

```bash
cd backend

# 1. Linter (Ruff)
poetry run ruff check .

# 2. Formatter (Black)
poetry run black --check .

# 3. Type Checker (MyPy)
poetry run mypy app/

# 4. Test imports
poetry run python -c "from app.main import app; print('OK')"
```

### Frontend

```bash
cd frontend

# 1. Linter (ESLint)
npm run lint

# 2. Type Checker (TypeScript)
npm run type-check

# 3. Build
npm run build
```

## Corrigir Erros Automaticamente

### Backend

```bash
cd backend

# Auto-fix linter issues
poetry run ruff check . --fix

# Auto-format code
poetry run black .
```

### Frontend

```bash
cd frontend

# Auto-fix lint issues
npm run lint -- --fix
```

## Workflow Recomendado

### Antes de Commitar

1. Rode todas as verificações:
   ```bash
   ./check-quality.sh
   ```

2. Se houver erros, corrija-os

3. Rode novamente até passar

4. Faça o commit

### Antes de Criar PR

1. Certifique-se de que está na branch correta

2. Rode as verificações:
   ```bash
   ./check-quality.sh
   ```

3. Teste manualmente as mudanças

4. Crie o PR

## CI/CD (Futuro)

As mesmas checagens rodam automaticamente no GitHub Actions quando você cria um PR.

## Configuração do Editor

### VS Code

Instale as extensões:
- **Python**: ms-python.python
- **Pylance**: ms-python.vscode-pylance
- **Ruff**: charliermarsh.ruff
- **ESLint**: dbaeumer.vscode-eslint
- **Prettier**: esbenp.prettier-vscode

### Settings (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Problemas Comuns

### "poetry: command not found"

```bash
pip install --user poetry
# ou
curl -sSL https://install.python-poetry.org | python3 -
```

### "npm: command not found"

Instale Node.js: https://nodejs.org

### "ModuleNotFoundError"

```bash
cd backend
poetry install
```

### "Package not found" (Frontend)

```bash
cd frontend
npm install
```

### Build failing

1. Limpe o cache:
   ```bash
   cd frontend
   rm -rf node_modules .next dist
   npm install
   npm run build
   ```

2. Verifique erros de TypeScript:
   ```bash
   npm run type-check
   ```

## Ignorar Checagens (NÃO RECOMENDADO)

Em casos extremos, você pode pular checagens, mas **NÃO É RECOMENDADO**:

```bash
# Pular pre-commit hooks
git commit --no-verify

# Mas você DEVE consertar depois!
```

## Responsabilidades

- **Desenvolvedores**: Rodar `./check-quality.sh` antes de commit
- **Revisores de PR**: Verificar que as checagens passaram
- **CI/CD**: Bloquear merge se checagens falharem

## Benefícios

✅ **Menos bugs** em produção
✅ **Código mais limpo** e consistente
✅ **Deploy mais confiável**
✅ **Menos retrabalho**
✅ **Melhor experiência** para todos

## Tempo Estimado

- **Primeira vez**: ~5-10 minutos (instala dependências)
- **Verificações normais**: ~2-3 minutos
- **Com cache**: ~1-2 minutos

Vale a pena para evitar bugs em produção! 🚀
