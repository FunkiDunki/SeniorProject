import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

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




