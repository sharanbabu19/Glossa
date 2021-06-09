# Necessary imports
import streamlit as st
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
import os
import time
import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import uuid
import json

# New environment, 'azure', created in conda for this project.
st.set_page_config(page_title="Glossa", page_icon="📝") 


def text_to_text_translation(sentence,target_language):
	subscription_key = "3e7d57d42487401e9ea1b73c0b0c4c75"
	endpoint = "https://api.cognitive.microsofttranslator.com"

	location = "eastus"

	path = '/translate'
	constructed_url = endpoint + path

	params = {
	    'api-version': '3.0',
	    'to': [target_language]
	}
	
	constructed_url = endpoint + path

	headers = {
	    'Ocp-Apim-Subscription-Key': subscription_key,
	    'Ocp-Apim-Subscription-Region': location,
	    'Content-type': 'application/json',
	    'X-ClientTraceId': str(uuid.uuid4())
	}

	body = [{'text': sentence}]
	request = requests.post(constructed_url, params=params, headers=headers, json=body)
	response = request.json()
	#st.json(response)
	source_language = response[0]['detectedLanguage']['language']
	result = response[0]['translations'][0]['text']
	return source_language, result



def text_synonyms(sentence,from_language, target_language):
	subscription_key = "3e7d57d42487401e9ea1b73c0b0c4c75"
	endpoint = "https://api.cognitive.microsofttranslator.com"

	location = "eastus"

	path = '/dictionary/lookup'
	constructed_url = endpoint + path

	params = {
	    'api-version': '3.0',
	    'from': from_language,
	    'to': [target_language]
	}
	
	constructed_url = endpoint + path

	headers = {
	    'Ocp-Apim-Subscription-Key': subscription_key,
	    'Ocp-Apim-Subscription-Region': location,
	    'Content-type': 'application/json',
	    'X-ClientTraceId': str(uuid.uuid4())
	}

	body = [{'text': sentence}]
	request = requests.post(constructed_url, params=params, headers=headers, json=body)
	response = request.json()
	#st.json(response)
	try:	
		length = len(response[0]['translations'])
	except:
		length = 0	
	if length > 0:
		synonym = response[0]['translations'][-1]['backTranslations'][-1]['displayText']
		intermediate_language, _ = text_to_text_translation(synonym,'en')
		if intermediate_language!='en':
			st.subheader("Synonym:")
			st.success(synonym)
		





st.sidebar.title('Glossa :memo:')
st.sidebar.text("@ your service")
st.sidebar.title('Page Selection Menu')
page = st.sidebar.radio("Select Page:",("Text to Text translation","Image OCR","What's this called?",'How "j" say it?',"Chatbot"))


if page == "Text to Text translation":
	st.title('Azure AI Hackathon 🤖')
	st.title('Glossa :memo:')
	st.markdown("*Your Language Assistant*")
	st.info("Select Page from Sidebar to the left")
	st.title('Text to Text Translation :u5408: ↔️ :capital_abcd:')
	st.markdown("Translate text from one language to another, get synonyms if available and listen to the pre-configured voice outputs.")
	examples = st.beta_expander("Example sentences:",expanded=False)
	examples.markdown("**English:**")
	examples.markdown('Hi, how are you?')
	examples.markdown("**French:**")
	examples.markdown('J’espère que vous faites du bien')
	st.write("")
	st.write("")

	source = st.text_area("Enter sentence (Language auto-detection enabled):","")
	target = st.selectbox("Select Target Language  🈴:",("French","Arabic","Japanese","English"))

	if st.button("Translate"):
		if source == "":
			st.error("Please enter a sentence first.")
		else:
			
			from_language, answer = text_to_text_translation(source,target.lower()[0:2])
			st.subheader("Translated Text:")
			st.success(answer)
			#st.success(from_language)

			text_synonyms(source,from_language,target.lower()[0:2])


			speech_config = SpeechConfig(subscription="1a274dcd9b7140059bc32b9b00404391", region="eastus")

			synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=None)

			st.text("")
			st.subheader("Voice Output:")
			if target == "French":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",answer).replace("my-lang","fr-FR").replace("my-voice","fr-FR-Julie").replace("my-speed","0.8")
			elif target == "Arabic":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",answer).replace("my-lang","ar-EG").replace("my-voice","ar-EG-Hoda").replace("my-speed","0.8")
			elif target == "Japanese":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",answer).replace("my-lang","ja-JP").replace("my-voice","ja-JP-Ichiro").replace("my-speed","0.8")
			elif target == "English":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",answer).replace("my-lang","en-GB").replace("my-voice","en-GB-George").replace("my-speed","0.8")		

			with st.spinner("Fetching Audio..."):
				result = synthesizer.speak_ssml_async(ssml_string).get()
				#print(ssml_string)

				stream = AudioDataStream(result)
				stream.save_to_wav_file("st_file1.wav")	
				time.sleep(0.1)
				st.audio("st_file1.wav")
				
		    	


