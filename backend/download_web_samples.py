import requests
import os

def download_specimens():
    targets = [
        ("AI", "V8_Sample_1.jpg", "https://preview.redd.it/trying-out-v8-v0-6d73uu5ekppg1.jpg?width=976&format=pjpg&auto=webp&s=e6232f69040a95884900a0b4a1a19abe93a9f7aa"),
        ("AI", "V8_Sample_2.jpg", "https://preview.redd.it/trying-out-v8-v0-b4ymeu5ekppg1.jpg?width=976&format=pjpg&auto=webp&s=cc5bc892104eaf28521a31ba4a9d80fe11e60f7f"),
        ("AI", "V8_Sample_3.jpg", "https://preview.redd.it/trying-out-v8-v0-uvwa2v5ekppg1.jpg?width=976&format=pjpg&auto=webp&s=35984e5ad9169aaf291d56997f6aa8121342f9ac"),
        ("AI", "V8_Sample_4.jpg", "https://preview.redd.it/trying-out-v8-v0-e0butb6ekppg1.jpg?width=976&format=pjpg&auto=webp&s=cb8920b56ee44e1abdb93852e3cb9557f81e5703"),
        ("AI", "V8_Sample_5.jpg", "https://preview.redd.it/trying-out-v8-v0-upfuo8041tpg1.jpeg?width=640&crop=smart&auto=webp&s=8ec17e005380e17826c4a628b8f55421008c9a9f"),
        ("Real", "Nikon_Z9_Sample.jpg", "https://live.staticflickr.com/65535/54888725738_b4e4c9e820_b.jpg"),
        ("Real", "Nikon_Z_70mm.jpg", "https://live.staticflickr.com/65535/54888742679_843dd5a9e3_b.jpg"),
        ("Real", "Canon_R5_Sample_1.jpg", "https://live.staticflickr.com/65535/50122817181_57e5f1c6a9_b.jpg"),
        ("Real", "Canon_R5_Sample_2.jpg", "https://live.staticflickr.com/65535/50109858977_2bf45eba6f_b.jpg"),
        ("Real", "Sony_A7R4_Sample.jpg", "https://live.staticflickr.com/65535/50109051258_d1576d3fc4_b.jpg")
    ]
    
    base_dir = "f:/Exp  AI Dect/Sample Data/Web"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    for category, name, url in targets:
        path = os.path.join(base_dir, name)
        print(f"Downloading {category}/{name}...")
        try:
            r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f"  [SUCCESS] -> {path}")
            else:
                print(f"  [FAILED] HTTP {r.status_code}")
        except Exception as e:
            print(f"  [ERROR] {e}")

if __name__ == "__main__":
    download_specimens()
