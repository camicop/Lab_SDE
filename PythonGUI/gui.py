import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from music_app import MusicApp
# import os
# import pathlib

class ModernMusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Processing App")
        self.root.geometry(f'450x{root.winfo_screenheight()-200}')
        self.root.configure(bg='#f0f0f0')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', 
                            padding=10, 
                            font=('Helvetica', 10),
                            background='#0066cc',
                            foreground='white')
        self.style.map('TButton',
                       background=[('active', '#0052a3')])
        self.style.configure('TLabel', 
                            background='#f0f0f0', 
                            font=('Helvetica', 10))
        self.style.configure('Header.TLabel', 
                            font=('Helvetica', 14, 'bold'))
        
        self.music_app =  MusicApp()
        self.create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.clear_extracted_song()
        self.root.destroy()

    def create_widgets(self):
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self.root, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Main container
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Step 1: Show available songs
        step1_frame = self.create_section_frame(main_frame, "Step 1: Available Songs")
        ttk.Button(step1_frame, text="Show Songs", command=self.show_songs).pack(pady=5)
        self.song_listbox = tk.Listbox(step1_frame, height=7, width=40, font=('Helvetica', 10))
        self.song_listbox.pack(pady=5)

        # Bind the listbox selection event to update the text entry in Step 2
        self.song_listbox.bind('<<ListboxSelect>>', self.on_song_select)
        
        # Step 2: Import song
        step2_frame = self.create_section_frame(main_frame, "Step 2: Import Song")
        entry_frame = ttk.Frame(step2_frame)
        entry_frame.pack(pady=5)
        self.song_entry = ttk.Entry(entry_frame, width=30, font=('Helvetica', 10))
        self.song_entry.pack(side="left", padx=5)
        ttk.Button(entry_frame, text="Import", command=self.import_song).pack(side="left", padx=5)
        self.import_status = ttk.Label(step2_frame, text="", font=('Helvetica', 10))
        self.import_status.pack(pady=5)
        
        # Step 3: Extract text
        step3_frame = self.create_section_frame(main_frame, "Step 3: Extract Text")
        ttk.Button(step3_frame, text="Extract Text", command=self.extract_text).pack(pady=5)
        self.text_display = tk.Text(step3_frame, height=4, width=40, font=('Helvetica', 10), wrap=tk.WORD, state='disabled')
        self.text_display.pack(pady=5)
        ttk.Button(step3_frame, text="Reproduce Text", command=self.reproduce_text).pack(pady=5)
        
        # Step 4: Search image
        step4_frame = self.create_section_frame(main_frame, "Step 4: Search Image")
        ttk.Button(step4_frame, text="Search Image", command=self.search_text).pack(pady=5)
        self.image_frame = ttk.Frame(step4_frame, width=400, height=300)
        self.image_frame.pack(pady=10)
        self.image_frame.pack_propagate(False)
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Button to trigger all steps sequentially
        step5_frame = self.create_section_frame(main_frame, "Step 5: Run all previous Steps")
        ttk.Button(step5_frame, text="Run", command=self.api_composition).pack(pady=20)

    def api_composition(self):
        # Step 1: Show available songs
        self.show_songs()
        
        # Step 2: Import the song
        self.root.after(1000, self.import_song_run_all)

        # Step 3: Extract the text after a delay
        self.root.after(2000, self.extract_text)

        # Step 4: Search for image after a further delay
        self.root.after(3000, self.search_text)

        # Step 5: Reproduce the extracted text
        # self.root.after(4000, self.reproduce_text)

    def create_section_frame(self, parent, title):
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill="x", pady=10)
        ttk.Label(frame, text=title, style='Header.TLabel').pack(anchor="w", pady=(0, 10))
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill="x")
        return content_frame

    def show_songs(self):
        self.song_listbox.delete(0, tk.END)
        try:
            songs = self.music_app.list_available_music()
            for song in songs:
                self.song_listbox.insert(tk.END, song)
        except Exception as e:
            self.song_listbox.insert(tk.END, f"Error: {str(e)}")

    def on_song_select(self, event):
        # Get the selected song from the listbox
        selected_index = self.song_listbox.curselection()
        if selected_index:
            selected_song = self.song_listbox.get(selected_index)
            # Update the song entry in Step 2 with the selected song
            self.song_entry.delete(0, tk.END)
            self.song_entry.insert(0, selected_song)

    def import_song(self):
        song_name = self.song_entry.get()
        if not song_name:
            self.update_status("Please enter a song name", "red")
            return
        
        try: 
            if self.music_app.import_song(song_name):
                self.update_status(f"{song_name} successfully imported!", "green")
            else:
                self.update_status(f"{song_name} does not exist!", "red")
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")

    """Function used when calling the run all action"""
    def import_song_run_all(self):

        song_name = "ShapeOfYou.mp3"

        #--- ui logic in order to fake selection ---
        self.song_entry.delete(0, tk.END)
        self.song_entry.insert(0, song_name)
        #-------------------------------------------
        
        try: 
            if self.music_app.import_song(song_name):
                self.update_status(f"{song_name} successfully imported!", "green")
            else:
                self.update_status(f"{song_name} does not exist!", "red")
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")

    def extract_text(self):
        try:
            song_text = self.music_app.extract_text()
            self.text_display.config(state='normal')  # Temporarily enable the widget
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, song_text)
            self.text_display.config(state='disabled')  # Disable the widget again
        except Exception as e:
            self.text_display.config(state='normal')  # Temporarily enable the widget
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, f"Error: {str(e)}")
            self.text_display.config(state='disabled')  # Disable the widget again

    def search_text(self):
        try:
            text = self.text_display.get(1.0, tk.END).strip()
            if not text:
                return
            
            image_path = self.music_app.search_and_download_image(text)
            if image_path:
                self.display_image(image_path)
        except Exception as e:
            print(f"Error searching/displaying image: {str(e)}")

    def display_image(self, image_path):
        try:
            pil_image = Image.open(image_path)
            pil_image.thumbnail((380, 280))
            photo = ImageTk.PhotoImage(pil_image)
            
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print(f"Error displaying image: {str(e)}")

    def reproduce_text(self):
        text = self.text_display.get(1.0, tk.END).strip()
        if not text:
            return
        
        self.music_app.reproduce_text(text)

    def update_status(self, message, color):
        self.import_status.config(text=message, foreground=color)

    def clear_extracted_song(self):
        self.music_app.clear_extracted_song()

def main():
    root = tk.Tk()
    app = ModernMusicApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
