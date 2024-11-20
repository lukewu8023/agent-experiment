from pydantic import BaseModel
from typing import Any


class Action(BaseModel):
    thought:str
    action:str
    action_input:str
    oberservation:str=""

    def to_string(self,keep_thought_prefix=True):

        if keep_thought_prefix:
            thought_str="Thought: "+self.thought+"\n"
        else:
            thought_str=self.thought+"\n"

        return thought_str+ \
               "Action: "+self.action+"\n"+ \
               "Action Input: "+self.action_input+"\n"+ \
               "Observation: "+self.oberservation
    
