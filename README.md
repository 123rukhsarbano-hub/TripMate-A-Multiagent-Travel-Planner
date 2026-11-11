# ✈️ TripMate AI — A Multi-Agent Travel Planner with LangGraph

An open-source AI travel planner that turns a natural-language trip request into a practical travel plan with flight suggestions, hotel ideas, and a day-by-day itinerary. The project uses a multi-agent workflow built with LangGraph, LangChain, and FastAPI.

## Why this project?

Planning a trip usually means jumping between multiple websites, tools, and spreadsheets. This project brings that flow into one experience by combining:

- a flight-search agent,
- a hotel-research agent,
- an itinerary-planning agent, and
- a final response agent,

all coordinated through a LangGraph workflow.

## Features

- ✈️ Flight research using AviationStack
- 🏨 Hotel suggestions using Tavily search
- 🧠 Multi-agent orchestration with LangGraph
- 📝 Structured travel itinerary generation
- 🌐 FastAPI backend with a simple web interface
- 💾 Conversation state persistence using PostgreSQL
- ⚡ LLM-powered responses with Groq

## Tech Stack

- Python 3.10+
- FastAPI
- Jinja2 + HTML/CSS/JavaScript frontend
- LangGraph
- LangChain
- Groq LLMs
- PostgreSQL
- Tavily API
- AviationStack API

## Project Structure

```text
.
├── app.py                # FastAPI app entry point
├── backend.py            # LangGraph travel workflow
├── requirements.txt      # Python dependencies
├── static/               # Static frontend assets
├── templates/            # HTML templates
└── tools/                # Flight and web search integrations
```

## Prerequisites

Before running the project locally, make sure you have:

- Python 3.10 or newer installed
- PostgreSQL running and accessible
- API keys for:
  - Groq
  - Tavily
  - AviationStack

## Environment Variables

Create a .env file in the project root with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
DEFAULT_ORIGIN_IATA=DAC
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the App

Start the FastAPI server:

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:8000/
```

## AWS CI/CD Deployment

The GitHub Actions workflow in `.github/workflows/cicd.yaml` validates the Python
sources, builds the Docker image, pushes it to Amazon ECR, and deploys it to an
EC2 instance through AWS Systems Manager (SSM).

Configure these variables in the GitHub `production` environment:

- `AWS_REGION`: AWS region containing the ECR repository and EC2 instance.
- `AWS_ROLE_ARN`: IAM role trusted for GitHub Actions OIDC.
- `ECR_REPOSITORY`: existing ECR repository name.
- `EC2_INSTANCE_ID`: target EC2 instance registered with SSM.
- `APP_SECRET_ID`: AWS Secrets Manager secret ID or ARN.

The GitHub Actions role needs permission to push images to the selected ECR
repository, update the specified Secrets Manager secret, and to send and inspect
SSM commands for the target instance. The EC2 instance needs an instance profile
that allows ECR image pulls, access to the specified Secrets Manager secret, and
SSM management. Install Docker, AWS CLI, and `curl` on the instance, and allow
inbound traffic to port `8000` as needed.

Add these required secrets to the GitHub `production` environment:
`DATABASE_URL`, `GROQ_API_KEY`, `AVIATIONSTACK_API_KEY`, and `TAVILY_API_KEY`.
Optional secrets are `OPENWEATHER_API_KEY`, `DEFAULT_ORIGIN_IATA`,
`LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_API_KEY`, and
`LANGSMITH_PROJECT`. During deployment, the workflow writes the configured
secrets to a temporary `.env`, syncs it to the named Secrets Manager secret, and
the EC2 instance retrieves it for the container. The temporary file is removed
after deployment.

## API Endpoints

- GET /health - Health check
- POST /api/travel - Submit a travel request

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

## How the Workflow Works

1. The user submits a travel request.
2. The flight agent gathers flight-related information.
3. The hotel agent searches for accommodation suggestions.
4. The itinerary agent creates a practical travel plan.
5. The final agent formats the result into a polished response.

## Contributing

Contributions are welcome. If you want to improve the app, add new travel features, or fix issues:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a pull request

## Acknowledgments

This project is built with the help of modern LLM tooling and travel APIs, and it is intended as a practical example of combining LangGraph agents with real-world applications.