# Guia de Deploy - MindHire

## Frontend (Vercel)

### Opção 1: Deploy via Dashboard Web

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em "Add New Project"
3. Importe o repositório GitHub: `Brunoliy/saas-plataform`
4. Configure o projeto:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Adicione as variáveis de ambiente:
   - `VITE_API_URL`: URL do backend no Render (ex: `https://saas-platform-backend.onrender.com`)
6. Clique em "Deploy"

### Opção 2: Deploy via CLI

```bash
# Instalar Vercel CLI globalmente
npm install -g vercel

# Fazer login
vercel login

# No diretório do frontend
cd frontend

# Deploy
vercel --prod
```

Durante o processo:
- Root Directory: `./`
- Build Command: `npm run build`
- Output Directory: `dist`
- Framework: `vite`

---

## Backend e Frontend (Render)

### Deploy Automático via render.yaml

1. Acesse [render.com](https://render.com) e faça login
2. Clique em "New +" → "Blueprint"
3. Conecte seu repositório GitHub: `Brunoliy/saas-plataform`
4. Selecione a branch `develop` ou `main`
5. O Render detectará automaticamente o `render.yaml` e criará 2 serviços:
   - **saas-platform-backend** (Web Service)
   - **saas-platform-frontend** (Static Site)

### Configurar Variáveis de Ambiente (Backend)

No dashboard do backend no Render, adicione:

- `DATABASE_URL`: URL do banco de dados PostgreSQL
- `SECRET_KEY`: Chave secreta para JWT (gere uma aleatória)
- `OPENAI_API_KEY`: Sua chave da API OpenAI
- `FRONTEND_URL`: URL do frontend no Vercel (ex: `https://seu-app.vercel.app`)

### Configurar Banco de Dados PostgreSQL

1. No Render, clique em "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `saas-platform-db`
   - **Database**: `mindhire`
   - **User**: `mindhire_user`
3. Após criar, copie a "Internal Database URL"
4. Cole na variável `DATABASE_URL` do backend

---

## Verificar Deploys

### Vercel (Frontend)
- URL de produção: `https://[seu-projeto].vercel.app`
- Dashboard: https://vercel.com/dashboard

### Render
- Backend: `https://saas-platform-backend.onrender.com`
- Frontend: `https://saas-platform-frontend.onrender.com`
- Dashboard: https://dashboard.render.com/

---

## Comandos Úteis

### Vercel CLI
```bash
# Ver logs
vercel logs

# Listar deployments
vercel ls

# Remover deployment
vercel rm [deployment-url]

# Adicionar variáveis de ambiente
vercel env add VITE_API_URL
```

### Git Deploy
```bash
# Deploy automático no Vercel e Render ao fazer push
git push origin main
```

---

## Troubleshooting

### Frontend não conecta ao Backend
- Verifique se `VITE_API_URL` está configurado corretamente no Vercel
- Verifique se o backend está rodando no Render
- Verifique CORS no backend

### Erro de Build no Vercel
- Verifique se todas as dependências estão no `package.json`
- Verifique se o Node.js version é compatível
- Veja os logs de build no dashboard

### Erro de Migração no Render
- Verifique se `DATABASE_URL` está configurado
- Verifique se o banco PostgreSQL está rodando
- Veja os logs do serviço no dashboard

### Serviço no Render fica "Suspended"
- Plano free dorme após 15min de inatividade
- Primeira requisição pode demorar 30-60s para acordar
- Considere upgrade para plano pago se necessário
