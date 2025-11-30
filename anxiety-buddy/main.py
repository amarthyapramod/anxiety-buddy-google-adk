import sys
import uuid
import asyncio
import logging
import warnings

# --- 1. SUPPRESS WARNINGS & LOGGING (To keep output clean) ---

# Suppress warnings about experimental features (e.g., ResumabilityConfig)
warnings.filterwarnings("ignore", category=UserWarning)

# Suppress the verbose 'non-text parts' warnings from the Gemini library
logger = logging.getLogger('google_genai.types')
logger.setLevel(logging.ERROR)

print("✅ Suppressed non-critical warnings.")


# --- 2. SETUP (Initialization of ADK components) ---

sys.path.insert(0, "/kaggle/working")

# Clear cache for dynamic imports (essential in notebooks/development environments)
for mod in list(sys.modules.keys()):
    if mod.startswith('src.'):
        del sys.modules[mod]

from src.agents.adk_orchestrator import create_orchestrator
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# --- 3. GLOBAL INITIALIZATION ---

print("Creating Anxiety Buddy App...")
# Note: create_orchestrator must be defined in /kaggle/working/src/agents/adk_orchestrator.py
anxiety_app = create_orchestrator(user_id="kaggle_demo")

print("Creating session service and runner...")
session_service = InMemorySessionService()
runner = Runner(app=anxiety_app, session_service=session_service)

print("✓ System initialized\n")


# --- 4. HELPER FUNCTION ---


def print_agent_response(events):
    """Print agent's text responses from events."""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"🤖 Agent > {part.text}")
                # Debug: show tool execution status
                if part.function_response and "status" in str(part.function_response.response):
                    print(f"   [Tool Output]: {part.function_response.response}")


# --- 5. CHAT TURN FUNCTION (Replaces run_anxiety_workflow) ---

async def handle_chat_turn(user_query: str, user_id: str, session_id: str, auto_confirm: bool = True):
    """Runs a single chat turn, handling the query, tool execution, and response."""

    print(f"\n{'='*60}")
    print(f"🗣️ User > {user_query}\n")

    query_content = types.Content(role="user", parts=[types.Part(text=user_query)])
    events = []

    # PASS 1: Initial Request
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=query_content
    ):
        events.append(event)

    # CHECK FOR PAUSE (for confirmation requests, kept for robustness)
    approval_request = None
    invocation_id = None

    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call and part.function_call.name == "adk_request_confirmation":
                    approval_request = part.function_call
                    invocation_id = event.invocation_id
                    break

    # PASS 2: Handle Approval (if paused)
    if approval_request:
        hint_text = approval_request.args.get('hint', 'Confirmation Required')
        print(f"⏸️  SYSTEM PAUSED: {hint_text}")
        print(f"🤔 Human Decision: {'✅ CONFIRM' if auto_confirm else '❌ REJECT'}\n")

        # Create confirmation response
        confirmation_response = types.FunctionResponse(
            id=approval_request.id,
            name="adk_request_confirmation",
            response={"confirmed": auto_confirm}
        )
        resume_message = types.Content(
            role="user",
            parts=[types.Part(function_response=confirmation_response)]
        )

        # RESUME the agent
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=resume_message,
            invocation_id=invocation_id
        ):
            events.append(event)

    # FINAL OUTPUT
    print_agent_response(events)
    print(f"{'='*60}")

print("✓ Workflow engine ready\n")


# --- 6. MAIN EXECUTION FUNCTION (Interactive Loop) ---

async def main():
    """Initializes the session and runs the interactive chat loop."""
    
    # --- Persistent Session Setup ---
    user_id = "interactive_user"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    app_name = "anxiety_buddy_app"

    # Create session ONCE for persistent conversation state
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    print(f"🎉 New Interactive Chat Session Started (ID: {session_id} | User: {user_id})")
    print("Anxiety Buddy is ready. Type 'quit' or 'exit' to end the session.")
    
    while True:
        # Use run_in_executor to safely handle synchronous input() in an async loop
        # The prompt is only printed when it's waiting for input.
        user_query = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: input("\n🗣️ You > ")
        )
        
        if user_query.lower() in ['quit', 'exit']:
            break
        
        if not user_query.strip():
            continue
            
        # Handle the user query
        await handle_chat_turn(user_query, user_id, session_id)
    
    print("\n👋 Session ended. Goodbye!")


# --- 7. RUN SCRIPT ---

if __name__ == "__main__":
    # Ensure the asynchronous main function is executed
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Session interrupted. Goodbye!")
    except Exception as e:
        # Catch and print any major runtime errors
        print(f"\n🛑 A critical error occurred: {e}")