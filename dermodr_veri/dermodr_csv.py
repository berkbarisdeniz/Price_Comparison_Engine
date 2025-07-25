import pandas as pd

# JSON dosyasını oku
df = pd.read_json("dermodr_all_products.json", encoding="utf-8")

# CSV olarak kaydet
df.to_csv("dermodr_com_urun_katalog.csv", index=False, encoding="utf-8-sig")

print("✅ CSV dosyası başarıyla oluşturuldu: dermodr_com_urun_katalog.csv")
