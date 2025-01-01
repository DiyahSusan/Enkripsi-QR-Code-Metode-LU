# **Tugas Makalah Aljabar Linear dan Geometri**
Program untuk melakukan enkripsi terhadap QR code menggunakan dekomposisi matriks LU
<br>

## Contributors
<div align="center">

| **NIM**  | **Nama** |
| ------------- |:-------------:|
| 13523080   | Diyah Susan Nugrahani |

</div>

## Apa itu Audio Enkripsi?
Enkripsi adalah sebuah proses penyandian yang merubah suatu informasi atau data menjadi bentuk yang hampir tidak dapat dikenali bentuknya dengan menggunakan algoritma tertentu. Untuk dapat mengakses informasi tersebut perlu dilakukan dekripsi. Dekripsi sendiri merupakan sebuah proses mengembalikan bentuk yang tidak dikenali tadi menjadi bentuk semula sehingga informasi semula yang ada di dalamnya dapat diakses.

## Teknologi yang Digunakan
- Javascript
- Flask     
- Python

## Bagaimana Cara Menjalankan Web-nya?
1. Pastikan python sudah terinstall. Install python dari https://www.python.org/downloads/
2. Install dependencies yang terdapat dalam requirements.txt . 
```sh
git clone https://github.com/DiyahSusan/Enkripsi-QR-Code-Metode-LU.git
cd src
pip install -r requirements.txt
```
3. Jalankan website menggunakan terminal dengan command
``` sh
cd src
python app.py
```
5. Buka link localnya http://127.0.0.1:5000

## Fitur yang Tersedia Dalam Website
1. Generate QR code
- fitur untuk membuat sebuah QR code sesuai dengan input yang diinginkan
2. Enkripsi QR code
- fitur untuk mengubah QR code menjadi gambar terenkripsi yang tidak dikenali bentuknya
3. Dekripsi QR code
- fitur untuk merekonstruksi kembali gambar terenkripsi menjadi bentuk QR semula

## Apa Kelebihan Program Ini?
Dengan menggunakan enkripsi dan dekripsi pada QR code, maka informasi dapat terjamin keamanannya karena terdapat perlindungan tambahan pada QR code tersebut. Informasi hanya dapat diakses oleh pihak yang memiliki kunci sehingga terjamin kerahasiaanya. Konsep ini dapat diterapkan dalam berbagai aspek kehidupan terutama pada kegiatan yang menggunakan QR code dalam aktivitasnya seperti pembayaran nontunai, tiket elektronik, dan masih banyak lagi.

