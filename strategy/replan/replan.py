from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json

from core.llm_chat import LLMChat
from core.context_manager import ContextManager
from core.llm_validator import LLMValidator
@dataclass
class ExecutionResult:
    output: str
    validation_score: float
    timestamp: datetime

@dataclass
class Node:
    id: str
    # task_name: str
    task_description: str
    next_nodes: List[str] = field(default_factory=list)
    execution_results: List[ExecutionResult] = field(default_factory=list)
    validation_threshold: float = 0.8
    max_attempts: int = 3
    current_attempts: int = 0
    failed_reasons: List[str] = field(default_factory=list)

    def execute(self):
        print(f"Executing Node {self.id}: {self.task_description}")
        result = perform_task(self)
        self.current_attempts += 1
        return result

    def validate(self, result):
        score = evaluate_result(self.task_description, result)
        execution_result = ExecutionResult(
            output=result,
            validation_score=score,
            timestamp=datetime.now()
        )
        self.execution_results.append(execution_result)
        return score

    def should_replan(self):
        last_score = self.execution_results[-1].validation_score if self.execution_results else None
        if last_score is not None and last_score >= self.validation_threshold:
            return False
        elif self.current_attempts >= self.max_attempts:
            failure_reason = f"Failed to reach threshold after {self.max_attempts} attempts."
            self.failed_reasons.append(failure_reason)
            return True
        else:
            return False

@dataclass
class ReplanHistory:
    history: List[Dict] = field(default_factory=list)

    def add_record(self, record):
        self.history.append(record)

@dataclass
class PlanGraph:
    nodes: Dict[str, Node] = field(default_factory=dict)
    start_node_id: Optional[str] = None
    replan_history: ReplanHistory = field(default_factory=ReplanHistory)
    current_node_id: Optional[str] = None

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        if self.start_node_id is None:
            self.start_node_id = node.id

    def execute_plan(self):
        self.current_node_id = self.current_node_id or self.start_node_id
        while self.current_node_id:
            if self.current_node_id not in self.nodes:
                print(f"Node {self.current_node_id} does not exist in the plan. Aborting execution.")
                break
            node = self.nodes[self.current_node_id]
            result = node.execute()
            score = node.validate(result)
            print(f"Node {node.id} execution score: {score}")
            if score >= node.validation_threshold:
                # Move to next node
                if node.next_nodes:
                    self.current_node_id = node.next_nodes[0]  # Simplification: take first next node
                else:
                    print("Plan execution completed successfully.")
                    break
            else:
                if node.should_replan():
                    print(f"Replanning needed at Node {node.id}")
                    failure_info = self.prepare_failure_info(node)
                    prompt = self.generate_llm_prompt(node, failure_info)
                    llm_response = call_llm_api(prompt)
                    adjustments = parse_llm_response(llm_response)
                    if adjustments:
                        self.replan(self.current_node_id, adjustments)
                        # Determine restart node
                        self.current_node_id = self.determine_restart_node(adjustments)
                    else:
                        # Handle parse error
                        print("Could not parse LLM response, aborting execution.")
                        break
                else:
                    # Retry the same node
                    print(f"Retrying Node {node.id}")
                    continue

    def prepare_failure_info(self, node):
        return {
            'failure_reason': node.failed_reasons[-1],
            'execution_history': [
                {
                    'node_id': n.id,
                    'results': [er.validation_score for er in n.execution_results]
                } for n in self.nodes.values()
            ],
            'replan_history': self.replan_history.history
        }

    def generate_llm_prompt(self, node, failure_info):
        plan_summary = self.summarize_plan()
        execution_history = failure_info['execution_history']
        failure_reason = failure_info['failure_reason']
        replan_history = failure_info['replan_history']
        prompt = f"""
    You are an intelligent assistant helping to adjust a task execution plan represented as a graph of subtasks. Below are the details:

    **Current Plan:**
    {plan_summary}

    **Execution History:**
    {execution_history}

    **Failure Reason:**
    {failure_reason}

    **Replanning History:**
    {replan_history}

    **Instructions:**
    - Analyze the failure and decide on one of two actions:
        1. **breakdown**: Break down the failed task into smaller subtasks.
        2. **replan**: Go back to a previous node for replanning.
    - If you choose **breakdown**, provide detailed descriptions of the new subtasks.
    - If you choose **replan**, specify which node to return to and suggest any modifications to the plan after that node.
    - Return your response in the following JSON format (do not include any additional text):

    ```json
    {{
        "action": "breakdown" or "replan",
        "new_subtasks": [  // Required if action is "breakdown"
            {{
                "id": "unique_task_id",
                "task_description": "Description of the subtask",
                "next_nodes": ["next_node_id_1", "next_node_id_2"],
                "validation_threshold": 0.8,
                "max_attempts": 3
            }}
        ],
        "restart_node_id": "node_id",  // Required if action is "replan"
        "modifications": [  // Optional, used if action is "replan"
            {{
                "node_id": "node_to_modify_id",
                "task_description": "Modified description",
                "next_nodes": ["next_node_id_1", "next_node_id_2"],
                "validation_threshold": 0.8,
                "max_attempts": 3
            }}
        ],
        "rationale": "Explanation of your reasoning here"
    }}

    **Note:** Ensure your response is valid JSON, without any additional text or comments.
    """
        return prompt

    def summarize_plan(self):
        summary = ""
        for node in self.nodes.values():
            summary += f"Node {node.id}: {node.task_description}, Next Nodes: {node.next_nodes}\n"
        return summary

    def replan(self, node_id, llm_response):
        # Record the replanning event
        self.replan_history.add_record({
            'timestamp': datetime.now(),
            'node_id': node_id,
            'failure_reason': self.nodes[node_id].failed_reasons[-1],
            'llm_response': llm_response
        })
        # Parsing and applying the LLM response to adjust the plan
        adjustments = parse_llm_response(llm_response)
        apply_adjustments_to_plan(self, node_id, adjustments)

    def determine_restart_node(self, llm_response):
        adjustments = json.loads(llm_response)
        
        if adjustments.get('action') == 'replan':
            restart_node_id = adjustments.get('restart_node_id')
        elif adjustments.get('action') == 'breakdown':
            if adjustments.get('new_subtasks') and len(adjustments.get('new_subtasks')) > 0:
                restart_node_id = adjustments.get('new_subtasks')[0].get('id')
            else:
                print("No subtasks found for breakdown action. Aborting execution.")
                return None
        else:
            print("Unknown action. Aborting execution.")
            return None

        if restart_node_id in self.nodes:
            return restart_node_id
        else:
            print(f"Restart node '{restart_node_id}' does not exist in the plan. Aborting execution.")
            return None
           
