import socket
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox

class MessengerClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.user_id = None
        self.target_id = None
        self.socket = None
        self.root = None
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу: {e}")
            return False
    
    def get_history(self):
        request = {
            'action': 'get_history',
            'user_id': self.user_id,
            'target_id': self.target_id
        }
        self.socket.send(json.dumps(request, ensure_ascii=False).encode('utf-8'))
        response = json.loads(self.socket.recv(4096).decode('utf-8'))
        return response.get('history', [])
    
    def send_message(self, text):
        if not text.strip():
            return False
        
        request = {
            'action': 'send_message',
            'from_id': self.user_id,
            'to_id': self.target_id,
            'text': text.strip()
        }
        self.socket.send(json.dumps(request, ensure_ascii=False).encode('utf-8'))
        response = json.loads(self.socket.recv(1024).decode('utf-8'))
        return response.get('status') == 'success'
    
    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)
        
        tk.Label(main_frame, text="Менеджер сообщений", font=("Arial", 16, "bold")).pack(pady=20)
        
        user_frame = tk.Frame(main_frame)
        user_frame.pack(pady=10)
        
        tk.Label(user_frame, text="Введите ваш айди:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        user_entry = tk.Entry(user_frame, width=20, font=("Arial", 12))
        user_entry.pack(side=tk.LEFT, padx=5)
        user_entry.focus()
        
        def on_user_submit():
            user_id = user_entry.get().strip()
            if user_id:
                self.user_id = user_id
                self.show_target_screen()
            else:
                messagebox.showwarning("Внимание", "Введите ваш айди")
        
        user_submit = tk.Button(main_frame, text="Подтвердить", font=("Arial", 10),
                                command=on_user_submit)
        user_submit.pack(pady=10)
        
        user_entry.bind('<Return>', lambda e: on_user_submit())
    
    def show_target_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)
        
        tk.Label(main_frame, text=f"Вы вошли как: {self.user_id}", 
                font=("Arial", 12)).pack(pady=10)
        tk.Label(main_frame, text="Менеджер сообщений", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        target_frame = tk.Frame(main_frame)
        target_frame.pack(pady=10)
        
        tk.Label(target_frame, text="Введите айди собеседника:", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        target_entry = tk.Entry(target_frame, width=20, font=("Arial", 12))
        target_entry.pack(side=tk.LEFT, padx=5)
        target_entry.focus()
        
        def on_target_submit():
            target_id = target_entry.get().strip()
            if target_id:
                self.target_id = target_id
                if self.connect():
                    self.show_chat_screen()
            else:
                messagebox.showwarning("Внимание", "Введите айди собеседника")
        
        target_submit = tk.Button(main_frame, text="Начать чат", font=("Arial", 10),
                                  command=on_target_submit)
        target_submit.pack(pady=10)
        
        back_button = tk.Button(main_frame, text="← Назад", font=("Arial", 10),
                                command=self.show_login_screen)
        back_button.pack(pady=5)
        
        target_entry.bind('<Return>', lambda e: on_target_submit())
    
    def show_chat_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title(f"Менеджер сообщений - {self.user_id} → {self.target_id}")
        
        info_frame = tk.Frame(self.root, bg='lightgray')
        info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(info_frame, text=f"Ваш ID: {self.user_id} | Собеседник: {self.target_id}", 
                font=("Arial", 10), bg='lightgray').pack(side=tk.LEFT, padx=10)
        
        def change_target():
            self.target_id = None
            if self.socket:
                self.socket.close()
                self.socket = None
            self.show_target_screen()
        
        change_btn = tk.Button(info_frame, text="Сменить собеседника", 
                              font=("Arial", 9), command=change_target)
        change_btn.pack(side=tk.RIGHT, padx=10)
        
        def logout():
            if self.socket:
                self.socket.close()
                self.socket = None
            self.user_id = None
            self.target_id = None
            self.show_login_screen()
        
        logout_btn = tk.Button(info_frame, text="Выйти", 
                              font=("Arial", 9), command=logout)
        logout_btn.pack(side=tk.RIGHT, padx=5)
        
        self.messages_area = scrolledtext.ScrolledText(self.root, width=65, height=20, 
                                                        font=("Arial", 10), state=tk.DISABLED)
        self.messages_area.pack(pady=10, padx=10)
        
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.message_entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
        self.message_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        send_button = tk.Button(input_frame, text="Отправить", font=("Arial", 10),
                                command=self.send_and_update)
        send_button.pack(side=tk.LEFT, padx=5)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        update_button = tk.Button(button_frame, text="Обновить чат", font=("Arial", 10),
                                  command=self.update_chat)
        update_button.pack(side=tk.LEFT, padx=5)
        
        self.message_entry.bind('<Return>', lambda e: self.send_and_update())
        
        self.update_chat()
        
        self.auto_update()
    
    def auto_update(self):
        if self.socket and self.target_id:
            self.update_chat()
        if self.root and self.target_id:
            self.root.after(3000, self.auto_update)
    
    def update_chat(self):
        if not self.socket:
            return
        
        try:
            history = self.get_history()
            
            self.messages_area.config(state=tk.NORMAL)
            self.messages_area.delete(1.0, tk.END)
            
            if not history:
                self.messages_area.insert(tk.END, "✉️ Нет сообщений\n")
                self.messages_area.insert(tk.END, "Напишите первое сообщение!\n")
            else:
                for msg in history:
                    if msg['from_id'] == self.user_id:
                        sender = "Вы →"
                        tag = "my_message"
                    else:
                        sender = f"{msg['from_id']} →"
                        tag = "other_message"
                    
                    self.messages_area.insert(tk.END, f"{sender} ", tag)
                    self.messages_area.insert(tk.END, f"{msg['text']}\n")
                    self.messages_area.insert(tk.END, "─" * 50 + "\n")
            
            self.messages_area.config(state=tk.DISABLED)
            self.messages_area.see(tk.END)
            
            self.messages_area.tag_config("my_message", foreground="blue", font=("Arial", 10, "bold"))
            self.messages_area.tag_config("other_message", foreground="green", font=("Arial", 10, "bold"))
            
        except Exception as e:
            pass
    
    def send_and_update(self):
        text = self.message_entry.get()
        if text.strip():
            if self.send_message(text):
                self.message_entry.delete(0, tk.END)
                self.update_chat()
    
    def run_gui(self):
        self.root = tk.Tk()
        self.root.title("Менеджер сообщений")
        self.root.geometry("550x650")
        
        self.show_login_screen()
        
        def on_closing():
            if self.socket:
                self.socket.close()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    client = MessengerClient()
    client.run_gui()
