from core.llm_chat import LLMChat
from core.context_manager import ContextManager
from core.planner import Planner
from core.llm_validator import LLMValidator

from prompt.coding import CODE_GENERATION_PROMPT
from strategy.replan.replan import PlanGraph, Node

# # Create a plan graph
# plan_graph = PlanGraph()

# # Create nodes
# node_a = Node(
#     id='A',
#     task_description='Main Task',
#     next_nodes=['B'],
#     validation_threshold=0.8,
#     max_attempts=3
# )
# node_b = Node(
#     id='B',
#     task_description='Subtask B',
#     next_nodes=[],
#     validation_threshold=0.8,
#     max_attempts=3
# )

# # Add nodes to the plan
# plan_graph.add_node(node_a)
# plan_graph.add_node(node_b)

# # Execute the plan
# plan_graph.execute_plan()

def run():
    print("Make a cake...")

    request = "Provide details to make a cake."

    planner = Planner()
    steps = planner.plan(request)
    plan_graph = PlanGraph()

    previous_node = None
    for index, step in enumerate(steps, start=1):
        # Create the graph and add nodes
        node_id = chr(65 + index - 1)  # Convert index to uppercase alphabetic character using ASCII values
        next_node_id = chr(65 + index) if index < len(steps) else ''

        node = Node(
            id=node_id,
            # task_name=step.name,
            task_description=step.description,
            next_nodes=[next_node_id],
            validation_threshold=0.8,
            max_attempts=3
        )

        setattr(node, f"_Node__str", f"Node {node_id}")

        plan_graph.add_node(node)

        # Set the flow
        if previous_node is not None:
            previous_node.set_next_node(node)
            previous_node = node

    print(plan_graph.summarize_plan)

    plan_graph.execute_plan()

if __name__ == "__main__":
    run()