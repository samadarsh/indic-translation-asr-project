import pandas as pd
import os

print("Building dataset from raw FLORES-200 files...")

BASE = "data/raw/flores200_dataset"
ENG_FILE = os.path.join(BASE, "devtest", "eng_Latn.devtest")
TAM_FILE = os.path.join(BASE, "devtest", "tam_Taml.devtest")
META_FILE = os.path.join(BASE, "metadata_devtest.tsv")

# Verify files exist
for f in [ENG_FILE, TAM_FILE, META_FILE]:
    if not os.path.exists(f):
        print(f"❌ File not found: {f}")
        exit(1)
    else:
        print(f"✅ Found: {f}")

# Read English sentences
with open(ENG_FILE, "r", encoding="utf-8") as f:
    english = [line.strip() for line in f.readlines()]

# Read Tamil sentences
with open(TAM_FILE, "r", encoding="utf-8") as f:
    tamil = [line.strip() for line in f.readlines()]

# Read metadata
meta_df = pd.read_csv(META_FILE, sep="\t")

print(f"\nEnglish sentences: {len(english)}")
print(f"Tamil sentences  : {len(tamil)}")
print(f"Metadata rows    : {len(meta_df)}")
print(f"Metadata columns : {meta_df.columns.tolist()}")

df = pd.DataFrame({
    "id": list(range(1, len(english) + 1)),
    "english": english,
    "tamil_reference": tamil,
    "domain": meta_df["domain"].values,
    "topic": meta_df["topic"].values,
})

df.to_csv("data/raw/translation_dataset.csv", index=False)
print(f"\n✅ Saved {len(df)} rows to data/raw/translation_dataset.csv")
print(df.head(3).to_string())