# Configuração CORS para Produção

## Problema
O registro de usuários está falhando com erro `400 Bad Request` na requisição OPTIONS (preflight).

## Causa Raiz
O backend não tem a URL do frontend na lista de origens permitidas (CORS origins).

## Solução

### 1. Configurar CORS_ORIGINS no Render (Backend)

Acesse o dashboard do seu serviço backend no Render e adicione a variável de ambiente:

**Nome da Variável**: `CORS_ORIGINS`

**Valor**: URL(s) do frontend (separadas por vírgula se forem múltiplas)

#### Exemplo com um domínio:
```
CORS_ORIGINS=https://seu-frontend.vercel.app
```

#### Exemplo com múltiplos domínios:
```
CORS_ORIGINS=https://seu-frontend.vercel.app,https://www.seu-dominio.com
```

#### Exemplo com frontend no Render:
```
CORS_ORIGINS=https://seu-app-frontend.onrender.com
```

### 2. Passos no Dashboard do Render

1. Acesse: https://dashboard.render.com
2. Selecione seu serviço backend (saas-plataform-backend)
3. Vá para a aba **Environment**
4. Clique em **Add Environment Variable**
5. Preencha:
   - **Key**: `CORS_ORIGINS`
   - **Value**: URL do seu frontend (ex: `https://seu-frontend.vercel.app`)
6. Clique em **Save Changes**
7. O serviço será automaticamente redeployado

### 3. Verificar Configuração

Após o deploy, você pode verificar se a configuração está correta checando os logs:

```
{"event": "Starting SaaS Platform API", ...}
{"event": "CORS origins configured", "cors_origins": ["https://seu-frontend.vercel.app"], ...}
```

### 4. Testar

Após configurar, teste o registro de usuários novamente. O OPTIONS deve retornar **200 OK** ao invés de **400 Bad Request**.

## URLs Importantes

- **Backend URL**: `https://saas-plataform-backend.onrender.com`
- **Frontend URL**: Configure de acordo com onde seu frontend está hospedado

## Formato Aceito

A variável `CORS_ORIGINS` aceita:

1. **JSON Array** (preferido):
   ```
   ["https://app1.com","https://app2.com"]
   ```

2. **Lista separada por vírgulas**:
   ```
   https://app1.com,https://app2.com
   ```

3. **Wildcard** (NÃO recomendado para produção):
   ```
   *
   ```

## Debugging

Se ainda tiver problemas:

1. Verifique os logs do backend para ver as origens configuradas
2. Confirme que a URL do frontend está exatamente como aparece no browser (com https://, sem trailing slash)
3. Se estiver usando domínio customizado, adicione tanto `www.` quanto sem `www.`

## Exemplo Completo

Se seu frontend está em `https://meu-saas.vercel.app`:

```bash
# No Render (Backend)
CORS_ORIGINS=https://meu-saas.vercel.app

# No Vercel (Frontend)
VITE_API_BASE_URL=https://saas-plataform-backend.onrender.com/api/v1
```

## Fallback de Segurança

Se `CORS_ORIGINS` não estiver configurado, o backend usará o default:
```
["http://localhost:3000", "http://localhost:5173"]
```

Isso funciona apenas para desenvolvimento local!
