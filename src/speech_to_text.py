import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import speech_recognition as sr
import pyttsx3
import threading
import time
import os
from PIL import Image, ImageTk

class SpeechToTextConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text Converter")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Initialize speech recognition and text-to-speech
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS
        self.tts_engine.setProperty('rate', 150)  # Speech rate
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)  # First available voice
        
        # Variables
        self.is_listening = False
        self.audio_source = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Speech to Text Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Text display area
        text_frame = ttk.LabelFrame(main_frame, text="Converted Text", padding="10")
        text_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_display = tk.Text(text_frame, height=15, wrap=tk.WORD, font=("Arial", 11))
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Listen button
        self.listen_button = ttk.Button(controls_frame, text="Start Listening", 
                                       command=self.toggle_listening)
        self.listen_button.grid(row=0, column=0, padx=5)
        
        # Clear button
        clear_button = ttk.Button(controls_frame, text="Clear Text", 
                                 command=self.clear_text)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Save button
        save_button = ttk.Button(controls_frame, text="Save to File", 
                                command=self.save_to_file)
        save_button.grid(row=0, column=2, padx=5)
        
        # Speak button
        speak_button = ttk.Button(controls_frame, text="Speak Text", 
                                 command=self.speak_text)
        speak_button.grid(row=0, column=3, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to listen", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        self.is_listening = True
        self.listen_button.config(text="Stop Listening")
        self.status_label.config(text="Listening... Speak now!")
        
        # Start listening in a separate thread to avoid freezing the GUI
        self.listening_thread = threading.Thread(target=self.listen_continuously)
        self.listening_thread.daemon = True
        self.listening_thread.start()
    
    def stop_listening(self):
        self.is_listening = False
        self.listen_button.config(text="Start Listening")
        self.status_label.config(text="Ready to listen")
    
    def listen_continuously(self):
        with sr.Microphone() as source:
            self.audio_source = source
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self.is_listening:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Recognize speech using Google's speech recognition
                   text = self.recognizer.recognize_sphinx(audio)
                    
                    # Update text display in the main thread
                    self.root.after(0, self.update_text_display, text + " ")
                    
                except sr.WaitTimeoutError:
                    # Timeout is expected, continue listening
                    pass
                except sr.UnknownValueError:
                    self.root.after(0, lambda: self.status_label.config(text="Could not understand audio"))
                except sr.RequestError as e:
                    self.root.after(0, lambda: self.status_label.config(text=f"Error: {e}"))
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(text=f"Unexpected error: {e}"))
    
    def update_text_display(self, text):
        self.text_display.insert(tk.END, text)
        self.text_display.see(tk.END)  # Auto-scroll to bottom
        self.status_label.config(text="Text added successfully")
    
    def clear_text(self):
        self.text_display.delete(1.0, tk.END)
        self.status_label.config(text="Text cleared")
    
    def save_to_file(self):
        text_content = self.text_display.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showwarning("Warning", "No text to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_content)
                self.status_label.config(text=f"Text saved to {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Text saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def speak_text(self):
        text_content = self.text_display.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showwarning("Warning", "No text to speak!")
            return
        
        # Speak in a separate thread to avoid freezing the GUI
        def speak():
            try:
                self.tts_engine.say(text_content)
                self.tts_engine.runAndWait()
                self.root.after(0, lambda: self.status_label.config(text="Text spoken successfully"))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Error speaking text: {e}"))
        
        threading.Thread(target=speak, daemon=True).start()
        self.status_label.config(text="Speaking...")

def main():
    root = tk.Tk()
    app = SpeechToTextConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
