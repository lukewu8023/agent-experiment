from langchain_core.tools import Tool,tool
from typing import Annotated, List
from core.llm_chat import LLMChat
import subprocess
import time
import os
import select
import signal
import fcntl


@tool
def read_code_from_file(file_path:Annotated[str,"file path to save the code"]):
    """Read code in given file"""
    print("Tool: read_code_from_file")
    print("File Path:",file_path)

    try:
        with open(file_path,"r",encoding="utf-8") as f:
            code=f.read()
    except Exception as e:
        return f"read code from file failed: {e}"

    return code


@tool
def save_code_to_file(code:Annotated[str,"Complete code save to one file"],
                      file_path:Annotated[str,"file path to save the code"]):
    """Create a file with file_path and save the code given in that file"""
    print("Tool: save_code_to_file")
    print("Code:",code)
    print("File Path:",file_path)

    try:
        with open(file_path,"w",encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        return f"save code to file failed: {e}"

    return f"code has been successfully saved to {os.path.abspath(file_path)}"

def set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

@tool
def execute_command_line(shell_command:Annotated[str,"Shell command to be executed in python subprocess"],
                         is_run_asynchronously:Annotated[bool,"if true, use subprocess.Popen without waiting for it to complete. If no, use subprocess.run, wait for finish and return"]):
    """Execute the command by python's subprocess.Popen or subprocess.run based on is_run_asynchronously and get the response. 
is_run_asynchronously is usefull when the command should keep running in background. 
Note only each execution is in the same session, the session will end after exit"""
    print("Tool: execute_command_line")
    print("Command:",shell_command)
    print("is_run_asynchronously:",is_run_asynchronously)


    process = subprocess.Popen(
            shell_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            preexec_fn=os.setsid
            )

    if is_run_asynchronously:
        set_nonblocking(process.stdout)
        set_nonblocking(process.stderr)
       
        time.sleep(10) # sleep a period before checking error
        stdout_ready, stderr_ready, _ = select.select([process.stdout], [process.stderr], [], 0)
        
        if stderr_ready:
            stderr = process.stderr.read(1024)
            stdout = process.stdout.read(1024)
            return f"stdout: {stdout}\n stderr: {stderr} The PID is: {process.pid}"
        else:
            response="No immediate errors. Process continues running in the background.The PID is: {process.pid}"
       

    else:
        try:
            # Poll the process for completion and set a timeout
            stdout, stderr = process.communicate(timeout=5*60)
            response=f"stdout: {stdout}\n stderr: {stderr}"
            
        except subprocess.TimeoutExpired:
            response="The command took too long and was terminated. Should the command run in async?"
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send SIGTERM to the process group
            
            # Kill the process
            process.kill()
            
            # Wait for the process to terminate
            process.wait()
            

    

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
def modify_code(language:Annotated[str,"the coding language"],
                file_path:Annotated[str,"file path of current code"],
                task:Annotated[str,"description of task the code need to achive"]):
    """Modify current code with given language to accomplish the task"""

    print("Tool: modify_code")
    print("file_path:",file_path)
    print("language:",language)
    print("task:",task)

    current_code=read_code_from_file(file_path)

    llm=LLMChat()
    system_prompt=f"""You are a {language} developer. Modify code based on user's query. 
You must output the complete code only and use comments to explain the code.

<current_code>
{current_code}
</current_code>
"""
    response=llm.prompt_respond(task, system_prompt)

    return response

@tool
def human_for_help(action:Annotated[str,"description of action that need human to do manully"]):
    """You can ask human for assistant to complete one single action such as: download a file, install a software...
    You need to provide the action instruction. Only ask human for assistant when is nessasary."""

    print("Tool: human_for_help")
    print("action:",action)

    response=input("Type the result after perform the action")

    return response