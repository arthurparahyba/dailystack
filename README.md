# Dailystack

Dailystack é uma aplicação desktop para desenvolvedores praticarem seus conhecimentos diariamente através de cenários e flashcards gerados por IA.

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python 3.10+
- Node.js 22+
- StackSpot Account (para acesso à GenAI)

### 1. Configuração do Frontend
O frontend é construído com Svelte e Tailwind CSS.

```bash
cd frontend
npm install
npm run build
```
Isso irá gerar os arquivos estáticos em `frontend/build`.

### 2. Configuração do Backend
O backend é uma aplicação Flask que serve o frontend e gerencia a comunicação com a IA.

1. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
Defina as seguintes variáveis de ambiente no seu Sistema Operacional (Windows/Linux/Mac):

- `STK_CLIENT_ID`: Seu Client ID da StackSpot
- `STK_CLIENT_KEY`: Sua Client Key da StackSpot
- `STK_REALM`: Seu Realm da StackSpot

3. Execute a aplicação:
```bash
python app.py
```

### 3. Gerando Executável
Para distribuir a aplicação como um executável único:

```bash
pyinstaller build.spec
```
O executável será gerado na pasta `dist/`.

---

## 🏗️ Arquitetura Backend

O backend foi refatorado seguindo os princípios da **Clean Architecture** para garantir manutenibilidade, testabilidade e escalabilidade.

### Estrutura de Camadas
A aplicação é dividida em 4 camadas principais:

1.  **Domain (`backend/domain/`)**:
    *   Contém as **Entidades** (regras de negócio fundamentais) como `DailyChallenge`, `Flashcard`, `Scenario`.
    *   Define **Interfaces de Repositórios** (contratos) que as camadas externas devem implementar.
    *   *Princípio*: Não depende de nenhuma outra camada.

2.  **Use Cases (`backend/use_cases/`)**:
    *   Contém a **Lógica de Aplicação** específica.
    *   Cada funcionalidade é um caso de uso isolado (ex: `EnsureAgentExists`, `GetDailyChallenge`, `ChatWithAgent`).
    *   *Princípio*: Depende apenas do Domínio.

3.  **Infrastructure (`backend/infrastructure/`)**:
    *   Implementações concretas de interfaces.
    *   **HTTP Clients**: `StackSpotAuthClient`, `StackSpotAgentClient`, etc.
    *   **Repositórios**: `InMemoryStateRepository`.
    *   *Princípio*: Depende de bibliotecas externas e frameworks.

4.  **Presentation (`backend/presentation/`)**:
    *   Ponto de entrada da API.
    *   **Rotas**: `status_routes`, `flashcard_routes`, `chat_routes`.
    *   **Dependências**: Container de injeção de dependências (`dependencies.py`).

### Funcionalidades Principais
*   **Gerenciamento Dinâmico de Agentes**: Cria e configura automaticamente agentes GenAI na StackSpot.
*   **Geração de Desafios**: Busca cenários e flashcards diários via LLM.
*   **Chat Contextual**: Permite conversar com o agente sobre o card atual, mantendo histórico.
*   **Streaming**: Respostas do chat são transmitidas em tempo real (Server-Sent Events).

---

## 🎨 Design e Frontend

O frontend foi projetado para ser **minimalista, responsivo e focado no conteúdo**.

### Tecnologias
*   **Svelte**: Framework reativo para alta performance e código limpo.
*   **Tailwind CSS**: Estilização utilitária para design rápido e consistente.
*   **Vite**: Build tool moderna e rápida.
*   **Marked + DOMPurify**: Renderização segura de Markdown no chat.

### Funcionalidades e UX
1.  **Flashcards Interativos**:
    *   Animação 3D de "flip" para revelar a resposta.
    *   Navegação intuitiva entre cards.

2.  **Chat Integrado**:
    *   Interface de chat moderna ao lado do card.
    *   Suporte a Markdown (código, listas, negrito) nas respostas da IA.
    *   Seleção de texto habilitada para copiar exemplos de código.

3.  **Modo Debug**:
    *   Painel de status para monitorar carregamento e erros.
    *   Detecção automática de ambiente (dev vs prod).

### Estrutura de Componentes
*   `App.svelte`: Layout principal e gerenciamento de estado global.
*   `Flashcard.svelte`: Componente visual do card com lógica de flip.
*   `Chat.svelte`: Interface de chat com histórico e input.
*   `Controls.svelte`: Botões de navegação e ações.
*   `Header.svelte`: Exibição do cenário e data atual.
