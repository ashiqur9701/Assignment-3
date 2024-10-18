import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import os  # Ensure os is imported
from tkinter import ttk

# AI model handler class
class AIModelHandler:
    def __init__(self):
        # Load the default MobileNetV2 model
        self.model = tf.keras.applications.MobileNetV2(weights='imagenet')

    def classify_image(self, image_path):
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Predict the image class
        predictions = self.model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=5)

        # Display top 5 predictions with confidence scores
        results = [f"{i+1}. {pred[1]} ({pred[2]*100:.2f}%)" for i, pred in enumerate(decoded_predictions[0])]
        return "\n".join(results)

# Main application class with Tkinter and AI model handling
class ImageClassifierApp(TkinterDnD.Tk, AIModelHandler):
    def __init__(self):
        TkinterDnD.Tk.__init__(self)  # Enable Drag and Drop functionality
        AIModelHandler.__init__(self)
        self.title("AI Image Classifier")
        self.geometry('800x1000')  # Adjusted width for side-by-side layout

        # Set vibrant background color and padding
        self.configure(bg='#1E1E1E')

        # Dictionary to store recent classifications and associated image paths
        self.classification_map = {}

        # Main frame to hold everything
        main_frame = tk.Frame(self, bg='#1E1E1E')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for Upload Button and Progress
        left_frame = tk.Frame(main_frame, bg='#1E1E1E')
        left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        # Right frame for Drop Target and Image Display
        right_frame = tk.Frame(main_frame, bg='#1E1E1E')
        right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

        # Title label with font and color
        self.title_label = tk.Label(left_frame, text="AI Image Classifier", font=("Helvetica", 20, "bold"), bg='#1E1E1E', fg="#FFD700")
        self.title_label.pack(pady=15)

        # Instructions with color
        self.instructions = tk.Label(left_frame, text="Upload or Drop an image to classify:", font=("Arial", 16), bg='#1E1E1E', fg="#FFD700")
        self.instructions.pack(pady=10)

        # Style for vibrant buttons
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 14, 'bold'), background='#FF4500', foreground='white')
        style.map('TButton', background=[('active', '#FF6347')], foreground=[('active', 'white')])

        # Upload button with vibrant styling
        self.upload_button = ttk.Button(left_frame, text="Upload Image(s)", command=self.upload_images, style='TButton')
        self.upload_button.pack(pady=10)

        # Drop target for drag-and-drop functionality with a vibrant background
        self.drop_target = tk.Label(right_frame, text="Or Drop Images Here", width=40, height=10, relief="sunken", bg="#444444", fg="white")
        self.drop_target.pack(pady=15)
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind('<<Drop>>', self.drop_files)

        # Progress bar
        self.progress = tk.Label(left_frame, text="", font=("Arial", 14), bg='#1E1E1E', fg="#FFD700")
        self.progress.pack(pady=10)

        # Label to display result
        self.result_label = tk.Label(left_frame, text="", font=("Arial", 16), bg='#1E1E1E', fg="#FFD700")
        self.result_label.pack(pady=20)

        # Save and load history buttons with vibrant styling
        self.save_history_button = ttk.Button(left_frame, text="Save History", command=self.save_history, style='TButton')
        self.save_history_button.pack(pady=5)

        self.load_history_button = ttk.Button(left_frame, text="Load History", command=self.load_history, style='TButton')
        self.load_history_button.pack(pady=5)

        # Recently classified images list with contrasting background
        self.history_label = tk.Label(left_frame, text="Recent Classifications:", font=("Arial", 16, "bold"), bg='#1E1E1E', fg="#FFD700")
        self.history_label.pack(pady=15)

        # Frame for Listbox and Scrollbar
        self.history_frame = tk.Frame(left_frame, bg='#1E1E1E')
        self.history_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Scrollbar for the Listbox
        self.scrollbar = tk.Scrollbar(self.history_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Increase Listbox height for better visibility of classifications
        self.history_box = tk.Listbox(self.history_frame, height=10, width=60, yscrollcommand=self.scrollbar.set, font=("Arial", 14), bg='#333333', fg="white")
        self.history_box.pack(pady=10, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.history_box.yview)

        # Bind selection event to history box
        self.history_box.bind("<<ListboxSelect>>", self.on_history_select)

        # Clear history button with vibrant styling
        self.clear_history_button = ttk.Button(left_frame, text="Clear History", command=self.clear_history, style='TButton')
        self.clear_history_button.pack(pady=15)

        # Create an image label for displaying images (keeps reference for proper updating), moved to the right
        self.image_label = tk.Label(right_frame, bg='#1E1E1E', width=400, height=400)  # Define specific width and height
        self.image_label.pack(pady=15)
        self.image_ref = None  # Placeholder to store image reference

    def drop_files(self, event):
        file_paths = self.tk.splitlist(event.data)
        self.upload_images(file_paths)

    def upload_images(self, file_paths=None):
        if file_paths is None:
            file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.png")])
        if file_paths:
            for file_path in file_paths:
                self.classify_and_display(file_path)

    def classify_and_display(self, file_path):
        self.progress.config(text=f"Classifying {os.path.basename(file_path)}...")
        self.update()

        # Display the image
        self.display_image(file_path)

        # Classify the image
        classification = self.classify_image(file_path)
        self.result_label.config(text=f"Top Predictions for {os.path.basename(file_path)}:\n{classification}")

        # Store both image path and classification result in a dictionary
        classification_entry = f"{os.path.basename(file_path)}"
        self.classification_map[classification_entry] = {"image_path": file_path, "classification": classification}

        # Insert entry into history listbox
        self.history_box.insert(tk.END, classification_entry)
        self.progress.config(text="Classification complete!")

    def display_image(self, path):
        # Ensure the image is resized appropriately and fully visible
        img = Image.open(path)
        img.thumbnail((400, 400))  # Resize to fit within a 400x400 box
        self.image_ref = ImageTk.PhotoImage(img)  # Store reference to prevent garbage collection
        self.image_label.config(image=self.image_ref)

    def save_history(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                for item in self.history_box.get(0, tk.END):
                    f.write(f"{item}\n")
            messagebox.showinfo("Save Successful", "History saved successfully!")

    def load_history(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                self.history_box.delete(0, tk.END)
                for line in f:
                    self.history_box.insert(tk.END, line.strip())

    def clear_history(self):
        self.history_box.delete(0, tk.END)

    def on_history_select(self, event):
        # Get the selected item
        if not self.history_box.curselection():
            return
        index = self.history_box.curselection()[0]
        selected_entry = self.history_box.get(index)

        # Find the corresponding file path and reload the image and classification
        selected_data = self.classification_map.get(selected_entry)
        if selected_data:
            file_path = selected_data["image_path"]
            classification = selected_data["classification"]
            
            # Display the image
            self.display_image(file_path)
            
            # Display the classification result
            self.result_label.config(text=f"Top Predictions for {os.path.basename(file_path)}:\n{classification}")

if __name__ == "__main__":
    app = ImageClassifierApp()
    app.mainloop()

