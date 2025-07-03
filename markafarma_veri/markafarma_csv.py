import pandas as pd

# JSON dosyasını oku
df = pd.read_json("markafarma_all_products.json", lines=True,  encoding="utf-8")

# CSV olarak kaydet
df.to_csv("markafarma_urun_katalog.csv", index=False, encoding="utf-8-sig")

print("✅ CSV dosyası başarıyla oluşturuldu: markafarma_urun_katalog.csv")
