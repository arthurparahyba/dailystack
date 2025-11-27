import json
from unittest.mock import MagicMock
from backend.client import StackSpotClient

# Mock the response data based on the user's report
mock_response_data = {
    'message': '{"date":"2024-06-18","scenario":{"title":"Configuração de Upload de Arquivos em Spring Boot com S3","problem_description":"Uma equipe de backend precisa permitir que usuários façam upload de arquivos...","architectural_overview":"...","technologies_involved":["Spring Boot","Amazon S3"]},"flashcards":[{"title":"Upload Multipart em Spring Boot","question":"Como implementar um endpoint de upload de arquivos em Spring Boot?","short_answer":"Usando um endpoint @PostMapping que aceita MultipartFile.","detailed_explanation":"...","visual_example":"...","code_example":"..."}]}'
}

def test_parsing():
    client = StackSpotClient()
    
    # Mock the authenticate method to avoid real network calls
    client.authenticate = MagicMock(return_value="fake_token")
    
    # Mock requests.post
    import requests
    original_post = requests.post
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None
    
    requests.post = MagicMock(return_value=mock_response)
    
    try:
        print("Testing get_daily_challenge parsing...")
        result = client.get_daily_challenge()
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and 'scenario' in result and 'flashcards' in result:
            print("SUCCESS: Parsed correctly!")
        else:
            print("FAILURE: Did not parse correctly.")
            print(f"Actual result: {result}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        requests.post = original_post

if __name__ == "__main__":
    test_parsing()
