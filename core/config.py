import os

class Config:

    OPENAI_MODEL_BASIC = 'gpt-4o-mini'
    OPENAI_MODEL_ADVANCED = 'gpt-4o'
    OPENAI_MODEL_EXPERT = 'o1-preview'
    os.environ['OPENAI_API_BASE'] = 'https://api.ohmygpt.com/v1/'
    os.environ['OPENAI_API_KEY'] = ''
