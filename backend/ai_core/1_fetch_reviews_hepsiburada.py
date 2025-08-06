import time
import json
import random
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

def setup_driver():
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Hata: WebDriver başlatılamadı. Hata detayı: {e}")
        return None
    return driver

def scrape_current_page(driver, reviews_list, max_reviews):
    """
    Mevcut sayfadaki yorumları çeker ve verilen listeye ekler.
    """
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    comment_selector = 'div[class^="hermes-ReviewCard-module-"] > span:not([class])'
    comment_elements = soup.select(comment_selector)
    
    new_comments_found = 0
    for element in comment_elements:
        if len(reviews_list) >= max_reviews:
            break
        comment_text = element.get_text(strip=True)
        if comment_text and not any(r['comment'] == comment_text for r in reviews_list):
            reviews_list.append({'comment': comment_text})
            new_comments_found += 1
            
    print(f"Bilgi: Bu sayfadan {new_comments_found} yeni yorum eklendi. Toplam: {len(reviews_list)}")

def fetch_reviews_hepsiburada(url, max_reviews=9999):
    reviews = []
    print(f"Hepsiburada için yorum çekme işlemi başlatıldı: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver: return []

        base_product_url = url.split('?')[0]
        print(f"Bilgi: Ana ürün sayfasına gidiliyor: {base_product_url}")
        driver.get(base_product_url)
        
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
            print("Bilgi: Çerez pop-up'ı kapatıldı.")
            time.sleep(random.uniform(1.0, 2.0))
        except Exception:
            print("Bilgi: Çerez pop-up'ı bulunamadı veya zaten kapalı.")

        try:
            print("Bilgi: 'Değerlendirmeler' sekmesini bulmak için bekleniyor...")
            selector = (By.XPATH, "//a[contains(@href, '-yorumlari')]")
            reviews_tab = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(selector))
            print("Bilgi: 'Değerlendirmeler' sekmesi bulundu. Tıklanıyor...")
            driver.execute_script("arguments[0].click();", reviews_tab)
            print("Bilgi: 'Değerlendirmeler' sekmesine başarıyla tıklandı.")
            time.sleep(3) # Yorumların ilk sayfasının yüklenmesi için bekle

        except Exception as e:
            print(f"\nKRİTİK HATA: 'Değerlendirmeler' sekmesi bulunamadı veya tıklanamadı. Hata: {e}")
            if driver: driver.quit()
            return []

        # --- YENİ SAYFALANDIRMA (PAGINATION) MANTIĞI ---
        print("\n--- Sayfalandırma Döngüsü Başlatılıyor ---")
        
        # 1. İlk sayfayı çek
        print("Bilgi: 1. sayfa taranıyor...")
        scrape_current_page(driver, reviews, max_reviews)

        page_to_click = 2
        while len(reviews) < max_reviews:
            try:
                # Sonraki sayfanın butonunu bul
                print(f"Bilgi: {page_to_click}. sayfa butonu aranıyor...")
                
                # XPath: İçindeki span'in metni bir sonraki sayfa numarası olan `li` elementini bulur.
                page_button_xpath = f"//li[.//span[text()='{page_to_click}']]"
                
                page_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, page_button_xpath))
                )
                
                # Butona tıkla
                driver.execute_script("arguments[0].click();", page_button)
                print(f"Bilgi: {page_to_click}. sayfaya başarıyla geçildi.")
                
                # Yeni sayfanın yüklenmesini bekle
                time.sleep(random.uniform(0.5, 1.5))
                
                # Yeni sayfadaki yorumları çek
                print(f"Bilgi: {page_to_click}. sayfa taranıyor...")
                scrape_current_page(driver, reviews, max_reviews)

                # Bir sonraki sayfa için sayacı artır
                page_to_click += 1

            except (TimeoutException, NoSuchElementException):
                print(f"Bilgi: {page_to_click}. sayfa butonu bulunamadı. Muhtemelen son sayfa.")
                break # Döngüyü sonlandır
            
    except Exception as e:
        print(f"Hata: İşlem sırasında beklenmedik bir hata oluştu: {e}")
    finally:
        if driver:
            driver.quit()
    
    print(f"\nToplam {len(reviews)} adet benzersiz yorum başarıyla çekildi.")
    return reviews

def main():
    parser = argparse.ArgumentParser(description='Hepsiburada yorum çekme aracı')
    parser.add_argument('--url', required=True, help='Hepsiburada ürün URL\'si')
    parser.add_argument('--max-reviews', type=int, default=50, help='Maksimum yorum sayısı (varsayılan: 50)')
    
    args = parser.parse_args()
    
    print(f"İşlem başlatıldı: {args.url}")
    reviews = fetch_reviews_hepsiburada(args.url, args.max_reviews)
    
    if not reviews:
        print("İşlem tamamlandı ancak hiç yorum çekilemedi.")
        return
        
    output_data = {
        "source_url": args.url,
        "scraped_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "comment_count": len(reviews),
        "reviews": reviews
    }
    
    # JSON dosyasına kaydet
    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nYorumlar 'reviews.json' dosyasına başarıyla kaydedildi.")
    print(f"Toplam {len(reviews)} yorum çekildi.")

if __name__ == "__main__":
    main() 