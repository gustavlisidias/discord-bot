import google.generativeai as genai

from settings import gkey, generation_config, safety_config
from google.api_core.exceptions import InternalServerError
from google.generativeai.types import content_types
from google.generativeai.generative_models import ChatSession


genai.configure(api_key=gkey)
gemini = genai.GenerativeModel('gemini-pro', generation_config=generation_config, safety_settings=safety_config)
geminivs = genai.GenerativeModel('gemini-pro-vision', generation_config=generation_config, safety_settings=safety_config)

history_clients = {}
max_length = 2000


def create_history(*args):
    '''
    In this model we have the following scenarios:
    1 - Generation of text with context (text-only)
    2 - Chat with context (history)
    3 - Chat with context and image (history)
    4 - Image with context (text-only)
    5 - Image without context (text-only)

    So as the only case when there is no context is the generation of text/description from an image we should deal with it here
    because history needs a context
    '''
    history = []
    for obj in args:
        content = obj['text'] or 'Me diga o que está escrito na imagem ou me dê detalhes do que a imagem se trata'
        content = content_types.to_content(content)
        content.role = ChatSession._USER_ROLE if obj['role'] == 'user' else ChatSession._MODEL_ROLE
        history.append(content)

    return history


async def question_gemini(context):
    '''
    For: Generate text from text inputs
    '''
    try:
      response = gemini.generate_content(context)
      return response.text
    
    except InternalServerError:
        return await question_gemini(context)
  
    except Exception as e:
        return f'Ops! Something went wrong: {e}'
    

async def chat_gemini(context, user, image):
    '''
    For: Chat with history and send images with or without context
    Note: The vision model gemini-pro-vision is not optimized for multi-turn chat.
    Obs: See that, as explained in the documentation note, 
    you are advised to use the gemini-pro-vision model only for image contexts, 
    so we will take the vision response and create a history to insert into 
    the ChatSession class
    '''
    if user not in history_clients:
        history_clients[user] = []

    answer, error = None, None

    if image:
        try:
            if context:
                response = geminivs.generate_content([context, image])
            else:
                response = geminivs.generate_content(image)

            response.resolve()
            answer = response.text

            history_clients[user] += create_history({'text': context, 'role': 'user'}, {'text': answer, 'role': 'model'})

        except InternalServerError:
            return await chat_gemini(context, user, image)

        except Exception as e:
            error = f'Ops! Something went wrong: {e}'
    
    else:
        try:
            chat = gemini.start_chat(history=history_clients[user])
            chat.send_message(context)
            history_clients[user] += chat.history

            answers = [message.parts[0].text for message in chat.history if message.role == 'model']
            answer = answers[-1]

            if len(answer) > max_length:
                answer = answer.splitlines()

        except InternalServerError:
            return await chat_gemini(context, user, image)

        except Exception as e:
            error = f'Ops! Something went wrong: {e}'

    return answer, error


async def vision_gemini(context, image):
    '''
    For: Send images with or without context
    '''
    try:
        if context:
            response = geminivs.generate_content([context, image])
        else:
            response = geminivs.generate_content(image)
            
        response.resolve()
        return response.text

    except Exception as e:
        error = f'Ops! Something went wrong: {e}'
        return error