import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame
import io
import threading
from PIL import Image, ImageTk
from langdetect import detect

from app.constant import read_file


def translate_text(text, target_language):
    translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
    return translated_text


def text_to_speech(text, lang='en'):
    global is_playing
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    pygame.mixer.init()

    pygame.mixer.music.load(fp, 'mp3')
    pygame.mixer.music.play()

    is_playing = True
    while pygame.mixer.music.get_busy() and is_playing:
        pygame.time.Clock().tick(10)


def stop_text_to_speech():
    global is_playing
    pygame.mixer.music.stop()
    is_playing = False


def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"),
                                                      ("Text Files", "*.txt"),
                                                      ("Word Documents", "*.doc;*.docx"),
                                                      ("Excel Files", "*.xls;*.xlsx"),
                                                      ("PDF Files", "*.pdf"),
                                                      ("PowerPoint Files", "*.pptx")
                                                      ])
    if file_path:
        file_content = read_file(file_path)
        if file_content:
            text_box.delete(1.0, tk.END)
            text_box.insert(tk.END, file_content)


def translate_custom():
    original_text = text_box.get(1.0, tk.END).strip()
    if original_text:
        translated_text = translate_text(original_text, target_language_var.get())
        translated_text_box.delete(1.0, tk.END)
        translated_text_box.insert(tk.END, translated_text)
    else:
        messagebox.showwarning("Warning", "Please enter text to translate.")


def translate_and_speak():
    file_content = text_box.get(1.0, tk.END).strip()
    if file_content:
        translated_text = translate_text(file_content, target_language_var.get())
        translated_text_box.delete(1.0, tk.END)
        translated_text_box.insert(tk.END, translated_text)

        thread = threading.Thread(target=text_to_speech, args=(translated_text,))
        thread.start()
    else:
        messagebox.showwarning("Warning", "Please load a file or enter text to translate.")


def text_to_speech_custom():
    text_to_read = translated_text_box.get(1.0, tk.END).strip()
    if text_to_read:
        thread = threading.Thread(target=text_to_speech, args=(text_to_read,))
        thread.start()
    else:
        messagebox.showwarning("Warning", "Please translate text first.")


def read_original_text():
    original_text = text_box.get(1.0, tk.END).strip()
    if original_text:
        lang = detect_language(original_text)
        thread = threading.Thread(target=text_to_speech, args=(original_text, lang))
        thread.start()
    else:
        messagebox.showwarning("Warning", "Please enter text to read.")


def detect_language(text):
    return detect(text)


def save_translation():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(translated_text_box.get(1.0, tk.END).strip())
            messagebox.showinfo("Success", "Translation saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {e}")


root = tk.Tk()
root.title("Text Translator and Speech Synthesis")

# Create GUI components
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

browse_button = tk.Button(frame, text="Browse File", command=browse_file)
browse_button.grid(row=0, column=0, padx=5, pady=5)

text_box_label = tk.Label(frame, text="Original Text:")
text_box_label.grid(row=1, column=0, padx=5, pady=5)

text_box = tk.Text(frame, height=10, width=80)
text_box.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Language selection dropdown
languages = ['en', 'fr', 'es', 'de', 'ja', 'ko', 'vi']
target_language_var = tk.StringVar(root)
target_language_var.set(languages[0])

language_menu = ttk.Combobox(frame, textvariable=target_language_var, values=languages)
language_menu.grid(row=3, column=0, padx=5, pady=5)

read_original_button = tk.Button(frame, text="Read Original Text", command=read_original_text)
read_original_button.grid(row=4, column=0, padx=5, pady=5)

translated_text_box_label = tk.Label(frame, text="Translated Text:")
translated_text_box_label.grid(row=5, column=0, padx=5, pady=5)

translated_text_box = tk.Text(frame, height=10, width=80)
translated_text_box.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

translate_custom_button = tk.Button(frame, text="Translate Custom", command=translate_custom)
translate_custom_button.grid(row=7, column=0, padx=5, pady=5, sticky="ew")

text_to_speech_custom_button = tk.Button(frame, text="Read Text", command=text_to_speech_custom)
text_to_speech_custom_button.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

translate_button = tk.Button(frame, text="Translate and Speak", command=translate_and_speak)
translate_button.grid(row=7, column=2, padx=5, pady=5, sticky="ew")

save_button = tk.Button(frame, text="Save Translation", command=save_translation)
save_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

stop_button = tk.Button(frame, text="Stop", command=stop_text_to_speech)
stop_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

# Control variable for speech playing state
is_playing = False

root.mainloop()
