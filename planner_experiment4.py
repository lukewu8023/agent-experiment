import re

from core.llm_chat import LLMChat,ReActBot
from core.context_manager import ContextManager
from core.planner import Planner
from core.step_manager import Step

from prompt.build_web_app import BUILD_WEB_APP_KNOWLEDGE
from prompt.coding import CODE_GENERATION_PROMPT
import core.tools as T

def run():
    print("Build web application...")

    #request = "Build a react web application, click button will popup hello world on the screen."
    background = "You are a full stack developer, always deliver best quality web application."
    request = """Use python to build a web application, click button will popup current time on the screen. The current time should be obtained from backend python service. """

    
    chat = LLMChat(model_type = 'BASIC')

    planner = Planner(chat)
    knowledge = BUILD_WEB_APP_KNOWLEDGE
    steps:Step = planner.plan(request, background=background,knowledge="")


    context_manager = ContextManager()
    tools=[T.save_code_to_file,T.read_code_from_file,T.execute_command_line,T.write_code,T.modify_code]
    react_chat=ReActBot(tools=tools,model_type = 'BASIC')

    index=1

    completed_steps=[]

    while len(steps)>0:


        step=steps.pop(0)

        step_response = react_chat.invoke(query=step.description)

        step.add_response(step_response)

        completed_steps.append(step)

        steps=planner.replan(request, completed_steps,background=background)



        # step_with_substeps=planner.low_level_plan(request, step,tools)

        # sub_steps=step_with_substeps.sub_steps

        # context_manager = ContextManager()

        # sub_index=1
        # while len(sub_steps)>0:
        #     sub_step=sub_steps[0]
        #     context_response = react_chat.invoke(query=sub_step.description)
        #     step_number = f"Step {index}.{sub_index}"
        #     context = f"{sub_step.description}: \n{context_response}"
        #     context_manager.add_context(step_number, context)

        #     original_tasks="\n".join(str(step) for step in sub_steps)
        #     sub_steps=planner.replan(request, step_with_substeps,tools,context_manager.context_to_str(),original_tasks,completed_tasks=context_manager.context_to_str())

        #     sub_index+=1

        index +=1




    # response = chat.context_respond(context_manager.context_to_str(), request+CODE_GENERATION_PROMPT)

    # return response

def extract_steps(plan_string):
    # Define an empty list to store the steps
    steps = []
    # Extracting step descriptions
    steps = re.findall(r"\d+\.\s(.*?)(?=\n\d+\.\s|\Z)", plan_string, re.DOTALL)
    return steps

if __name__ == "__main__":
    run()