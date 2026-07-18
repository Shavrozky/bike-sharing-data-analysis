# Bike Sharing Data Analysis Dashboard

Proyek ini merupakan submission akhir kelas **Belajar Analisis Data dengan Python** dari Dicoding.

Proyek menggunakan **Bike Sharing Dataset** untuk menganalisis pola penyewaan sepeda berdasarkan waktu, jenis hari, kondisi cuaca, dan tipe pengguna selama periode 2011–2012.

## Deskripsi Proyek

Bike Sharing Dataset berisi data historis penyewaan sepeda dari sistem Capital Bikeshare di Washington D.C.

Dataset terdiri dari dua tingkat agregasi:

- Data harian pada `day.csv`
- Data per jam pada `hour.csv`

Analisis dilakukan mulai dari proses data wrangling, exploratory data analysis, visualisasi, explanatory analysis, hingga penyusunan kesimpulan dan rekomendasi bisnis.

## Pertanyaan Bisnis

Analisis ini bertujuan menjawab pertanyaan berikut:

1. Pada jam berapa rata-rata jumlah penyewaan sepeda mencapai nilai tertinggi pada hari kerja dan non-hari kerja selama periode 2011–2012?

2. Seberapa besar perbedaan rata-rata penyewaan sepeda pada setiap kondisi cuaca selama periode 2011–2012, dan kelompok pengguna mana yang paling sensitif terhadap perubahan cuaca?

## Insight Utama

Beberapa insight utama yang diperoleh dari proses analisis:

- Pada hari kerja, rata-rata penyewaan tertinggi terjadi pada pukul 17.00.
- Pada non-hari kerja, rata-rata penyewaan tertinggi terjadi sekitar pukul 13.00.
- Hari kerja memiliki pola permintaan yang berkaitan dengan jam berangkat dan pulang kerja.
- Permintaan penyewaan menurun ketika kondisi cuaca memburuk.
- Pengguna casual lebih sensitif terhadap perubahan cuaca dibandingkan pengguna registered.
- Pengguna registered memberikan kontribusi terbesar terhadap total penyewaan.
- Segmentasi permintaan berbasis kuartil dapat digunakan untuk mengelompokkan hari ke dalam kategori Low, Medium, High, dan Very High.

## Struktur Direktori

```text
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
