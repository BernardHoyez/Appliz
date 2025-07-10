import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import piexif
import webbrowser

def dms_to_dd(d, m, s, ref):
    dd = d + m / 60 + s / 3600
    if ref in ['S', 'W']:
        dd *= -1
    return dd

def format_coord(value, is_lat):
    deg = int(abs(value))
    min_decimal = abs(value - deg) * 60
    direction = ('N' if value >= 0 else 'S') if is_lat else ('E' if value >= 0 else 'W')
    return f"{deg}°{min_decimal:.2f}{direction}"

def extract_gps(file_path):
    try:
        img = Image.open(file_path)
        exif_data = piexif.load(img.info['exif'])

        gps = exif_data["GPS"]
        lat = dms_to_dd(*[x[0]/x[1] for x in gps[2]], gps[1].decode())
        lon = dms_to_dd(*[x[0]/x[1] for x in gps[4]], gps[3].decode())

        date = exif_data["Exif"][36867].decode().split()[0].replace(":", "/")
        formatted = f"{date}_{format_coord(lat, True)}, {format_coord(lon, False)}"
        return formatted, lat, lon
    except Exception as e:
        return None, None, None

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg")])
    if not file_path:
        return
    result, lat, lon = extract_gps(file_path)
    if result:
        result_label.config(text=result)
        view_button.config(state=tk.NORMAL)
        view_button.lat = lat
        view_button.lon = lon
    else:
        messagebox.showerror("Erreur", "Impossible de lire les coordonnées GPS.")

def open_map():
    if hasattr(view_button, "lat") and hasattr(view_button, "lon"):
        lat, lon = view_button.lat, view_button.lon
        url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        webbrowser.open(url)

root = tk.Tk()
root.title("GPS Extracteur")
root.geometry("500x200")

btn = tk.Button(root, text="Choisir une image", command=open_image)
btn.pack(pady=10)

result_label = tk.Label(root, text="Coordonnées :")
result_label.pack(pady=10)

view_button = tk.Button(root, text="Voir sur carte", command=open_map, state=tk.DISABLED)
view_button.pack(pady=10)

root.mainloop()
