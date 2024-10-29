from core.llm_chat import LLMChat
from core.context_manager import ContextManager
from core.planner import Planner

from prompt.coding import CODE_GENERATION_PROMPT
from strategy.replan.graph import Graph
from strategy.replan.node import Node

# Not in used
def run():
    print("Make a cake...")

    request = "Provide details to make a cake."

    planner = Planner()
    steps = planner.plan(request)
    graph = Graph()

    previous_node = None
    for index, step in enumerate(steps, start=1):
        # Create the graph and add nodes

        node = graph.add_node(step.name, step.description)

        # Set the flow
        if previous_node is not None:
            previous_node.set_next_node(node)
            previous_node = node

    print(graph.summarize)
    
    chat = LLMChat()
    context_manager = ContextManager()

    # Execute the flow
    # TODO: implement the graph flow execution
    # problem_node = flow_action(graph, "Task A", example_execution_function)

    # for index, step in enumerate(steps, start=1):

    #     # TODO: use tool to get result

    #     context_response = chat.context_respond(context_manager.context_to_str(), step.description)
    #     step_number = f"Step {index}"
    #     context = f"{context_response['messages'][0]}: \n{context_response['answer']}"
    #     context_manager.add_context(step_number, context)

    # response = chat.context_respond(context_manager.context_to_str(), request+CODE_GENERATION_PROMPT)

    # return response

if __name__ == "__main__":
    run()