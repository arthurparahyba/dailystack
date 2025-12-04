"""
Script de teste para verificar criação e consulta de agente.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.client import StackSpotClient

def test_agent_management():
    print("=== Teste de Gerenciamento de Agente ===\n")
    
    client = StackSpotClient()
    
    print(f"Configurações:")
    print(f"  Nome do agente: {client.agent_name}")
    print(f"  Descrição: {client.agent_description[:80]}...")
    print(f"  Prompt: {client.agent_prompt[:100]}...\n")
    
    print("1. Testando autenticação...")
    token = client.authenticate()
    if token:
        print(f"   [OK] Autenticado com sucesso (token: {token[:20]}...)\n")
    else:
        print(f"   [ERROR] Falha na autenticação: {client.last_error}\n")
        return
    
    print("2. Verificando se agente existe...")
    agent_id = client.ensure_agent_exists()
    
    if agent_id:
        print(f"   [OK] Agente disponível com ID: {agent_id}\n")
    else:
        print(f"   [ERROR] Falha ao obter/criar agente\n")
        return
    
    print("3. Testando consulta por nome...")
    agent = client.get_agent_by_name(client.agent_name)
    if agent:
        print(f"   [OK] Agente encontrado: {agent.name} (ID: {agent.id})\n")
    else:
        print(f"   [ERROR] Agente não encontrado\n")
    
    print("=== Teste concluído com sucesso! ===")

if __name__ == "__main__":
    test_agent_management()
