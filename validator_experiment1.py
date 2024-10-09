from core.llm_chat import LLMChat
from core.context_manager import ContextManager
from core.planner import Planner
from core.llm_validator import LLMValidator

from prompt.build_web_app import BUILD_WEB_APP_KNOWLEDGE
from prompt.coding import CODE_GENERATION_PROMPT

def run():
    print("Complete task with validation...")

    # request = "step by step to solve P vs NP Problem, list detaled formular"
    # request = "step by step to build a LLM code extractor, to extract all information from java project source code and store into vector database for inquery."
    request = "step by step to write out magnus carlson series of moves in his game against Alireza Firouzja and propose an alternate strategy"

    planner = Planner()
    steps = planner.plan(request)

    chat = LLMChat()
    context_manager = ContextManager()
    llm_validator = LLMValidator()

    for index, step in enumerate(steps, start=1):

        # TODO: use tool to get result

        context_response = chat.context_respond(context_manager.context_to_str(), step.description)
        
        validation_result = llm_validator.validate(step.description, context_response['answer'])
        print(validation_result)
        decision, total_score, scores = llm_validator.parse_scored_validation_response(validation_result)
        print("\nTotal Score:", total_score)
        print("Scores by Criterion:", scores)
        print("Final Decision:", decision)
        
        step_number = f"Step {index}"
        context = f"{context_response['messages'][0]}: \n{context_response['answer']}"
        context_manager.add_context(step_number, context)

    response = chat.context_respond(context_manager.context_to_str(), request+CODE_GENERATION_PROMPT)
    validation_result = llm_validator.validate(request, response['answer'])
    print(validation_result)
    # decision = llm_validator.parse_validation_response(validation_result)
    # print("\nFinal Decision:", decision)
    decision, total_score, scores = llm_validator.parse_scored_validation_response(validation_result)
    print("\nTotal Score:", total_score)
    print("Scores by Criterion:", scores)
    print("Final Decision:", decision)

    return response

if __name__ == "__main__":
    run()