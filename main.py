import subprocess
import tkinter as tk
import util
import cv2
from PIL import Image, ImageTk
# import face_recognition
import os.path
import datetime
import geopy
from geopy.geocoders import Nominatim
import json
import requests
# from test import test
import pickle
import cv2
from tensorflow.keras.preprocessing.image import img_to_array
import os
import numpy as np
import opencage.geocoder
from tensorflow.keras.models import model_from_json
# Load Face Detection Model
face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")
# Load Anti-Spoofing Model graph
json_file = open('antispoofing_models/finalyearproject_antispoofing_model_mobilenet.json','r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
# load antispoofing model weights
model.load_weights('antispoofing_models/finalyearproject_antispoofing_model_74-0.986316.h5')
print("Model loaded from disk")


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")
        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)
        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray', self.register_new_user, fg='black')

        self.register_new_user_button_main_window.place(x=750, y=400)
        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)
        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):

        label1=""
        video = cv2.VideoCapture(0)
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            print("entered")
            face = frame[y - 5:y + h + 5, x - 5:x + w + 5]
            resized_face = cv2.resize(face, (160, 160))
            resized_face = resized_face.astype("float") / 255.0
            # resized_face = img_to_array(resized_face)
            resized_face = np.expand_dims(resized_face, axis=0)
            # pass the face ROI through the trained liveness detector
            # model to determine if the face is "real" or "fake"
            preds = model.predict(resized_face)[0]
            print(preds,"no predictions")
            if preds > 0.7:
                label1 = 'spoof'

            else:
                label1 = 'real'
            break
        video.release()
        cv2.destroyAllWindows()


        print(label1)

        # label=1
        # unknown_img_path = './.tmp.jpg'
        #
        # cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)
        #
        # output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
        # name = output.split(',')[1][:-5]
        # print(name)
        if label1 == "real":
           #  name = util.recognize(self.most_recent_capture_arr, self.db_dir)
            unknown_img_path = './.tmp.jpg'

            cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

            output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
            name = output.split(',')[1][:-5]
            print(name)
            if name in ['unknown_person', 'no_persons_found']:
                util.msg_box('Ups...', 'Unknown user. Please register new user or try again.')
            else:
                # Get the current location name
                geolocator = Nominatim(user_agent="my_app")

                # make an API call to get the user's current location
                response = requests.get("https://ipinfo.io/json")
                data = json.loads(response.text)
                # extract the latitude and longitude coordinates from the API response
                lat, lng = data['loc'].split(',')
                key = 'c9108ca48b98481b9625802a5b2affa4'  # replace with your OpenCage API key
                geocoder = opencage.geocoder.OpenCageGeocode(key)

                results = geocoder.reverse_geocode(lat,
                                                   lng)  # pass in the latitude and longitude coordinates of your current location
                print(lat,lng)

                print(results[0]['components']['state_district'])
                # location_name = geolocator.reverse("{},{}".format(lat, lng)).address
                # print(location_name)
                location_name=results[0]['components']['state_district']

                # util.msg_box('Welcome back !', 'Welcome, {}. You are in {}.'.format(name, location_name))
                util.msg_box('Welcome back !', 'Welcome, {}. You are in Visakhapatnam.'.format(name))
                print("alredy give msg")

                with open(self.log_path, 'a') as f:
                    f.write('{},{},{},in\n'.format(name, datetime.datetime.now(), location_name))
                    f.close()
                print("ended")
        else:
            util.msg_box('Hey, you are a spoofer!', 'You are fake !')

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)

        self.accept_button_register_new_user_window.place(x=750, y=200)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red',  self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=300)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)



        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=120)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, \ninput username:')
        self.text_label_register_new_user.place(x=750, y=70)

    def start(self):
        self.main_window.mainloop()

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()


    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        cv2.imwrite(os.path.join(self.db_dir, '{}.jpg'.format(name)), self.register_new_user_capture)

        util.msg_box('Success!', 'User was registered successfully !')

        self.register_new_user_window.destroy()


if __name__ == "__main__":
    app = App()
    app.start()
