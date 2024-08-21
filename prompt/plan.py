PLAN_FORMAT = """
Based on background and knowledge given above to generate a plan. This plan should involve individual tasks, that if executed correctly will yield the correct answer.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.
ex: step_name: Prepare eggs, step_description: Get the eggs from the fridge and put on the table.
"""

RE_PLAN_FORMAT = """
Based on background and knowledge given below to generate a plan. This plan should involve individual tasks, that if executed correctly will yield the correct answer.
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
Put each step in the json format as the output, step has attribute step_name and step_description, all steps should form a list under 'steps' root attribute.
ex: step_name: Prepare eggs, step_description: Get the eggs from the fridge and put on the table.

<background>

{background}

</background>

<objective>

{request}

</objective>

<knowledge>

{knowledge}

</knowledge>

<original_plan>

{plan}

</original_plan>

<completed_steps>

{past_steps}

</completed_steps>

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.
"""
