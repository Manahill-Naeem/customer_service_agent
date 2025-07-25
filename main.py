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
                "handmade pearl bag": {
                "description": "Our exquisite handmade pearl bag is meticulously crafted with individually selected lustrous pearls, featuring a durable satin lining and a secure magnetic snap closure, perfect for adding a touch of elegance to any evening ensemble or special occasion.",
                "price_range_PKR": "PKR 2,500 - PKR 10,000+",
                "notes": "Prices vary widely based on the quality and size of pearls (real vs. artificial), the intricacy of the design, and overall craftsmanship. More elaborate designs with genuine pearls can command higher prices."
                 },
                "handcrafted bouquet": {
                "description": "This stunning handcrafted bouquet features a vibrant assortment of premium artificial silk flowers, including realistic roses, delicate peonies, and lush eucalyptus, artfully arranged to create a timeless and everlasting display. Each stem is wired for easy posing, and the bouquet is hand-tied with a beautiful satin ribbon.",
                "price_range_PKR": "PKR 1,500 - PKR 8,000+",
                "notes": "The price depends on the type and quality of artificial flowers, the size and complexity of the arrangement, and additional embellishments. Bouquets using higher-grade silk flowers and intricate designs will be at the higher end."
                 },
                "crystal bag": {
                "description": "Dazzle with our luxurious crystal bag, intricately adorned with hundreds of sparkling, high-quality rhinestones on a sturdy metallic frame. This eye-catching clutch includes a detachable chain strap for versatility and a compact interior, ideal for carrying your essentials with unparalleled glamour.",
                "price_range_PKR": "PKR 7,500 - PKR 30,000+",
                "notes": "Prices are influenced by the type and number of crystals (e.g., glass rhinestones vs. higher-grade crystals), the material of the bag's frame, the complexity of the crystal work, and the brand or designer."
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
    You are a helpful customer service assistant for Crafted Whispers business.
    Use the provided tools to answer customer queries about products, shipping, returns, order status, and technical support.
    Be concise and professional.
    """,
    model=model,
    tools=[customer_service_tool, ] 
)


@cl.on_chat_start
async def start():
    cl.user_session.set("history",[])
    await cl.Message("Hello! I'm your Customer Service Assistant of Crafted Whispers. How can I help you today?").send()


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
