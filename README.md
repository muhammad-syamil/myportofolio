Nama : Muhammad Syamil

NPM : 2506547746

Kelas : PBP D

## Features

- Personal profile, skills, projects, dan social media links.
- Halaman Achievements dengan fitur tambah, pencarian, edit, dan hapus data.
- Halaman Experience dengan fitur tambah, edit, dan hapus menggunakan form.
- Pencarian Experience berdasarkan judul serta filter kategori dan status.
- Konfirmasi sebelum menghapus Experience.
- Notifikasi sukses setelah menambah, mengedit, atau menghapus Experience.
- Endpoint JSON untuk data Achievements dan Experience.
- Deserialisasi JSON sebelum data ditampilkan melalui template Django.
- Template inheritance menggunakan `base.html`.
- Responsive layout dengan efek hover dan penanda fokus pada halaman Experience.
- Registrasi, login, logout, session, dan cookie `last_login`.
- Hak akses pengunjung, pengguna biasa, Editor, dan superuser.
- Fitur star/unstar Experience dengan jumlah star per item.
- Endpoint JSON Experience dengan whitelist field publik.
- Navbar responsif dengan indikator halaman aktif dan tombol autentikasi.

## Tech Stack

- Python 3
- Django
- Django ModelForm
- Django Authentication, Group, Session, dan Cookie
- JSON dan Django serializers
- HTML5
- CSS3
- Git & GitHub

## Project Structure

Struktur utama proyek:

```text
myportofolio/
├── main/
│   ├── migrations/
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── portofolio/
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── img/
├── templates/
│   ├── components/
│   │   ├── achievement_delete_modal.html
│   │   ├── experience_delete_modal.html
│   │   └── experience_star.html
│   ├── base.html
│   ├── index.html
│   ├── achievements.html
│   ├── achievement_form.html
│   ├── experience.html
│   ├── experience_form.html
│   ├── login.html
│   └── register.html
├── manage.py
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Clone repository

Ganti `<repository-url>` dengan URL repositori proyek.

```bash
git clone <repository-url> myportofolio
cd myportofolio
```

### 2. Create virtual environment

```bash
python -m venv env
```

Pada macOS/Linux, gunakan `python3` jika perintah `python` tidak tersedia.

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.\env\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source env/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Run Django

```bash
python manage.py runserver
```

Website dapat diakses melalui:
http://127.0.0.1:8000/

### 7. Create portfolio owner

Buat akun superuser yang berperan sebagai pemilik portofolio:

```bash
python manage.py createsuperuser
```

Setelah server berjalan, buka `http://127.0.0.1:8000/admin/` dan login menggunakan akun tersebut.

### 8. Create an Editor

Melalui Django Admin, buka **Authentication and Authorization → Groups**, buat grup bernama `Editor`, lalu tambahkan akun yang dipilih ke grup tersebut. Nama grup harus ditulis persis `Editor`.

### 9. Run tests

```bash
python manage.py test main
```

## Halaman dan Endpoint

| URL | Fungsi |
| --- | --- |
| `/` | Menampilkan profil pribadi |
| `/register/` | Membuat akun pengguna biasa |
| `/login/` | Login dan membuat session pengguna |
| `/logout/` | Logout dan menghapus cookie `last_login` |
| `/admin/` | Mengelola akun dan grup `Editor` |
| `/achievements/` | Menampilkan daftar prestasi |
| `/achievements/add/` | Menambahkan prestasi |
| `/achievements/<id>/edit/` | Mengedit prestasi sebagai Editor atau superuser |
| `/api/achievements/` | Mengembalikan data prestasi dalam JSON |
| `/experience/` | Menampilkan dan memfilter pengalaman |
| `/experience/add/` | Menambahkan pengalaman |
| `/experience/<uuid>/edit/` | Mengedit pengalaman berdasarkan ID |
| `/experience/<uuid>/delete/` | Menghapus pengalaman melalui POST |
| `/experience/<uuid>/star/` | Memberi atau membatalkan star melalui POST |
| `/api/experience/` | Mengembalikan data pengalaman dalam JSON |

