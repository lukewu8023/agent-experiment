import os
from dotenv import load_dotenv



class Config:

    OPENAI_MODEL_BASIC = 'gpt-4o-mini'
    OPENAI_MODEL_ADVANCED = 'gpt-4o'
    OPENAI_PROXY='http://localhost:8001'
    #os.environ['OPENAI_API_BASE'] = 'https://api.ohmygpt.com/v1/'
    #os.environ['OPENAI_API_KEY'] = ''

    load_dotenv()
