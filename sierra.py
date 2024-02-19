import cv2
import time
import os
import requests
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import requests
import json
import base64
from vosk import Model, KaldiRecognizer, SetLogLevel
import pyaudio


engine = pyttsx3.init()

model = Model(
    r"C:/Users/vanga_ht20k/Desktop/projects/python/saight-master/vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15/"
)
print("kaldi gonn astart")
recognizer = KaldiRecognizer(model, 16000)

print("mic test")
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1,
                  rate=16000, input=True, frames_per_buffer=8196)
stream.start_stream()


cap = cv2.VideoCapture("http://172.18.73.110:8080/video")

print("Initialized sierra. Ready to use.")
speechVar = "Initialized sierra. Ready to use."
engine.say(speechVar)
engine.runAndWait()


while True:

    try:
        data = stream.read(8196)

        if recognizer.AcceptWaveform(data):
            text = recognizer.Result()
            if "sierra" in text:
                print("sierra : ", text)

                # Capture a new image from the webcam
                ret, frame = cap.read()

                speechVar = "Request received. Processing"
                engine.say(speechVar)
                engine.runAndWait()

                # Save the captured image
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)

                # Function to encode the image
                def encode_image(image_path):
                    with open(image_path, "rb") as image_file:
                        return base64.b64encode(image_file.read()).decode('utf-8')

                speechVar = "Processing request."
                engine.say(speechVar)
                engine.runAndWait()
                
                # Getting the base64 string
                base64_image = encode_image(image_path)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer "
                }
                
                payload = {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"{text} ( new line ) if the person asked you to help them see or help them understand what they are looking at (you are their eyes), then give a vivid description and perhaps using ocr, read out the text you see. keep this response between 10-20 words. if not, then reply back friendlier and engage in a normal conversation."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 300
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

                received_response = response.json()
                generated_text = received_response['choices'][0]['message']['content']
                print(generated_text)

                speechVar = generated_text
                engine.say(speechVar)
                engine.runAndWait()

            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(0.1)
