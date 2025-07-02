import pandas as pd

# JSON dosyasını oku
df = pd.read_json("dermoecz_all_products.json", encoding="utf-8")

# CSV olarak kaydet
df.to_csv("dermoecz_urun_katalog.csv", index=False, encoding="utf-8-sig")

print("✅ CSV dosyası başarıyla oluşturuldu: recetem_com_urun_katalog.csv")
