import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk

def load_image():
    """Load an image using file dialog and display it."""
    global img, img_display, original_size, initial_scale, save_scale
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])

    if not file_path:  # If no file selected, do nothing
        return

    img = cv2.imread(file_path)

    if img is None:
        messagebox.showerror("Error", "Could not open image file!")
        return

    # Convert the image to RGB (for display) but keep the original for saving
    img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Store the original image resolution (height, width)
    original_size = img.shape[:2]  # (height, width)

    # Adjust slider max based on image size to fit the window
    scale_w = max_size[0] / original_size[1]
    scale_h = max_size[1] / original_size[0]
    max_scale = min(scale_w, scale_h) * 100  # Convert to percentage

    slider.config(from_=10, to=max_scale)

    # Set the slider to the scale to fit the window
    initial_scale = 100 * min(scale_w, scale_h)
    slider.set(initial_scale)

    save_scale = 1.0  # Reset save scale to 1.0
    update_scale_label(initial_scale)
    display_image(img_display)  # Display the image
    
    print(initial_scale)

def resize_image(value):
    """Resize the image based on the slider's value and update display."""
    global save_scale, initial_scale, original_size

    if img is None:  # Prevent resizing if no image is loaded
        return

    # Save current image state to undo stack
    global undo_stack
    undo_stack.append((img.copy(), save_scale))
    if len(undo_stack) > 10:  # Limit undo history to the last 10 versions
        undo_stack.pop(0)

    scale_preview = float(value) / 100
    resized_img_preview = cv2.resize(img, (int(original_size[1] * scale_preview), int(original_size[0] * scale_preview)))
    resized_img_preview = cv2.cvtColor(resized_img_preview, cv2.COLOR_BGR2RGB)
    update_scale_label(value)  # Update scale label
    display_image(resized_img_preview)

    # Update save_scale for saving image later
    save_scale = (float(value) / 100) / (initial_scale / 100)  # Correct save scale

def display_image(image):
    """Convert image for Tkinter display and ensure it fits within the window."""
    image = Image.fromarray(image)

    # Ensure image fits within max display area (constrained by max_size)
    image.thumbnail(max_size, Image.LANCZOS)  # Update deprecated ANTIALIAS to LANCZOS

    tk_image = ImageTk.PhotoImage(image)
    img_label.config(image=tk_image)
    img_label.image = tk_image  # Keep reference

def update_scale_label(value):
    """Update the scale percentage label with a relative value."""
    # Calculate the relative scale based on the current slider value
    relative_scale = (float(value) / slider.cget('to')) * 100  # Relative scale based on slider max value
    scale_label.config(text=f"Scale: {relative_scale:.1f}%")

def save_image():
    """Save the resized image to a file."""
    global original_size, save_scale, img
    if img is None:
        messagebox.showwarning("Warning", "No image to save!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"),
                                                      ("JPEG files", "*.jpg"),
                                                      ("All Files", "*.*")])
    if not file_path:
        return  # Do nothing if user cancels

    # Ensure we are using valid original_size and save_scale values
    print(original_size)
    print(save_scale)
    
    # Use the original image resolution and scale for saving
    resized_img_save = cv2.resize(img, 
                                  (int(original_size[1] * save_scale), 
                                   int(original_size[0] * save_scale)))
    cv2.imwrite(file_path, resized_img_save)
    messagebox.showinfo("Success", f"Image saved to {file_path}")

def undo():
    """Undo the last image modification."""
    global img, img_display, save_scale, undo_stack
    if undo_stack:
        img, save_scale = undo_stack.pop()  # Pop the last state from the stack
        img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        update_scale_label(save_scale * 100)
        slider.set(save_scale * 100)  # Update the slider position
        display_image(img_display)
    else:
        messagebox.showwarning("Undo", "No more actions to undo!")

# --- GUI Setup ---
root = tk.Tk()
root.title("Image Resizer")

# Get screen size and adjust window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
win_width = int(screen_width * 0.6)  # 60% of screen width
win_height = int(screen_height * 0.7)  # 70% of screen height
root.geometry(f"{win_width}x{win_height}")

# Define max display size for images
max_size = (win_width - 150, win_height - 200)

# Global variables
img = None
img_display = None
original_size = (0, 0)  # Initial resolution (height, width)
save_scale = 1.0  # Default scale for saving the image
undo_stack = []  # Stack to store previous image states for undo

# Frames
frame_image = tk.Frame(root)
frame_image.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.BOTTOM, fill=tk.X)

# Image label
img_label = tk.Label(frame_image)
img_label.pack(expand=True)

# Load Button
btn_load = tk.Button(frame_controls, text="Load Image", command=load_image)
btn_load.pack(side=tk.LEFT, padx=10, pady=10)

# Undo Button
btn_undo = tk.Button(frame_controls, text="Undo", command=undo)
btn_undo.pack(side=tk.LEFT, padx=10, pady=10)

# Scale Label
scale_label = tk.Label(frame_controls, text="Scale: 100.0%")
scale_label.pack(side=tk.LEFT, padx=10)

# Slider (without numbers)
slider = tk.Scale(frame_controls, from_=10, to=100, orient=tk.HORIZONTAL, resolution=1,
                  command=resize_image, length=400, showvalue=False)
slider.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

# Save Button
btn_save = tk.Button(frame_controls, text="Save Image", command=save_image)
btn_save.pack(side=tk.RIGHT, padx=10, pady=10)

root.mainloop()
