# DailyStack - Guia de Desenvolvimento Local

## 🚀 Rodando Backend e Frontend Separadamente

### 1. Backend (Flask) - Porta 5000

Para rodar apenas o backend Flask:

```bash
cd c:\Users\arthu\antigravity-workspace\dailystack
python run_backend_dev.py
```

O backend estará disponível em: `http://127.0.0.1:5000`

**Endpoints disponíveis:**
- `GET /api/scenario` - Retorna o cenário do dia
- `GET /api/flashcard/current` - Retorna o flashcard atual
- `POST /api/flashcard/next` - Avança para o próximo flashcard
- `POST /api/ask-llm` - Envia pergunta para o LLM (streaming)
- `GET /api/chat/history` - Retorna histórico do chat
- `GET /api/check-auth` - Verifica autenticação
- `POST /api/save-credentials` - Salva credenciais

### 2. Frontend (Vite) - Porta 5173

Para rodar o frontend em modo desenvolvimento:

```bash
cd c:\Users\arthu\antigravity-workspace\dailystack\frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:5173`

**⚠️ Importante:** Para que o frontend consiga se comunicar com o backend, você precisa:

1. **Instalar flask-cors** (se ainda não tiver):
   ```bash
   pip install flask-cors
   ```

2. **Configurar proxy no Vite** para redirecionar chamadas da API para o backend.

### 3. Configurando Proxy no Vite

Atualize o `vite.config.js` para adicionar proxy:

```javascript
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: '../frontend_dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    }
  }
})
```

### 4. Workflow Completo de Desenvolvimento

**Terminal 1 - Backend:**
```bash
cd c:\Users\arthu\antigravity-workspace\dailystack
python run_backend_dev.py
```

**Terminal 2 - Frontend:**
```bash
cd c:\Users\arthu\antigravity-workspace\dailystack\frontend
npm run dev
```

Agora você pode:
- Acessar `http://localhost:5173` no navegador
- Ver mudanças no frontend em tempo real (hot reload)
- O frontend fará chamadas para `/api/*` que serão redirecionadas para `http://127.0.0.1:5000/api/*`

### 5. Rodando a Aplicação Completa (Produção)

Para rodar a aplicação completa com WebView:

```bash
cd c:\Users\arthu\antigravity-workspace\dailystack
npm run build --prefix frontend  # Build do frontend
python app.py                     # Roda Flask + WebView
```

## 📝 Resumo

| Modo | Backend | Frontend | URL |
|------|---------|----------|-----|
| **Dev Separado** | `python run_backend_dev.py` | `npm run dev` | http://localhost:5173 |
| **Produção** | `python app.py` | Build incluído | http://127.0.0.1:5000 (WebView) |
