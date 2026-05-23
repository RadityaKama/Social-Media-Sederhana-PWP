# Social Media Sederhana (PWP)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![MySQL/SQLite](https://img.shields.io/badge/Database-SQL-blue?style=for-the-badge&logo=mysql&logoColor=white)

Sebuah platform web media sosial skala kecil yang dibangun menggunakan **Python** dengan framework **Flask**. Proyek ini dikembangkan untuk mengimplementasikan fungsionalitas dasar aplikasi jejaring sosial, mulai dari manajemen pengguna (otentikasi) hingga manajemen konten dalam arsitektur web yang solid.

---

## Deskripsi Proyek
Aplikasi ini merupakan implementasi nyata dari konsep *Pemrograman Web*, menggunakan arsitektur *routing* Flask yang terintegrasi dengan basis data relasional. Antarmuka pengguna (UI) dirancang agar responsif dan ramah pengguna dengan memanfaatkan HTML, CSS, dan framework *frontend* (seperti Bootstrap), didukung dengan sistem *backend* yang efisien.

## Fitur Utama
* **Otentikasi Pengguna:** Sistem registrasi dan login yang aman untuk mengelola sesi pengguna.
* **Manajemen Profil:** Pengguna dapat melihat dan menyesuaikan identitas akun mereka.
* **Sistem Publikasi/Posting:** Fitur untuk membuat, membaca, dan mengelola unggahan status atau konten sederhana.
* **Arsitektur Modular:** Pemisahan yang jelas antara logika *backend* (`app.py`), tampilan antarmuka (`templates/`), dan aset statis (`static/`).

## Persyaratan Sistem & Tech Stack
* **Bahasa Pemrograman:** Python 3.x
* **Framework Web:** Flask
* **Sistem Database:** SQL (MySQL / MariaDB / SQLite)
* **Frontend:** HTML5, CSS3, (Bootstrap untuk *styling* responsif)

## Cara Menjalankan Aplikasi Lokal

1. **Clone repositori ini**
   ```bash
   git clone [https://github.com/RadityaKama/Social-Media-Sederhana-PWP.git](https://github.com/RadityaKama/Social-Media-Sederhana-PWP.git)
   cd Social-Media-Sederhana-PWP
2. Aktifkan Virtual Environment
   Windows:
   venv\Scripts\activate
   Mac/Linux:
   source venv/bin/activate
3. Instal dependensi yang dibutuhkan
   pip install -r requirements.txt
4. Konfigurasi Database & Environment
   Pastikan konfigurasi database URI di dalam app.py sudah sesuai dengan environment lokal kamu.
5. Jalankan aplikasi Flask
   flask run
   # atau bisa juga dengan:
   # python app.py
6. Buka browser dan akses http://localhost:5000 (atau port lain yang tertera di terminal).
