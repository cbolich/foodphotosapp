# Note that the database only accepts connections for explicitly whitelisted IP addresses


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

password = quote_plus("mongodbpass")

uri = "mongodb+srv://jfrabut2:" + password + "@foodphotosapp.4vgexei.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# print(client.settings.find_one({'width': 768}))