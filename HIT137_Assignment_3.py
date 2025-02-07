import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Scale, HORIZONTAL

class ImageProcessor:
    def __init__(self, root):
        # Variables
        self.root = root
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

            #Get the Width and Height of the GUI Window.
            window_w = self.root.winfo_width()
            window_h = self.root.winfo_height()

            image_resized = cv2.resize(self.image, (window_w, window_h))

            #Display the resized image and set the mouse callback to the select_crop_area function
            cv2.imshow("Image", image_resized)
            cv2.setMouseCallback("Image", self.select_crop_area)

    def enable_cropping(self):
        if self.image is None:
            print("Select an image first!")
            return
        """ Activate cropping functionality when the Crop button is pressed. """
        self.cropping = True
        print("Cropping enabled. Make a selection on the image.")

    def select_crop_area(self, event, x, y, flags, param):
        if not self.cropping:
            return
        """Handles mouse events for selecting and inverting the crop area."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.ref_point = [(x, y)]

        elif event == cv2.EVENT_LBUTTONUP:
            self.ref_point.append((x, y))

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
                
                self.cropping = False

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
            scale_percent = float(scale_value) / 100.0
            width = int(self.modified_image.shape[1] * scale_percent)  # Fix: Use shape[1] for width
            height = int(self.modified_image.shape[0] * scale_percent)  # Fix: Use shape[0] for height
            resized = cv2.resize(self.modified_image, (width, height), interpolation=cv2.INTER_AREA)

            cv2.imshow("Resized Image", resized)
            self.modified_image = resized  # Update modified_image to the resized version
        else:
            print("No image loaded to resize! Upload an Image!")
            
    def save_image(self):
        """ Save the resized or modified image."""
        if self.modified_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All Files", "*.*")])
            if save_path:
                cv2.imwrite(save_path, self.modified_image)  # Corrected from imwriter to imwrite
                print("Image saved successfully!")
        else:
            print("No Image loaded to save!")

def main():
    root = Tk()
    root.title("Simple Image Editor")

    #Get the current User's screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    #Set the window size to half of the screen size.
    window_width = int(screen_width / 2)
    window_height = int(screen_height / 2)

    #Sets the geometry, takes a String representation as arguments to set the window width and height.
    root.geometry(str(window_width) + "x" + str(window_height))

    #Instantiate ImageProcessor class object.
    processor = ImageProcessor(root)

    #Buttons for Upload, Crop, Resize, and Save
    upload_button = Button(root, text="Upload Image", command=processor.load_image)
    upload_button.pack()

    crop_button = Button(root, text="Crop", command=processor.enable_cropping)
    crop_button.pack()

    resize_slider = Scale(root, from_=10, to=100, orient=HORIZONTAL, label="Resize %", command=processor.resize_image)
    resize_slider.set(100)  #Default 100%
    resize_slider.pack()

    #Bind the ButtonRelease SEQUENCE to the slider release function.
    resize_slider.bind("<ButtonRelease-1>", processor.resize_image)

    save_button = Button(root, text="Save Image", command=processor.save_image)
    save_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()


                

       