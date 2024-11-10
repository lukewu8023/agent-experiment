from strategy.replan.node import Node

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, task_name, task_description):
        node = Node(task_name, task_description)
        self.nodes[task_name] = node
        return node

    def get_node(self, task_name):
        return self.nodes.get(task_name)

    def summarize(self):
        summary = []
        for task_name, node in self.nodes.items():
            summary.append({
                'task_name': task_name,
                'next_node': node.next_node.task_name if node.next_node else None,
                'execution_results': node.execution_results,
                'validation_scores': node.validation_scores,
                'failed_attempts': node.failed_attempts
            })
        return summary