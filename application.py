from flask import Flask
from threading import Thread

application = Flask(__name__)

@application.route('/')
def home():
  return "Hello. I am alive!"

# def run():
#   application.run(host='0.0.0.0',port=8080)

# def keep_alive():
#   # use seperate thread for bot and web server
#   t = Thread(target=run)
#   t.start()