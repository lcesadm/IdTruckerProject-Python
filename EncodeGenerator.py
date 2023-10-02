import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://reconhecimentofacial-83d23-default-rtdb.firebaseio.com/",
    'storageBucket': "reconhecimentofacial-83d23.appspot.com"
})

#Criando a pasta Images
print("Criando a pasta Images...")
if os.path.exists("Images"):
    for path in os.listdir("Images"):
        os.remove(f"Images/{path}")
    os.removedirs("Images")
os.makedirs('Images')

# Importando as imagens
truckersId = []
imgList = []
ref = db.reference(f'/Truckers').get()
for id in ref:
    fileName = f'Images/{id}.png'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.download_to_filename(f'Images/{id}.png')

    imgList.append(cv2.imread(os.path.join('Images',f'{id}.png'))) 
    blob.upload_from_filename(fileName)
    truckersId.append(id)

print("Importandos as imagens para a pasta...\n", "Ids:", truckersId)

# Fazendo o encode nas imagens
def findEncodings(imageList):
    encodeList = []
    for img in imageList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, truckersId]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
