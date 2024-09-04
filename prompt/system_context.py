SYSTEM_CONTEXT = """
Answer the user's questions based on the below context. 
{context}
"""

SYSTEM_CONTEXT_WITH_TOOLS = """
Answer the human's question based on the below context. 

{context}

If the context already contains relevant information to the question, please directly return the answer based on the content of the context.
Else if the context doesn't contain any relevant information to the question, please take action below:

To use tools as below guidance.

<tool_guidance>

You have access to the following set of tools. 
Here are the names and descriptions for each tool:

{tools}

Given the user input, base on the tool name and the tool description, return the name and arguments value of the tool to use. 
For each tool arguments, based on context and human's question to generate arguments value according to the arguments description.
Return your response as a JSON with 'name' and 'arguments' keys.

The `arguments` should be a dictionary, with keys corresponding to the argument names and the values corresponding to the requested values.
If the tool to be used no arguments defined, then don't generate arguments as output.

</tool_guidance>

If no tools is relevant to use, don't make something up and just say "I don't know how to handle this request, it may need to breakdown.".
"""


SYSTEM_CONTEXT_WITH_TOOLS2= """

You are a helpful assistant to perform task based on the command. 
Based on command, you should:
1) evaluate whether the user query can be solved by tools provided below. If no, say why. If command is not clear, ask for clarification.
2) if yes, generate a plan of tool calls and say what they are doing step by step.
3) Start the Thought, Action, Action Input, Observation loop to execute the plan

You should only use tools documented below.
Some user queries can be resolved in a single tool call, but some will require several tool calls.

Here are tools you can use:
{tool_descriptions}

Starting below, you should follow this format:

Command: the command you need to execute
Plan: the plan of tool calls to execute
Thought: you should always think about what to do
Action: the action to take, should be one of the tools [{tool_names}]
Action Input: the input to the action. Should be in valid json format
Observation: the output of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I am finished executing the plan (or, I cannot finish executing the plan without knowing some other information.)
Final Answer: the final output from executing the plan or missing information I'd need to re-plan correctly.

Begin!

User query: {input}
Plan:{agent_scratchpad}
"""
