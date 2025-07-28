# 🕵️ Digital Forensic Metadata Extractor

Aplikasi berbasis Flask untuk mengekstrak metadata dari gambar/video seperti EXIF, GPS, waktu, perangkat, dan menyimpan riwayat metadata. Cocok untuk digital forensik dan investigasi.

## 🌐 Fitur
- Upload & view metadata dari gambar/video
- Tampilkan lokasi GPS di peta (Folium)
- Export metadata ke PDF
- Login admin & dashboard histori
- Dibuat dengan Flask, ExifRead, Pillow, ReportLab

## 🚀 Cara Deploy (via Render)
1. Fork/Clone repo ke GitHub
2. Buat akun di [Render.com](https://render.com)
3. Deploy New Web Service:
   - Connect GitHub repo
   - Environment = Python
   - Start Command: `python server.py`
4. Tambahkan Environment Variables:
   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`

## 🧪 Local Dev
```bash
pip install -r requirements.txt
python server.py
```

📁 Akses di `http://localhost:10000`
