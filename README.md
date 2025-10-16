# P2P Chat ve Dosya Paylaşım Uygulaması

Aynı ağdaki bilgisayarlar arasında basit chat ve dosya paylaşımı uygulaması.

## Özellikler

- 💬 Anlık mesajlaşma
- 📁 Dosya gönderimi
- 👥 Çoklu kullanıcı desteği
- 🔄 Peer-to-peer mimari (merkezi sunucu yok)

## Kurulum

Python 3.6 veya üzeri gerekli. Ek kütüphane kurulumu gerekmiyor (sadece standart kütüphaneler).

## Kullanım

### 1. Uygulamayı Başlat

```bash
python p2p_chat.py
```

### 2. Kullanıcı Adı Girin

Program başladığında sizden bir kullanıcı adı isteyecek.

### 3. IP Adresinizi Not Edin

Program size IP adresinizi gösterecek. Diğer kullanıcılar bu IP ile size bağlanacak.

### 4. Başka Bir Kullanıcıya Bağlan

```
/connect 192.168.1.100
```

IP adresini kendi ağınızdaki diğer bilgisayarın IP'si ile değiştirin.

## Komutlar

- `/connect <ip>` - Bir kullanıcıya bağlan
- `/file <dosya_yolu>` - Dosya gönder
- `/list` - Bağlı kullanıcıları listele
- `/quit` - Çıkış

## Örnek Kullanım

### Bilgisayar 1:
```bash
$ python p2p_chat.py
Kullanıcı adınızı girin: Ali
✓ Ali olarak bağlandınız
✓ IP Adresiniz: 192.168.1.100:5555
```

### Bilgisayar 2:
```bash
$ python p2p_chat.py
Kullanıcı adınızı girin: Ayşe
✓ Ayşe olarak bağlandınız
✓ IP Adresiniz: 192.168.1.101:5555

/connect 192.168.1.100
✓ Ali (192.168.1.100) ile bağlantı kuruldu
```

### Mesaj Gönderme:
```
Merhaba Ali!
```

### Dosya Gönderme:
```
/file /path/to/document.pdf
✓ Dosya gönderildi: document.pdf
```

Alınan dosyalar `received_files` klasörüne kaydedilir.

## Nasıl Çalışır?

1. Her bilgisayar hem sunucu hem istemci olarak çalışır
2. 5555 portunu dinler ve gelen bağlantıları kabul eder
3. Diğer bilgisayarlara `/connect` komutu ile bağlanabilirsiniz
4. Mesajlar ve dosyalar tüm bağlı kullanıcılara gönderilir

## Notlar

- Tüm bilgisayarlar aynı ağda (WiFi/LAN) olmalı
- Güvenlik duvarı 5555 portunu engellememelidir
- Farklı port kullanmak için kodu düzenleyebilirsiniz
- Alınan dosyalar otomatik olarak `received_files` klasörüne kaydedilir

## Sorun Giderme

**Bağlantı kurulamıyor:**
- Bilgisayarların aynı ağda olduğundan emin olun
- IP adresinin doğru olduğunu kontrol edin
- Güvenlik duvarını kontrol edin

**Port hatası:**
- 5555 portu başka bir uygulama tarafından kullanılıyor olabilir
- Kodu düzenleyerek farklı bir port seçin
