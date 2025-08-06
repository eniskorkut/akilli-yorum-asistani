# Hepsiburada Scraper Modülü
# Bu dosya Hepsiburada ürün sayfalarından yorumları çeker
# Selenium kullanarak web scraping yapar
#
# Özellikler:
# - Hepsiburada ürün sayfalarından yorum çekme
# - Otomatik sayfa navigasyonu
# - Çerez pop-up yönetimi
# - Sayfalandırma desteği
# - Çoklu seçici desteği
#
# Kullanım:
# python hepsiburada_scraper.py --url "https://www.hepsiburada.com/urun-url" --max-reviews 50
#
# Gereksinimler:
# - selenium
# - beautifulsoup4
# - webdriver-manager
#
# Lisans: MIT
# Yazar: Akıllı Yorum Asistanı Projesi

import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

def setup_driver():
    """
    Chrome WebDriver'ı yapılandırır ve başlatır
    """
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mod aktif
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Hata: WebDriver başlatılamadı. Hata detayı: {e}")
        return None

def scrape_current_page(driver, reviews_list, max_reviews):
    """
    Mevcut sayfadaki yorumları çeker ve verilen listeye ekler.
    """
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Hepsiburada yorum seçicileri
    comment_selectors = [
        'div[class^="hermes-ReviewCard-module-"] > span:not([class])',
        'div[class*="ReviewCard"] span:not([class])',
        'div[class*="review"] span:not([class])',
        '.review-comment',
        '.comment-text'
    ]
    
    comment_elements = []
    for selector in comment_selectors:
        comment_elements = soup.select(selector)
        if comment_elements:
            print(f"Yorum seçici bulundu: {selector}")
            break
    
    new_comments_found = 0
    for element in comment_elements:
        if len(reviews_list) >= max_reviews:
            break
        comment_text = element.get_text(strip=True)
        if comment_text and len(comment_text) > 10 and not any(r['comment'] == comment_text for r in reviews_list):
            reviews_list.append({
                'comment': comment_text,
                'rating': 0,
                'user': 'Anonim',
                'date': '',
                'source': 'hepsiburada_selenium'
            })
            new_comments_found += 1
            
    print(f"Bilgi: Bu sayfadan {new_comments_found} yeni yorum eklendi. Toplam: {len(reviews_list)}")

def fetch_reviews_hepsiburada(url, max_reviews=50):
    """
    Hepsiburada ürün sayfasından yorumları çeker
    """
    reviews = []
    print(f"Hepsiburada için yorum çekme işlemi başlatıldı: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver: 
            return []

        base_product_url = url.split('?')[0]
        print(f"Bilgi: Ana ürün sayfasına gidiliyor: {base_product_url}")
        driver.get(base_product_url)
        
        # Çerez pop-up'ını kapat
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
            print("Bilgi: Çerez pop-up'ı kapatıldı.")
            time.sleep(random.uniform(1.0, 2.0))
        except Exception:
            print("Bilgi: Çerez pop-up'ı bulunamadı veya zaten kapalı.")

        # Değerlendirmeler sekmesini bul ve tıkla
        try:
            print("Bilgi: 'Değerlendirmeler' sekmesini bulmak için bekleniyor...")
            selectors = [
                (By.XPATH, "//a[contains(@href, '-yorumlari')]"),
                (By.XPATH, "//a[contains(text(), 'Değerlendirmeler')]"),
                (By.XPATH, "//a[contains(text(), 'Yorumlar')]"),
                (By.CSS_SELECTOR, "a[href*='yorum']"),
                (By.CSS_SELECTOR, "a[href*='degerlendirme']")
            ]
            
            reviews_tab = None
            for selector in selectors:
                try:
                    reviews_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(selector))
                    print(f"Bilgi: 'Değerlendirmeler' sekmesi bulundu: {selector}")
                    break
                except:
                    continue
            
            if reviews_tab:
                driver.execute_script("arguments[0].click();", reviews_tab)
                print("Bilgi: 'Değerlendirmeler' sekmesine başarıyla tıklandı.")
                time.sleep(3)  # Yorumların ilk sayfasının yüklenmesi için bekle
            else:
                print("Bilgi: Değerlendirmeler sekmesi bulunamadı, mevcut sayfayı taramaya devam ediliyor.")

        except Exception as e:
            print(f"Bilgi: Değerlendirmeler sekmesi bulunamadı: {e}")

        # --- SAYFALANDIRMA (PAGINATION) MANTIĞI ---
        print("\n--- Sayfalandırma Döngüsü Başlatılıyor ---")
        
        # 1. İlk sayfayı çek
        print("Bilgi: 1. sayfa taranıyor...")
        scrape_current_page(driver, reviews, max_reviews)

        page_to_click = 2
        max_pages = 10  # Maksimum sayfa sayısı
        
        while len(reviews) < max_reviews and page_to_click <= max_pages:
            try:
                # Sonraki sayfanın butonunu bul
                print(f"Bilgi: {page_to_click}. sayfa butonu aranıyor...")
                
                # Farklı sayfa butonu seçicileri
                page_button_selectors = [
                    f"//li[.//span[text()='{page_to_click}']]",
                    f"//a[text()='{page_to_click}']",
                    f"//button[text()='{page_to_click}']",
                    f"//span[text()='{page_to_click}']/.."
                ]
                
                page_button = None
                for selector in page_button_selectors:
                    try:
                        page_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, selector)))
                        print(f"Bilgi: Sayfa butonu bulundu: {selector}")
                        break
                    except:
                        continue
                
                if page_button:
                    # Sayfa butonuna tıkla
                    driver.execute_script("arguments[0].click();", page_button)
                    print(f"Bilgi: {page_to_click}. sayfaya geçildi.")
                    time.sleep(2)  # Sayfanın yüklenmesi için bekle
                    
                    # Yeni sayfadaki yorumları çek
                    scrape_current_page(driver, reviews, max_reviews)
                    page_to_click += 1
                else:
                    print(f"Bilgi: {page_to_click}. sayfa butonu bulunamadı. Sayfalandırma tamamlandı.")
                    break
                    
            except Exception as e:
                print(f"Bilgi: Sayfa {page_to_click} geçişinde hata: {e}")
                break

        print(f"\nBilgi: Toplam {len(reviews)} yorum çekildi.")
        
    except Exception as e:
        print(f"Hata: Hepsiburada yorum çekme işleminde beklenmeyen hata: {e}")
    finally:
        if driver:
            driver.quit()
            print("Bilgi: WebDriver kapatıldı.")
    
    return reviews

def main():
    """
    Test fonksiyonu
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Hepsiburada yorum çekme')
    parser.add_argument('--url', required=True, help='Hepsiburada ürün URL\'si')
    parser.add_argument('--max-reviews', type=int, default=50, help='Maksimum yorum sayısı')
    
    args = parser.parse_args()
    
    reviews = fetch_reviews_hepsiburada(args.url, args.max_reviews)
    
    # Yorumları JSON dosyasına kaydet
    with open('hepsiburada_reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    
    print(f"Toplam {len(reviews)} yorum 'hepsiburada_reviews.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main() 