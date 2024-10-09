class Node:
    threshold = 0.8  # Example threshold for validation score

    def __init__(self, task_name, task_description):
        self.task_name = task_name
        self.task_description = task_description
        self.next_node = None
        self.execution_results = []
        self.validation_scores = []
        self.failed_attempts = 0

    def add_execution_result(self, result, score):
        self.execution_results.append(result)
        self.validation_scores.append(score)
        if score < self.threshold:
            self.failed_attempts += 1
        else:
            self.failed_attempts = 0

    def set_next_node(self, next_node):
        self.next_node = next_node