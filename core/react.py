import json
from typing import List,Union
import re

from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage

from core.config import Config
from core.action import Action

from prompt.system_context import SYSTEM_CONTEXT_WITH_TOOLS2

class ReActBot(object):

    def __init__(self,model_type = 'BASIC',tools=[]):

        if model_type == 'ADVANCED':
            model = Config.OPENAI_MODEL_ADVANCED
        else:
            model = Config.OPENAI_MODEL_BASIC

        self.chat = ChatOpenAI(model=model, temperature=0.1, max_tokens=4096,verbose=True)

        self.stop=[
            f"\nObservation:",
            f"\n\tObservation:",
        ]
        self.chat=self.chat.bind(stop=self.stop)
        self.tools:list[Tool]=tools

        self.messages=[]
        self.intermediate_steps:List[Action]=[]

        self.prompt = PromptTemplate(
        template=SYSTEM_CONTEXT_WITH_TOOLS2,
            input_variables=["input", "agent_scratchpad","history_message"],
            partial_variables={
                "tool_names": ", ".join([tool.name for tool in self.tools]),
                "tool_descriptions": "\n".join(
                    [f"{tool.name}: {tool.description}\n{tool.args}" for tool in self.tools]
                ),
            },
        )
        
        self.agent=self.prompt | self.chat | self.parse_output


    def invoke(self,query,suggestions=""):

        finished=False
        retry=0
        query=query+suggestions

        while retry<3 and (not finished):
            try:
                agent_scratchpad=self._build_agent_scratchpad()
                response=self.agent.invoke({"input":query,"agent_scratchpad":agent_scratchpad,"history_message":"\n".join(self.messages)})

                if isinstance(response,str):
                    finished=True

                    current_message=f"""Command: {query}
    {agent_scratchpad}
    Final Answer: {response}
    """
                    self.messages.append(current_message)

                    self.intermediate_steps=[]
                elif isinstance(response,Action):
                    try:
                        observation=self.execute_action(response)
                        response.oberservation=observation
                        self.intermediate_steps.append(response)
                    except Exception as e:
                        pass
                    
                else:
                    retry+=1

            except Exception as e:
                print("Generate failed, retry.",str(e))
                retry+=1
        
        if retry>=3:
            response="The step cannot be executed correctly."

        return response,current_message
    
    def execute_action(self,action:Action):
        for tool in self.tools:
            if action.action==tool.name:
                input_dict=json.loads(action.action_input.replace("```json", '').replace("```", ''))
                result=tool.invoke(input_dict)
                return result
        
        raise Exception("Not Found tool :{action.action}")
    
    def _build_agent_scratchpad(self):
        outputs=[]
        
        for step in self.intermediate_steps:
            outputs.append(step.to_string())

        return "\n".join(outputs)
    
    def parse_output(self,message: AIMessage)-> Union[Action, str]:
        text = message.content

        action_regex =r"(?:Thought\s*:)?s*(.*?)\n\s*Action\s*:\s*(.*?)\n\s*Action\s*Input\s*:\s*(.*)"

        final_answer_regex=r"Final\s*Answer\s*:\s*(.*)\n?"

        m_final_answer=re.search(final_answer_regex,text)
        m_action=re.search(action_regex,text)

        if m_final_answer and m_action:
            if m_final_answer.start()<m_action.start():
                return text[m_final_answer.start(1):m_action.start()]
        

        if m_final_answer:
            return m_final_answer.group(1)
        
        if m_action:
            return Action(thought=m_action.group(1),action=m_action.group(2).strip(),action_input=m_action.group(3).strip())
        
        return Exception(f"Could not parse LLM output: `{text}`")
    