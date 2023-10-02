import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://reconhecimentofacial-83d23-default-rtdb.firebaseio.com/",
    'storageBucket': "reconhecimentofacial-83d23.appspot.com"
})

bucket = storage.bucket()

modeType = 0
counter = 0
id = -1
imgStudent = []

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')
# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#print(len(imgModeList))

# Load the encode file
print("Loading Encode File...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentsIds = encodeListKnownWithIds
#print(studentsIds)
print("Encode File Loaded...")

while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+631, 808:808+415] = imgModeList[modeType]
    # cv2.imshow("WebCam", img)
    ref = db.reference(f'Students/{id}')

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        #print("matches", matches)
        #print("faces", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("match Index", matchIndex)
        if matches[matchIndex]:
            #print("Know Face Detected")
            #print(studentsIds[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentsIds[matchIndex]


            if counter == 0:
                counter = 1
                modeType = 1

    if counter != 0:

        if counter ==1:
            # GetData
            studentInfo = db.reference(f'Truckers/{id}').get()
            print(studentInfo)

            #Get Image
            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

            # Update date of login
            datetimeObject = datetime.strptime(studentInfo['Data_de_registro'],
                                              "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondsElapsed)

            ref = db.reference(f'Truckers/{id}')
            studentInfo['logins'] +=1
            ref.child('logins').set(studentInfo['logins'])
            ref.child('Data_de_registro').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if 10<counter<20:
            modeType = 2
        imgBackground[44:44 + 631, 808:808 + 415] = imgModeList[modeType]
        if counter<=10:
            cv2.putText(imgBackground, str(studentInfo['nome']),(808,445),
                cv2.FONT_HERSHEY_COMPLEX, 1,(50,50,50),1)
            cv2.putText(imgBackground, str(studentInfo['rg']),(1006,493),
                cv2.FONT_HERSHEY_COMPLEX, 0.5,(255,255,255),1)
            cv2.putText(imgBackground, str(studentInfo['carteiraMotorista']),(1006,550),
                cv2.FONT_HERSHEY_COMPLEX, 0.5,(255,255,255),1)



            imgBackground[175:175+216, 909:909+216] = imgStudent

        counter +=1

        if counter>=20:
            counter = 0
            modeType = 0
            studentInfo = []
            imgStudent = []
            imgBackground[44:44 + 631, 808:808 + 415] = imgModeList[modeType]

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
