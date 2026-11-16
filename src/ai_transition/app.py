import os
import json
from typing import Iterable
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

app = FastAPI(title="Enterprise Customer Intelligence Copilot", version="1.0")

class SupportRequest(BaseModel):
    customer_id: str
    user_query: str

def get_ai_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

def query_billing_database(customer_id: str) -> str:
    print(f"      [System] SELECT * FROM invoices WHERE customer_id = '{customer_id}'...")
    if customer_id == "CUST-4042":
        return "Account is Past Due. Outstanding balance: $4,500. Last payment failed on Nov 1st."
    return "Account is active and in good standing."

async def billing_agent(customer_id: str, query: str, client: AsyncOpenAI)-> str:
    print(f"   [Billing Agent] Analyzing financial request for {customer_id}")

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system",
         "content": f"You are an Enterprise Billing AI assisting Customer ID: {customer_id}. Use your tools to check the customer's account status and provide a professional financial summary."},
        {"role": "user", "content": query}
    ]
    tools: Iterable[ChatCompletionToolParam] = [{
        "type": "function",
        "function": {
            "name": "query_billing_database",
            "description": "Fetch the current billing status and outstanding invoices for a customer.",
            "parameters": {"type": "object", "properties": {"cust_id": {"type": "string"}}, "required": ["cust_id"]}
        }
    }]
    response = await client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages, tools=tools,
                                                    tool_choice="auto")
    msg = response.choices[0].message
    # print(f" 1st response from the billing agent: {msg.content}")

    if msg.tool_calls:
        cust_id = json.loads(msg.tool_calls[0].function.arguments).get("cust_id", customer_id)
        db_result = query_billing_database(cust_id)

        messages.extend([msg, {"role": "tool", "tool_call_id": msg.tool_calls[0].id, "content": db_result}])
        final_res = await client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages)
        return final_res.choices[0].message.content or "Billing resolution failed."

    return msg.content or "No billing data found."


def query_server_logs(customer_id: str) -> str:
    print(f"      [System] POST /api/v1/splunk/search query='error customer:{customer_id}'...")
    if customer_id == "CUST-4042":
        return "FATAL ERROR: NullPointerException in HierarchyManagement API at 04:30 AM UTC. API latency spiked to 6.0s."
    return "No errors found. Systems operating normally."


async def tech_support_agent(customer_id: str, query: str, client: AsyncOpenAI) -> str:
    print(f"   [Tech Support Agent] Analyzing system logs for {customer_id}")

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system",
         "content": f"You are a Level 3 Support AI assisting Customer ID: {customer_id}. Use your tools to check server logs and diagnose the technical issue."},
        {"role": "user", "content": query}
    ]
    tools: Iterable[ChatCompletionToolParam] = [{
        "type": "function",
        "function": {
            "name": "query_server_logs",
            "description": "Fetch recent error logs and system health metrics for a specific customer instance.",
            "parameters": {"type": "object", "properties": {"cust_id": {"type": "string"}}, "required": ["cust_id"]}
        }
    }]

    response = await client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages, tools=tools,
                                                    tool_choice="auto")
    msg = response.choices[0].message
    print(f" 1st response from the support agent: {msg.content}")

    if msg.tool_calls:
        cust_id = json.loads(msg.tool_calls[0].function.arguments).get("cust_id", customer_id)
        log_result = query_server_logs(cust_id)

        messages.extend([msg, {"role": "tool", "tool_call_id": msg.tool_calls[0].id, "content": log_result}])
        final_res = await client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages)
        return final_res.choices[0].message.content or "Technical diagnostic failed."

    return msg.content or "No technical data found."


@app.post("/api/copilot")
async def support_copilot(request: SupportRequest, client: AsyncOpenAI = Depends(get_ai_client)):
    print(f"\n[Supervisor] Received query from {request.customer_id}: '{request.user_query}'")

    # The Supervisor's tools are the actual Sub-Agents!
    supervisor_tools: Iterable[ChatCompletionToolParam] = [
        {
            "type": "function",
            "function": {
                "name": "route_to_billing",
                "description": "Route requests about invoices, payments, subscriptions, or account standing to the Billing Agent.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "route_to_tech_support",
                "description": "Route requests about bugs, errors, latency, outages, or technical issues to the Tech Support Agent.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        }
    ]

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system",
         "content": "You are a Routing Supervisor. Analyze the user's request and delegate it to the correct specialized sub-agent. Do not try to answer the question yourself."},
        {"role": "user", "content": request.user_query}
    ]

    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=supervisor_tools,
        tool_choice="required"  # Force the supervisor to pick a route
    )

    tool_call = response.choices[0].message.tool_calls[0]

    # Execute the routing decision
    if tool_call.function.name == "route_to_billing":
        final_answer = await billing_agent(request.customer_id, request.user_query, client)
        routed_to = "Billing & Finance"
    elif tool_call.function.name == "route_to_tech_support":
        final_answer = await tech_support_agent(request.customer_id, request.user_query, client)
        routed_to = "L3 Tech Support"
    else:
        final_answer = "Error: Invalid agent routing."
        routed_to = "None"

    return {
        "customer_id": request.customer_id,
        "handled_by": routed_to,
        "resolution": final_answer
    }