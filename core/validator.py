from typing_extensions import Annotated
from pydantic import BaseModel, ValidationError, AfterValidator, ValidationInfo

class Validator:

    CHECK_UNCERTAINTY = 1
    CHECK_NOT_ANSWERED = 2
    ARGUMENTS_NOT_MATCH = 3

    def validate(self, request, response, validation_type):

        def _check_uncertainty(response: str):
            if "I don't know" in response:
                raise ValueError("Response is uncertain")
            return response

        def _check_not_answered(response: str):

            print(f"Request text: {request}")
            print(f"Response text: {response}")

            from core.llm_chat import LLMChat
            chat = LLMChat()

            check_string = '''
Does below RESPONSE provide exactly what is expected and needed from the user who asked the REQUEST? 
If yes, output string 'yes', if no or response contains further questions or refuse to answer, output sting 'no', nothing else to be outputed.

# REQUEST
''' + request + '''

# RESPONSE
''' + response

            print(check_string)

            check_result = chat.one_time_respond(check_string)

            if "no" == check_result:
                raise ValueError("Request is not answered")
            return response   

        # def _arguments_not_match(response: str):
            # print(f"actual_arguments: {response}")
            # return response     
        
        def _arguments_not_match(expected_arguments: str, actual_arguments: str):
            #TODO doesn't work yet
            print(f"expected_arguments: {expected_arguments}")
            print(f"actual_arguments: {actual_arguments}")
            # if "I don't know" in response:
            #     raise ValueError("Response is uncertain")
            return response     

        class Response(BaseModel):
            if (validation_type==self.CHECK_UNCERTAINTY):
                response: Annotated[str, AfterValidator(_check_uncertainty)]
            if (validation_type==self.CHECK_NOT_ANSWERED):
                response: Annotated[str, AfterValidator(_check_not_answered)]
            if (validation_type==self.ARGUMENTS_NOT_MATCH):
                response: Annotated[str, AfterValidator(_arguments_not_match)]

        Response.model_validate({'response': response})