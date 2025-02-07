import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Scale, HORIZONTAL

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Editor")

        self.root.
        # Buttons for Upload, Crop, Resize, and Save
        self.upload_button = Button(self.root, text="Upload Image", command=self.load_image)
        self.upload_button.pack()

        self.crop_button = Button(self.root, text="Crop", command=self.crop_image)
        self.crop_button.pack()

        self.resize_slider = Scale(self.root, from_=10, to=100, orient=HORIZONTAL, label="Resize %", command=self.resize_image)
        self.resize_slider.pack()

        self.save_button = Button(self.root, text="Save Image", command=self.save_image)
        self.save_button.pack()

        # Variables
        self.image = None
        self.clone = None
        self.ref_point = []
        self.cropping = False
        self.modified_image = None

    def load_image(self):
        """ Load an image and open an OpenCV window. """
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if file_path is not None:
            self.image = cv2.imread(file_path)
            self.clone = self.image.copy()
            self.modified_image = self.clone.copy()
            cv2.imshow("Image", self.image)
            cv2.setMouseCallback("Image", self.select_crop_area)

            return self.image
        return None

    def select_crop_area(self, event, x, y, flags, param):
        """Handles mouse events for selecting and inverting the crop area."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.ref_point = [(x, y)]
            self.cropping = True 

        elif event == cv2.EVENT_LBUTTONUP:
            self.ref_point.append((x, y))
            self.cropping = False

            # Get selected area
            x1, y1 = self.ref_point[0]
            x2, y2 = self.ref_point[1]

            # Ensure correct rectangle selection
            if x1 < x2 and y1 < y2:
                # Invert the selected area
                roi = self.clone[y1:y2, x1:x2]
                inverted_roi = cv2.bitwise_not(roi)
                self.clone[y1:y2, x1:x2] = inverted_roi

                # Store modified image
                self.modified_image = self.clone.copy()
                cv2.imshow("Modified Image", self.modified_image)

    def crop_image(self):
        """ Perform the cropping operation when the button is clicked. """
        if len(self.ref_point) == 2:
            x1, y1 = self.ref_point[0]
            x2, y2 = self.ref_point[1]
            # Ensure correct rectangle selection
            if x1 < x2 and y1 < y2:
                self.modified_image = self.clone[y1:y2, x1:x2]
                cv2.imshow("Modified Image", self.modified_image)
                
            else:
                print("Invalid crop area.")
        else:
            print("No crop area selected.")

    def resize_image(self, scale_value):
        """Resize the modified image based on slider input."""
        if self.modified_image is not None:
            scale_percent = int(scale_value) / 100.0
            width = int(self.modified_image.shape[1] * scale_percent)
            height = int(self.modified_image.shape[0] * scale_percent)
            resized = cv2.resize(self.modified_image, (width, height), interpolation=cv2.INTER_AREA)
            cv2.imshow("Resized Image", resized)
            self.modified_image = resized  # Update modified_image to the resized version

    def save_image(self):
        """ Save the resized or modified image."""
        if self.modified_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All Files", "*.*")])
            
            if save_path is not None:
                cv2.imwrite(save_path, self.modified_image)  #Corrected from imwriter to imwrite
                print("Image saved successfully!")    

root = Tk()
app = ImageEditorApp(root)
root.mainloop()