# 🌍 AI Travel Planner - Multi-Agent System

An AI-powered travel planning application that utilizes a multi-agent system to fetch real flight data, discover budget hotels, and generate a comprehensive day-by-day itinerary. The system is built with LangGraph for agent orchestration, allowing for a Human-in-the-Loop (HITL) approval process before finalizing the trip plan.

## 🚀 Features
- **Multi-Agent Architecture:** Specialized AI agents handle different aspects of the trip planning process (Flights, Hotels, Itinerary, Formatting).
- **Real-Time Data:** Integrates with real flight APIs and Tavily Search for current hotel recommendations.
- **Human-in-the-Loop (HITL):** Pauses execution to allow the user to review and confirm the draft itinerary before generating the final polished plan.
- **Persistent Memory:** Uses a PostgreSQL checkpointer to save the state of the conversation, allowing users to safely pause and resume their planning session without losing data.
- **Interactive UI:** A clean, easy-to-use frontend built with Streamlit.

## ⚙️ How It Works (The Workflow)

```text
[User Input via Streamlit]
            ↓
[Flight Agent]
            ↓
[Hotel Agent]
            ↓
[Itinerary Agent]
            ↓
[Human Approval / Pause]
            ↓
[Response Agent]
            ↓
[Final Trip Plan Displayed]
```

The application utilizes a LangGraph `StateGraph` where information flows sequentially through different agent nodes.

1. **User Input:** The user enters their Origin, Destination, and Number of Days in the Streamlit UI. A unique `session_id` is generated and tracked.
2. **Flight Agent (`flight_agent`):** Extracts the origin and destination, maps them to major airports, and calls a live aviation API to retrieve active flight schedules and information.
3. **Hotel Agent (`hotel_agent`):** Performs a targeted web search (via Tavily) to find budget-friendly hotel options in the destination city for the specified duration.
4. **Itinerary Agent (`itinerary_agent`):** Consolidates the flight and hotel data, along with the user's initial query, and passes it to an LLM to draft a practical, time-saving, and budget-friendly day-by-day itinerary.
5. **⏸️ Human Approval (HITL Interruption):** The LangGraph execution pauses (`interrupt_before=["response_agent"]`). The Streamlit UI detects this paused state and displays the draft itinerary to the user. The state is securely saved in the PostgreSQL database.
6. **Response Agent (`response_agent`):** Once the user clicks "Confirm", the graph resumes. This final agent analyzes all previous data and formats a beautiful, engaging final response that includes:
   - Trip Summary
   - Flight Information
   - Hotel Suggestions
   - Approved Day-by-Day Itinerary
   - Estimated Budget
   - Final Recommendations

## 🛠️ Technology Stack
- **LangGraph & LangChain:** Core multi-agent orchestration and LLM interactions.
- **Streamlit:** Interactive web frontend.
- **PostgreSQL (`PostgresSaver`):** Database checkpointer for state memory and workflow pausing.
- **OpenAI (`gpt-4o-mini`):** The core LLM powering the agents' reasoning and generation.
- **Tavily Search API:** Used for real-time web search capabilities (Hotels).

## 🏃‍♂️ How to Run Locally

1. **Environment Variables:** Ensure you have an `.env` file with the required API keys and database URL:
   ```env
   OPENAI_API_KEY=your_openai_key
   TAVILY_API_KEY=your_tavily_key
   DATABASE_URL=your_postgres_connection_string
   API_KEY=your_flight_api_key
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application:**
   ```bash
   uv run streamlit run app.py
   ```
