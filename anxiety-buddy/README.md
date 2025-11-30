Anxiety Buddy: ADK-Powered Emotional Support Agent

The Anxiety Buddy is an interactive, stateful AI companion built using the Agent Development Kit (ADK). It is designed to detect a user's emotional state, provide relevant coping techniques (like breathing exercises or grounding), and log the interaction for pattern tracking.

✨ Key Features

Emotional State Detection: Analyzes user input to classify emotion (panic, anxious, stressed, sad, neutral, positive) and assigns an intensity score (0-5).

Contextual Intervention: Automatically provides specific, RAG-retrieved calming techniques based on the detected intensity level (e.g., Box Breathing for high panic, 5-4-3-2-1 grounding for moderate anxiety).

Session Memory: Logs every interaction to an internal memory (sample_logs.json) to maintain state.

Pattern Analysis: Can retrieve and summarize recent emotional history upon request, providing insights into mood patterns.

ADK Framework: Built as a single App for state management and conversational Resumability across turns.

🧱 Project Structure and Components

The project code is organized into three main directories under src/: agents, tools, and utils.

Agent Architecture

The Anxiety Buddy uses a single LlmAgent orchestrator that drives the entire interaction based on a pre-defined, multi-step workflow: Detect $\rightarrow$ Intervene (if needed) $\rightarrow$ Log $\rightarrow$ Respond.

Component/Tool

File

Role

Orchestrator Agent

src/agents/adk_orchestrator.py

The main LlmAgent that receives the user's message. It uses the other tools to execute the mandatory workflow and generates the final, supportive text response.

DetectorAgent

src/agents/detector_agent.py

Analyzes Emotion. Uses either a hardcoded keyword fallback or a Gemini call to classify emotion and intensity from the user's text.

MemoryAgent

src/agents/memory_agent.py

Manages State. Provides two tools: save_to_memory for logging the current emotional state, and get_mood_history for retrieving summaries of past mood logs.

RAG Tool

src/tools/rag.py

Provides Interventions. Performs a simple keyword-based search against the internal RAG document store to retrieve the most relevant coping mechanism (e.g., breathing or grounding) text.

RAG Content Files

The core intervention content is stored in simple text files within src/data/rag/:

breathing.txt: Contains detailed steps for breathing exercises (e.g., Box Breathing, 4-7-8).

grounding.txt: Contains instructions for grounding techniques (e.g., 5-4-3-2-1 method, Cold Water).

reassurance.txt: Contains scripts and phrases for cognitive reframing and calming truths.

⚙️ Setup and Prerequisites

This project is designed for execution within a single Python notebook environment (like Kaggle) where ADK and the necessary dependencies are available.

Dependencies and Libraries

The project relies on the following core libraries:

google-adk: The Agent Development Kit for creating the agent structure, tools, and the orchestrator workflow.

google-genai: Used directly by the llm_wrapper.py utility for making direct calls to the Gemini API (specifically for the DetectorAgent).

numpy and pandas: Included for standard data manipulation, though primarily used for environment compatibility in the notebook setup.

LLM Model Used

The core reasoning and response generation are powered by:

gemini-2.5-flash: Used for the main LlmAgent orchestrator and for the optional, higher-fidelity emotional detection in the DetectorAgent.

Configuration Requirements

Google AI API Key: Must be loaded as an environment variable (GOOGLE_API_KEY).

Project Structure: All project files (detector_agent.py, rag.py, etc.) must be created under the /kaggle/working/src/ path as defined in the initial setup cells of the notebook.

🚀 Usage (Testing in Notebook Environment)

The application is executed by running the run_anxiety_workflow asynchronous function provided in the testing section of the notebook. This function handles session creation and the multi-step run/resume process required by the ADK.

How to Run

Execute all the setup cells sequentially: API key loading, directory creation, file writing, agent and orchestrator creation.

Run the final cell block labeled --- 🤖 STARTING INTEGRATION TESTS ---. This cell executes a series of predefined tests to demonstrate the agent's functionality across different intensity levels (panic, anxious, mild) and memory inquiry.

# Example execution from the test block:
await run_anxiety_workflow("Help! I'm having a panic attack and can't breathe!")
await run_anxiety_workflow("I'm really anxious about my exam tomorrow.")
await run_anxiety_workflow("How have my moods been?")
# ... and so on.


Simulated Interaction

The output simulates a stateful chat interaction, demonstrating how the agent handles different intensity levels and uses its memory:

============================================================
🗣️ User > I think I am having a panic attack, my heart is racing!

   [Tool Output]: {'status': 'saved', 'entry_id': '...'}
🤖 Agent > I'm here with you. You're safe. Let's try this breathing exercise:
[... Box Breathing Steps ...]
If you're in danger, call 911 or text 988.
Try this now. Let me know how you feel.
============================================================

============================================================
🗣️ User > How have my moods been recently?

... (Tool execution for get_mood_history) ...

🤖 Agent > I see you've logged a few entries recently.
Recent mood logs:
- 2025-11-30: anxious (intensity 3)
- 2025-11-30: panic (intensity 5)
Last 2 entries avg intensity 4.00. Common: panic(1), anxious(1).
============================================================

Running in a Kaggle Notebook

Since the notebook environment uses an asynchronous kernel, you must import the script and then call the primary entry function using the await keyword. This starts the interactive loop where you can type your chat messages.

Ensure all setup cells are run first.

Execute the following command in a new code cell:
============================================================
import main_interactive_runner
await main_interactive_runner.main()
============================================================

The console will then prompt you to start chatting:
============================================================
🎉 New Interactive Chat Session Started...
Anxiety Buddy is ready. Type 'quit' or 'exit' to end the session.

🗣️ You >
============================================================

Interactive Runner Script (main.py)

This script initializes the ADK runner and starts an asynchronous loop for continuous conversation.