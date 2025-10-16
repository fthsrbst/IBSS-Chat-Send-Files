#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2P Chat ve Dosya Paylaşım - GUI Versiyonu
Tkinter ile grafik arayüz
"""

import socket
import threading
import json
import os
import base64
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

class P2PChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Chat ve Dosya Paylaşım")
        self.root.geometry("800x600")

        self.port = 5555
        self.running = False
        self.peers = set()
        self.username = ""
        self.my_ip = ""

        # GUI oluştur
        self.create_login_screen()

    def create_login_screen(self):
        """Giriş ekranı"""
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.pack(expand=True, fill='both')

        ttk.Label(self.login_frame, text="P2P Chat", font=('Arial', 24, 'bold')).pack(pady=20)
        ttk.Label(self.login_frame, text="Kullanıcı Adınız:", font=('Arial', 12)).pack(pady=10)

        self.username_entry = ttk.Entry(self.login_frame, font=('Arial', 12), width=30)
        self.username_entry.pack(pady=10)
        self.username_entry.focus()
        self.username_entry.bind('<Return>', lambda e: self.start_chat())

        ttk.Button(self.login_frame, text="Başla", command=self.start_chat).pack(pady=20)

    def start_chat(self):
        """Chat'i başlat"""
        self.username = self.username_entry.get().strip()

        if not self.username:
            messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin!")
            return

        # Socket başlat
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(5)

            self.my_ip = self.get_local_ip()
            self.running = True

            # Gelen bağlantıları dinle
            threading.Thread(target=self.accept_connections, daemon=True).start()

            # Ana ekranı göster
            self.login_frame.destroy()
            self.create_chat_screen()

        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu başlatılamadı: {e}")

    def get_local_ip(self):
        """Local IP adresini al"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def create_chat_screen(self):
        """Ana chat ekranı"""
        # Üst panel - Bilgiler
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill='x')

        ttk.Label(top_frame, text=f"👤 {self.username}", font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        ttk.Label(top_frame, text=f"📍 IP: {self.my_ip}:{self.port}", font=('Arial', 10)).pack(side='left', padx=10)

        ttk.Button(top_frame, text="Bağlan", command=self.show_connect_dialog).pack(side='right', padx=5)
        ttk.Button(top_frame, text="Dosya Gönder", command=self.send_file_dialog).pack(side='right', padx=5)

        # Ana panel
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Sol panel - Kullanıcılar
        left_frame = ttk.LabelFrame(main_frame, text="Bağlı Kullanıcılar", padding="10")
        left_frame.pack(side='left', fill='both', padx=(0, 5))

        self.users_listbox = tk.Listbox(left_frame, width=20, font=('Arial', 10))
        self.users_listbox.pack(expand=True, fill='both')

        # Sağ panel - Chat
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', expand=True, fill='both')

        # Mesaj alanı
        self.chat_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=('Arial', 10), state='disabled')
        self.chat_area.pack(expand=True, fill='both', pady=(0, 10))

        # Mesaj gönderme alanı
        input_frame = ttk.Frame(right_frame)
        input_frame.pack(fill='x')

        self.message_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.message_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.focus()

        ttk.Button(input_frame, text="Gönder", command=self.send_message).pack(side='right')

        # Hoş geldin mesajı
        self.add_system_message(f"Hoş geldiniz {self.username}!")
        self.add_system_message(f"IP adresiniz: {self.my_ip}:{self.port}")

    def show_connect_dialog(self):
        """Bağlantı dialogu"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Kullanıcıya Bağlan")
        dialog.geometry("300x120")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="IP Adresi:", font=('Arial', 10)).pack(pady=10)

        ip_entry = ttk.Entry(dialog, font=('Arial', 11), width=25)
        ip_entry.pack(pady=5)
        ip_entry.focus()

        def connect():
            ip = ip_entry.get().strip()
            if ip:
                dialog.destroy()
                self.connect_to_peer(ip)

        ip_entry.bind('<Return>', lambda e: connect())
        ttk.Button(dialog, text="Bağlan", command=connect).pack(pady=10)

    def send_file_dialog(self):
        """Dosya gönderme dialogu"""
        if not self.peers:
            messagebox.showwarning("Uyarı", "Henüz hiç kullanıcı bağlı değil!")
            return

        filepath = filedialog.askopenfilename(title="Dosya Seçin")
        if filepath:
            self.send_file(filepath)

    def add_system_message(self, text):
        """Sistem mesajı ekle"""
        self.chat_area.configure(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.chat_area.insert(tk.END, f"[{timestamp}] ℹ️  {text}\n", 'system')
        self.chat_area.tag_config('system', foreground='gray')
        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)

    def add_message(self, sender, text, is_own=False):
        """Chat mesajı ekle"""
        self.chat_area.configure(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')

        if is_own:
            self.chat_area.insert(tk.END, f"[{timestamp}] Siz: {text}\n", 'own')
            self.chat_area.tag_config('own', foreground='blue')
        else:
            self.chat_area.insert(tk.END, f"[{timestamp}] {sender}: {text}\n", 'other')
            self.chat_area.tag_config('other', foreground='green')

        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)

    def update_users_list(self):
        """Kullanıcı listesini güncelle"""
        self.users_listbox.delete(0, tk.END)
        for peer_ip, _, peer_name in self.peers:
            self.users_listbox.insert(tk.END, f"👤 {peer_name}")

    def accept_connections(self):
        """Gelen bağlantıları kabul et"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                ).start()
            except:
                break

    def handle_client(self, client_socket, address):
        """Client ile iletişimi yönet"""
        peer_name = None
        try:
            # Handshake
            data = client_socket.recv(4096).decode('utf-8')
            if data:
                message = json.loads(data)
                if message['type'] == 'handshake':
                    peer_name = message['username']
                    peer_info = (address[0], client_socket, peer_name)
                    self.peers.add(peer_info)

                    # Yanıt gönder
                    response = {
                        'type': 'handshake',
                        'username': self.username
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))

                    # GUI güncelle
                    self.root.after(0, lambda: self.add_system_message(f"{peer_name} bağlandı"))
                    self.root.after(0, self.update_users_list)

            # Mesajları dinle
            while self.running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                message = json.loads(data)
                self.handle_message(message, peer_name)

        except:
            pass
        finally:
            if peer_name:
                self.peers = {p for p in self.peers if p[2] != peer_name}
                self.root.after(0, lambda: self.add_system_message(f"{peer_name} ayrıldı"))
                self.root.after(0, self.update_users_list)
            client_socket.close()

    def handle_message(self, message, sender):
        """Gelen mesajı işle"""
        msg_type = message['type']

        if msg_type == 'chat':
            self.root.after(0, lambda: self.add_message(sender, message['content']))

        elif msg_type == 'file':
            filename = message['filename']
            file_data = base64.b64decode(message['data'])

            # Dosyayı kaydet
            save_path = os.path.join('received_files', filename)
            os.makedirs('received_files', exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(file_data)

            self.root.after(0, lambda: self.add_system_message(f"📁 {sender} dosya gönderdi: {filename}"))

    def connect_to_peer(self, ip):
        """Peer'a bağlan"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, self.port))

            # Handshake
            handshake = {
                'type': 'handshake',
                'username': self.username
            }
            client_socket.send(json.dumps(handshake).encode('utf-8'))

            # Yanıt bekle
            data = client_socket.recv(4096).decode('utf-8')
            response = json.loads(data)
            peer_name = response['username']

            # Peer'ı ekle
            peer_info = (ip, client_socket, peer_name)
            self.peers.add(peer_info)

            self.add_system_message(f"{peer_name} ile bağlantı kuruldu")
            self.update_users_list()

            # Mesajları dinle
            threading.Thread(
                target=self.handle_client,
                args=(client_socket, (ip, self.port)),
                daemon=True
            ).start()

        except Exception as e:
            messagebox.showerror("Hata", f"Bağlantı hatası: {e}")

    def send_message(self):
        """Mesaj gönder"""
        text = self.message_entry.get().strip()

        if not text:
            return

        if not self.peers:
            messagebox.showwarning("Uyarı", "Henüz hiç kullanıcı bağlı değil!")
            return

        message = {
            'type': 'chat',
            'content': text,
            'username': self.username
        }

        self.broadcast(message)
        self.add_message("Siz", text, is_own=True)
        self.message_entry.delete(0, tk.END)

    def send_file(self, filepath):
        """Dosya gönder"""
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()

            filename = os.path.basename(filepath)
            file_base64 = base64.b64encode(file_data).decode('utf-8')

            message = {
                'type': 'file',
                'filename': filename,
                'data': file_base64
            }

            self.broadcast(message)
            self.add_system_message(f"📁 Dosya gönderildi: {filename}")

        except Exception as e:
            messagebox.showerror("Hata", f"Dosya gönderme hatası: {e}")

    def broadcast(self, message):
        """Mesajı tüm peer'lara gönder"""
        data = json.dumps(message).encode('utf-8')
        disconnected = []

        for peer_ip, peer_socket, peer_name in self.peers:
            try:
                peer_socket.send(data)
            except:
                disconnected.append((peer_ip, peer_socket, peer_name))

        # Bağlantısı kopanları temizle
        for peer in disconnected:
            self.peers.discard(peer)

        if disconnected:
            self.update_users_list()

    def on_closing(self):
        """Uygulama kapanırken"""
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = P2PChatGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
