# Doc: https://ai.google.dev/tutorials/python_quickstart
import google.generativeai as genai

from settings import gkey, generation_config, safety_config
from models import Mensagem, Sala
from utils import image_to_byte

from google.api_core.exceptions import InternalServerError
from google.generativeai.types import content_types
from google.generativeai.generative_models import ChatSession


genai.configure(api_key=gkey)
gemini = genai.GenerativeModel('gemini-pro', generation_config=generation_config, safety_settings=safety_config)
geminivs = genai.GenerativeModel('gemini-pro-vision', generation_config=generation_config, safety_settings=safety_config)

history_clients = {}
max_length = 2000


def create_history(*args):
    history = []
    for obj in args:
        content = obj['text'] or 'Me diga o que está escrito na imagem ou me dê detalhes do que a imagem se trata'
        content = content_types.to_content(content)
        content.role = ChatSession._USER_ROLE if obj['role'] == 'user' else ChatSession._MODEL_ROLE
        history.append(content)

    return history


async def question_gemini(ctx, arguments):
    '''
    For: Generate text from text inputs
    '''
    try:
      response = gemini.generate_content(arguments)
      sala = await Sala(servidor=ctx.guild.id).get()
      await Mensagem(sala=sala, autor=ctx.author.id, mensagem=arguments, resposta=response.text).save()
      return response.text
    
    except InternalServerError:
        return await question_gemini(arguments)
  
    except Exception as e:
        return f'Ops! Something went wrong: {e}'
    

async def vision_gemini(ctx, arguments, image):
    '''
    For: Send images with or without context
    '''
    try:
        if arguments:
            response = geminivs.generate_content([arguments, image])
        else:
            response = geminivs.generate_content(image)
            
        response.resolve()
        sala = await Sala(servidor=ctx.guild.id).get()
        await Mensagem(sala=sala, autor=ctx.author.id, mensagem=arguments, resposta=response.text, arquivo=image_to_byte(image)).save()
        return response.text

    except Exception as e:
        error = f'Ops! Something went wrong: {e}'
        return error
    

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

    mensagens = await Mensagem(autor=user).get()
    for mensagem in mensagens:
        history_clients[user] += create_history({'text': mensagem['mensagem'], 'role': 'user'}, {'text': mensagem['resposta'], 'role': 'model'})

    answer, error = None, None

    if image:
        try:
            if context:
                response = geminivs.generate_content([context, image])
            else:
                response = geminivs.generate_content(image)

            response.resolve()
            answer = response.text
            await Mensagem(autor=user, mensagem=context, arquivo=image_to_byte(image), resposta=answer).save()

        except InternalServerError:
            return await chat_gemini(context, user, image)

        except Exception as e:
            error = f'Ops! Something went wrong: {e}'
    
    else:
        try:
            chat = gemini.start_chat(history=history_clients[user])
            chat.send_message(context)

            answers = [message.parts[0].text for message in chat.history if message.role == 'model']
            answer = answers[-1]
            await Mensagem(autor=user, mensagem=context, resposta=answer).save()

            if len(answer) > max_length:
                answer = answer.splitlines()

        except InternalServerError:
            return await chat_gemini(context, user, image)

        except Exception as e:
            error = f'Ops! Something went wrong: {e}'

    return answer, error