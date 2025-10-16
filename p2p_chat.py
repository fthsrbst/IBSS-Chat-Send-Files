#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit P2P Chat ve Dosya Paylaşım Uygulaması
Aynı ağdaki bilgisayarlar arasında chat ve dosya paylaşımı
"""

import socket
import threading
import json
import os
import base64
from datetime import datetime

class P2PChat:
    def __init__(self, port=5555):
        self.port = port
        self.running = False
        self.peers = set()  # Bağlı kullanıcılar
        self.username = input("Kullanıcı adınızı girin: ")

        # Sunucu soketi oluştur
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)

        # Kendi IP adresini al
        self.my_ip = self.get_local_ip()
        print(f"\n✓ {self.username} olarak bağlandınız")
        print(f"✓ IP Adresiniz: {self.my_ip}:{self.port}")
        print("\nKomutlar:")
        print("  /connect <ip>  - Bir kullanıcıya bağlan")
        print("  /file <dosya>  - Dosya gönder")
        print("  /list          - Bağlı kullanıcıları listele")
        print("  /quit          - Çıkış\n")

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

    def start(self):
        """Uygulamayı başlat"""
        self.running = True

        # Gelen bağlantıları dinle
        accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        accept_thread.start()

        # Kullanıcı girişlerini oku
        self.handle_user_input()

    def accept_connections(self):
        """Gelen bağlantıları kabul et"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                thread.start()
            except:
                break

    def handle_client(self, client_socket, address):
        """Bir client ile iletişimi yönet"""
        peer_name = None
        try:
            # İlk mesajı bekle (handshake)
            data = client_socket.recv(4096).decode('utf-8')
            if data:
                message = json.loads(data)
                if message['type'] == 'handshake':
                    peer_name = message['username']
                    peer_info = (address[0], client_socket, peer_name)
                    self.peers.add(peer_info)
                    print(f"\n✓ {peer_name} ({address[0]}) bağlandı")

                    # Handshake yanıtı gönder
                    response = {
                        'type': 'handshake',
                        'username': self.username
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))

            # Mesajları dinle
            while self.running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                message = json.loads(data)
                self.handle_message(message, peer_name)

        except Exception as e:
            pass
        finally:
            # Bağlantıyı kapat
            if peer_name:
                self.peers = {p for p in self.peers if p[2] != peer_name}
                print(f"\n✗ {peer_name} ayrıldı")
            client_socket.close()

    def handle_message(self, message, sender):
        """Gelen mesajı işle"""
        msg_type = message['type']

        if msg_type == 'chat':
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{timestamp}] {sender}: {message['content']}")

        elif msg_type == 'file':
            filename = message['filename']
            file_data = base64.b64decode(message['data'])

            # Dosyayı kaydet
            save_path = os.path.join('received_files', filename)
            os.makedirs('received_files', exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(file_data)

            print(f"\n✓ Dosya alındı: {filename} -> {save_path}")

    def connect_to_peer(self, ip):
        """Bir peer'a bağlan"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, self.port))

            # Handshake gönder
            handshake = {
                'type': 'handshake',
                'username': self.username
            }
            client_socket.send(json.dumps(handshake).encode('utf-8'))

            # Yanıtı bekle
            data = client_socket.recv(4096).decode('utf-8')
            response = json.loads(data)
            peer_name = response['username']

            # Peer'ı listeye ekle
            peer_info = (ip, client_socket, peer_name)
            self.peers.add(peer_info)

            print(f"✓ {peer_name} ({ip}) ile bağlantı kuruldu")

            # Mesajları dinle
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, (ip, self.port)),
                daemon=True
            )
            thread.start()

        except Exception as e:
            print(f"✗ Bağlantı hatası: {e}")

    def send_message(self, content):
        """Tüm peer'lara mesaj gönder"""
        message = {
            'type': 'chat',
            'content': content,
            'username': self.username
        }
        self.broadcast(message)

    def send_file(self, filepath):
        """Tüm peer'lara dosya gönder"""
        try:
            if not os.path.exists(filepath):
                print(f"✗ Dosya bulunamadı: {filepath}")
                return

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
            print(f"✓ Dosya gönderildi: {filename}")

        except Exception as e:
            print(f"✗ Dosya gönderme hatası: {e}")

    def broadcast(self, message):
        """Mesajı tüm peer'lara gönder"""
        data = json.dumps(message).encode('utf-8')
        disconnected = []

        for peer_ip, peer_socket, peer_name in self.peers:
            try:
                peer_socket.send(data)
            except:
                disconnected.append((peer_ip, peer_socket, peer_name))

        # Bağlantısı kopan peer'ları temizle
        for peer in disconnected:
            self.peers.discard(peer)

    def list_peers(self):
        """Bağlı kullanıcıları listele"""
        if not self.peers:
            print("\n✗ Hiç kullanıcı bağlı değil")
        else:
            print(f"\n✓ Bağlı kullanıcılar ({len(self.peers)}):")
            for peer_ip, _, peer_name in self.peers:
                print(f"  - {peer_name} ({peer_ip})")

    def handle_user_input(self):
        """Kullanıcı girişlerini işle"""
        while self.running:
            try:
                user_input = input()

                if user_input.startswith('/'):
                    parts = user_input.split(' ', 1)
                    command = parts[0].lower()

                    if command == '/quit':
                        print("\nÇıkılıyor...")
                        self.running = False
                        break

                    elif command == '/connect':
                        if len(parts) > 1:
                            ip = parts[1].strip()
                            self.connect_to_peer(ip)
                        else:
                            print("Kullanım: /connect <ip>")

                    elif command == '/file':
                        if len(parts) > 1:
                            filepath = parts[1].strip()
                            self.send_file(filepath)
                        else:
                            print("Kullanım: /file <dosya_yolu>")

                    elif command == '/list':
                        self.list_peers()

                    else:
                        print(f"✗ Bilinmeyen komut: {command}")

                else:
                    # Normal mesaj gönder
                    if user_input.strip():
                        self.send_message(user_input)

            except KeyboardInterrupt:
                print("\n\nÇıkılıyor...")
                self.running = False
                break
            except Exception as e:
                print(f"✗ Hata: {e}")

        # Temizlik
        self.server_socket.close()

if __name__ == "__main__":
    print("=" * 50)
    print("P2P Chat ve Dosya Paylaşım Uygulaması")
    print("=" * 50)

    app = P2PChat()
    app.start()
