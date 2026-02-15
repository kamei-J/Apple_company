import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
class QueryRequest(BaseModel):
    query: str

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)
#tools
# 1. support
# 2. product
# 3. vague

@tool
def support(query: str) -> str:
    """
    Support Tool - Handles Apple customer support queries.
    Returns search results to help with:
    - Device troubleshooting
    - Software issues
    - Apple ID problems
    - Warranty and repair information
    - Service center details
    - Billing and subscription support
    - Technical assistance for Apple services
    """
    try:
        chunks = tavily_client.search(query)
        print(f"support tool used, chunk: {chunks}")
        return str(chunks)
    except Exception as e:
        return f"Error searching for support info: {str(e)}"

@tool
def product(query: str) -> str:
    """
    Product Tool - Provides Apple product information.
    Returns search results about:
    - Product specifications
    - Features and comparisons
    - Pricing details
    - Availability
    - Release information
    - Compatibility details
    - Hardware and software descriptions
    """
    try:
        chunks = tavily_client.search(query)
        print(f"product tool used, chunk: {chunks}")
        return str(chunks)
    except Exception as e:
        return f"Error searching for product info: {str(e)}"

@tool
def vague(query: str) -> str:
    """
        Vague Tool
        provides a static messages,use this message to handle query that are:
        - Vague or unclear
        - Related to competitors (e.g., Samsung, Google, Microsoft, etc.)
        - Not related to Apple products or Apple support
        - General technology questions unrelated to Apple

        This tool acts as a fallback for any query that does not clearly belong
        to the Apple Support Tool or Apple Product Tool.
        """
    res = 'hi i am Apple AI assistant. I cannot help you with the following query. I can only help with Apple product/support related queries.'
    print('vague tool is used')
    return res



agent = create_agent(
    model=llm,
    tools=[support, product, vague],
    system_prompt="""You are an Apple AI assistant specialized in helping customers with Apple products and support.

CRITICAL: First, check if the query mentions competitor brands (Nokia, Samsung, Google, Android, Windows, Microsoft, etc.) or is unrelated to Apple. If YES, immediately use the vague tool and do NOT use other tools.

Instructions:
1. Check for competitor/off-topic queries → Use vague tool immediately
2. For Apple troubleshooting and technical issues → Use support tool
3. For Apple product information (specs, features, pricing, availability) → Use product tool

Guidelines:
- Always route competitor brand questions to the vague tool first
- Provide accurate, helpful answers based on search results
- Synthesize search results into clear, concise responses
- Maintain a professional and friendly tone
- Never provide information about non-Apple products or competitors"""
)

@app.get("/")
def read_root():
    return {"Hello": "World"}



@app.post("/query")
def handle_query(request: QueryRequest):
    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": request.query}]}
        )
        final_message = response["messages"][-1]
        content = getattr(final_message, "content", str(final_message))
        return {"agent_response": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

