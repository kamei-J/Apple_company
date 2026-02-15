from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import SystemMessage, ToolMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages 
from langchain.agents import create_agent

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

tavily_client = TavilyClient(api_key="tvly_API_KEY")

@tool
def support(query: str) -> str:
    """Provides apple phone support information """
    return (
        "Apple Support provides help for devices, Apple ID, "
        "repairs, warranty, and software troubleshooting."
    )



@tool
def sell(query: str) -> str:
    """Provides information about Apple product related query"""

    apple_products = {
        "iphone": "iPhone is Apple's smartphone line.",
        "macbook": "MacBook is Apple's laptop computer.",
        "ipad": "iPad is Apple's tablet device.",
        "apple watch": "Apple Watch is Apple's smartwatch."
    }
    
    for key in apple_products:
        if key in query.lower():
            return apple_products[key]
    
    return "No matching Apple product found."


@tool
def weight(query: str) -> str:
    """Provide information about apple product only"""
    weights = {
    }
    
    for key in weights:
        if key in query.lower():
            return weights[key]
    
    return "Weight information not found for that Apple product."


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


agent = create_agent(
    model=llm,
    tools=[support, sell, weight],
    system_prompt= "You are an AI assistant for Apple Inc. " \
    "You ONLY answer questions related to Apple products, support, or product weight. " \
    "If the question is unrelated to Apple products, politely refuse. Always use tools when product information is required."
)

def run_agent():
    print("\n Apple Agent Ready (type 'exit' to quit)\n")

    while True:
        user_input = input("Ask about Apple products: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent.invoke({
            "messages": [HumanMessage(content=user_input)]
        })

        print("\nAnswer:")
        print(result["messages"][-1].content)
        print()

run_agent()