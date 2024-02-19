import os
import requests
import cv2
import time
import pickle
from firebase_admin import db
from firebase_admin import storage
import face_recognition
from firebase_admin import credentials
import firebase_admin

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'serviceAccountKey.json'

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "",
    "storageBucket": "face-recognition-1d3e3.appspot.com"
})

folderPath = 'Images'
paths = os.listdir(folderPath)
imgs = []
userids = []

for path in paths:
    imgs.append(cv2.imread(os.path.join(folderPath, path)))
    imgs.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    print(storage)
    bucket = storage.bucket()

    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(userids)


def faceEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

knownEncodings = faceEncodings(imgs)
knownEncodingswIds = [knownEncodings, userids]

file = open("faceEncodings.p", 'wb')
pickle.dump(knownEncodingswIds, file)
file.close()

