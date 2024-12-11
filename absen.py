import tkinter as tk
import cv2
import os
import pymongo
from PIL import Image, ImageTk
import threading
from dotenv import load_dotenv, find_dotenv
import face_recognition
from pymongo import MongoClient

# Koneksi
koneksi = f"mongodb+srv://ryan04:SL5epR1No0ptL3b4@ryan.rcqjcxt.mongodb.net/"
client = MongoClient(koneksi)
db = client.get_database("absensi_db")
collection = db.get_collection("users")

image_directory = f'C:\\Users\\ryan\\absens\\images\\'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

def add_data_to_db(name, student_id, class_name, image_path):
    student_data = {
        'name': name,
        'student_id': student_id,
        'class_name': class_name,
        'image_path': image_path
    }
    collection.insert_one(student_data)

# Fungsi untuk membersihkan label kamera
def clear_camera_label():
    label_camera.config(image='')
    label_camera.img = None

# Fungsi untuk registrasi wajah
def register_face():
    name = entry_name.get()
    student_id = entry_id.get()
    class_name = entry_class.get()

    global capture_flag, captured_image
    capture_flag = True
    captured_image = []

    # Aktifkan kamera dan simpan gambar wajah
    def capture_and_display():
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if ret:
            # Simpan gambar ke file
            image_path = os.path.join(image_directory, f'{student_id}.png')
            cv2.imwrite(image_path, frame)
            print(f"Image saved at: {image_path}")  # Debugging line

            # Simpan data ke MongoDB
            add_data_to_db(name, student_id, class_name, image_path)

            # Konversi gambar dari OpenCV (BGR) ke format yang dapat ditampilkan di tkinter (RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=image)

            # Tampilkan rekaman di GUI
            label_camera.config(image=imgtk)
            label_camera.img = imgtk

        camera.release()

    threading.Thread(target=capture_and_display).start()

# Fungsi untuk mengenali wajah
def recognize_face():
    clear_camera_label()
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    camera.release()

    if not ret:
        message_label.config(text="Gagal menangkap gambar!", fg="red")
        return

    # Ubah frame menjadi format face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    current_face_encodings = face_recognition.face_encodings(rgb_frame)

    if not current_face_encodings:
        message_label.config(text="Tidak ada wajah terdeteksi!", fg="red")
        return

    current_face_encoding = current_face_encodings[0]

    # Cocokkan dengan wajah yang terdaftar
    for data in collection.find():
        registered_image_path = data['image_path']
        registered_image = face_recognition.load_image_file(registered_image_path)
        registered_face_encodings = face_recognition.face_encodings(registered_image)

        if not registered_face_encodings:
            continue

        registered_face_encoding = registered_face_encodings[0]

        # Bandingkan wajah
        match_results = face_recognition.compare_faces([registered_face_encoding], current_face_encoding)
        if match_results[0]:
            message_label.config(text=f"Selamat Datang, Wajah dikenali: {data['name']}", fg="green")
            return

    message_label.config(text="Wajah tidak dikenali!", fg="red")

def close_image():
    clear_camera_label()

# Buat GUI
root = tk.Tk()
root.title("Aplikasi Absensi")

# Atur ukuran dan tata letak
root.geometry("400x400")
root.configure(bg='lightblue')

label_name = tk.Label(root, text="Nama:", bg='lightblue')
label_name.pack(pady=5)
entry_name = tk.Entry(root)
entry_name.pack(pady=5)

label_id = tk.Label(root, text="Nomor Induk:", bg='lightblue')
label_id.pack(pady=5)
entry_id = tk.Entry(root)
entry_id.pack(pady=5)

label_class = tk.Label(root, text="Kelas:", bg='lightblue')
label_class.pack(pady=5)
entry_class = tk.Entry(root)
entry_class.pack(pady=5)

button_register = tk.Button(root, text="Registrasi Wajah", command=register_face, bg='green', fg='white')
button_register.pack(pady=10)

button_recognize = tk.Button(root, text="Pengenalan Otomatis", command=recognize_face, bg='blue', fg='white')
button_recognize.pack(pady=10)

label_camera = tk.Label(root)
label_camera.pack(pady=10)

message_label = tk.Label(root, text="", bg='lightblue')
message_label.pack(pady=5)

root.mainloop()
