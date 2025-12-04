import os
import re
import requests
import json
import time
import sys
from backend.models import DailyChallenge, Agent, AgentCreationRequest

class StackSpotClient:
    def __init__(self):
        self.reload_credentials()
        self.token = None
        self.token_expires_at = 0
        self.last_error = None
        self.agent_id = None  # Cache for agent ID
        self.session = requests.Session()  # Reuse session for better performance

    def reload_credentials(self):
        self.client_id = os.environ.get("STK_CLIENT_ID")
        self.client_key = os.environ.get("STK_CLIENT_KEY")
        self.realm = os.environ.get("STK_REALM")
        
        # Agent configuration
        self.agent_name = os.environ.get("STK_AGENT_NAME", "Flashcards - Java/Python/AWS")
        self.agent_description = os.environ.get(
            "STK_AGENT_DESCRIPTION",
            "Agent that generates daily learning scenarios and flashcards for Java/Kotlin developers using Spring Boot and AWS"
        )
        self.agent_prompt = os.environ.get(
            "STK_AGENT_PROMPT",
            'Você é um agente gerador de **cenários técnicos** e **flashcards de estudo** para desenvolvedores Java/Kotlin e Lambda em Python que usam Spring Boot e AWS. '
            '**Regra principal:** sempre que receber a mensagem exata **"próximo cenário"**, gere UM cenário + 10 flashcards seguindo estritamente as restrições abaixo. '
            '## Formato de saída - Responda em **Português**. - Primeiro: **Cenário** (muito curto). - Depois: **Explicação arquitetural objetiva**. '
            '- Depois: **Decisões de arquitetura, justificativas e trade-offs** (lista curta). - Finalmente: **Exatamente 10 flashcards** com os campos: '
            '`title`, `question`, `answer`, `detailed_explanation`, `visual_example`, `code_example`. '
            '## Regras de conteúdo 1. **Tamanho do cenário:** máximo **3 sentenças**. 2. **Tecnologias:** limite o conjunto a **2–3 tecnologias**. '
            '3. **Explicação arquitetural:** máximo **3 sentenças**. 4. **Decisões & trade-offs:** 3 itens no máximo. '
            '5. **Flashcards:** gere **exatamente 10**. Cada `answer` deve ter **máx. 2 frases**. '
            '6. **Visual:** todo `visual_example` deve ser um diagrama ASCII de 1–6 linhas. 7. **Tamanho total:** mantenha a saída enxuta. 8. **Tom:** prático e direto.'
        )

    def authenticate(self):
        if self.token and self.token_expires_at > time.time():
            return self.token

        if not all([self.client_id, self.client_key, self.realm]):
            self.last_error = "Missing credentials"
            return None

        url = f"https://idm.stackspot.com/{self.realm}/oidc/oauth/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_key,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            json_response = response.json()
            self.token = json_response['access_token']
            self.token_expires_at = time.time() + json_response['expires_in'] - 60 # Buffer
            return self.token
        except Exception as e:
            self.last_error = f"Authentication failed: {e}"
            print(f"Authentication failed: {e}")
            return None

    def get_daily_challenge(self) -> DailyChallenge | None:
        """
        Fetches the daily challenge from the GenAI Agent.
        
        Returns:
            DailyChallenge: Object containing date, scenario, and flashcards
            None: If authentication or request fails
        """
        self.last_error = None # Reset error
        token = self.authenticate()
        if not token:
            self.last_error = "Failed to authenticate."
            print("Failed to authenticate.", file=sys.stderr)
            return None

        # Ensure agent exists and get its ID
        agent_id = self.ensure_agent_exists()
        if not agent_id:
            self.last_error = "Failed to get or create agent."
            print("Failed to get or create agent.", file=sys.stderr)
            return None

        url = f'https://genai-inference-app.stackspot.com/v1/agent/{agent_id}/chat'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        payload = {
            "streaming": False,
            "user_prompt": "proximo cenário",
            "stackspot_knowledge": False,
            "return_ks_in_response": False,
            "use_conversation": True,
            "conversation_id": "01KB1ATKQDKNWZXSV3JNCP72KB" 
        }

        try:
            # Timeout of 60 seconds to accommodate LLM generation time
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Use ascii() to avoid UnicodeEncodeError on Windows consoles
            print(f"DEBUG - Raw API response: {ascii(data)}", flush=True)
            
            # Parse the response to get the actual data
            parsed_data = self._parse_agent_response(data)
            
            print(f"DEBUG - Parsed data: {ascii(parsed_data)}", flush=True)
            
            if parsed_data:
                # Convert to DailyChallenge object
                return DailyChallenge.from_dict(parsed_data)
            
            self.last_error = "Parsed data is None"
            return None

        except Exception as e:
            self.last_error = f"Failed to get daily challenge: {e}"
            print(f"Failed to get daily challenge: {ascii(e)}")
            return None
    
    def _parse_agent_response(self, data: dict) -> dict | None:
        """
        Parses the agent response to extract the actual data.
        Handles different response formats from the GenAI Agent.
        
        Args:
            data: Raw response from the agent
            
        Returns:
            dict: Parsed data or None if parsing fails
        """
            # Handle different response formats
        if 'message' not in data and isinstance(data['message'], str):
            print(f"Failed to parse agent response There is no message attribute: {data}")
            return None
        try:
            return json.loads(data['message'])
        except json.JSONDecodeError:
            print(f"Failed to parse agent response: {e}")
            return None

    def get_agent_by_name(self, agent_name: str) -> Agent | None:
        """
        Get agent by name from the GenAI API.
        
        Args:
            agent_name: Name of the agent to search for
            
        Returns:
            Agent object if found, None otherwise
        """
        token = self.authenticate()
        if not token:
            return None
            
        url = "https://genai-agent-tools-api.stackspot.com/v1/agents?visibility=personal"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            agents = response.json()
            for agent in agents:
                if agent.get('name') == agent_name:
                    print(f"Found agent '{agent_name}' with ID: {agent['id']}", file=sys.stderr)
                    return Agent(id=agent['id'], name=agent['name'])
            
            print(f"Agent '{agent_name}' not found.", file=sys.stderr)
            return None
            
        except Exception as e:
            print(f"Error getting agent by name: {e}", file=sys.stderr)
            return None

    def _generate_slug(self, name: str) -> str:
        """Generate a valid slug from the agent name."""
        # Convert to lowercase
        slug = name.lower()
        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def create_agent(self, request: AgentCreationRequest) -> Agent | None:
        """
        Create a new GenAI agent.
        
        Args:
            request: AgentCreationRequest with agent configuration
            
        Returns:
            Agent object if created successfully, None otherwise
        """
        token = self.authenticate()
        if not token:
            return None

        url = "https://genai-agent-tools-api.stackspot.com/v1/agents"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "type": "CONVERSATIONAL",
            "name": request.name,
            "system_prompt": request.prompt,
            "suggested_prompts": [],
            "slug": self._generate_slug(request.name),
            "knowledge_sources_config": {
                "max_number_of_kos": 4,
                "relevancy_threshold": 40,
                "knowledge_sources": []
            },
            "tools": [],
            "mode": "autonomous",
            "enabled_tools": True,
            "memory": "buffer",
            "model_id": "01JZTZQFP4QHTB1500FFW5KT08",
            "model_name": "gpt-4.1",
            "llm_settings": {
                "temperature": 0.4,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            },
            "builtin_tools_ids": [],
            "custom_tools": []
        }
        
        # Add structured_output if provided
        if request.output_schema:
            body["enabled_structured_outputs"] = True
            body["structured_output"] = request.output_schema
        else:
            body["enabled_structured_outputs"] = False
            body["structured_output"] = None
        
        try:
            # Debug: Print complete payload
            print(f"DEBUG: Creating agent with payload:", file=sys.stderr)
            print(f"  - name: {body['name']}", file=sys.stderr)
            print(f"  - slug: {body['slug']}", file=sys.stderr)
            print(f"  - model_id: {body['model_id']}", file=sys.stderr)
            print(f"  - structured_output enabled: {body.get('enabled_structured_outputs', False)}", file=sys.stderr)
            print(f"DEBUG: Full payload JSON:", file=sys.stderr)
            print(json.dumps(body, indent=2), file=sys.stderr)
            
            response = self.session.post(url, headers=headers, json=body)
            
            if response.status_code == 201:
                agent_data = response.json()
                agent_id = agent_data["id"]
                print(f"Agent created successfully with ID: {agent_id}", file=sys.stderr)
                return Agent(id=agent_id, name=request.name)
            else:
                print(f"Failed to create agent: {response.status_code}", file=sys.stderr)
                print(f"Response body: {response.text}", file=sys.stderr)
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}", file=sys.stderr)
                except:
                    pass
                return None
                
        except Exception as e:
            print(f"Error creating agent: {e}", file=sys.stderr)
            return None

    def ensure_agent_exists(self) -> str | None:
        """
        Ensure the agent exists, creating it if necessary.
        
        Returns:
            Agent ID if successful, None otherwise
        """
        # Return cached ID if available
        if self.agent_id:
            return self.agent_id
        
        # Try to get existing agent
        agent = self.get_agent_by_name(self.agent_name)
        
        if agent:
            self.agent_id = agent.id
            return self.agent_id
        
        # Agent doesn't exist, create it
        print(f"Agent '{self.agent_name}' not found. Creating...", file=sys.stderr)
        
        # Define the output schema for structured responses
        output_schema = {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Data atual no formato YYYY-MM-DD"
                },
                "scenario": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "problem_description": {"type": "string"},
                        "architectural_overview": {"type": "string"},
                        "technologies_involved": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "problem_description", "architectural_overview", "technologies_involved"]
                },
                "flashcards": {
                    "type": "array",
                    "minItems": 10,
                    "maxItems": 10,
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "question": {"type": "string"},
                            "short_answer": {"type": "string"},
                            "detailed_explanation": {"type": "string"},
                            "visual_example": {"type": "string"},
                            "code_example": {"type": "string"}
                        },
                        "required": ["title", "question", "short_answer", "detailed_explanation", "visual_example", "code_example"]
                    }
                }
            },
            "required": ["date", "scenario", "flashcards"]
        }
        
        request = AgentCreationRequest(
            name=self.agent_name,
            description=self.agent_description,
            prompt=self.agent_prompt,
            output_schema=output_schema
        )
        
        agent = self.create_agent(request)
        
        if agent:
            self.agent_id = agent.id
            return self.agent_id
        
        return None

    def chat_with_agent(self, conversation_id, user_prompt):
        """Sends a message to the GenAI Code Buddy Agent and yields streaming responses."""
        token = self.authenticate()
        if not token:
            print("Failed to authenticate.")
            return

        url = "https://genai-code-buddy-api.stackspot.com/v3/chat"

        data = {
            "context": {
                "conversation_id": conversation_id,
                "stackspot_ai_version": "2.3.0"
            },
            "user_prompt": f"{user_prompt}"
        }

        headers = {
            'Content-Type': 'application/json',
            'authorization': f'Bearer {token}'
        }

        try:
            response = requests.post(url, json=data, headers=headers, stream=True)
            print(f"Chat response status: {response.status_code}")

            if response.status_code == 403 or response.status_code == 401:
                print(f"Erro: Status code {response.status_code} - {response.text}")
                yield {"error": f"Erro: Status code {response.status_code} - {response.text}"}
                return

            if response.status_code != 200:
                print(f"Erro: Status code {response.status_code} - {response.text}")
                yield {"error": f"Erro: Status code {response.status_code} - {response.text}"}
                return

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    if decoded_line.startswith('data: '):
                        try:
                            json_data = decoded_line[6:] # Slice after 'data: '
                            if json_data.strip():
                                data_dict = json.loads(json_data)
                                if "answer" in data_dict:
                                    yield data_dict
                        except Exception as e:
                            print(f"Failed to parse line: {decoded_line}, error: {e}")
                    
                    if 'event: end_event' in decoded_line:
                        break

        except Exception as e:
            print(f"Failed to chat with agent: {e}")
            yield {"error": str(e)}
