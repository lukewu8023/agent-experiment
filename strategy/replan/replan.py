from strategy.replan.graph import Graph

def execute_node(node, execution_function):
    result, score = execution_function(node.task_name)
    node.add_execution_result(result, score)
    if node.failed_attempts >= 3:
        return False  # Indicate failure
    return True  # Indicate success

def flow_action(graph, start_task_name, execution_function):
    current_node = graph.get_node(start_task_name)
    while current_node:
        success = execute_node(current_node, execution_function)
        if not success:
            return current_node  # Return the problematic node for replanning
        current_node = current_node.next_node
    return None  # Indicate successful completion of the flow

def generate_replanning_prompt(problem_node, graph_summary):
    prompt = f"""
    The following task flow has encountered a problem at task '{problem_node.task_name}'.
    The task has failed to meet the validation score threshold three times.

    Here is the current task flow summary:
    {graph_summary}

    Please provide a new plan to address the issue. You can either:
    1. Change the tasks next to the problem sub-task (included) to others.
    2. Break down the problem task into further sub-tasks.

    Ensure that the new tasks avoid the same failure reason: {problem_node.execution_results[-1]}.

    Provide the updated task flow in a structured format.
    """
    return prompt

def example_execution_function(task_name):
    # Simulate execution result and validation score
    import random
    result = f"Result of {task_name}"
    score = random.uniform(0, 1)
    return result, score

# Create the graph and add nodes
graph = Graph()
node_a = graph.add_node("Task A")
node_b = graph.add_node("Task B")
node_c = graph.add_node("Task C")

# Set the flow
node_a.set_next_node(node_b)
node_b.set_next_node(node_c)

# Execute the flow
problem_node = flow_action(graph, "Task A", example_execution_function)

# If there's a problem, generate a prompt for the LLM
if problem_node:
    graph_summary = graph.summarize()
    prompt = generate_replanning_prompt(problem_node, graph_summary)
    print(prompt)