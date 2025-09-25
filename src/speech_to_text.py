import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import speech_recognition as sr
import pyttsx3
import threading
import time
import os
from PIL import Image, ImageTk

class OfflineSpeechToTextConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Offline Speech to Text Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize speech recognition and text-to-speech
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS
        self.tts_engine.setProperty('rate', 150)
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        
        # Variables
        self.is_listening = False
        self.audio_source = None
        self.recognition_engine = "sphinx"  # Default to offline engine
        
        self.setup_ui()
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check if required dependencies are available"""
        try:
            # Test if pocketsphinx is available
            import pocketsphinx
            self.status_label.config(text="Offline mode: Ready to listen")
            self.engine_var.set("sphinx")
        except ImportError:
            self.status_label.config(text="Warning: PocketSphinx not installed. Falling back to online mode.")
            self.engine_var.set("google")
            messagebox.showwarning(
                "Offline Mode Not Available", 
                "PocketSphinx not installed. Using online Google recognition.\n"
                "Install with: pip install pocketsphinx"
            )
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Offline Speech to Text Converter", 
                               font=("Arial", 16, "bold"), foreground="darkblue")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Recognition engine selection
        engine_frame = ttk.LabelFrame(main_frame, text="Recognition Engine", padding="5")
        engine_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.engine_var = tk.StringVar(value="sphinx")
        
        ttk.Radiobutton(engine_frame, text="Offline (PocketSphinx)", 
                       variable=self.engine_var, value="sphinx",
                       command=self.engine_changed).grid(row=0, column=0, padx=10)
        
        ttk.Radiobutton(engine_frame, text="Online (Google)", 
                       variable=self.engine_var, value="google",
                       command=self.engine_changed).grid(row=0, column=1, padx=10)
        
        # Engine info label
        self.engine_info = ttk.Label(engine_frame, text="✓ Works completely offline", 
                                    foreground="green")
        self.engine_info.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Text display area
        text_frame = ttk.LabelFrame(main_frame, text="Converted Text", padding="10")
        text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_display = tk.Text(text_frame, height=15, wrap=tk.WORD, font=("Arial", 11))
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Listen button
        self.listen_button = ttk.Button(controls_frame, text="Start Listening", 
                                       command=self.toggle_listening, width=15)
        self.listen_button.grid(row=0, column=0, padx=5)
        
        # Clear button
        clear_button = ttk.Button(controls_frame, text="Clear Text", 
                                 command=self.clear_text, width=12)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Save button
        save_button = ttk.Button(controls_frame, text="Save to File", 
                                command=self.save_to_file, width=12)
        save_button.grid(row=0, column=2, padx=5)
        
        # Speak button
        speak_button = ttk.Button(controls_frame, text="Speak Text", 
                                 command=self.speak_text, width=12)
        speak_button.grid(row=0, column=3, padx=5)
        
        # Audio settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Audio Settings", padding="5")
        settings_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Sensitivity adjustment
        ttk.Label(settings_frame, text="Microphone Sensitivity:").grid(row=0, column=0, sticky=tk.W)
        self.sensitivity_var = tk.DoubleVar(value=1.0)
        sensitivity_scale = ttk.Scale(settings_frame, from_=0.1, to=2.0, 
                                     variable=self.sensitivity_var, orient=tk.HORIZONTAL)
        sensitivity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        settings_frame.columnconfigure(1, weight=1)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Initializing...", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Initialize engine info
        self.engine_changed()
        
    def engine_changed(self):
        """Update UI when recognition engine is changed"""
        engine = self.engine_var.get()
        if engine == "sphinx":
            self.engine_info.config(text="✓ Works completely offline", foreground="green")
        else:
            self.engine_info.config(text="✗ Requires internet connection", foreground="red")
        
    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        self.is_listening = True
        self.listen_button.config(text="Stop Listening")
        self.status_label.config(text="Listening... Speak now!")
        
        # Start listening in a separate thread
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
            
            # Adjust for ambient noise with sensitivity
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.energy_threshold = 300 * self.sensitivity_var.get()
            self.recognizer.dynamic_energy_threshold = True
            
            while self.is_listening:
                try:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Recognize speech based on selected engine
                    engine = self.engine_var.get()
                    if engine == "sphinx":
                        text = self.recognize_with_sphinx(audio)
                    else:
                        text = self.recognize_with_google(audio)
                    
                    if text:
                        self.root.after(0, self.update_text_display, text + " ")
                    
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
    
    def recognize_with_sphinx(self, audio):
        """Recognize speech using offline PocketSphinx"""
        try:
            text = self.recognizer.recognize_sphinx(audio)
            self.root.after(0, lambda: self.status_label.config(text="Offline recognition successful"))
            return text
        except sr.UnknownValueError:
            self.root.after(0, lambda: self.status_label.config(text="Offline: Could not understand audio"))
            return ""
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Offline error: {str(e)}"))
            return ""
    
    def recognize_with_google(self, audio):
        """Recognize speech using online Google recognition"""
        try:
            text = self.recognizer.recognize_google(audio)
            self.root.after(0, lambda: self.status_label.config(text="Online recognition successful"))
            return text
        except sr.UnknownValueError:
            self.root.after(0, lambda: self.status_label.config(text="Online: Could not understand audio"))
            return ""
        except sr.RequestError as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Online error: No internet connection"))
            return ""
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Online error: {str(e)}"))
            return ""
    
    def update_text_display(self, text):
        self.text_display.insert(tk.END, text)
        self.text_display.see(tk.END)
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
    app = OfflineSpeechToTextConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
