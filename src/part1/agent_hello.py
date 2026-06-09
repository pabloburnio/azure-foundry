import os
from urllib import response
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.core.exceptions import ResourceNotFoundError
from dotenv import load_dotenv
from openai import NOT_GIVEN, OpenAI

load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")
AGENT_NAME = os.environ.get("AGENT_NAME", "customer-service-agent")
AGENT_INSTRUCTIONS = os.environ.get(
    "AGENT_INSTRUCTIONS",
    "You are an assistant that helps users with their online orders. "
    "If the user asks about the status of their order, respond with a fake order status."
    "If they ask about which orders they mentioned, please provide order details like order numbers."
    "For any other questions, respond with 'Sorry, I can only help with order status inquiries.'",
)


def create_agent(project: AIProjectClient):
    try:
        return project.agents.get(agent_name=AGENT_NAME)
    except ResourceNotFoundError:
        return project.agents.create_version(
            agent_name=AGENT_NAME,
            definition=agent_v1_initial(),
            description="Initial version of the customer service agent.",
        )


def agent_v1_initial():
    return PromptAgentDefinition(model=MODEL_NAME, instructions=AGENT_INSTRUCTIONS)


def run_conversation(client: OpenAI, agent, query, previous_response_id=NOT_GIVEN):
    response = client.responses.create(
        model=MODEL_NAME,
        input=[{"role": "user", "content": query}],
        previous_response_id=previous_response_id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        stream=False,
    )

    return response


def cleanup(project: AIProjectClient, agent_name):
    project.agents.delete(agent_name=agent_name, force=True)
    pass


if __name__ == "__main__":
    credential = DefaultAzureCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

    agent = create_agent(project)
    client = project.get_openai_client()

    previous_response_id = NOT_GIVEN
    while True:
        query = input("Agent: How can I help? (type 'exit' to quit): ")
        if query.lower() in ("exit", "quit"):
            break
        response = run_conversation(client, agent, query, previous_response_id)
        previous_response_id = response.id
        print(f"Agent: {response.output_text}")

    # cleanup(project, agent)
