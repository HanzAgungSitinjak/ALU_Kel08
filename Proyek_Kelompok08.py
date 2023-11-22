import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo

app = tk.Tk()
app.title("Aplikasi Penentu Kematangan Buah Mangga")
app.geometry("1000x400")
app.resizable(False, False)

# Membuat PanedWindow untuk membagi window menjadi dua bagian
panedwindow = ttk.Panedwindow(app, orient=tk.HORIZONTAL)
panedwindow.pack(fill=tk.BOTH, expand=True)

# Membuat dua frame di dalam PanedWindow
frame1 = ttk.Frame(panedwindow, width=350, height=200, relief=tk.SUNKEN)
frame2 = ttk.Frame(panedwindow, width=700, height=200, relief=tk.SUNKEN)

# Menambahkan frame ke dalam PanedWindow
panedwindow.add(frame1)
panedwindow.add(frame2)

# Variabel untuk menyimpan nama file
selected_file_name = ""
username_entered = ""

class FruitInfo:
    def __init__(self, hue_value, rgb_values, maturity_level, is_unripe):
        self.hue_value = hue_value
        self.rgb_values = rgb_values
        self.maturity_level = maturity_level
        self.is_unripe = is_unripe

# Fungsi tombol pada frame 1
def rgb_to_hue(rgb):
    R, G, B = rgb
    hue = np.arctan2(np.sqrt(3) * (G - B), 2 * R - G - B)
    hue_degrees = np.degrees(hue)

    # Pastikan nilai Hue tidak negatif
    if hue_degrees < 0:
        hue_degrees += 360

    return hue_degrees

def is_unripe_color(rgb):
    # Ambil nilai warna RGB
    red, green, blue = rgb

    # Tentukan aturan berdasarkan nilai RGB
    if green > 150 and red < 150 and blue > 100:
        return True  # Warna cocok dengan kondisi buah belum matang
    else:
        return False  # Warna tidak sesuai dengan kondisi buah belum matang

