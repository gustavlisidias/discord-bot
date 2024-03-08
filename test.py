# import google.generativeai as genai

# from settings import gkey, generation_config, safety_config
# # from libtiff import TIFF
# from PIL import Image


# genai.configure(api_key=gkey)
# model = genai.GenerativeModel('gemini-pro-vision', generation_config=generation_config, safety_settings=safety_config)

# img = Image.open('documents/teste.tif')
# response = model.generate_content(img)

# print(response.text)