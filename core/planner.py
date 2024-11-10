import json

from core.step_manager import Step

from prompt.plan import PLAN_FORMAT,RE_PLAN_FORMAT,LOW_LEVEL_PLANNER_FORMAT,REVIEW_FORMAT
from core.llm_chat import LLMChat


class Planner:

    def __init__(self,model_type=None):
        self.history_steps=[]
        self.steps = []
        self.chat = LLMChat(model_type)

    def plan_with_template_format(self, request, background="",knowledge=""):

        if knowledge:
            knowledge=f"<knowledge>\n{knowledge}\n</knowledge>\n"

        sys_prompt=PLAN_FORMAT.format(background=background,knowledge=knowledge)
                    
        response = self.chat.prompt_respond(request, sys_prompt).replace("```json", '').replace("```", '')
        steps_data = json.loads(response)["steps"]
        for i,step_data in enumerate(steps_data):
            step = Step(i+1,step_data["step_name"], step_data["step_description"])
            self.steps.append(step)
        return self.steps[:]
    
    def replan(self,request, completed_steps:list[Step], background="",knowledge=""):


        if knowledge:
            knowledge=f"<knowledge>\n{knowledge}\n</knowledge>\n"

        original_plan_str="\n".join(str(step) for step in self.steps)
        completed_steps_str="\n".join([step.get_context_str() for step in completed_steps])


        critiqe_prompt=REVIEW_FORMAT.format(request=request,
                                original_plan=original_plan_str,completed_steps=completed_steps_str)
        critique_response=self.chat.one_time_respond(critiqe_prompt)



        prompt=RE_PLAN_FORMAT.format(background=background,knowledge=knowledge,request=request,
                                     original_plan=original_plan_str,completed_steps=completed_steps_str,criteque=critique_response)
        
        
        
        response = self.chat.one_time_respond(prompt).replace("```json", '').replace("```", '')
        steps_data = json.loads(response)["steps"]

        self.history_steps.append(self.steps)

        remaining_steps=[]

        for i,step_data in enumerate(steps_data):
            step = Step(len(completed_steps)+i+1,step_data["step_name"], step_data["step_description"])
            remaining_steps.append(step)
        
        self.steps=completed_steps+remaining_steps

        return remaining_steps


    def low_level_plan(self,request, step:Step,tools):
        tool_descriptions="\n".join([f"{tool.name}: {tool.description}" for tool in tools])
        prompt=LOW_LEVEL_PLANNER_FORMAT.format(request=request,step=step,tools=tool_descriptions)
        
        
        response = self.chat.one_time_respond(prompt).replace("```json", '').replace("```", '')
        steps_data = json.loads(response)["steps"]

        sub_steps=[]

        for step_data in steps_data:
            sub_step = Step(step_data["step_name"], step_data["step_description"])
            sub_steps.append(sub_step)

        step.add_sub_steps(sub_steps)
        return step