elif page == "Image OCR":
	st.title('Glossa :memo:')
	st.markdown("*Your Language Assistant*")
	st.title('Image OCR 🖼️ ↔️ 🔤 ↔️ 🈴')
	st.markdown("Upload Image and get it's text extracted in language of your choice.")

	st.write("")
	sample_images = st.beta_expander("Sample Images:",expanded=False)
	col_1, col_2 = sample_images.beta_columns(2)
	col_1.image('example_text.PNG')
	col_2.image('text_sample.jpg')
	st.write("")
	st.write("")

	image = st.file_uploader("Upload Image:",type=['jpg','png','jpeg','JPG','PNG','JPEG'])
	st.write("")
	st.write("")
	dest = st.selectbox("Select Target Language  🈴:",("French","Arabic","Japanese","English"))

	st.write("")
	if st.button('Process'):
		if image is None:
			st.error("Please upload a valid image first.")
		else:
			full_text=""
			uploaded_image = st.beta_expander("Uploaded Image:",expanded=True)
			uploaded_image.image(image)
			st.write("")
			st.write("")
			#st.image(image)
			cog_key = "a2bbcdeb645342eb815710df027d72b0"
			cog_endpoint = "https://aiocr-1.cognitiveservices.azure.com/"
			computervision_client = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

			#image_path = 'example_text.png'
			#image_stream = open(image,"rb")
			image_stream = image

			with st.spinner('Fetching Results...'):
				recognize_handw_results = computervision_client.read_in_stream(image_stream,  raw=True)
				operation_location_remote = recognize_handw_results.headers["Operation-Location"]
				operation_id = operation_location_remote.split("/")[-1]
				while True:
				    get_handw_text_results = computervision_client.get_read_result(operation_id)
				    if get_handw_text_results.status not in ['notStarted', 'running']:
				        break
				    time.sleep(1)

				
				if get_handw_text_results.status == OperationStatusCodes.succeeded:
					#print(get_handw_text_results.analyze_result.read_results)
					if len(get_handw_text_results.analyze_result.read_results[0].lines)>0:
						st.subheader('Output')
						for text_result in get_handw_text_results.analyze_result.read_results:
							for line in text_result.lines:
								full_text += line.text+"\n"
								st.markdown(line.text)
					else:
						st.info('No text detected.')			
					    
					        
					        	
					        	
				if full_text!='':
					from_language, answer = text_to_text_translation(full_text,dest.lower()[0:2])
					st.subheader("Translated Text:")
					st.success(answer)        	
			            
			

							    


elif page == "What's this called?":
	st.title('Glossa :memo:')
	st.markdown("*Your Language Assistant*")
	st.title('Image Captioning 🖼️ ↔️ 📃➕🗞️')
	st.markdown("Upload an Image, get it's textual description in language of your choice and be able to search content related to it.")

	st.write("")
	sample_image = st.beta_expander("Sample Images:",expanded=False)
	col_1, col_2 = sample_image.beta_columns(2)
	col_1.image('landmark.jpg')
	col_2.image('text_sample.jpg')
	st.write("")
	st.write("")

	picture = st.file_uploader("Upload Image:",type=['jpg','png','jpeg','JPG','PNG','JPEG'])
	st.write("")
	st.write("")
	dest = st.selectbox("Select Target Language  🈴:",("English","Arabic","Japanese","French"))
	st.write("")
	st.write("")
	if st.button('Generate'):
		if picture is None:
			st.error('Please upload a valid image first.')
		else:
			cog_key = "a2bbcdeb645342eb815710df027d72b0"
			cog_endpoint = "https://aiocr-1.cognitiveservices.azure.com/"
			computervision_client = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))
			uploaded_image = st.beta_expander("Uploaded Image:",expanded=True)
			uploaded_image.image(picture)
			st.write("")
			st.write("")
			with st.spinner('Fetching Results...'):
				description = computervision_client.describe_image_in_stream(picture)

				
				if (len(description.captions) == 0):
				    st.warning("No description detected.")
				else:
					st.subheader('Caption:')
					for caption in description.captions:
						st.success("'{}'".format(caption.text))	
					full_text = description.captions[0].text 
					from_language, answer = text_to_text_translation(full_text,dest.lower()[0:2])
					if from_language!=dest.lower()[0:2]:
						st.subheader("Translated Caption:")
						st.success(answer)
					subscription_key = "7e1a2f7b90464dbd90e5a4e353e4b3fe"
					headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
					search_term = full_text
					search_url = "https://api.bing.microsoft.com/v7.0/news/search"
					params  = {"q": search_term, "textDecorations": True, "textFormat": "HTML","count":2}
					response = requests.get(search_url, headers=headers, params=params)
					response.raise_for_status()
					search_results = response.json()
					if len(search_results['value'])>0:
						st.subheader("News Links:")
						for x in search_results['value']:
							st.markdown(f"{x['name']}, {x['url']}")
					else:	
						st.subheader("No relevant news available currently.")
				    	
				    		
				    
				    				    
