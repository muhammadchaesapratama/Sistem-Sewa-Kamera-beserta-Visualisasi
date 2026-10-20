# Library
import datetime
import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict

# Nama Database
Nama_DB = 'daftar_sewa_kamera.db'

# Connect Database
def setup_database():
    conn = sqlite3.connect('daftar_sewa_kamera.db')
    cursor = conn.cursor()

# Membuat table kamera
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kamera (
        id INTEGER PRIMARY KEY,
        merek TEXT NOT NULL,
        model TEXT NOT NULL,
        harga INTEGER NOT NULL,
        tersedia INTEGER NOT NULL --1 for True, 0 for False
    )
    """)

# Membuat tabel transaksi sewa kamera
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_kamera INTEGER NOT NULL,
        nama_pelanggan TEXT NOT NULL,
        hari_sewa INTEGER NOT NULL,
        total_biaya INTEGER NOT NULL,
        tanggal_sewa TEXT NOT NULL,
        tanggal_pengembalian TEXT NOT NULL,
        FOREIGN KEY (id_kamera) REFERENCES kamera (id) --Membangun hubungan id_kamera berdasarkan id
    )
    """)

# Insert data awal kamera
    cursor.execute('SELECT COUNT(*) FROM kamera')
    if cursor.fetchone()[0] == 0:
        kl = [
            (1, "Cannon", "EOS R5", 50000, 1),
            (2, "Sony", "ZV-E10", 150000, 1),
            (3, "Nikon", "D3200", 70000, 1),
            (4, "Fujifilm", "XT100", 125000, 1),
            (5, "Cannon", "5D MARK III", 300000, 1)
        ]
        cursor.executemany('''
        INSERT INTO kamera (id, merek, model, harga, tersedia)
        VALUES (?, ?, ?, ?, ?)
        ''', kl)

    conn.commit()
    conn.close()

def tampilkan_kamera():
    conn = sqlite3.connect(Nama_DB)
    cursor = conn.cursor()

    print("\n")
    print("-"*65)
    print("               Daftar Kamera dan Harga Sewa Kamera                   ")
    # Membuat Header Tabel
    print("-"*65)
    print(f"{'ID':<5} {'Merek':<12} {'Model':<16} {'Harga/hari':<12} {'Status':<10} ")
    print("-"*65)

    cursor.execute('''
        SELECT id, merek, model, harga, tersedia FROM kamera
        ''')
    for row in cursor.fetchall():
        id_kamera, merek, model, harga, tersedia = row
        status = "Tersedia" if tersedia else "Disewa"
        print(f"{id_kamera:<5} {merek:<12} {model:<16} {harga:<12} {status:<10} ")

