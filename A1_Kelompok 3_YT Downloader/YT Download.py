# Program Pengunduh YouTube (Lengkap dengan Thumbnail dan Tema)
# Variabel dan fungsi menggunakan Bahasa Indonesia

import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
from PIL import Image
import requests
from io import BytesIO
import threading

# =====================
# KONFIGURASI AWAL GUI
# =====================
ctk.set_appearance_mode("System")  # Tema awal
ctk.set_default_color_theme("blue")

jendela = ctk.CTk()
jendela.title("Pengunduh YouTube Indonesia")
jendela.geometry("700x600")

# =====================
# VARIABEL GLOBAL
# =====================
url_masukan = ctk.StringVar()
folder_pilihan = ""
kualitas_pilihan = ctk.StringVar(value="720p")
format_pilihan = ctk.StringVar(value="mp4")

# =====================
# FUNGSI PILIH FOLDER
# =====================
def pilih_folder():
    global folder_pilihan
    folder_pilihan = filedialog.askdirectory()
    if folder_pilihan:
        label_folder.configure(text=f"Folder: {folder_pilihan}")

# =====================
# FUNGSI AMBIL THUMBNAIL
# =====================
def tampilkan_thumbnail(url):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            thumbnail_url = info.get("thumbnail")
        
        respon = requests.get(thumbnail_url)
        gambar = Image.open(BytesIO(respon.content))
        gambar = gambar.resize((320, 180))
        gambar_ctk = ctk.CTkImage(light_image=gambar, size=(320, 180))
        label_thumbnail.configure(image=gambar_ctk)
        label_thumbnail.image = gambar_ctk
    except:
        label_thumbnail.configure(text="Thumbnail tidak dapat dimuat")

# =====================
# CALLBACK PROGRESS
# =====================
def proses_progress(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 0)
        unduh = d.get('downloaded_bytes', 0)
        if total > 0:
            persen = int(unduh / total * 100)
            progress_bar.set(persen / 100)
            label_status.configure(text=f"Mengunduh... {persen}%")
        
    elif d['status'] == 'finished':
        progress_bar.set(1)
        label_status.configure(text="Selesai mengunduh.")

# =====================
# FUNGSI UNDUH
# =====================
def mulai_unduh():
    url = url_masukan.get()
    if not url:
        label_status.configure(text="Masukkan URL terlebih dahulu.")
        return

    if not folder_pilihan:
        label_status.configure(text="Pilih folder penyimpanan.")
        return

    # Tampilkan thumbnail
    tampilkan_thumbnail(url)

    formatnya = format_pilihan.get()
    kualitas = kualitas_pilihan.get()

    opsi = {
        'outtmpl': f'{folder_pilihan}/%(title)s.%(ext)s',
        'progress_hooks': [proses_progress]
    }

    # Format MP4
    if formatnya == "mp4":
        opsi['format'] = f"bestvideo[height={kualitas}]+bestaudio/best"
    else:  # MP3
        opsi.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        })

    def jalankan():
        try:
            with yt_dlp.YoutubeDL(opsi) as ydl:
                info = ydl.extract_info(url)
                nama = info.get("title")
                label_file.configure(text=f"File: {nama}")
        except Exception as e:
            label_status.configure(text=f"Gagal: {e}")

    threading.Thread(target=jalankan).start()

# =====================
# FUNGSI UBAH TEMA
# =====================
def ubah_tema(pilihan):
    ctk.set_appearance_mode(pilihan)

# =====================
# GUI
# =====================

judul = ctk.CTkLabel(jendela, text="Pengunduh YouTube", font=("Arial", 22))
judul.pack(pady=10)

kotak_url = ctk.CTkEntry(jendela, textvariable=url_masukan, width=450, placeholder_text="Masukkan URL YouTube")
kotak_url.pack(pady=10)

# Thumbnail
label_thumbnail = ctk.CTkLabel(jendela, text="Thumbnail akan muncul di sini")
label_thumbnail.pack(pady=10)

# Folder
tombol_folder = ctk.CTkButton(jendela, text="Pilih Folder", command=pilih_folder)
tombol_folder.pack()
label_folder = ctk.CTkLabel(jendela, text="Belum memilih folder")
label_folder.pack(pady=5)

# Format
label_format = ctk.CTkLabel(jendela, text="Format:")
label_format.pack(pady=5)

pilihan_format = ctk.CTkOptionMenu(jendela, values=["mp4", "mp3"], variable=format_pilihan)
pilihan_format.pack()

# Kualitas
label_kualitas = ctk.CTkLabel(jendela, text="Kualitas video:")
label_kualitas.pack(pady=5)

pilihan_kualitas = ctk.CTkOptionMenu(jendela, values=["360p", "480p", "720p", "1080p"], variable=kualitas_pilihan)
pilihan_kualitas.pack()

# Tema
label_tema = ctk.CTkLabel(jendela, text="Tema tampilan:")
label_tema.pack(pady=5)

pilihan_tema = ctk.CTkOptionMenu(jendela, values=["Light", "Dark", "System"], command=ubah_tema)
pilihan_tema.pack()

# Tombol Unduh
unduh_tombol = ctk.CTkButton(jendela, text="Mulai Unduh", command=mulai_unduh)
unduh_tombol.pack(pady=10)

# Informasi file
label_file = ctk.CTkLabel(jendela, text="File: -")
label_file.pack(pady=5)

# Progress
progress_bar = ctk.CTkProgressBar(jendela, width=400)
progress_bar.set(0)
progress_bar.pack(pady=5)

# Status
label_status = ctk.CTkLabel(jendela, text="Status: -")
label_status.pack(pady=10)

jendela.mainloop()