Parameter pencarian dan filter Experience dapat digunakan pada halaman daftar maupun endpoint JSON:

- `title`: mencari judul tanpa membedakan huruf besar dan kecil.
- `category`: memfilter kategori, misalnya `internship` atau `volunteer`.
- `status`: `ongoing` untuk pengalaman yang masih berlangsung atau `completed` untuk pengalaman yang selesai.

Contoh:

```text
/experience/?title=mentor&category=volunteer&status=ongoing
/api/experience/?category=internship
```

Status pengalaman ditentukan dari `ended_at`: kosong berarti masih berlangsung, sedangkan terisi berarti selesai. Form Experience saat ini belum menyediakan pengubahan tanggal tersebut.

## Development Progress

### Tugas 4 — Authentication, Session & Cookies

Tugas 4 menerapkan autentikasi dan otorisasi dari Tutorial 4 pada bagian Experience yang dibuat di Tugas 3.

1. **Relasi star**
   Model `Experience` memiliki relasi `ManyToManyField` bernama `starred_by` ke model `User`. Relasi ini mencegah satu pengguna memberikan lebih dari satu star pada Experience yang sama.

2. **Empat tingkat akses**
   Pengunjung tetap dapat membaca data. Pengguna biasa dapat star/unstar. Anggota grup `Editor` juga dapat mengedit Experience dan Achievements. Superuser sebagai pemilik portofolio dapat menambah, mengedit, dan menghapus data.

3. **Proteksi server dan template**
   `login_required` mengarahkan pengunjung ke login, sedangkan aksi tanpa izin menghasilkan HTTP 403. Tombol tambah, edit, dan hapus juga hanya ditampilkan kepada role yang sesuai.

4. **Star berbasis POST**
   Star dan unstar diproses melalui request POST dengan CSRF token. Halaman menampilkan jumlah star dan status star pengguna yang sedang login.

5. **Keamanan JSON**
   Endpoint JSON menggunakan whitelist field publik agar relasi `starred_by` dan informasi akun tidak ikut dikirim.

6. **Peningkatan UI/UX**
   Navbar dibuat responsif dengan susunan brand, navigasi utama, aksi autentikasi, dan indikator halaman aktif. Tampilan diverifikasi pada ukuran desktop dan mobile.

7. **Pengujian**
   Test mencakup matriks akses seluruh role, perubahan status star, visibilitas tombol, metode POST, serta keamanan field endpoint JSON.

### Tugas 3 — Form & Data Delivery

Tugas 3 melanjutkan implementasi Tutorial 3 dengan menerapkan pengelolaan data pada bagian Experience.

1. **Template inheritance**  
   Halaman Experience menggunakan `base.html` sebagai kerangka bersama agar navbar, footer, dan pemuatan CSS tidak ditulis berulang.

2. **ModelForm**  
   `ExperienceForm` menyediakan field `title`, `description`, `category`, dan `thumbnail`. Form digunakan untuk menerima serta memvalidasi input pengguna.

3. **Create dan update**  
   Pengguna dapat menambahkan dan mengedit pengalaman. Proses update menggunakan `instance` agar perubahan disimpan pada objek yang sama. Kedua halaman memakai `experience_form.html`.

4. **Delete dengan konfirmasi**  
   Tombol hapus menampilkan konfirmasi melalui komponen `experience_delete_modal.html`. Penghapusan dilakukan melalui POST dengan CSRF token.

5. **JSON data delivery**  
   Data Experience diambil dari database, diserialisasi menjadi JSON, kemudian dideserialisasi sebelum dikirim melalui context ke template.

6. **Pencarian dan filter**  
   Pengguna dapat menggabungkan pencarian judul, filter kategori, dan filter status. Tombol reset mengembalikan daftar tanpa filter.

7. **Peningkatan UI/UX**  
   Halaman menyediakan pesan sukses, informasi ketika hasil pencarian kosong, efek hover kartu dan tombol, serta penanda fokus untuk navigasi keyboard. Efek gerakan dinonaktifkan ketika pengguna memilih pengurangan animasi.

