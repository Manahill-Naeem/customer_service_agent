from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled,function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
# from whatsapp import send_whatsapp_message
import asyncio
import chainlit as cl


load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)


@function_tool
def customer_service_tool(
    query_type: str,
    product_name: str = None,
    order_id: str = None,
    issue_description: str = None
) -> str:
    """
    Provides customer service information, handles common queries, or retrieves order details.

    Args:
        query_type (str): The type of query (e.g., "product_info", "shipping_info", "return_policy", "order_status", "tech_support").
        product_name (str, optional): The name of the product if the query is product-specific.
        order_id (str, optional): The order ID if checking order status.
        issue_description (str, optional): A description of the technical issue for support.

    Returns:
        str: The response to the customer service query.
    """
    if query_type == "product_info":
        if product_name:
            # Simulate a database lookup for product info
            products = {
                "smartphone": "Our latest smartphone features a 6.7-inch OLED display, 128GB storage, and a triple camera system.",
                "laptop": "This laptop comes with an Intel i7 processor, 16GB RAM, and a 512GB SSD, perfect for productivity.",
                "headphones": "Noise-cancelling over-ear headphones with 30-hour battery life and superior sound quality."
            }
            info = products.get(product_name.lower())
            if info:
                return f"Here is the information for {product_name}: {info}"
            else:
                return f"I couldn't find information for the product: {product_name}. Could you please be more specific?"
        else:
            return "Please specify which product you need information about."

    elif query_type == "shipping_info":
        return "Standard shipping takes 5-7 business days. Express shipping is available for an additional fee and takes 2-3 business days."

    elif query_type == "return_policy":
        return "You can return most items within 30 days of purchase, provided they are in their original condition with all packaging. Please visit our website for the full return policy."

    elif query_type == "order_status":
        if order_id:
            # Simulate an order lookup
            mock_orders = {
                "ORD12345": {"status": "Shipped", "eta": "July 28, 2025"},
                "ORD67890": {"status": "Processing", "eta": "August 1, 2025"}
            }
            status = mock_orders.get(order_id)
            if status:
                return f"Order {order_id} status: {status['status']}. Estimated delivery: {status['eta']}."
            else:
                return f"I couldn't find an order with ID: {order_id}. Please double-check the ID."
        else:
            return "Please provide your order ID to check the status."

    elif query_type == "tech_support":
        if issue_description:
            # In a real scenario, this would log the issue, provide basic troubleshooting, or suggest contacting live support.
            return f"Thank you for describing your issue: '{issue_description}'. For immediate assistance, please visit our FAQ page or connect with a live agent during business hours."
        else:
            return "Please describe your technical issue so I can assist you."

    else:
        return "I can help with product information, shipping, returns, order status, and technical support. How can I assist you?"

# Customer Service Agent
customer_service_agent = Agent(
    name="Customer Service Bot",
    instructions="""
    You are a helpful customer service assistant for a business.
    Use the provided tools to answer customer queries about products, shipping, returns, order status, and technical support.
    Be concise and professional.
    """,
    model=model,
    tools=[customer_service_tool, ] 
)


@cl.on_chat_start
async def start():
    cl.user_session.set("history",[])
    await cl.Message("Hello! I'm your Customer Service Assistant. How can I help you today?").send()


# Runner
@cl.on_message
async def main(message:cl.Message):
    await cl.Message("Thinking...").send() 
    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})
    
    result = Runner.run_sync(
        starting_agent=customer_service_agent,
        input= history
    )
    
    
    history.append({"role": "assistant", "content": result.final_output})
    
    cl.user_session.set("history",history)
    
    await cl.Message(content=result.final_output).send() 