def feature_extraction_and_color_analysis(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image from BGR to HSV
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Extract the Hue values
    hue_values = image_hsv[:,:,0].flatten()

    # Calculate the mean Hue value
    mean_hue = int(np.mean(hue_values))

    # Extract the RGB values and convert them to integers
    rgb_values = image.mean(axis=(0, 1)).astype(int)

    # Check if the color indicates unripe fruit
    unripe_color = is_unripe_color(rgb_values)

    return mean_hue, rgb_values, unripe_color

def define_maturity_rules():
    # Define color-based rules for determining maturity based on Hue value
    rules = [
        {"hue_range": (190, 330), "maturity_level": "Terlalu Matang"},
        {"hue_range": (171, 189), "maturity_level": "Matang"},
        {"hue_range": (0, 170), "maturity_level": "Belum Matang"},
    ]
    return rules

def backtracking_algorithm(rgb_values, maturity_rules):
    # Convert RGB values to Hue degrees
    hue_degrees = rgb_to_hue(rgb_values)

    # Backtracking algorithm to explore the decision space based on defined rules.
    for rule in maturity_rules:
        if rule["hue_range"][0] <= hue_degrees <= rule["hue_range"][1]:
            return rule["maturity_level"]
    return "Tingkat Kematangan tidak ditemukan"

def get_description_based_on_maturity(maturity_level):
    if maturity_level == "Terlalu Matang":
        return "Buah ini sudah mencapai tingkat kematangan maksimum."
    elif maturity_level == "Matang":
        return "Buah ini sudah cukup matang dan siap untuk dikonsumsi."
    elif maturity_level == "Belum Matang":
        return "Buah ini masih belum matang dan sebaiknya tunggu beberapa \n waktu sebelum dikonsumsi."
    else:
        return "Deskripsi tidak tersedia."

def tombol_username():
    global username_entered
    nilai_username = USERNAME.get()
    if not nilai_username:
        pesan = "Error", "Mohon masukkan username"
        showinfo(title="Tolong dibaca", message=pesan)
        return
    username_entered = nilai_username
    label_sambut.config(text=f"Selamat menggunakan {nilai_username}")
    # Menambahkan label_sambut ke frame2 setiap kali tombol ditekan
    label_sambut.pack(pady=20)

# Fungsi untuk membuka dialog pemilihan gambar pada frame 2
def open_file_dialog():
    global selected_file_name
    global username_entered

    if not username_entered:
        pesan = "Mohon masukkan username terlebih dahulu"
        showinfo(title="Tolong dibaca", message=pesan)
        return

    file_path = filedialog.askopenfilename(title="Pilih Gambar", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        selected_file_name = file_path.split("/")[-1]
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, selected_file_name)
        label_file_name.config(text=f"Nama File: {selected_file_name}")
        hue_value, rgb_values, unripe_color = feature_extraction_and_color_analysis(file_path)
        maturity_level = backtracking_algorithm(rgb_values, define_maturity_rules())

        # Simpan informasi buah
        fruit_info = FruitInfo(hue_value, rgb_values, maturity_level, unripe_color)

        # Update label dengan tingkat kematangan
        result_label.config(text=f"Tingkat Kematangan:   {fruit_info.maturity_level}")

        # Update label dengan kode warna RGB+
        rgb_label.config(text=f"Warna RGB:   ({fruit_info.rgb_values[0]}, {fruit_info.rgb_values[1]}, {fruit_info.rgb_values[2]})")

        deskripsi = get_description_based_on_maturity(fruit_info.maturity_level)
        deskripsi_isi.config(text=f"{deskripsi}")

        display_image(file_path, selected_file_name)

# Fungsi untuk menampilkan gambar pada frame 2
def display_image(image_path, file_name):
    # Load the image
    image = Image.open(image_path)

    # Resize the image to fit the specified dimensions
    resized_image = image.resize((150, 190))  # Sesuaikan ukuran sesuai kebutuhan

    # Convert the resized image to PhotoImage format for Tkinter
    image_tk = ImageTk.PhotoImage(resized_image)

    # Update the image label with the new image
    image_label.config(image=image_tk)
    image_label.image = image_tk  # Keep a reference to prevent garbage collection

    # Update the image path entry with the file name
    image_path_entry.delete(0, tk.END)
    image_path_entry.insert(0, file_name)

    # Update the label_file_name with the file name
    label_file_name.config(text=f"Nama File: {file_name}")

    # Menampilkan label-label tambahan
    result_label.place(relx=0.34, rely=0.4, anchor="w")
    rgb_label.place(relx=0.34, rely=0.48, anchor="w")
    deskripsi_label.place(relx=0.34, rely=0.56, anchor="w")
    deskripsi_isi.place(relx=0.34, rely=0.64, anchor="w")

# Widget pada frame 1
label_text = "Selamat Datang Di Aplikasi Kami"
label_username_text = "Masukkan Nama Anda:"
label_username = tk.Label(frame1, text=label_username_text)
USERNAME = tk.StringVar()
input_username = tk.Entry(frame1, width=30, font=("Helvetica", 12), textvariable=USERNAME)  # Mengatur lebar dan font
label = tk.Label(frame1, text=label_text, font=("Helvetica", 16))
tombol_input_username = tk.Button(frame1, width=30, text="Masukan", command=tombol_username)

# Meletakkan widget yang dibuat ke dalam frame 1
label.place(relx=0.5, rely=0.3, anchor="center")
label_username.place(relx=0.5, rely=0.5, anchor="center")
input_username.place(relx=0.5, rely=0.7, anchor="center")
tombol_input_username.place(relx=0.5, rely=0.8, anchor="center")

# Widget pada frame 2
label_sambut = tk.Label(frame2, text="Bisa beritahu nama anda?", font=("Helvetica", 16))
label_gambar = tk.Label(frame2, text="Pilih gambar buah:")
tombol_mencari_gambar = tk.Button(frame2, text="Pilih Gambar", command=open_file_dialog)
image_path_entry = ttk.Entry(frame2, state="readonly", width=30)
image_label = ttk.Label(frame2, text="", width=100)
label_file_name = tk.Label(frame2, text="Nama File: ")

# Label-label tambahan yang ingin disembunyikan
result_label = tk.Label(frame2, text="Tingkat Kematangan:")
rgb_label = tk.Label(frame2, text="Warna RGB:")
deskripsi_label = tk.Label(frame2, text="Deskripsi:")
deskripsi_isi = tk.Label(frame2, text="")

# Meletakkan widget yang dibuat ke dalam frame 2
label_sambut.place(relx=0.5, rely=0.1, anchor="center")
label_gambar.place(relx=0.4, rely=0.2, anchor="center")
tombol_mencari_gambar.place(relx=0.6, rely=0.2, anchor="center")
label_file_name.place(relx=0.5, rely=0.3, anchor="center")
image_path_entry.place(relx=0.5, rely=8, anchor="center")
image_label.place(relx=0.2, rely=0.6, anchor="center")

# Menjalankan aplikasi
app.mainloop()
