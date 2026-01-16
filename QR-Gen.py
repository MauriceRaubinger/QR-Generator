import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import qrcode
import urllib.parse
import re
import os
import subprocess
import tempfile
import platform  # <--- Needed to detect Windows vs Mac

# --- CONFIGURATION ---
BASE_URL = "https://mauriceraubinger.github.io/fliesen-info/"

# Variable to remember where we saved the last file
last_saved_path = None


def clean_filename(text):
    """Creates a clean filename"""
    return re.sub(r'[^a-zA-Z0-9]', '_', text).lower()


def open_file():
    """Opens the saved file using the default OS viewer (Cross-Platform)"""
    global last_saved_path

    if not last_saved_path or not os.path.exists(last_saved_path):
        messagebox.showwarning("Fehler", "Keine Datei gefunden.\nBitte erst einen Code generieren.")
        return

    current_os = platform.system()

    try:
        if current_os == "Windows":
            os.startfile(last_saved_path)
        elif current_os == "Darwin":  # Darwin is the internal name for macOS
            subprocess.run(["open", last_saved_path])
        else:
            # Linux fallback
            subprocess.run(["xdg-open", last_saved_path])

    except Exception as e:
        messagebox.showerror("Fehler", f"Konnte Datei nicht öffnen:\n{e}")


def generate_qr():
    global last_saved_path

    # 1. Get Data
    name = entry_name.get()
    price = entry_price.get()
    details = entry_details.get()

    if not name or not price:
        messagebox.showwarning("Achtung", "Bitte gib mindestens Name und Preis ein!")
        return

    # 2. URL Encoding
    safe_name = urllib.parse.quote(name)
    safe_price = urllib.parse.quote(price)
    safe_details = urllib.parse.quote(details)

    # 3. Build Link
    final_url = f"{BASE_URL}?name={safe_name}&price={safe_price}&details={safe_details}"

    # 4. Create QR
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(final_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 5. Save (Temp Folder - Cross Platform)
    try:
        temp_dir = tempfile.gettempdir()
        filename = f"QR_{clean_filename(name)}.png"
        full_save_path = os.path.join(temp_dir, filename)

        img.save(full_save_path)

        last_saved_path = full_save_path

        # 6. Preview
        img_preview = img.resize((200, 200))
        tk_img = ImageTk.PhotoImage(img_preview)

        label_preview.config(image=tk_img)
        label_preview.image = tk_img

        # Status update
        status_label.config(text=f"✅ Bereit zum Drucken: {filename}", fg="green")

        # Enable Button
        btn_open.config(state=tk.NORMAL, bg="#0366d6", cursor="hand2")

    except Exception as e:
        messagebox.showerror("Fehler", f"Konnte Datei nicht speichern:\n{e}")
        status_label.config(text="❌ Fehler", fg="red")


# --- GUI SURFACE ---
root = tk.Tk()
root.title("Fliesen QR Generator")
root.geometry("400x700")
root.resizable(False, False)

# Header
tk.Label(root, text="Fliesen-Label Generator", font=("Arial", 18, "bold")).pack(pady=15)
tk.Label(root, text="Erstellt QR-Code (Temp Mode)", font=("Arial", 9), fg="gray").pack()

# Form
frame_form = tk.Frame(root)
frame_form.pack(pady=20)

tk.Label(frame_form, text="Produkt Name:", font=("Arial", 10, "bold")).pack(anchor="w")
entry_name = tk.Entry(frame_form, width=35, font=("Arial", 11))
entry_name.pack(pady=5)

tk.Label(frame_form, text="Preis (z.B. 49,90 €):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
entry_price = tk.Entry(frame_form, width=35, font=("Arial", 11))
entry_price.pack(pady=5)

tk.Label(frame_form, text="Details / Beschreibung:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
entry_details = tk.Entry(frame_form, width=35, font=("Arial", 11))
entry_details.pack(pady=5)

# Button Generate
btn = tk.Button(root, text="QR Code Erstellen", command=generate_qr, bg="#2ea44f", fg="white",
                font=("Arial", 12, "bold"), height=2, width=30)
btn.pack(pady=10)

# Status
status_label = tk.Label(root, text="Bereit...", fg="#666", wraplength=380)
status_label.pack()

# Preview
label_preview = tk.Label(root)
label_preview.pack(pady=10)

# Open Button
btn_open = tk.Button(root, text="📂 Öffnen & Drucken", command=open_file,
                     bg="#dddddd", fg="white", state=tk.DISABLED,
                     font=("Arial", 11, "bold"), height=2, width=30)
btn_open.pack(pady=(0, 20))

root.mainloop()