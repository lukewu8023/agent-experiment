from core.llm_chat import LLMChat
from core.context_manager import ContextManager
from core.planner import Planner

from prompt.build_web_app import BUILD_WEB_APP_KNOWLEDGE
from prompt.coding import CODE_GENERATION_PROMPT

def run():
    print("Build web application...")

    request = "Build a react web application, click button will popup hello world on the screen."

    planner = Planner()
    background = "You are a web developer, always deliver best quality web application"
    knowledge = BUILD_WEB_APP_KNOWLEDGE
    steps = planner.plan(request, background=background, knowledge=knowledge)

    chat = LLMChat()
    context_manager = ContextManager()

    for index, step in enumerate(steps, start=1):

        # TODO: use tool to get result

        context_response = chat.context_respond(context_manager.context_to_str(), step.description)
        step_number = f"Step {index}"
        context = f"{context_response['messages'][0]}: \n{context_response['answer']}"
        context_manager.add_context(step_number, context)

    response = chat.context_respond(context_manager.context_to_str(), request+CODE_GENERATION_PROMPT)

    return response

if __name__ == "__main__":
    run()