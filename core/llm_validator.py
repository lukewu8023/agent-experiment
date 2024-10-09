import re

from typing_extensions import Annotated
from pydantic import BaseModel, ValidationError, AfterValidator, ValidationInfo

class LLMValidator:

    def create_validator_prompt(self, request, response):
        # prompt = f"""
        # You are an expert validator of AI-generated outputs. Evaluate the provided subtask output based on the following criteria: Accuracy, Completeness, Relevance, Coherence and Clarity, Consistency, Following Instructions, Error Analysis, and Ethical Compliance.

        # For each criterion, provide:

        # - **Pass/Fail**
        # - **Justification:** A brief explanation for your decision.

        # At the end, provide a final recommendation: **Accept Output** or **Rerun Subtask** based on the evaluations. If any critical criteria failed, recommend rerunning the subtask.

        # ---

        # **Subtask Description:**
        # {request}

        # **Subtask Output:**
        # {response}

        # **Evaluation:**
        # """

        prompt = f"""
        You are an expert validator of AI-generated outputs. Evaluate the provided subtask output based on the following criteria:

        1. **Accuracy** (Score 1-5): The output fulfills the requirements of the subtask accurately.
        2. **Completeness** (Score 1-5): The output addresses all aspects of the subtask.
        3. **Relevance** (Score 1-5): The content is directly relevant to the subtask without extraneous information.
        4. **Coherence and Clarity** (Score 1-5): The output is logically structured, clear, and easy to understand.
        5. **Consistency** (Score 1-5): The output is consistent with previous subtasks and doesn't contradict itself.
        6. **Following Instructions** (Score 1-5): The output adheres to any specific instructions or formats specified.
        7. **Error Analysis** (Score 1-5): The output is free from factual, grammatical, and logical errors.
        8. **Ethical Compliance** (Score 1-5): The content complies with ethical guidelines and policies.

        For each criterion, provide:

        - **Score (1-5)**
        - **Justification:** A brief explanation for your score.

        At the end:

        - Calculate the **Total Score**.
        - Provide a final recommendation:

        - **Accept Output** if the total score is above 35 and no criterion scored below 3.
        - **Rerun Subtask** if the total score is 35 or below, or if any criterion scored below 3.

        - If recommending a rerun, provide suggestions on how to improve the output.

        ---

        **Subtask Description:**
        {request}

        **Subtask Output:**
        {response}

        **Evaluation:**
        """
        return prompt

    def parse_validation_response(self, validation_response):
        accept_keywords = ["Accept Output", "accept output"]
        rerun_keywords = ["Rerun Subtask", "rerun subtask"]
        
        if any(keyword in validation_response for keyword in accept_keywords):
            return "Accept Output"
        elif any(keyword in validation_response for keyword in rerun_keywords):
            return "Rerun Subtask"
        else:
            return "Undetermined"
        
    def parse_scored_validation_response(self, validation_response):
        scores = []
        total_score = 0
        lines = validation_response.strip().split('\n')
        for line in lines:
            # match = re.match(r'\d+\.\s\*\*([A-Za-z\s]+)\*\*\s\(Score\s1-5\):\s*Score:\s*(\d)', line)
            # match = re.match(r'\d+\.\s\*\*([A-Za-z\s]+) \(Score (\d+)\)', line)
            match = re.match(r'\d+\.\s+\*\*([A-Za-z\s]+)\s*\(Score:? (\d+)\)\*\*', line)            
            if match:
                criterion = match.group(1).strip()
                score = int(match.group(2))
                scores.append((criterion, score))
                total_score += score

        # Check for any criterion scored below 3
        any_low_scores = any(score < 3 for _, score in scores)
        
        # Final decision
        if total_score > 35 and not any_low_scores:
            decision = "Accept Output"
        else:
            decision = "Rerun Subtask"

        return decision, total_score, scores

    def validate(self, request, response):
        prompt = self.create_validator_prompt(request, response)
        
        from core.llm_chat import LLMChat
        chat = LLMChat()

        validation_response = chat.one_time_respond(prompt)
        
        # validation_response = check_result['choices'][0]['message']['content']
        return validation_response

# Example usage
if __name__ == "__main__":
    subtask_description = "Translate the following English text into French: 'The quick brown fox jumps over the lazy dog.'"
    subtask_output = "Le rapide renard brun saute par-dessus le chien paresseux."
    llm_validator = LLMValidator()
    validation_result = llm_validator.validate(subtask_description, subtask_output)
    print(validation_result)

    # Continuing from previous code
    # decision = llm_validator.parse_validation_response(validation_result)
    # print("\nFinal Decision:", decision)

    # Continuing from previous code
    decision, total_score, scores = llm_validator.parse_scored_validation_response(validation_result)
    print("\nTotal Score:", total_score)
    print("Scores by Criterion:", scores)
    print("Final Decision:", decision)
