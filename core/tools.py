from langchain_core.tools import Tool,tool
from typing import Annotated, List
from core.llm_chat import LLMChat
import subprocess



@tool
def save_code_to_file(code:Annotated[str,"Complete code save to one file"],
                      file_path:Annotated[str,"file path to save the code"]):
    """Create a file with file_path and save the code given in that file"""
    print("Tool: save_code_to_file")
    print("Code:",code)
    print("File Path:",file_path)

    with open(file_path,"w",encoding="utf-8") as f:
        f.write(code)

    return f"code has been successfully saved to {file_path}"


@tool
def execute_command_line(shell_command:Annotated[list[str],"Shell command to be executed in python subprocess"],
                         is_run_asynchronously:Annotated[bool,"if yes, use Popen without waiting for it to complete. If no, use run, wait for finish and return"]):
    """Execute the command by python's subprocess.Popen or subprocess.run based on  is_run_asynchronously and get the response. """
    print("Tool: execute_command_line")
    print("Command:",shell_command)
    print("is_run_asynchronously:",is_run_asynchronously)

    if is_run_asynchronously:
        process = subprocess.Popen(
            shell_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )

        # Immediately return the process object to interact with stdout and stderr later
        stdout, stderr = process.communicate(timeout=5)
        response=f"stdout: {stdout}\n stderr: {stderr}"
       

    else:
        result = subprocess.run(shell_command, capture_output=True, text=True)
        response=f"stdout: {result.stdout}\n stderr: {result.stderr}"

    

    return response

@tool
def execute_command_line_mock(shell_command:Annotated[list[str],"Shell command to be executed in python subprocess.run"]):
    """Execute the command by python's subprocess.run and get the response"""
    print("Tool: execute_command_line")
    print("Command:",shell_command)

    result="Succeed"
    return f"Response of the command: {result}"


@tool
def write_code(language:Annotated[str,"the coding language"],
               task:Annotated[str,"description of task the code need to achive"]):
    """write code with given language to accomplish the task"""

    print("Tool: write_code")
    print("language:",language)
    print("task:",task)

    llm=LLMChat()
    system_prompt=f"""You are a {language} developer. Write code based on user's query. 
    You must output the code only and use comments to explain the code."""
    response=llm.prompt_respond(task, system_prompt)

    return response


@tool
def human_for_help(action:Annotated[str,"description of action that need human to do manully"]):
    """You can always ask human for assistant to complete one single action such as: download a file, install a software...
    You need to provide the action instruction"""

    print("Tool: human_for_help")
    print("action:",action)

    response=input("Type the result after perform the action")

    return response