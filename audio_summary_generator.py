import os
import openai
from pydub import AudioSegment
from pydub.utils import make_chunks
from tkinter import Tk, Button, Label, Entry, filedialog
from tkinter import ttk
import threading
from tkinter import StringVar


# Function to set the OpenAI API key
def set_openai_api_key():
    openai.api_key = api_key_entry.get()
    api_key_status_text.set("API Key successfully set and activated.")

def speech_to_text(audio_file):
    response = openai.Audio.transcribe("whisper-1", audio_file)
    return response.text

def generate_bullet_points(text):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that summarizes text in bullet points."},
        {"role": "user", "content": f"Please summarize the following text in bullet points:\n{text}. Make sure every bullet point uses '-' as the bullet. Please make content easy to read. Please have bullets for any small talk at the beginning. Do not include the prompt in the output."}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.7
    )
    
    return response.choices[0].message['content'].strip()

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("M4A files", "*.m4a")])
    file_path_entry.delete(0, "end")
    file_path_entry.insert(0, file_path)

def generate_summary():
    status_text.set("In progress. Please keep the app open.")

    file_path = file_path_entry.get()
    print(f"File path: {file_path}")  # Added print statement to display file path


    # Load and split the audio
    audio = AudioSegment.from_file(file_path, "m4a")
    chunks = make_chunks(audio, 300000)

    # Convert each chunk into text
    texts = []
    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        chunk.export(f"chunk{i}.wav", format="wav")
        with open(f"chunk{i}.wav", "rb") as audio_file:
            text = speech_to_text(audio_file)
            texts.append(text)
        os.remove(f"chunk{i}.wav")

        progress_bar['value'] = (i + 1) / (2 * total_chunks) * 100  # Update the progress bar for audio processing
        root.update_idletasks()  # Refresh the GUI

    # Generate bullet point summaries for each chunk
    bullet_point_summaries = []
    for i, text in enumerate(texts):
        summary = generate_bullet_points(text)
        bullet_point_summaries.append(summary)

        progress_bar['value'] = 50 + (i + 1) / (2 * total_chunks) * 100  # Update the progress bar for summary generation
        root.update_idletasks()  # Refresh the GUI

    # Concatenate all summaries into a single string
    all_summaries = "\n".join(bullet_point_summaries)

    # Generate final bullet point summary
    final_summary = all_summaries
    # Save the final summary to a text file in the Downloads folder
    downloads_folder = os.path.expanduser("~/Downloads")
    output_file_path = os.path.join(downloads_folder, "summary.txt")
    
    with open(output_file_path, "w") as f:
        f.write(final_summary)

    print(f"Summary saved to {output_file_path}")

    progress_bar['value'] = 0  # Reset the progress bar
    status_text.set("")  # Clear the status text when finished


def start_generate_summary_thread():
    summary_thread = threading.Thread(target=generate_summary)
    summary_thread.start()

root = Tk()
root.title("Audio Summary Generator")

# Create and place the widgets
api_key_label = Label(root, text="OpenAI API Key:")
api_key_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

api_key_entry = Entry(root, width=50)
api_key_entry.grid(row=0, column=1, padx=10, pady=10)

set_api_key_button = Button(root, text="Set API Key", command=set_openai_api_key)
set_api_key_button.grid(row=0, column=2, padx=10, pady=10)

api_key_status_text = StringVar()
api_key_status_label = Label(root, textvariable=api_key_status_text)
api_key_status_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

browse_label = Label(root, text="Choose Audio File:")
browse_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
browse_button = Button(root, text="Browse File", command=browse_file)
browse_button.grid(row=2, column=2, padx=10, pady=10)

file_path_entry = Entry(root, width=50)
file_path_entry.grid(row=2, column=1, padx=10, pady=10)

generate_button = Button(root, text="Generate Summary", command=start_generate_summary_thread)
generate_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

status_text = StringVar()
status_label = Label(root, textvariable=status_text)
status_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()

