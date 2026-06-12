import anthropic
import threading
import webbrowser
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog

def open_github(event=None):
    webbrowser.open("https://github.com/OrpheasGeorgakopoulos")

# Initialize the Anthropic client (reads ANTHROPIC_API_KEY from environment)
client = anthropic.Anthropic()

# System prompt – change this to give the bot a personality or focus
SYSTEM_PROMPT = "You are a friendly and helpful assistant. Keep your answers concise. You know a lot about microcontrollers and generally tech!"

# Tkinter UI class
class ChatbotUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Universal Assistant")
        self.root.geometry("800x800")
        self.root.configure(bg="#2E2E2E")

        self.messages = []

        tk.Label(
            root, text="Universal Assistant", font=("Helvetica", 16, "bold"),
            fg="#FFFFFF", bg="#2E2E2E"
        ).pack(pady=10)

        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, height=33, width=90, font=("Arial", 11),
            bg="#3C3C3C", fg="#E0E0E0", insertbackground="white"
        )
        self.chat_area.pack(pady=10, padx=10)
        self.chat_area.insert(tk.END,
                              "Welcome to Universal Chatbot Assistant\n"
                              "Ask about anything!\n")
        self.chat_area.config(state="disabled")

        input_frame = tk.Frame(root, bg="#2E2E2E")
        input_frame.pack(pady=5)

        self.input_field = tk.Entry(
            input_frame, width=40, font=('Arial', 11), bg="#4A4A4A", fg="#FFFFFF",
            insertbackground="white"
        )
        self.input_field.pack(side=tk.LEFT, padx=5)
        self.input_field.bind("<Return>", self.send_message)

        # Send button
        tk.Button(
            input_frame, text="Send", command=self.send_message, font=("Arial", 11),
            bg="#4CAF50", fg="#FFFFFF", activebackground="#45A049"
        ).pack(side=tk.LEFT, padx=5)

        # Save chat button
        tk.Button(
            root, text="Save Chat", command=self.save_chat, font=("Arial", 11),
            bg="#2196F3", fg="#FFFFFF", activebackground="#1976D2"
        ).pack(pady=5)

        # Clear button
        tk.Button(
            root, text="Clear Chat", command=self.clear_chat, font=("Arial", 11),
            bg="#F44336", fg="#FFFFFF", activebackground="#D32F2F"
        ).pack(pady=5)


        link = tk.Label(
            root,
            text="Made by Orpheas Georgakopoulos.",
            font=("Helvetica", 16, "bold"),
            fg="#4DA6FF",
            bg="#2E2E2E",
            cursor="hand2"
        )

        link.pack(pady=10)
        link.bind("<Button-1>", open_github)


    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"\nYou: {user_input}\n")
        self.chat_area.insert(tk.END, "Bot: ")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
        self.input_field.delete(0, tk.END)

        self.messages.append({"role": "user", "content": user_input})

        self.input_field.config(state='disabled')
     #  self.send_button.config(state='disabled')

        thread = threading.Thread(target=self.stream_response, daemon=True)
        thread.start()

    def stream_response(self):
        full_response = ""

        with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=self.messages,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                self.root.after(0, self.append_text, text)

        self.messages.append({"role": "assistant", "content": full_response})

        self.root.after(0, self.finish_response)

    def append_text(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, text)
        # self.chat_area.config(state='disabled')
        # self.chat_area.see(tk.END)

    def finish_response(self):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, "\n")
        self.chat_area.config(state='disabled')
        self.input_field.config(state='normal')
        # self.send_button.config(state='normal')
        # self.input_field.focus()

    def save_chat(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )

        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("# Chat History\n\n")

            for message in self.messages:
                role = "You" if message["role"] == "user" else "Bot"
                file.write(f"## {role}\n\n")
                file.write(message["content"] + "\n\n")

    def clear_chat(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.insert(tk.END,
                              "Welcome to Universal Chatbot Assistant!\n"
                              "Ask about anything.\n")
        self.chat_area.config(state='disabled')














# Main function
def main():
    root = tk.Tk()
    app = ChatbotUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