8. **Pengujian**  
   Pengujian Django mencakup akses halaman, kombinasi filter, kesesuaian hasil JSON dan halaman, serta operasi tambah, edit, dan hapus beserta pesan suksesnya.


### Refleksi Tugas 1

1. Ya, saya menggunakan elemen semantic HTML5 yaitu <section> dan <article>. Saya menggunakan elemen <section> untuk membagi web portofolio menjadi beberapa bagian, seperti About Me, Skills, Projects, dan Experiences. Saya juga menggunakan <article> untuk membuat setiap kartu projek bisa berdiri sendiri dan mudah untuk di edit.

Menurut saya, elemen semantic sangat membantu untuk membuat struktur website yang rapi dan lebih readable. Elemen ini juga mempermudah penerapan css sehingga tiap halaman mempunya fungsi yang berbeda. Kemudia saya tidak menggunakan <aside> karena website saya tidak memiliki konten sampingan yang terpisah dari konten Utama

2. Bagi saya menyesuaikan tata letak dari screen desktop ke mobile cukup sulit karena saya harus memikirkan ulang tata letak yang bagus dan mudah dibaca. Layar mobile yang jauh lebih kecil membuat saya untuk mengatur ulang proporsi tiap elemen. Kemudian, saya kesulitan untuk menentukan interaksi apa yang cocok untuk beberapa section supaya pengguna mengetahui konten atau fitur yang tersedia. 

Cara saya mengevaluasi elemen apa yang perlu diubah adalah berdasarkan kepentingan informasi yang perlu disampaikan. Konten utama seperti nama, deskripsi, dan projek menjadi prioritas saya supaya pengguna mudah membacanya. Lalu, elemen pendukung diletakkan di ruang yang tidak mengganggu informasi penting. Untuk menyesuaikan ruang saya mengubah layout 2 kolom menjadi satu kolom.

Perubahan tersebut diterapkan menggunakan media query. Sebagai contoh, pada layar mobile saya mengubah project dan experience menjadi satu kolom. Saya juga mengurangi ukuran teks dan jarak antarelemen serta membuat ukuran gambar menyesuaikan lebar layar. Hasilnya kemudian dievaluasi menggunakan fitur responsive device mode pada browser untuk memastikan tidak ada elemen yang terpotong, bertumpuk, atau sulit digunakan pada berbagai ukuran layar.

3. Batasan yang saya rasakan adalah seluruh informasi masih ditulis langsung di dalam HTML. Sehingga Ketika ingin menambah konten seperti projek, pengalaman, dan skills saya harus mengubah langsung di html. website nya juga belum bisa menerima dan menyimpan data dari user dan gapunya interaksi yang kompleks.

pada proyek berikutnya, saya ingin meningkatkan fungsionalitas dari website nya menggunakan database. Saya ingin membuat system Kelola supaya konten seperti projek dll bisa di update melalui halaman admin tanpa mengubah html. Kemudian, saya ingin membuat section yang dapat menerima pesan dari pengunjung.

### AI Disclosure Tugas 1
Saya menggunakan claude untuk membantu membuat gambaran design secara garis besar dan saya mencoba menerapkan nya ke html secara mandiri. Ketika ada yang error dan ketidakseuaian design yang saya mau, saya minta bantuan claude untuk membenarkan code nya.


### Refleksi Tugas 2

1. Pertama, Ketika pengguna membuka /achievements, urls.py proyek melanjutkan permintaan ke urls.py aplikasi main, yang setelah itu memanggil view show_achievements. Kemudian, view mengambil data dari database melalui model Achievements, lalu mengirimkannya melalui context ke template achievements.html. Template menampilkan data menggunakan perulangan atau pesan kosong jika belum ada data. Django kemudian mengirim hasil HTML ke browser untuk ditampilkan.

