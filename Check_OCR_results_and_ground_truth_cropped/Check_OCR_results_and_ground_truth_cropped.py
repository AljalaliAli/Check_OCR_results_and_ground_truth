
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import os
import configparser
from functions import *
from Image_functions import *

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the INI file
config.read('config.ini')

class ImageDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.resizable(width=True, height=True)
        # Access data
        cropped_imgs_dir = config.get('Paths', 'cropped_imgs_dir')
        self.ground_truth_dir = config.get('Paths', 'ground_truth_dir')
        
        self.db_dir  = config.get('Paths', 'db_dir')
        self.entry_default_value = 'default_value'

        self.create_image_label()
        self.create_entry_and_button()
        
        self.old_par_value=None
        self.corrected_par_value=None
        self.image_index = 0
        self.images_list = get_image_files_in_directory(cropped_imgs_dir)

    def create_image_label(self):
        self.img_canvas = tk.Canvas(self.root, bg='#fff')
        self.img_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



    def create_entry_and_button(self):
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(expand=True)  # Center the frame in the window

        # Create a sub-frame for centering the entry and button
        self.sub_frame = tk.Frame(self.control_frame)
        self.sub_frame.pack()

        self.entry_value = tk.StringVar(value=self.entry_default_value)
        self.entry = tk.Entry(self.sub_frame, width=50, font=("Courier", 12, "bold"), textvariable=self.entry_value)
        self.entry.pack(padx=10, pady=5)  # Add padding around the entry

        self.next_img_button = tk.Button(self.sub_frame, text="Next Image", command=self.show_next_image)
        self.next_img_button.pack(pady=5)  # Add padding around the button

        # Bind the <Return> key to call show_next_image
        self.entry.bind('<Return>', lambda event: self.show_next_image())

        # Center the sub-frame in the control frame
        self.sub_frame.pack(expand=True)

        # Center the control frame in the root window
        self.control_frame.pack(expand=True, padx=20, pady=20)


    def display_image(self, img_dir_and_path):
        img_dir, img_name = img_dir_and_path

        self.update_entry_value(img_name)

        original_image = Image.open(os.path.join(img_dir, img_name))
        self.img = ImageTk.PhotoImage(original_image)
        self.img_canvas.create_image(0, 0, image=self.img, anchor="nw")
        self.img_canvas.config(scrollregion=self.img_canvas.bbox(tk.ALL))

    def update_entry_value(self, img_name):
        db_name, ts, par_name = extract_metadata_from_img_name(img_name)
        self.old_par_value = get_value_by_timestamp(os.path.join(self.db_dir, db_name), 'MDE', ts, par_name)
        self.entry_value.set(self.old_par_value)

    def show_next_image(self):
        self.corrected_par_value = self.entry_value.get()
        pre_img_dir, pre_img_name = self.images_list[self.image_index]
        create_gt_text_file(pre_img_dir, pre_img_name ,self.old_par_value,self.corrected_par_value , self.ground_truth_dir)
        
        self.image_index = (self.image_index + 1) % len(self.images_list)
        self.display_image(self.images_list[self.image_index])

    def on_close(self):
        print("Entry value:", self.entry_value.get())
        self.root.destroy()

    def run(self):
        self.display_image(self.images_list[self.image_index])
        self.root.mainloop()
 

if __name__ == "__main__":
    app = ImageDisplay()
    app.run()