def sewa_kamera():
    total_biaya_sesi = 0
    penyewaan_sesi = []

    while True:
        tampilkan_kamera()
        try:
            print("="*65)
            id_k = int(input("\nMasukkan ID Kamera yang ingin disewa: "))

            conn = sqlite3.connect(Nama_DB)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT merek, model, harga, tersedia FROM kamera
                WHERE id = ?
                ''', (id_k,))
            row = cursor.fetchone()

            if row:
                merek, model, harga, tersedia = row
                if tersedia:
                    nama_pelanggan = input("Masukkan nama pelanggan: ")
                    hari_sewa = int(input("Masukkan jumlah hari sewa: "))

                    biaya_total = harga * hari_sewa
                    tanggal_sewa = datetime.date.today() # Menggunakan library datetime untuk menampilkan tanggal sewa
                    tanggal_pengembalian = tanggal_sewa + datetime.timedelta(days = hari_sewa)

                    # Update status sewa kamera
                    cursor.execute('''
                        UPDATE kamera SET tersedia = 0
                        WHERE id = ?
                        ''', (id_k,))

                    # Insert transaksi
                    cursor.execute('''
                        INSERT INTO transaksi (id_kamera, nama_pelanggan, hari_sewa, total_biaya, tanggal_sewa, tanggal_pengembalian)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (id_k, nama_pelanggan, hari_sewa, biaya_total, str(tanggal_sewa), str(tanggal_pengembalian)))

                    conn.commit()

                    # Total Biaya Sesi
                    total_biaya_sesi += biaya_total
                    penyewaan_sesi.append({
                        'nama': nama_pelanggan,
                        'merek': merek,
                        'model': model,
                        'hari_sewa': hari_sewa,
                        'biaya_total': biaya_total,
                        'tanggal_sewa': tanggal_sewa,
                        'tanggal_pengembalian': tanggal_pengembalian
                    })

                    # Fungsi untuk menginput ingin menyewa kamera lagi atau tidak
                    lagi = input("\nApakah ingin menyewa kamera lagi?(y/n): ").lower()
                    if lagi == 'y':
                        conn.close()
                        continue
                    elif lagi == 'n':
                        # Tampilkan ringkasan output
                        print("\n" + "="*65)
                        print("📋 Ringkasan Penyewaan:")
                        print("="*65)
                        for i, sewa in enumerate(penyewaan_sesi, 1):
                            print(f"\nPenyewaan {i}:")
                            print(f"  👤Nama Penyewa: {sewa['nama']}")
                            print(f"  📷Kamera: {sewa['merek']} {sewa['model']}")
                            print(f"  ⏳Durasi: {sewa['hari_sewa']} hari")
                            print(f"  💰Biaya: Rp{sewa['biaya_total']:,}")
                            print(f"  📅Tanggal Sewa: {sewa['tanggal_sewa']}")
                            print(f"  🔄Tanggal Pengembalian: {sewa['tanggal_pengembalian']}")
                        print(f"\n💰 Total Biaya Seluruhnya: Rp{total_biaya_sesi:,}")
                        print("🌟 Terima Kasih telah menggunakan jasa sewa kamera kami!.🌟")
                        print("="*65)
                        conn.close()
                        return
                    else:
                        print("Input Tidak Valid!.")
                        conn.close()
                        return
                else:
                    print(f"\nKamera {merek} {model} sedang disewa.")
                    conn.close()
                    break
            else:
                print("\nKamera tidak ditemukan.")
                conn.close()
                break
        except ValueError:
            print("\nInput Tidak Valid. Pastikan Angka ID Kamera dan Jumlah Hari Sewa Valid!.")
            break

def kembalikan_kamera():
    try:
        tampilkan_kamera() # Menampilkan daftar kamera yang tersedia dan sedang disewa sebelum dikembalikan
        id_k = int(input("\nMasukkan ID Kamera yang ingin dikembalikan: "))

        conn = sqlite3.connect(Nama_DB)
        cursor = conn.cursor()

        # Mengecek apa ada transaksi di model dan merek kamera tersebut
        cursor.execute('''
            SELECT COUNT(*) FROM transaksi
            WHERE id_kamera = ?
            ''', (id_k,))
        if cursor.fetchone()[0] > 0:
            cursor.execute('''
                SELECT merek, model FROM kamera
                WHERE id = ?
                ''', (id_k,))
            row = cursor.fetchone()
            if row:
              merek, model = row
              tanggal_pengembalian = datetime.date.today()
              # Update Status Pengembalian Kamera
              cursor.execute('''
                UPDATE kamera SET tersedia = 1
                WHERE id = ?
                ''', (id_k,))
              conn.commit()
              print(f"Kamera {merek} {model} berhasil dikembalikan pada tanggal {tanggal_pengembalian}!")
              print("Terima kasih telah menyewa kamera kami!.")
            else:
                print("Kamera tidak ditemukan.")
        else:
            print(f"Tidak ada transaksi untuk ID kamera {id_k} ini.")

        conn.close()
    except ValueError:
        print("\nInput Tidak Valid. Pastikan Angka ID Kamera Valid!.")

