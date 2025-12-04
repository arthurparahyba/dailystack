# Backend Architecture - Clean Architecture Pattern

Este diretório implementa uma arquitetura limpa (Clean Architecture) com separação clara de responsabilidades.

## Estrutura

```
backend/
├── domain/              # Camada de Domínio (Regras de Negócio)
│   ├── entities.py      # Entidades (Flashcard, Scenario, Agent, etc.)
│   └── repositories.py  # Interfaces de repositórios (Protocols)
│
├── use_cases/           # Camada de Aplicação (Casos de Uso)
│   ├── agents/
│   │   └── ensure_agent_exists.py  # Exemplo: Lógica de negócio isolada
│   ├── auth/
│   ├── challenges/
│   └── chat/
│
├── infrastructure/      # Camada de Infraestrutura (Implementações)
│   └── http/
│       ├── stackspot_auth_client.py   # Cliente de autenticação
│       └── stackspot_agent_client.py  # Cliente de gerenciamento de agentes
│
├── presentation/        # Camada de Apresentação (API/UI)
│   └── routes/
│
├── client.py           # LEGADO: Mantido para compatibilidade
├── api.py              # LEGADO: Mantido como entry point
└── models.py           # LEGADO: Mantido para compatibilidade
```

## Princípios

### 1. Separação de Responsabilidades
Cada camada tem uma responsabilidade específica:
- **Domain**: Define entidades e regras de negócio
- **Use Cases**: Orquestra a lógica de aplicação
- **Infrastructure**: Implementa detalhes técnicos (HTTP, DB, etc.)
- **Presentation**: Expõe a API/UI

### 2. Dependency Inversion
As camadas internas não dependem das externas:
```
Domain ← Use Cases ← Infrastructure
                  ← Presentation
```

### 3. Testabilidade
Cada camada pode ser testada isoladamente com mocks.

## Exemplos Implementados

### Cliente HTTP (Infrastructure)
```python
# backend/infrastructure/http/stackspot_auth_client.py
class StackSpotAuthClient:
    def get_token(self) -> Optional[str]:
        # Implementação de autenticação
```

### Use Case (Application Logic)
```python
# backend/use_cases/agents/ensure_agent_exists.py
class EnsureAgentExists:
    def __init__(self, agent_client: StackSpotAgentClient, ...):
        self.agent_client = agent_client
    
    def execute(self) -> Optional[str]:
        # Lógica de negócio: buscar ou criar agente
```

### Uso no API (Presentation)
```python
# Exemplo de como usar (futuro)
from backend.infrastructure.http.stackspot_auth_client import StackSpotAuthClient
from backend.infrastructure.http.stackspot_agent_client import StackSpotAgentClient
from backend.use_cases.agents.ensure_agent_exists import EnsureAgentExists

# Injeção de dependências
auth_client = StackSpotAuthClient()
agent_client = StackSpotAgentClient(auth_client)
ensure_agent = EnsureAgentExists(
    agent_client=agent_client,
    agent_name="My Agent",
    agent_description="...",
    agent_prompt="...",
    output_schema={...}
)

# Executar use case
agent_id = ensure_agent.execute()
```

## Como Expandir

### Adicionar Novo Cliente HTTP
1. Criar arquivo em `infrastructure/http/`
2. Injetar `StackSpotAuthClient` no construtor
3. Implementar métodos específicos da API

### Adicionar Novo Use Case
1. Criar arquivo em `use_cases/<categoria>/`
2. Injetar dependências (clientes, outros use cases) no construtor
3. Implementar método `execute()` com a lógica de negócio
4. Retornar entidades do domínio

### Adicionar Nova Rota
1. Criar arquivo em `presentation/routes/`
2. Criar instâncias dos use cases necessários
3. Chamar `use_case.execute()` e retornar resposta

## Migração Gradual

O código legado (`client.py`, `api.py`) continua funcionando.
A migração pode ser feita gradualmente:

1. ✅ Estrutura criada
2. ✅ Exemplos de clientes e use cases implementados
3. ⏳ Migrar endpoints um por um
4. ⏳ Adicionar testes para novos componentes
5. ⏳ Remover código legado quando tudo estiver migrado

## Benefícios

- **Testabilidade**: Mocks fáceis, testes isolados
- **Manutenibilidade**: Responsabilidades claras
- **Escalabilidade**: Fácil adicionar features
- **Flexibilidade**: Trocar implementações sem afetar lógica

## Próximos Passos

1. Migrar mais clientes HTTP (challenge_client, chat_client)
2. Criar use cases para challenges e chat
3. Refatorar rotas em `api.py` para usar use cases
4. Adicionar testes unitários para cada camada
5. Documentar padrões de injeção de dependências
