import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://reconhecimentofacial-83d23-default-rtdb.firebaseio.com/"
})

ref = db.reference('Truckers')

data = {
    "159837":
        {
            "nome": "Gustavo",
            "carteiraMotorista": "11111111",
            "rg": "11111111",
            "logins": 1,
            "Data_de_registro": "2023-08-22 21:47:32"
        },
    "160605":
        {
            "nome": "Gabriel",
            "carteiraMotorista": "2222222",
            "rg": "222222222",
            "logins": 1,
            "Data_de_registro": "2023-08-22 21:47:32"
        },
    "167630":
        {
            "nome": "Julia",
            "carteiraMotorista": "333333333",
            "rg": "33333333",
            "logins": 1,
            "Data_de_registro": "2023-08-22 21:47:32"
        }
}

for key, value in data.items():
    ref.child(key).set(value)