def perform_task(node):
    chat = LLMChat()
    context_manager = ContextManager()
    context_response = chat.context_respond(context_manager.context_to_str(), node.task_description)
    step_number = f"Step {node.id}"
    context = f"{context_response['messages'][0]}: \n{context_response['answer']}"
    context_manager.add_context(step_number, context)
    return context_response['answer']

def evaluate_result(rtask_description, result):
    llm_validator = LLMValidator()
    validation_result = llm_validator.validate(rtask_description, result)
    print(validation_result)
    decision, total_score, scores = llm_validator.parse_scored_validation_response(validation_result)
    print("\nTotal Score:", total_score)
    print("Scores by Criterion:", scores)
    print("Final Decision:", decision)
    return total_score / 40

def call_llm_api(prompt):
    # LLM API call
    print("Calling LLM with prompt:")
    print(prompt)

    chat = LLMChat(model_type='ADVANCED')
    response = chat.one_time_respond(prompt).replace("```json", '').replace("```", '')
    data_dict = json.loads(response)
    # steps_data = json.loads(response)["steps"]
    # for step_data in steps_data:
    #     step = Step(step_data["step_name"], step_data["step_description"])
    #     self.steps.append(step)
    formatted_response = json.dumps(data_dict, indent=4)
    print(formatted_response)
    return formatted_response

def parse_llm_response(llm_response):
    try:
        adjustments_dict = json.loads(llm_response)
        adjustments = json.dumps(adjustments_dict, indent=4)
        return adjustments
    except json.JSONDecodeError as e:
        print("Failed to parse LLM response as JSON:", e)
        # Handle error, maybe retry or report failure
        return None
    
def apply_adjustments_to_plan(plan_graph, node_id, adjustments_str):
    # Apply the adjustments to the plan
    adjustments = json.loads(adjustments_str)
    if adjustments['action'] == 'breakdown':
        # Remove the problematic node and add new subtasks
        original_node = plan_graph.nodes.pop(node_id)
        for subtask in adjustments['new_subtasks']:
            new_node = Node(
                id=subtask['id'],
                # task_name=subtask['task_name'],
                task_description=subtask['task_description'],
                next_nodes=original_node.next_nodes,
                validation_threshold=original_node.validation_threshold,
                max_attempts=original_node.max_attempts
            )
            plan_graph.add_node(new_node)
            # Update connections
            # For simplicity, assume linear execution of new subtasks
        # Reconnect previous nodes to the first new subtask
        for nid, node in plan_graph.nodes.items():
            if node_id in node.next_nodes:
                node.next_nodes.remove(node_id)
                node.next_nodes.append(adjustments['new_subtasks'][0]['id'])
    elif adjustments['action'] == 'replan':
        # Implement the replanning logic based on adjustments provided
        restart_node_id = adjustments.get('restart_node_id')
        modifications = adjustments.get('modifications', [])
        
        # Apply modifications to the plan
        for mod in modifications:
            mod_node_id = mod['node_id']
            if mod_node_id in plan_graph.nodes:
                # Modify existing node
                node = plan_graph.nodes[mod_node_id]
                # node.task_name = mod.get('task_name', node.task_name)
                node.task_description = mod.get('task_description', node.task_description)
                node.next_nodes = mod.get('next_nodes', node.next_nodes)
                node.validation_threshold = mod.get('validation_threshold', node.validation_threshold)
                node.max_attempts = mod.get('max_attempts', node.max_attempts)
            else:
                # If the node doesn't exist, create it
                new_node = Node(
                    id=mod_node_id,
                    task_description=mod['task_description'],
                    next_nodes=mod.get('next_nodes', []),
                    validation_threshold=mod.get('validation_threshold', 0.8),
                    max_attempts=mod.get('max_attempts', 3)
                )
                plan_graph.add_node(new_node)
        
        # Validate that the restart node exists
        if restart_node_id not in plan_graph.nodes:
            print(f"Restart node '{restart_node_id}' does not exist. Adding it to the plan.")
            # Create the restart node with default values (this can be adjusted as needed)
            new_node = Node(
                id=restart_node_id,
                task_description='Automatically added restart node',
                next_nodes=[],
                validation_threshold=0.8,
                max_attempts=3
            )
            plan_graph.add_node(new_node)
        
        # Update the plan's starting point or current node if needed
        plan_graph.current_node_id = restart_node_id
    else:
        print("Unknown action in adjustments.")