def visualisasi_penyewaan_perbulan():
    conn = sqlite3.connect(Nama_DB)
    cursor = conn.cursor()

    # Query untuk mengelompokkan penyewaan berdasarkan bulan, kamera, dan menghitung jumlahnya
    cursor.execute('''
        SELECT strftime('%Y-%m', tanggal_sewa) as bulan, merek || ' ' || model as kamera, COUNT(*) as jumlah
        FROM transaksi
        JOIN kamera ON transaksi.id_kamera = kamera.id
        GROUP BY bulan, kamera
        ORDER BY bulan, kamera
    ''')
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("Tidak ada data penyewaan untuk divisualisasikan!.")
        return

    # Mengumpulkan data ke dalam dict: bulan -> {kamera: jumlah}
    bulan_dict = defaultdict(lambda: defaultdict(int))
    kamera_set = set()
    bulan_list = []
    for bulan, kamera, jumlah in data:
        bulan_dict[bulan][kamera] += jumlah
        kamera_set.add(kamera)
        if bulan not in bulan_list:
            bulan_list.append(bulan)
    bulan_list.sort()
    kamera_list = sorted(kamera_set)

    # Membuat grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    bar_width = 0.6 / len(kamera_list) if kamera_list else 0.6  # Lebar bar
    bar_spacing = 0.05  # Jarak antar bar dalam grup
    group_spacing = 0.3  # Jarak antar grup bulan
    for i, kamera in enumerate(kamera_list):
        jumlah_per_bulan = [bulan_dict[bulan].get(kamera, 0) for bulan in bulan_list]
        positions = [j * (len(kamera_list) * (bar_width + bar_spacing) + group_spacing) + i * (bar_width + bar_spacing) for j in range(len(bulan_list))]
        ax.bar(positions, jumlah_per_bulan, width=bar_width, label=kamera)

    group_centers = [(j * (len(kamera_list) * (bar_width + bar_spacing) + group_spacing) + (len(kamera_list) * (bar_width + bar_spacing) - bar_spacing) / 2) for j in range(len(bulan_list))]
    ax.set_xticks(group_centers)
    ax.set_xticklabels(bulan_list, rotation=45)

    ax.set_xlabel('Bulan (YYYY-MM)')
    ax.set_ylabel('Jumlah Penyewaan')
    ax.set_title('Visualisasi Penyewaan Kamera Per Bulan Berdasarkan Kamera')
    ax.legend(title='Kamera')
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('visualisasi_penyewaan_per_kamera.png')  # Menyimpan grafik sebagai gambar
    plt.close('all')  # Menutup grafik
    print("Grafik visualisasi penyewaan kamera per bulan berdasarkan kamera telah disimpan sebagai 'visualisasi_penyewaan_per_kamera.png'.")

    # Pilihan untuk kembali ke menu utama
    lagi = input("\nApakah ingin kembali ke menu utama? (y/n): ").lower()
    if lagi == 'n':
        print("Terima Kasih telah menggunakan jasa sewa kamera kami!.")
        exit()  # Keluar dari program
    elif lagi != 'y':
        print("Input Tidak Valid! Kembali ke menu utama.")

def menu_utama():
    setup_database() #Memanggil setup database di awal
    while True:
        print("\n")
        print("="*65)
        print("===================== Sistem Sewa Kamera ========================")
        print("="*65)
        print("1. Tampilkan Daftar Kamera")
        print("2. Sewa kamera")
        print("3. Pengembalian Kamera")
        print("4. Visualisasi Penyewaan Kamera Per Bulan")
        print("5. Keluar")
        print("-"*65)

        pilihan = input("Pilih menu(1-5): ")

        if pilihan == "1":
            tampilkan_kamera()
        elif pilihan == "2":
            sewa_kamera()
        elif pilihan == "3":
            kembalikan_kamera()
        elif pilihan == "4":
            visualisasi_penyewaan_perbulan()
        elif pilihan == "5":
            print("Terima Kasih telah menggunakan jasa sewa kamera kami!.")
            break
        else:
            print("Input Tidak Valid!.")

# Menjalankan menu utama
if __name__ == "__main__":
    menu_utama()
