import google.generativeai as genai

from settings import gkey, generation_config, safety_config
from google.api_core.exceptions import InternalServerError


genai.configure(api_key=gkey)
model = genai.GenerativeModel('gemini-pro', generation_config=generation_config, safety_settings=safety_config)
history_clients = {}


async def question_gemini(context):
    try:
      response = model.generate_content(context)
      return response.text
    
    except InternalServerError:
        return await question_gemini(context)
  
    except Exception as e:
        return f'Ops! Something went wrong: {e}'
    

async def chat_gemini(context, user):
    if user not in history_clients:
        history_clients[user] = []

    answer, error = None, None
    try:
        chat = model.start_chat(history=history_clients[user])
        chat.send_message(context)
        history_clients[user] += chat.history

        answers = [message.parts[0].text for message in chat.history if message.role == 'model']
        answer = answers[-1]

    except InternalServerError:
        return await chat_gemini(context, user)

    except Exception as e:
        error = f'Ops! Something went wrong: {e}'

    return answer, error
