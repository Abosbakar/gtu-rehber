"""Docker derlemesi sırasında GGUF modelini Hugging Face'ten indirir.

Kullanım: python download_model.py <repo> <dosya> <hedef_klasör>
"""

import sys
import time
import urllib.request
from pathlib import Path

MIN_SIZE = 100 * 1024 * 1024  # Yarım inmiş ya da hata sayfası olan dosyayı yakalamak için


def download(repo: str, filename: str, target_dir: str, attempts: int = 3) -> None:
    url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
    target = Path(target_dir) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".part")

    for attempt in range(1, attempts + 1):
        try:
            print(f"Model indiriliyor ({attempt}/{attempts}): {url}", flush=True)
            urllib.request.urlretrieve(url, tmp)
            if tmp.stat().st_size < MIN_SIZE:
                raise RuntimeError(f"İndirilen dosya çok küçük: {tmp.stat().st_size} bayt")
            tmp.rename(target)
            print(f"Model hazır: {target} ({target.stat().st_size // (1024 * 1024)} MB)", flush=True)
            return
        except Exception as exc:
            print(f"İndirme başarısız: {exc}", flush=True)
            tmp.unlink(missing_ok=True)
            time.sleep(5 * attempt)
    sys.exit("Model indirilemedi. İnternet bağlantısını kontrol edip derlemeyi tekrar deneyin.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    download(*sys.argv[1:])