2. Data lebih baik disimpan dalam database melalui model supaya masing-masing berdiri secara independen. Sehingga, data mudah untuk diubah, ditambah, dan dihapus tanpa mengubah ubah HTML nya. Hal ini juga memudahkan untuk pemelihraan aplikasi. Pengembangan fitur seperti pencarian, filter, dll juga lebih mudah karena datanya terstruktur.

3. makemigrations membuat berkas migrasi yang berisi catatan perubahan model, sedangkan migrate adalah command untuk menerapkan perubahan tersebut ke database. Contohnya, ketika menambahkan field image_url pada model Achievements, makemigrations dan migrate perlu dijalankan agar kolom baru tersedia di database.

### Refleksi Tugas 3
1. ModelForm memudahkan untuk pembuatan form sesuai model django sehinga field form, tipe data, dll dapat dihasilkan model tanpa perlu menulisnya secara manual. Data yang valid juga bisa disimpan ke database.

Ketika mengunakan form HTML manual, kita perlu menangani input, validasi dan penyimpanan datanya sendiri. Dan disini, peran ModelForm adalah untuk mengurangi pengulangan kode dan menjaga konsistensi form dan model. 

{% csrf_token %} digunakan pada form POST internal untuk melindungi aplikasi dari serangan Cross-Site Request Forgery (CSRF). Serangan ini mencoba membuat browser pengguna yang sedang login mengirimkan permintaan tanpa persetujuannya. Tag tersebut menghasilkan input tersembunyi berisi token yang diperiksa Django saat permintaan diterima. Jika token tidak ada atau tidak valid, Django biasanya menolak permintaan dengan respons 403 Forbidden.

2. Menurut saya JSON lebih disukai karena beberapa faktor. Pertama, lebih ringkas, JSON tidak membutuhkan tag pembuka dan penutup seperti XML. Kedua, Strukturnya sederhana, objek dan array cocok untuk pertukaran data antara frontend dan backend. Ketiga, Mendukung tipe data dasar, string, angka, boolean, array, objek, dan null dapat direpresentasikan langsung.

3. Berikut alur dari view mengembalikan data portofolio sebagai json. Client mengirim request ke URL endpoint data portofolio. Lalu, Django mencocokkan URL dengan fungsi view melalui urls.py. Kemudian, View mengambil data dari database menggunakan ORM Django. Data diserialisasi menjadi format JSON. Setelah itu, View mengembalikan respons HTTP dengan tipe konten application/json. Terakhir, Client membaca JSON dan menggunakannya, misalnya untuk menampilkan daftar portofolio.



### AI Disclosure Tugas 3
Saya menggunakan chatgpt untuk menjelaskan overview alur dari pengerjaan tutorial dan tugas lalu mencoba mengerjakannnya sendiri. Ketika ada problem saya juga meminta chatgpt untuk mencari akar masalah dan juga minta untuk cek kode sebelum di push.

Keterbatasan AI: contoh kode yang diberikan belum selalu sesuai dengan kondisi proyek saya karena saya tidak menggunakan ai yang terintegrasi dengan vscode.


### AI Disclosure Tugas 4

Saya menggunakan ChatGPT untuk memahami alur pengerjaan tutorial dan tugas supaya lebih mudah dimengerti, kemudian saya juga menggunakannya untuk mengoreksi atau memastikan tidak ada langkah yang salah dari pengerjaan saya. Selain itu, saya juga meminta ai untuk memberikan beberapa ide untuk fitur tambahan di navbar.


Ringkasan alur prompting:

1. Meminta analisis instruksi Tugas 4 dan penyesuaian terhadap alur Tutorial 4.
2. Meminta pengerjaan dibagi menjadi lima bagian commit progresif.
3. memastikan setiap sebelum commit kode saya sudah tepat

Keterbatasan AI yang ditemukan adalah solusi umum tidak selalu langsung sesuai dengan struktur proyek. Contohnya, fitur Tutorial 4 diterapkan pada Achievements, sedangkan Tugas 4 harus melanjutkan Experience dari Tugas 3. Pembuatan akun superuser dan penetapan anggota grup `Editor` tetap harus dilakukan melalui environment dan Django Admin, bukan diasumsikan selesai oleh kode.
