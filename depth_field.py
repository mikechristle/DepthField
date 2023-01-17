# ---------------------------------------------------------------------------
# Depth Field
# Mike Christle 2023
# ---------------------------------------------------------------------------

import tkinter as tk

from tkinter import messagebox
from make_df import run
from os.path import exists

FONT = "Arial", 16


# ---------------------------------------------------------------------------
def run_btn():
    cam = camera.get()
    cam = tuple(map(float, cam.split(',')))
    tar = target.get()
    tar = tuple(map(float, tar.split(',')))
    file_name = model.get()
    view = view_region.get()
    view = tuple(map(float, view.split(',')))
    size = image_size.get()
    size = tuple(map(int, size.split(',')))

    if not exists(file_name):
        msg = f'File does not exist: {file_name}'
        tk.messagebox.showerror(title=None, message=msg)
        return

    try:
        run(file_name, cam, tar, view, size)
    except Exception as error:
        tk.messagebox.showerror(title=None, message=error)


# ---------------------------------------------------------------------------
root = tk.Tk()
root.geometry('850x675')
root.title('Depth Field Maker   V1.0')

camera = tk.StringVar(root, '50., 50., 50.')
target = tk.StringVar(root, '0.0, 0.0, 0.0')
model = tk.StringVar(root, 'cube.obj')
view_region = tk.StringVar(root, '8.0, 6.0')
image_size = tk.StringVar(root, '800, 600')

label0 = tk.Label(root, text='TARGET', font=FONT, bd=20)
label0.grid(row=0, column=0)

entry0 = tk.Entry(root, textvariable=target, bd=5, font=FONT, width=15)
entry0.grid(row=0, column=1)

label1 = tk.Label(root, text='CAMERA', font=FONT, bd=20)
label1.grid(row=1, column=0)

entry1 = tk.Entry(root, textvariable=camera, bd=5, font=FONT, width=15)
entry1.grid(row=1, column=1)

label2 = tk.Label(root, text='MODEL', font=FONT, bd=20)
label2.grid(row=2, column=0)

entry2 = tk.Entry(root, textvariable=model, bd=5, font=FONT, width=15)
entry2.grid(row=2, column=1)

label3 = tk.Label(root, text='VIEW REGION', font=FONT, bd=20)
label3.grid(row=0, column=2)

entry3 = tk.Entry(root, textvariable=view_region, bd=5, font=FONT, width=15)
entry3.grid(row=0, column=3)

label4 = tk.Label(root, text='IMAGE SIZE', font=FONT, bd=20)
label4.grid(row=1, column=2)

entry4 = tk.Entry(root, textvariable=image_size, bd=5, font=FONT, width=15)
entry4.grid(row=1, column=3)

button0 = tk.Button(root, text="RUN", command=run_btn, bg='#00FF00', font=FONT, bd=5)
button0.grid(row=5, column=0)

root.mainloop()
