import json
from typing import Dict, Any,List,Union
import re

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.globals import set_debug
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from core.config import Config

from prompt.system_context import SYSTEM_CONTEXT, SYSTEM_CONTEXT_WITH_TOOLS

set_debug(True)


class LLMChat:

    def __init__(self, model_type = 'BASIC',validator=None):

        if model_type == 'ADVANCED':
            model = Config.OPENAI_MODEL_ADVANCED
        else:
            model = Config.OPENAI_MODEL_BASIC

        self.chat = ChatOpenAI(model=model, temperature=0.1, max_tokens=4096,verbose=True)
        self.chat_history_for_chain = ChatMessageHistory()

        self.validator=validator

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
                    # self.validator.validate(input_args, arg_definition, validator.ARGUMENTS_NOT_MATCH) #TODO
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
            try:
                self.validator.validate(request, response, self.validator.CHECK_UNCERTAINTY)
                return response
            except ValueError as error:
                attempt += 1
                print("An error occurred:", error)
                print(f"Attempt {attempt}: Invalid response, retrying...")
        return "Failed to get a valid response after several attempts."
