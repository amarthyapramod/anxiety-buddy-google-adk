import os
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from google.adk.apps.app import App, ResumabilityConfig

# TOOLS

async def detect_emotion(text: str) -> dict:
    '''Analyzes emotional state and returns emotion, intensity, needs_intervention'''
    from ..agents.detector_agent import DetectorAgent
    detector = DetectorAgent(use_llm=True)
    result = detector.classify(text)
    print(f"  Detected: {result.get('emotion')} (intensity {result.get('intensity')})")
    return result


async def retrieve_technique(intensity: int) -> str:
    '''Retrieves calming technique based on intensity level'''
    from ..tools.rag import RAG
    rag = RAG()
    
    if intensity >= 4:
        results = rag.retrieve("panic breathing exercise", top_k=1)
        print(f"  Retrieved panic breathing technique")
    elif intensity >= 2:
        results = rag.retrieve("anxiety grounding technique", top_k=1)
        print(f"  Retrieved grounding technique")
    else:
        return "No specific technique needed."
    
    return results[0] if results else "Technique not found."


async def save_to_memory(user_id: str, text: str, emotion: str, intensity: int) -> dict:
    '''Saves mood entry to memory for pattern tracking'''
    from ..agents.memory_agent import MemoryAgent
    memory = MemoryAgent()
    
    detector_out = {
        "emotion": emotion,
        "intensity": intensity,
        "trigger_tags": []
    }
    
    entry = memory.save_entry(user_id, text, detector_out)
    print(f"  Saved to memory")
    return {"status": "saved", "entry_id": entry['id']}


async def get_mood_history(last_n: int = 7) -> str:
    '''Gets recent mood history and patterns'''
    from ..agents.memory_agent import MemoryAgent
    memory = MemoryAgent()
    
    entries = memory.load_last_n(last_n)
    if not entries:
        return "No previous mood logs."
    
    summary = "Recent mood logs:\\\\n"
    for e in entries[-3:]:
        summary += f"- {e.get('timestamp', 'N/A')[:10]}: {e.get('emotion')} (intensity {e.get('intensity')})\\\\n"
    
    return summary + "\\\\n" + memory.compact_summary(last_n)

# AGENT CREATION

retry_config = types.HttpRetryOptions(
    attempts=3,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def create_orchestrator(user_id="demo_user"):
    '''Create Anxiety Buddy with ADK'''
    
    print(f"✓ Initialized Anxiety Buddy for user: {user_id}")
    
    # Create LlmAgent
    anxiety_agent = LlmAgent(
        name="anxiety_buddy",
        model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
        instruction=f'''You are Anxiety Support Buddy, a warm and compassionate AI companion for user {user_id}.

WORKFLOW FOR EVERY MESSAGE:

1. Call detect_emotion(user's message) to get emotion and intensity
2. Based on intensity:
   - If 4-5: Call retrieve_technique(intensity) for panic breathing
   - If 2-3: Call retrieve_technique(intensity) for grounding
3. Call save_to_memory(user_id="{user_id}", text=message, emotion=detected, intensity=detected)
4. Write a supportive response:

FOR PANIC (intensity 4-5):
"I'm here with you. You're safe. Let's try this breathing exercise:
[Share the technique in numbered steps]
If you're in danger, call 911 or text 988.
Try this now. Let me know how you feel."

FOR ANXIETY (intensity 2-3):
"I hear you - that sounds difficult. Let's try this technique:
[Share the technique]
Would you like to try this, or talk more?"

FOR MILD (intensity 0-1):
"[Acknowledge warmly]
I'm here to listen. Would you like to talk or try a calming technique?"

SPECIAL:
- "How am I doing?" → Call get_mood_history()

STYLE: Warm, clear, 3-6 sentences. Remind: "I'm support, not therapy."
CRITICAL: Always provide a text response after calling tools.''',
        tools=[
            FunctionTool(func=detect_emotion),
            FunctionTool(func=retrieve_technique),
            FunctionTool(func=save_to_memory),
            FunctionTool(func=get_mood_history)
        ]
    )
    
    # Wrap in App
    agent = App(
        name="anxiety_buddy_app",
        root_agent=anxiety_agent,
        resumability_config=ResumabilityConfig(is_resumable=True)
    )
    
    return agent