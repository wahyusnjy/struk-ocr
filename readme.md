 # 🧾 Aplikasi OCR Struk Belanja Pakai Streamlit

 Hai teman-teman! Aplikasi ini tuh demo keren yang pakai OCR (Optical Character Recognition), tepatnya pakai EasyOCR, buat baca struk belanja kamu. Fokus utamanya sih baru untuk struk Shell, biar kita bisa langsung ambil data penting kayak lokasi, tanggal, waktu, jenis bensin, total harga, berapa liter, sama harga per liternya. Asyiknya lagi, aplikasi ini dibikin pakai Streamlit, jadi gampang banget dipakenya lewat web!

 ---

 ## ✨ Fitur-fitur Kece!

 * Bisa Pindai dari Mana Aja: Kamu bisa langsung jepret pakai kamera HP (kalau browsernya ngizinin ya!) atau upload foto struk (JPG, JPEG, PNG) dari galeri. Gampang kan?

 * Deteksi Teks Cepat Kilat: Dia pakai EasyOCR buat nyari tulisan di gambar kamu, cepet banget lho!

 * Lihat Hasilnya Langsung: Nanti gambarmu bakal ditampilin lagi, tapi udah ada kotak-kotak kuning di sekeliling teks yang kebaca, plus tulisan merah hasil OCR-nya. Jadi jelas banget deh mana yang udah kedeteksi!

 * Oh, Ini Struk Shell ya?: Aplikasi ini pinter! Dia bisa langsung tahu kalau struk itu dari Shell, cuma dari kata-kata yang dia temukan.

 * Narik Data Penting (Kalau dari Shell!): Nah, kalau udah ketahuan ini struk Shell, dia bakal coba ngekstrak detail-detail penting kayak:

   * Tempat Beli

   * Kapan Beli & Jam Berapa (dia udah bisa ngurusin tahun yang cuma 2 angka lho!)

   * Nama Belanjanya (misalnya: "Beli bensin V-Power")

   * Total Harganya (dia juga udah bisa benerin angka yang salah baca kayak 'o' jadi '0'!)

   * Volume Bensinnya

   * Harga per Liter

 * Outputnya JSON dong!: Hasil ekstraksi datanya bakal muncul dalam format JSON yang rapi. Jadi kalau mau disambungin ke aplikasi lain, gampang banget!

 * Gampang Digunain: Karena pakai Streamlit, tampilannya simpel dan bikin kamu betah pakainya.

 ---

 ## 🛠️ Cara Pasangnya

 Buat kamu yang mau nyobain di komputer sendiri, ikutin aja langkah-langkah ini ya:

 1. Ambil kodenya dulu:

        git clone https://github.com/namauser/nama-repo-anda.git     
        cd nama-repo-anda         

    (Jangan lupa ganti namauser/nama-repo-anda dengan informasi repositori kamu ya!)

 2. Bikin Rumah Baru buat Kodenya (Opsional sih, tapi bagusnya gitu!):

        python -m venv venv     
        # Untuk Windows     venv\Scripts\activate     
        # Untuk macOS/Linux     source venv/bin/activate         

 3. Instal alat-alatnya:

        pip install -r requirements.txt         

    (Kalau belum ada, bikin aja file requirements.txt isinya kayak gini:)

        streamlit     
        easyocr     
        numpy     
        opencv-python-headless    
        Pillow         

 ---

 ## 🚀 Yuk, Jalanin!

 Setelah semua alat siap, tinggal ketik perintah ini di terminal:

  streamlit run your_app_file_name.py  

 (Ingat ya, ganti your_app_file_name.py sama nama file Python utama aplikasimu, contohnya app.py atau main.py)

 Nanti aplikasinya bakal langsung kebuka otomatis di browser kamu (biasanya di http://localhost:8501).

 ---

 ## 💡 Gimana Cara Pakainya?

 1. Begitu aplikasinya kebuka di browser, kamu bakal lihat judul "Kamera & OCR Streamlit Demo".

 2. Nangkap Gambar:

   * Kamu bisa "Ambil gambar dari kamera" kalau lagi pakai HP atau perangkat yang ada kameranya.

   * Atau, "Upload file gambar" aja kalau fotonya udah ada di komputermu.

 3. Lihat Hasilnya:

   * Foto yang kamu upload/jepret bakal langsung nongol.

   * Aplikasi bakal gercep proses gambarnya, terus nampilin "Hasil Kata yang Terdeteksi" dalam bentuk daftar.

   * Di bagian "Informasi Struk", dia bakal kasih tahu apakah struk itu dari Shell atau bukan.

   * "Data OCR (JSON)" itu tempat semua data yang udah diekstrak muncul, formatnya rapi. Kalau ini struk Shell, detail pentingnya ada di sini semua!

   * Terus, ada "Preview Gambar dengan Highlight Teks" juga, biar kamu bisa lihat sendiri kotak-kotak di teks yang kebaca.

 ---

 ## ⚠️ Penting Nih, Dibaca Dulu ya!

 * Akurasi OCR itu Tergantung Gambar: Hasil OCR bisa bagus apa enggak, tergantung banget sama kualitas gambarmu (jernih enggak, terang enggak, fokus enggak, miring enggak). Struk yang kusut, buram, atau pakai tulisan aneh, bisa bikin hasilnya kurang oke.

 * Ekstraksi Data itu Butuh Format Konsisten: Logika buat narik detail-detail kayak tanggal atau jumlah itu pakai rumus-rumus (Regex) dan ngincer baris tertentu. Jadi, ini ngarepin banget format struk Shell itu konsisten. Kalau ada beda dikit aja di tata letaknya, bisa-bisa datanya enggak kedeteksi sempurna.

 * Tahun 2 Angka: Buat tahun yang cuma 2 angka (misal: 25 buat 2025), aplikasinya cuma nebak lho. Jadi kalau kamu punya struk jadul banget dari abad lain, bisa jadi tebakannya salah.

 * Bukan Ahli Baca Struk Khusus: Proyek ini pakai EasyOCR yang sifatnya umum. Dia bukan ahli khusus yang dilatih buat baca struk belanja. Jadi, kalau kamu butuh akurasi super tinggi buat data struk dalam jumlah besar, mungkin perlu solusi yang lebih canggih (kayak AI yang memang dilatih khusus buat baca dokumen atau API parsing struk).

 ---

 ## 🤝 Mau Bantu?

 Kalau kamu punya ide, mau benerin yang salah, atau mau nambahin sesuatu, seneng banget deh! Bikin aja issue atau kirim pull request di GitHub ya! Makasih banyak!