elif page == 'How "j" say it?':
	st.title('Glossa :memo:')
	st.markdown("*Your Language Assistant*")
	st.title('How "j" say it  ✍️  ↔️ ✔️  ↔️ 🗣️')
	st.markdown("This feature helps you get better at writing and speaking English.")	
	st.markdown("Type an English sentence, get the spellings corrected and receive the pronunciation for the same.")	
	st.write("")
	sample_query = st.beta_expander("Example sentence:",expanded=False)
	sample_query.markdown("Ho aer yu?")
	st.write("")
	#st.write("")
	sentence = st.text_input("Enter your Sentence:","")
	st.text("")
	#st.text("")
	voice_selection = st.selectbox("Select Voice Type:",("US English - Female","US English - Male","UK English - Female","UK English - Male"))
	st.text("")

	speed = st.select_slider("Adjust Speech Speed:",options=['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1',],value='0.8')
	st.write("")
	st.write("")
	if st.button('Process'):
		if sentence == "":
			st.error("Please enter a sentence first.")
		else:
			comparison_sentence = sentence
			endpoint = "https://api.bing.microsoft.com/v7.0/SpellCheck"
			subscription_key = "7e1a2f7b90464dbd90e5a4e353e4b3fe"
			data = {'text': sentence}


			params = {
			    'mkt':'en-us',
			    'mode':'proof'
			    }


			headers = {
			    'Content-Type': 'application/x-www-form-urlencoded',
			    'Ocp-Apim-Subscription-Key': subscription_key,
			    }

			response = requests.post(endpoint, headers=headers, params=params, data=data)

			json_response = response.json()
			#print(json.dumps(json_response, indent=4))
			#st.json(json_response)


			#st.markdown(json_response["flaggedTokens"])
			for x in json_response["flaggedTokens"]:
				word_to_be_corrected = x["token"]
				correct_word = x["suggestions"][0]['suggestion']
				sentence = sentence.replace(word_to_be_corrected,correct_word)
			if sentence != comparison_sentence:
				st.subheader('Corrected Sentence is:')
				st.success(sentence)
			else:
				st.success("Your sentence had no spelling mistakes.")	

			st.subheader('Pronunciation of the sentence:')
			speech_config = SpeechConfig(subscription="1a274dcd9b7140059bc32b9b00404391", region="eastus")

			synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=None)

			
			if voice_selection == "US English - Female":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",sentence).replace("my-lang","en-US").replace("my-voice","en-US-AriaRUS").replace("my-speed",speed)
			elif voice_selection == "US English - Male":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",sentence).replace("my-lang","en-US").replace("my-voice","en-US-BenjaminRUS").replace("my-speed",speed)
			elif voice_selection == "UK English - Female":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",sentence).replace("my-lang","en-GB").replace("my-voice","en-GB-Susan").replace("my-speed",speed)
			elif voice_selection == "UK English - Male":
				ssml_string = open("ssml.xml", "r").read().replace("my-sentence",sentence).replace("my-lang","en-GB").replace("my-voice","en-GB-George").replace("my-speed",speed)		

			with st.spinner("Fetching Audio..."):
				result = synthesizer.speak_ssml_async(ssml_string).get()
				#print(ssml_string)

				stream = AudioDataStream(result)
				stream.save_to_wav_file("st_file2.wav")	
				time.sleep(0.1)
				st.audio("st_file2.wav")


