from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

db = firestore.Client()
doc_ref = db.collection("test").document("testdoc")
doc_ref.set({"hello": "world"})
print(doc_ref.get().to_dict())