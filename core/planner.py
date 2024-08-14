import json

from core.llm_chat import LLMChat
from core.step_manager import Step

from prompt.plan import PLAN_FORMAT

class Planner:

    def __init__(self):
        self.steps = []

    def plan(self, request, **kwargs):

        plan_content = ""
        background = ""
        if 'background' in kwargs:
            background = kwargs['background']
        plan_content += f"<background>\n{background}\n</background>\n"
        knowledge = ""
        if 'knowledge' in kwargs:
            knowledge = kwargs['knowledge']
        plan_content += f"<knowledge>\n{knowledge}\n</knowledge>\n"
        plan_content += PLAN_FORMAT

        chat = LLMChat()
        
        response = chat.prompt_respond(request, plan_content).replace("```json", '').replace("```", '')
        steps_data = json.loads(response)["steps"]
        for step_data in steps_data:
            step = Step(step_data["step_name"], step_data["step_description"])
            self.steps.append(step)
        return self.steps
