import os
import sys
import certifi
from pathlib import Path
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

# ==========================================
# Environment configuration
# ==========================================

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
print("OPENWEATHER_API_KEY: ", OPENWEATHER_API_KEY)

# Automatically find the current project folder.
# This replaces the hard-coded Windows paths.
PROJECT_DIR = Path(__file__).resolve().parent
WEATHER_SERVER_PATH = PROJECT_DIR / "custom_weather_mcp_server.py"
print("WEATHER_SERVER_PATH: ", WEATHER_SERVER_PATH)

# Preserve the complete Windows environment when starting local stdio MCP Server
AVIATION_ENV = os.environ.copy()
AVIATION_ENV["AVIATIONSTACK_API_KEY"] = (AVIATIONSTACK_API_KEY or "")

WEATHER_ENV = os.environ.copy()
WEATHER_ENV["OPENWEATHER_API_KEY"] = (OPENWEATHER_API_KEY or "")

# ==========================================
# LLM
# ==========================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY
)

# ==========================================
# MCP client configuration
# ==========================================

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["aviationstack-mcp"],
            "env": AVIATION_ENV
        },
        "weather": {
            "transport": "stdio",
            # Use the same Python environment that runs app.py.
            # "command": r"C:\TripMate-A-Multiagent-Travel-Planner\.venv\Scripts\python.exe",
            # "command": r"C:\Users\RUKHSAR BANO\.local\bin\python3.11.exe",
            # "command": "uv",
             "command": sys.executable,
            # Automatically use custom_weather_mcp_server.py from the current project directory.
            "args": ["run", "--project", str(PROJECT_DIR), "python", str(WEATHER_SERVER_PATH)],
            "env": WEATHER_ENV,
            "cwd": str(PROJECT_DIR)
        }
    }
)

# ==========================================
# Diagnostic function
# ==========================================

async def get_all_tools():
    """Load each MCP  server separately
    
    A broken server will no longer prevent
    the other working servers from loading
    """
    
    for server_name in ("tavily", "aviationstack", "weather"):
        try:
            tools = await client.get_tools(server_name=server_name)
            
            print(f"Available tools from {server_name} MCP:\n")
            for tool in tools:
                print(tool.name)
        except Exception as e:
            # print(f"Could not connect to {server_name} MCP: {e}")
            import traceback
            print(f"Could not connect to {server_name} MCP")

            traceback.print_exception(
                type(e),
                e,
                e.__traceback__
            )
    
# ==========================================
# Tavily MCP tool
# ==========================================

tavily_tool = None # contains the object of the required tool

async def initialize_tavily_tool():
    """
    Initialize only Tavily.

    Previously this function initialized all MCP servers,
    so an AviationStack or Weather failure also caused
    Tavily hotel search to fail.
    """
    global tavily_tool
    
    if tavily_tool is not None:
        return
    
    tools = await client.get_tools(server_name="tavily")
    tools_by_name = {tool.name: tool for tool in tools}
    
    tavily_tool = tools_by_name.get("tavily_search")
    
    if tavily_tool is None:
        available_tools = ", ".join(tools_by_name.keys())
        
        raise RuntimeError(
            "Tavily MCP connected, but the "
            "'tavily_search' tool was not found. "
            f"Available tools: "
            f"{available_tools or 'none'}"
        )

async def tavily_mcp_search(query: str):
    await initialize_tavily_tool()
    result = await tavily_tool.ainvoke({
        "query": query
    })
    return result

# ==========================================
# AviationStack MCP tool
# ==========================================

aviation_tools = {}

async def initialize_aviation_tools():
    global aviation_tools
    if aviation_tools:
        return
    
    # Load tools available in AviationStack MCP.
    tools = await client.get_tools(server_name="aviationstack")
    tools_by_name = {tool.name: tool for tool in tools}
    
    if not tools_by_name:
        raise RuntimeError("AviationStack MCP connected but returned no tools.")
    
async def avaition_mcp_search(tool_name: str, tool_args: dict = None):
    await initialize_aviation_tools()
    tool = aviation_tools.get(tool_name)
    
    if tool is None:
        available_tools = ", ".join(sorted(aviation_tools.key()))
        raise ValueError(
            f"AviationStack tool '{tool_name}' was not found. "
            f"Available tools: {available_tools or 'none'}"
        )

    result = await tool.ainvoke(tool_args or {})
    return result

# ==========================================
# Weather MCP tools
# ==========================================

weather_tool = None
forecast_tool = None

async def initialize_weather_tools():
    global weather_tool
    global forecast_tool
    
    if (weather_tool is not None and forecast_tool is not None):
        return
    
    if not WEATHER_SERVER_PATH.exists():
        raise FileNotFoundError(f"Weather MCP server file was not found: {WEATHER_SERVER_PATH}")
    
    # Load only Weather.
    tools = await client.get_tools(server_name="weather")
    
    tools_by_name = {tool.name: tool for tool in tools}
    
    weather_tool = tools_by_name.get("get_current_weather")
    forecast_tool = tools_by_name.get("get_weather_forecast")
    
    missing_tools = []
    if weather_tool is None: missing_tools.append("get_current_weather")
    if forecast_tool is None: missing_tools.append("get_weather_forecast")
    
    if missing_tools:
        available_tools = ', '.join(tools_by_name.keys())
        raise RuntimeError(f"Missing Weather MCP tools: {', '.join(missing_tools)}."
            f"Available tools: {available_tools or 'none'}")
    
async def weather_mcp_server(city: str):
    await initialize_weather_tools()
    result = await weather_tool.ainvoke({
        "city": city
    })
    return result

async def forecast_mcp_server(city: str):
    await initialize_weather_tools()
    result = await forecast_tool.ainvoke({
        "city": city
    })
    return result

# ==========================================
# Destination extractor
# ==========================================

def extract_destination(query: str):
    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """
    
    response = llm.invoke(prompt)
    
    return response.content.strip()
    