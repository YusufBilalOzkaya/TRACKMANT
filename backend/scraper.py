import asyncio
import re
from playwright.async_api import async_playwright
from typing import Optional

async def fetch_element_value(url: str, selector: str) -> Optional[str]:
    """
    Loads the URL with stealth settings, waits for the selector, and returns the text content.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
            extra_http_headers={
                "Referer": "https://www.google.com/",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        )
        page = await context.new_page()
        
        # --- STEALTH: Advanced Spoofing ---
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['tr-TR', 'tr'] });
            window.chrome = { runtime: {} };
        """)
        
        # Block images and heavy media but KEEP CSS for better layout compatibility
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())
        
        try:
            import random
            
            print(f"Navigating to {url} (Advanced Stealth Mode)...")
            await page.goto(url, timeout=45000, wait_until="domcontentloaded")
            
            # --- HANDLE OVERLAYS AND ADS ---
            # Wait for dynamic JS content to render (prices, tables etc.)
            await page.wait_for_timeout(4000)
            
            await page.evaluate("""() => {
                const toxic = [
                    '#onetrust-consent-sdk', '.modal-close', '.overlay', 
                    '.popup-close', '[id*="cookie"]', '.reklam-kapat',
                    '.ad-close', '#interstitial-close', '.close-button'
                ];
                toxic.forEach(s => {
                    document.querySelectorAll(s).forEach(el => {
                        el.click(); // Try to click it
                        el.style.display = 'none'; // Then hide it
                    });
                });
            }""")
            
            await page.mouse.wheel(0, random.randint(200, 400)) # Small scroll to trigger lazy loads
            await page.wait_for_timeout(2000)
            
            # --- PRIMARY ATTEMPT ---
            try:
                # Wait longer for the specific selector
                element = await page.wait_for_selector(selector, state="visible", timeout=20000)
                if element:
                    raw_value = await element.inner_text()
                    lines = [l.strip() for l in raw_value.split('\n') if l.strip()]
                    value = lines[0]
                    for line in lines:
                        if any(char.isdigit() for char in line) and any(c in line for c in ['TL', '€', '$', '%', ',']):
                            value = line
                            break
                    print(f"SUCCESS (Primary): Fetched '{value.strip()}' from {url}")
                    return value.strip()
            except:
                print(f"Primary selector failed for {url}. Attempting auto-discovery...")

            # --- FALLBACK: Auto-discovery for anything that looks like a price ---
            found = await page.evaluate("""() => {
                const candidates = document.querySelectorAll('[data-test-id*="price"], [class*="price"], [id*="price"], span, div, b');
                for (let el of candidates) {
                    const text = el.innerText.trim();
                    // Desen: 12.345,67 TL (veya sadece rakam + birim)
                    if (/\\d+[.,]\\d+\\s*(TL|€|\\$)/i.test(text) && text.length < 25) {
                        return text;
                    }
                }
                return null;
            }""")
            
            if found:
                print(f"SUCCESS (Fallback): Found '{found}' from {url}")
                return found.strip()
                
            return None
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return None
        finally:
            await browser.close()


def parse_numeric_value(text: str) -> Optional[float]:
    """
    Extracts the first number found in a string (e.g., '1.250,50 TL' -> 1250.50).
    """
    if not text:
        return None
    
    # Remove thousand separators and replace decimal comma with dot (Turkish/European style)
    # This is a bit tricky, let's try a heuristic
    cleaned = text.replace('.', '').replace(',', '.')
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", cleaned)
    
    if numbers:
        return float(numbers[0])
    return None

if __name__ == "__main__":
    # Test
    async def test():
        val = await fetch_element_value("https://www.google.com", "body")
        print(f"Test value: {val[:50]}...")
    
    asyncio.run(test())
