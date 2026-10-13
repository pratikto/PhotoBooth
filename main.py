import tkinter as tk


def start_session():
    status_label.config(
        text="Tombol berfungsi! Berikutnya kita sambungkan kamera."
    )


app = tk.Tk()
app.title("Photo Booth")
app.geometry("900x600")
app.configure(bg="#111827")

title = tk.Label(
    app,
    text="PHOTO BOOTH",
    font=("Arial", 32, "bold"),
    fg="white",
    bg="#111827",
)
title.pack(pady=(40, 10))

preview = tk.Frame(app, width=700, height=300, bg="#1f2937")
preview.pack(pady=25)
preview.pack_propagate(False)

preview_label = tk.Label(
    preview,
    text="AREA PREVIEW KAMERA",
    font=("Arial", 20),
    fg="#9ca3af",
    bg="#1f2937",
)
preview_label.pack(expand=True)

start_button = tk.Button(
    app,
    text="MULAI FOTO",
    font=("Arial", 18, "bold"),
    command=start_session,
    padx=30,
    pady=12,
)
start_button.pack(pady=5)

status_label = tk.Label(
    app,
    text="",
    font=("Arial", 12),
    fg="#d1d5db",
    bg="#111827",
)
status_label.pack(pady=10)

app.bind("<Escape>", lambda event: app.destroy())
app.mainloop()