import json
from typing import Dict, Any,List,Union
import re

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.globals import set_debug
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from core.config import Config
from core.validator import Validator
from core.step_manager import Step
from core.action import Action

from prompt.system_context import SYSTEM_CONTEXT, SYSTEM_CONTEXT_WITH_TOOLS,SYSTEM_CONTEXT_WITH_TOOLS2

set_debug(True)

class ReActBot(object):

    def __init__(self,model_type = 'BASIC',tools=[]):

        if model_type == 'ADVANCED':
            model = Config.OPENAI_MODEL_ADVANCED
        else:
            model = Config.OPENAI_MODEL_BASIC

        self.chat = ChatOpenAI(model=model, temperature=0.1, max_tokens=4096, openai_proxy=Config.OPENAI_PROXY,verbose=True)

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


    def invoke(self,query):

        finished=False
        retry=0

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

        return response
    
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
    

class LLMChat:

    def __init__(self, model_type = 'BASIC'):

        if model_type == 'ADVANCED':
            model = Config.OPENAI_MODEL_ADVANCED
        else:
            model = Config.OPENAI_MODEL_BASIC

        self.chat = ChatOpenAI(model=model, temperature=0.1, max_tokens=4096, openai_proxy=Config.OPENAI_PROXY,verbose=True)
        self.chat_history_for_chain = ChatMessageHistory()

    def one_time_respond_str(self, prompt):
 
        output_parser = StrOutputParser()
        chain = self.chat | output_parser
        response = chain.invoke(prompt)
        return response

    def one_time_respond(self, request):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        response = chain.invoke(
            {
                "messages": [
                    HumanMessage(content=request),
                ],
            }
        )
        return response

    def prompt_with_message(self, messages, parameters=None):
        if parameters is None:
            parameters = {}
        prompt = ChatPromptTemplate.from_messages(messages)
        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        response = chain.invoke(parameters)
        return response

    def prompt_respond(self, request, system_prompt):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        response = chain.invoke(
            {
                "messages": [
                    HumanMessage(content=request),
                ],
            }
        )
        return response

    def conversational_respond(self, request):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        # chat_history_for_chain = ChatMessageHistory()
        chain_with_message_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: self.chat_history_for_chain,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        response = chain_with_message_history.invoke(
            {"input": request},
            {"configurable": {"session_id": "unused"}},
        )
        print("[Conversation History Start]")
        print(self.chat_history_for_chain)
        print("[Conversation History End]")
        return response

    def context_respond(self, context_str, messages_str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_CONTEXT,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        context_chain = create_stuff_documents_chain(self.chat, prompt)
        docs = [Document(context_str)]
        print(docs)
        context_entity = lambda data: self._convert(data, docs)
        messages = [messages_str]
        retrieval_chain = RunnablePassthrough.assign(
            context=context_entity,
        ).assign(
            answer=context_chain,
        )
        response = retrieval_chain.invoke(
            {
                "messages": messages,
            }
        )
        return response

    def context_respond_with_tools(self, context_str, tools, messages_str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_CONTEXT_WITH_TOOLS,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        context_chain = create_stuff_documents_chain(self.chat, prompt)

        context_docs = [Document(context_str)]
        print(context_docs)
        context_entity = lambda data: self._convert(data, context_docs)

        tool_strings = []
        for tool in tools:
            args_schema = str(tool.args)
            tool_strings.append(f"Tool name: {tool.name}, Tool description: {tool.description}, Tool args: {args_schema}")
        rendered_tools = "\n".join(tool_strings)
        print(rendered_tools)

        tools_docs = [Document(rendered_tools)]
        print(tools_docs)
        tools_entity = lambda data: self._convert(data, tools_docs)

        messages = [messages_str]
        retrieval_chain = RunnablePassthrough.assign(
            context=context_entity,
            tools=tools_entity
        ).assign(
            answer=context_chain,
        )

        attempt = 0
        while attempt < 3:
            result = retrieval_chain.invoke(
                {
                    "messages": messages,
                }
            )
            validator = Validator()
            try:
                try:
                    answer_data = json.loads(result['answer'])
                except json.JSONDecodeError:  
                    answer_data = result['answer']

                answer_string = json.dumps(answer_data)
                if "\"arguments\": {" in answer_string:
                    tool_name_to_tool = {tool.name: tool for tool in tools}
                    name = answer_data['name']

                    tool_name_to_arguments = {tool.name: tool.args for tool in tools}
                    arg_definition = tool_name_to_arguments[name]
                    arguments = answer_data['arguments']
                    input_args = arguments
                    print(f"arg_definition: {arg_definition}")
                    print(f"input_args: {input_args}")
                    # validator.validate(input_args, arg_definition, validator.ARGUMENTS_NOT_MATCH) #TODO
                    if not self._validate_arguments(input_args,arg_definition):
                        message_str = messages[0]
                        input_args_str = json.dumps(input_args)
                        # new_message_str = message_str + " (the arguments ["+input_args_str+"] are generated incorrectly, please regenerate differently)"
                        new_message_str = message_str + " (do not generate arguments ["+input_args_str+"] which is incorrect, generate different one)"
                        messages[0] = new_message_str
                        raise ValueError("Arguments do not match")
                    
                    requested_tool = tool_name_to_tool[name]
                    response = requested_tool.invoke(arguments)
                else: 
                    response = answer_string
                return response
            except ValueError as error:
                attempt += 1
                print("An error occurred:", error)
                print(f"Attempt {attempt}: Invalid response, retrying...")
        return "Failed to get a valid response after several attempts."

    def _convert(self, data: Dict[str, Any], docs: str):
        return docs
    
    def _validate_arguments(self, input_args, arg_definition):
        if len(arg_definition) != 0:
            for key, value in arg_definition.items():
                if key not in input_args:
                    return False
        else:
            if input_args:
                return False
        return True

    def one_time_respond_with_validation(self, request):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        output_parser = StrOutputParser()
        chain = prompt | self.chat | output_parser
        attempt = 0
        while attempt < 3:
            response = chain.invoke(
                {
                    "messages": [
                        HumanMessage(content=request),
                    ],
                }
            )
            validator = Validator()
            try:
                validator.validate(request, response, validator.CHECK_UNCERTAINTY)
                return response
            except ValueError as error:
                attempt += 1
                print("An error occurred:", error)
                print(f"Attempt {attempt}: Invalid response, retrying...")
        return "Failed to get a valid response after several attempts."
