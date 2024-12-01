import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import os

class TextAdventureGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Adventure Game")
        self.root.geometry("1000x800")
        
        # Main Frame to hold all widgets
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # Background Canvas
        background_image_path = "C:/Users/bella/Documents/GitHub/SeniorProject/Free Pixel Art Hill/Free Pixel Art Hill/PNG/background.png"
        bg_image = Image.open(background_image_path).resize((1000, 600))  # Resize to fit the window
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        self.canvas = tk.Canvas(main_frame, width=800, height=500)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)

        # Add the Notes Button on the Canvas
        self.notes_button = tk.Button(
            self.canvas,
            text="Notes",
            font=("Courier", 14),
            command=self.open_notes,
            bg="white",
            fg="black"
        )
        # Position the button on the canvas 
        self.notes_button_window = self.canvas.create_window(100, 20, anchor=tk.NE, window=self.notes_button)

        # Frame for Text Box and Input Field
        bottom_frame = tk.Frame(main_frame, bg="black")
        bottom_frame.pack(fill="x", side="bottom")

        # Text Box for Game Output
        self.text_box = ScrolledText(bottom_frame, wrap=tk.WORD, height=12, font=("Courier", 14), bg="black", fg="white")
        self.text_box.pack(fill="x", side="top")
        self.text_box.insert(tk.END, "Welcome to the Adventure Game! Type 'start' to begin.\n")

         # Frame for Input Field with Prompt Marker
        input_frame = tk.Frame(bottom_frame, bg="black")
        input_frame.pack(fill="x", side="top", pady=5)

        # Add the prompt marker as a label
        self.prompt_label = tk.Label(input_frame, text=">", font=("Courier", 14), bg="black", fg="white")
        self.prompt_label.pack(side="left", padx=5)

        # Input Field
        self.input_field = tk.Entry(input_frame, font=("Courier", 14), fg="white", bg="black", insertbackground="white")
        self.input_field.pack(fill="x", side="left", padx=5, expand=True)
        self.input_field.bind("<Return>", self.process_input)

        # Game State
        self.state = "start"
    
    def process_input(self, event):
        """Handle player input and update the game."""
        action = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)

        # Example game logic
        if self.state == "start" and action.lower() == "start":
            self.text_box.insert(tk.END, "\nThe game begins! What will you do?\n")
            self.state = "playing"
        elif self.state == "playing":
            self.text_box.insert(tk.END, f"\nYou chose: {action}\n")
        else:
            self.text_box.insert(tk.END, "\nInvalid action. Try again.\n")

        self.text_box.see(tk.END)  # Scroll to the latest text

    def open_notes(self):
        """Open a new window for writing notes."""
        notes_window = tk.Toplevel(self.root)
        notes_window.title("Notes")
        notes_window.geometry("600x400")

        # Frame for Save button
        button_frame = tk.Frame(notes_window)
        button_frame.pack(fill="x", padx=10, pady=5)

        # Frame to organize the layout
        notes_frame = tk.Frame(notes_window)
        notes_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ScrolledText for the notebook
        notes_text = ScrolledText(notes_frame, wrap=tk.WORD, font=("Courier", 12), bg="white", fg="black")
        notes_text.pack(fill="both", expand=True)

        # Add a Save button
        save_button = tk.Button(button_frame, text="Save Notes", font=("Courier", 12), command=lambda: self.save_notes(notes_text))
        save_button.pack(side="right")

        # Load existing notes if available
        if os.path.exists("notes.txt"):
            with open("notes.txt", "r") as file:
                notes_content = file.read()
                notes_text.insert(tk.END, notes_content)



    def save_notes(self, notes_widget):
        """Save notes to a file."""
        notes_content = notes_widget.get("1.0", tk.END).strip()
        with open("notes.txt", "w") as file:
            file.write(notes_content)
        self.text_box.insert(tk.END, "\nNotes saved successfully!\n")
        self.text_box.see(tk.END)

    def get_user_input(self, event):
        action = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)
        return action

    def display_text(self, text="ey bruh"):
        formated_text = f"\n{text}\n"
        self.text_box.insert(tk.END, formated_text)


# start frontend function
def start_frontend():
    root = tk.Tk()
    app = TextAdventureGameGUI(root)
    root.mainloop()

start_frontend()


