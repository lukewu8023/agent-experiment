# one level planner

PLAN_FORMAT = """{background}
Based on the request given below to generate a plan for AI assistant to execute automatically. This plan should involve individual steps, that if executed correctly will yield the correct answer. 
Do not create any superfluous steps. Do not contain manual steps required to execute by human.
You can refer to the knowledge to generate the plan if given.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Each step will be executed in order independently, note that in memory result will not be kept to next step!
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.
ex: step_name: Prepare eggs, step_description: Get the eggs from the fridge and put on the table.

{knowledge}

"""

REVIEW_FORMAT="""You task is to give critiques for current plan given an objective.
Given the objective and response of completed steps, review the original plan and provide criteques for following two points only. Don't provide revised steps!
1) what is different between the last completed step and the original plan
2) suggestion about how to change the REMAINING plan based on completed steps.Ensure the steps should be able to execute by AI assistant not human.

<objective>

{request}

</objective>

<original_plan>

{original_plan}

</original_plan>

<completed_steps>

{completed_steps}

</completed_steps>

"""

RE_PLAN_FORMAT = """{background}
Based on the infor given below to generate a plan for computer to execute automatically. This plan should involve individual steps, that if executed correctly will yield the correct answer. 
Do not create any superfluous steps.  Do not contain manual steps required to execute by human.
You can refer to the knowledge to generate the plan if given.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Each step will be executed in order independently, note that in memory result will not be kept to next step!
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.
ex: step_name: Prepare eggs, step_description: Get the eggs from the fridge and put on the table.

{knowledge}

<objective>

{request}

</objective>

<original_plan>

{original_plan}

</original_plan>

<completed_steps>

{completed_steps}

</completed_steps>

<critique>

{criteque}

</criteque>

Revise the remaining steps of your previous plan using the new information.
You should use the critique, response of completed_steps, review the original plan and update your steps accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the steps. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.
Only return the steps in json format, don't add anything else!
"""





# Two level planner

HIGHER_LEVEL_PLANNER_FORMAT = """
Based on background and knowledge given above to generate a plan for AI assistant. This plan should involve individual tasks, that if executed correctly will yield the correct answer.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.
ex: step_name: Prepare eggs, step_description: Get the eggs from the fridge and put on the table.
"""

LOW_LEVEL_PLANNER_FORMAT="""
Provide the final objective and current step. Break down the current step to individual tasks, that if executed correctly will yield the correct answer for the step. Do not create any superfluous tasks. 
Only breakdown the current step, don't add other tasks beyond the scope of given step.
You can refer to the tools available to break down the step.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.

<objective>

{request}

</objective>

<current_step>

{step}

</current_step>

<tools>

{tools}

</tools>

"""






LOW_LEVEL_RE_PLAN_FORMAT = """
Provide the final objective and current step. Break down the current step to individual tasks, that if executed correctly will yield the correct answer for the step. Do not create any superfluous tasks. 
Only breakdown the current step, don't add other tasks beyond the scope of given step.
You can refer to the tools available to break down the step.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.

<objective>

{request}

</objective>

<current_step>

{step}

</current_step>

<tools>

{tools}

</tools>

<original_tasks>

{original_tasks}

</original_tasks>

<completed_tasks>

{completed_tasks}

</completed_tasks>

Update your tasks accordingly. If no more tasks are needed and you can return to the user, then respond with that. Otherwise, fill out the tasks. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.
"""
