import re

from core.llm_chat import LLMChat
from core.react import ReActBot
from core.planner import Planner
from core.step_manager import Step
from core.llm_validator import Validator
import core.tools as T

def run():
    print("Build web application...")

    background = """You are a full stack developer, always deliver best quality application. You need to make sure devlivered application meet request. 
    Develop a new the application or modify existing application based on user's request.
    Create a new folder if it is a new project. Only start up service in the end of development."""

    knowledge=""
    
    #request = "Build a react web application, click button will popup hello world on the screen."

    request = """Use python to build a web application, click button will popup current time on the screen. The current time should be obtained from backend python service. """
    
    # request = """Modify the current code in time_popup_app and make sure the application satisfy the following requirement: 
    # use python to build a web application, click button will popup current time on the screen. The current time should be obtained from backend python service. """
    
    #request = """modify code in app.py and static. add an input box on the page to accept user's name. after click button, the popup should display username and current time"""


    planner = Planner(model_type = 'BASIC')

    validator=Validator(model_type = 'ADVANCED')

    tools=[T.save_code_to_file,T.read_code_from_file,T.execute_command_line,T.write_code,T.modify_code]
    react_chat=ReActBot(tools=tools,model_type = 'BASIC')

    index=1

    completed_steps=[]

    steps:list[Step] = planner.plan_with_template_format(request, background=background,knowledge=knowledge)

    while len(steps)>0:

        is_rerun=True
        suggestions=""
        
        step=steps.pop(0)

        while is_rerun:
            # TODO: rerun with reversed steps
            step_response, whole_process= react_chat.invoke(query=step.description,suggestions=suggestions)

            validator_response=validator.validate(step.description,step_response)
            decision, total_score, scores,suggestions = validator.parse_scored_validation_response(validator_response)
            print(validator_response)
            print("Total Score:", total_score)
            print("Scores by Criterion:", scores)
            print("Final Decision:", decision)
            print("Suggestion:", suggestions)

            if decision=="Accept Output":
                is_rerun=False
                suggestions=""


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


if __name__ == "__main__":
    run()