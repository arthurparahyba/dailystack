"""
Data models for DailyStack backend.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import date
import uuid


@dataclass
class Flashcard:
    """Represents a single flashcard."""
    question: str
    answer: str
    category: str = "General"
    detailed_explanation: Optional[str] = None
    code_example: Optional[str] = None
    visual_example: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Flashcard':
        """Create a Flashcard from a dictionary."""
        return cls(
            question=data.get('question', ''),
            answer=data.get('short_answer', ''),
            category=data.get('category', 'General'),
            detailed_explanation=data.get('detailed_explanation'),
            code_example=data.get('code_example', ''),
            visual_example=data.get('visual_example', '')
        )
    
    def to_dict(self) -> dict:
        """Convert Flashcard to dictionary."""
        return {
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'detailed_explanation': self.detailed_explanation,
            'code_example': self.code_example,
            'visual_example': self.visual_example
        }


@dataclass
class Scenario:
    """Represents the daily scenario/context."""
    title: str
    description: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Scenario':
        """Create a Scenario from a dictionary."""
        print(f"DEBUG - Scenario.from_dict input: {data}", flush=True)
        scenario = cls(
            title=data.get('title', ''),
            description=data.get('problem_description', '')
        )
        print(f"DEBUG - Created Scenario object: title='{scenario.title}', description='{scenario.description}'", flush=True)
        return scenario
    
    def to_dict(self) -> dict:
        """Convert Scenario to dictionary."""
        return {
            'title': self.title,
            'description': self.description
        }


@dataclass
class DailyChallenge:
    """Represents the complete daily challenge with scenario and flashcards."""
    date: str
    scenario: Scenario
    flashcards: List[Flashcard] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DailyChallenge':
        """Create a DailyChallenge from a dictionary."""
        scenario_data = data.get('scenario', {})
        flashcards_data = data.get('flashcards', [])
        
        return cls(
            date=data.get('date', str(date.today())),
            scenario=Scenario.from_dict(scenario_data),
            flashcards=[Flashcard.from_dict(fc) for fc in flashcards_data]
        )
    
    def to_dict(self) -> dict:
        """Convert DailyChallenge to dictionary."""
        return {
            'date': self.date,
            'scenario': self.scenario.to_dict(),
            'flashcards': [fc.to_dict() for fc in self.flashcards]
        }


@dataclass
class ConversationState:
    """Represents the state of a conversation for a specific flashcard."""
    id: str
    messages: List[dict] = field(default_factory=list)
    is_first: bool = True


@dataclass
class AppState:
    """Manages the global application state with type safety."""
    daily_challenge: Optional[DailyChallenge] = None
    current_flashcard_index: int = 0
    current_conversation_id: Optional[str] = None
    is_first_message_for_card: bool = True
    is_loading: bool = True
    error: Optional[str] = None
    conversations: Dict[int, ConversationState] = field(default_factory=dict)
    
    def get_scenario(self) -> Optional[Scenario]:
        """Get the current scenario."""
        if self.daily_challenge:
            return self.daily_challenge.scenario
        return None
    
    def get_current_flashcard(self) -> Optional[Flashcard]:
        """Get the current flashcard."""
        if not self.daily_challenge or not self.daily_challenge.flashcards:
            return None
        
        # Safety check
        if self.current_flashcard_index >= len(self.daily_challenge.flashcards):
            self.current_flashcard_index = 0
        
        return self.daily_challenge.flashcards[self.current_flashcard_index]
    
    def next_flashcard(self) -> Optional[Flashcard]:
        """Advance to the next flashcard and return it."""
        if not self.daily_challenge or not self.daily_challenge.flashcards:
            return None
        
        self.current_flashcard_index += 1
        
        # Loop back to 0 if we exceed the list
        if self.current_flashcard_index >= len(self.daily_challenge.flashcards):
            self.current_flashcard_index = 0
        
        # Check if we have a conversation for this card
        if self.current_flashcard_index in self.conversations:
            # Restore conversation
            conv_data = self.conversations[self.current_flashcard_index]
            self.current_conversation_id = conv_data.id
            self.is_first_message_for_card = conv_data.is_first
        else:
            # Create new conversation
            self.initialize_conversation(self.current_flashcard_index)
        
        return self.get_current_flashcard()
    
    def initialize_conversation(self, index: int) -> str:
        """Initialize a new conversation for a flashcard index."""
        conv_id = self.generate_ulid()
        self.current_conversation_id = conv_id
        self.is_first_message_for_card = True
        
        initial_messages = []
        
        # Seed with detailed explanation if available
        # REMOVED: User requested to remove static detailed explanation in favor of dynamic LLM explanation
        # if self.daily_challenge and index < len(self.daily_challenge.flashcards):
        #     flashcard = self.daily_challenge.flashcards[index]
        #     content_parts = []
        #     
        #     if flashcard.detailed_explanation:
        #         content_parts.append(f"**Detailed Explanation:**\n{flashcard.detailed_explanation}")
        #     
        #     if flashcard.code_example:
        #         content_parts.append(f"**Code Example:**\n```\n{flashcard.code_example}\n```")
        #         
        #     if content_parts:
        #         initial_messages.append({
        #             "role": "bot",
        #             "content": "\n\n".join(content_parts)
        #         })

        self.conversations[index] = ConversationState(
            id=conv_id,
            messages=initial_messages,
            is_first=True
        )
        return conv_id

    def generate_ulid(self) -> str:
        """Generates a ULID-like string (26 chars) using Crockford's Base32."""
        import time
        import random
        
        CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        t = int(time.time() * 1000)
        
        # Timestamp (10 chars)
        timestamp_str = ""
        for _ in range(10):
            timestamp_str = CROCKFORD_BASE32[t % 32] + timestamp_str
            t //= 32
            
        # Randomness (16 chars)
        random_str = ""
        for _ in range(16):
            random_str += random.choice(CROCKFORD_BASE32)
            
        return timestamp_str + random_str
    
    def get_conversation(self, index: int) -> Optional[ConversationState]:
        """Get the conversation state for a specific flashcard index."""
        return self.conversations.get(index)
    
    def get_flashcard_count(self) -> int:
        """Get the total number of flashcards."""
        if self.daily_challenge and self.daily_challenge.flashcards:
            return len(self.daily_challenge.flashcards)
        return 0
    
    def get_current_date(self) -> Optional[str]:
        """Get the current challenge date."""
        if self.daily_challenge:
            return self.daily_challenge.date
        return None

