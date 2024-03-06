
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import base64
import requests
import PyPDF2

class GPT4VisionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT-4 Vision App")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#CCCCCC', foreground='#ffffff', borderwidth=0)
        
        self.style.map('TButton', background=[('active', '#a0d8b0')])
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        self.style.configure('Header.TLabel', background='#f0f0f0', font=('Arial', 14, 'bold'))

        self.mainframe = ttk.Frame(root, padding="20")
        self.mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.prompt_label = ttk.Label(self.mainframe, text="Your Prompt:")
        self.prompt_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.prompt_entry = ttk.Entry(self.mainframe, width=40)
        self.prompt_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.browse_button_icon = Image.open("icon_2.jpg") 
        self.browse_button_icon = self.browse_button_icon.resize((32, 32), Image.LANCZOS)
        self.browse_button_icon = ImageTk.PhotoImage(self.browse_button_icon)

        self.browse_button = ttk.Button(self.mainframe, image=self.browse_button_icon, command=self.browse_file)
        self.browse_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.run_button = ttk.Button(self.mainframe, text="Send Message", command=self.run_openai)
        self.run_button.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.output_label = ttk.Label(self.mainframe, text="", wraplength=300, anchor="w", justify="left")
        self.output_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.image_label = ttk.Label(self.mainframe)
        self.image_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.file_path = None  # Variablendeklaration für den Dateipfad

        self.is_pdf = False

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path.lower().endswith('.pdf'):
            self.file_path = file_path
            self.is_pdf = True
            self.display_pdf(file_path)
            
        else:
            self.display_image(file_path)

    def display_image(self, file_path):
        if file_path:
            image = Image.open(file_path)
            image = image.resize((300, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        else:
            
            self.image_label.config(image=None)
            self.image_label.image = None

    def display_pdf(self, file_path):
        if file_path:
            pdf_text = self.extract_text_from_pdf(file_path)
            self.prompt_entry.delete(0, tk.END)
            self.prompt_entry.insert(0, pdf_text)
            

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                text += page.extractText()
        return text

    def encode_image(self, file_path):
        if self.is_pdf == False:
            if file_path:
                with open(file_path, "rb") as file:
                    return base64.b64encode(file.read()).decode('utf-8')
        else:
            return None

    def run_openai(self):
        prompt_text = self.prompt_entry.get()
       
        
        base64_image = self.encode_image(self.file_path)

        api_key = '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'

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }

        if self.is_pdf: 
            payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }

        if base64_image:
            payload["messages"][0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            try:
                data = response.json()
                
                output = data['choices'][0]['message']['content']
                self.display_output(output)
            except (KeyError, IndexError):
                self.display_output("Ungültige Antwort von OpenAI.")
        else:
            self.display_output("Fehler beim Abrufen der Antwort von OpenAI.")



    def display_output(self, output):
        if output:
            self.output_label.config(text=output)
            self.add_icon()
        else:
            self.output_label.config(text="Keine Antwort von OpenAI.")

    def add_icon(self):
        icon = Image.open("gpt_logo.png")  # Laden des Icons
        icon = icon.resize((32, 32), Image.LANCZOS)
        icon = ImageTk.PhotoImage(icon)
        icon_label = ttk.Label(self.mainframe, image=icon)
        icon_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.output_label.grid(row=2, column=1, columnspan=2, padx=(5, 0), pady=5, sticky="w")
        icon_label.image = icon

def main():
    root = tk.Tk()
    app = GPT4VisionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
 
