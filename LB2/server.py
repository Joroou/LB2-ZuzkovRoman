import socket
import threading
import json
import os
HISTORY_FILE = "messages.json"

class MessageServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages = self.load_messages()
        
    def load_messages(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_messages(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
    
    def get_chat_history(self, user_id, target_id):
        history = []
        for msg in self.messages:
            if (msg['from_id'] == user_id and msg['to_id'] == target_id) or \
               (msg['from_id'] == target_id and msg['to_id'] == user_id):
                history.append(msg)
        return history
    
    def add_message(self, from_id, to_id, text):
        message = {
            'from_id': from_id,
            'to_id': to_id,
            'text': text
        }
        self.messages.append(message)
        self.save_messages()
        return message
    
    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                request = json.loads(data)
                action = request.get('action')
                
                if action == 'get_history':
                    user_id = request['user_id']
                    target_id = request['target_id']
                    history = self.get_chat_history(user_id, target_id)
                    response = {'status': 'success', 'history': history}
                    
                elif action == 'send_message':
                    from_id = request['from_id']
                    to_id = request['to_id']
                    text = request['text']
                    message = self.add_message(from_id, to_id, text)
                    response = {'status': 'success', 'message': message}
                
                else:
                    response = {'status': 'error', 'message': 'Unknown action'}
                
                client_socket.send(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Сервер запущен на {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server.accept()
            print(f"Подключен клиент: {address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = MessageServer()
    server.start()
