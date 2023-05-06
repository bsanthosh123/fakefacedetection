import os
import pickle

import tkinter as tk
from tkinter import messagebox
import face_recognition
import cv2


def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
                        window,
                        text=text,
                        activebackground="black",
                        activeforeground="white",
                        fg=fg,
                        bg=color,
                        command=command,
                        height=2,
                        width=15,
                        font=('Helvetica bold', 13)
                    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 13), justify="left")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=1,
                       width=10, font=("Arial", 25))
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)

def recognize(img, db_path):
    # Create a Haar Cascade classifier to detect faces
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # If no faces are found in the image, return 'no_persons_found'
    if len(faces) == 0:
        return 'no_persons_found'

    # Load face recognition model (optional)
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Load the face database and train the recognition model
    db_dir = sorted(os.listdir(db_path))
    for i, filename in enumerate(db_dir):
        path_ = os.path.join(db_path, filename)
        img_db = cv2.imread(path_)
        img_db_gray = cv2.cvtColor(img_db, cv2.COLOR_BGR2GRAY)
        faces_db = face_cascade.detectMultiScale(img_db_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces_db) > 0:
            x, y, w, h = faces_db[0]
            face = img_db_gray[y:y + h, x:x + w]
            face = cv2.resize(face, (100, 100))
            recognizer.update([face], [i])

    recognizer.train()

    # Iterate through each face found in the image and compare it to the faces in the database
    for x, y, w, h in faces:
        # Extract the face region from the image
        face = gray[y:y + h, x:x + w]

        # Resize the face region to a fixed size
        face = cv2.resize(face, (100, 100))

        # Use the recognition model to predict the identity of the face
        label, confidence = recognizer.predict(face)

        # If the predicted identity is in the database, return the corresponding name
        if label < len(db_dir):
            return db_dir[label][:-7]

    # If no matches are found, return 'unknown_person'
    return 'unknown_person'


# def recognize(img, db_path):
#
#     # it is assumed there will be at most 1 match in the db
#
#     embeddings_unknown = face_recognition.face_encodings(img)
#     if len(embeddings_unknown) == 0:
#         return 'no_persons_found'
#     else:
#         embeddings_unknown = embeddings_unknown[0]
#
#     db_dir = sorted(os.listdir(db_path))
#
#     match = False
#     j = 0
#     while not match and j < len(db_dir):
#         path_ = os.path.join(db_path, db_dir[j])
#
#         file = open(path_, 'rb')
#         embeddings = pickle.load(file)
#
#         match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
#         j += 1
#
#     if match:
#         return db_dir[j - 1][:-7]
#     else:
#         return 'unknown_person'