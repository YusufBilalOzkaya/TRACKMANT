import asyncio
import os
import sys
from playwright.async_api import async_playwright
import tkinter as tk
from tkinter import simpledialog, messagebox

async def run_picker():
    # URL Al
    root = tk.Tk()
    root.withdraw()
    url = simpledialog.askstring("TRACKMANT Picker", "Enter the link of the page to track:", initialvalue="https://www.google.com")
    
    if not url:
        return

    async with async_playwright() as p:
        print("Playwright başlatılıyor...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        async def on_selected(selector):
            print(f"\n[!] SELECTOR BULUNDU: {selector}")
            root.clipboard_clear()
            root.clipboard_append(selector)
            messagebox.showinfo("SUCCESS!", f"Code copied to clipboard:\n\n{selector}\n\nNow you can paste this code into the CSS Selector field in the web panel.")
            await asyncio.sleep(1)
            await browser.close()

        await page.expose_function("sendSelectorToPython", on_selected)
        
        selection_js = """
        (function() {
            function initTrackmant() {
                if (window.trackmantInitialized) return;
                window.trackmantInitialized = true;

                const style = document.createElement('style');
                style.innerHTML = `
                    .trackmant-highlight { 
                        outline: 4px solid #6366f1 !important; 
                        outline-offset: -4px !important; 
                        background: rgba(99, 102, 241, 0.2) !important; 
                        cursor: crosshair !important; 
                    }
                    #trackmant-toolbar { 
                        position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 999999999; 
                        background: #6366f1; color: white; padding: 12px 24px; border-radius: 50px; 
                        font-weight: bold; font-family: sans-serif; box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
                        border: 2px solid white; pointer-events: none;
                    }
                `;
                document.head.appendChild(style);

                const toolbar = document.createElement('div');
                toolbar.id = 'trackmant-toolbar';
                toolbar.innerText = '➔ CLICK ON THE ELEMENT/VALUE YOU WANT TO TRACK';
                
                const injectToolbar = () => {
                    if (document.body && !document.getElementById('trackmant-toolbar')) {
                        document.body.appendChild(toolbar);
                    } else { setTimeout(injectToolbar, 100); }
                };
                injectToolbar();

                function getUniqueSelector(el) {
                    if (!(el instanceof Element)) return '';
                    
                    // Rastgele görünen veya çok uzun olan dinamik sınıfları ele (Hepsiburada gibi siteler için)
                    function isBadClass(c) { 
                        return c.length > 20 || /\\\\d/.test(c) || ['hover', 'active', 'onetrust'].some(kw => c.includes(kw));
                    }

                    // 1. Kararlı data öznitelikleri (Hepsiburada ve modern sitelerin can damarı)
                    const stableAttrs = ['data-test-id', 'data-test', 'data-field', 'data-realtime', 'data-price'];
                    for (let attr of stableAttrs) {
                        let found = el.closest('[' + attr + ']');
                        if (found) return '[' + attr + '="' + found.getAttribute(attr) + '"]';
                    }

                    // 2. Kararlı e-ticaret sınıfları
                    const ecommClasses = ['prc-dsc', 'instrument-price_last', 'last-price', 'product-price', 'current-price', 'price'];
                    for (let c of ecommClasses) {
                       let found = el.closest('.' + c);
                       if (found && !isBadClass(c)) return '.' + c;
                    }

                    // 3. ID (Rastgele rakam içermiyorsa)
                    if (el.id && !/\\\\d/.test(el.id) && !['onetrust', 'cookie', 'trackmant'].some(s => el.id.includes(s))) {
                        return '#' + CSS.escape(el.id);
                    }

                    // 4. Akıllı Hiyerarşi
                    var path = [];
                    while (el && el.nodeType === Node.ELEMENT_NODE) {
                        var sel = el.nodeName.toLowerCase();
                        if (el.className && typeof el.className === "string") {
                            let classes = el.className.split(/\\\\s+/).filter(c => c.length > 2 && !isBadClass(c));
                            if (classes.length > 0) {
                                sel += '.' + CSS.escape(classes[0]);
                                if (path.length > 0) { path.unshift(sel); break; }
                            }
                        }
                        var sib = el, nth = 1;
                        while (sib = sib.previousElementSibling) { if (sib.nodeName.toLowerCase() === el.nodeName.toLowerCase()) nth++; }
                        if (nth !== 1) sel += ":nth-of-type(" + nth + ")";
                        path.unshift(sel);
                        el = el.parentNode;
                        if (sel === 'body' || path.length > 3) break;
                    }
                    return path.join(" > ");
                }

                document.body.addEventListener('mouseover', e => e.target.classList.add('trackmant-highlight'), true);
                document.body.addEventListener('mouseout', e => e.target.classList.remove('trackmant-highlight'), true);
                
                let startTime = Date.now();
                document.body.addEventListener('click', e => {
                    // Sadece GERÇEK kullanıcı tıklamalarını kabul et (isTrusted)
                    // Ve sayfa açıldıktan sonra ilk 1 saniye tıklamaları görmezden gel (reklamlar için)
                    if (!e.isTrusted || (Date.now() - startTime < 1000)) return;
                    
                    e.preventDefault(); e.stopPropagation();
                    
                    let selector = getUniqueSelector(e.target);
                    
                    // Reklam veya Toolbar tıklamalarını engelle
                    if (selector.includes('trackmant') || selector.includes('trc_') || selector.includes('taboola')) {
                        console.log("Ad or system element blocked.");
                        return;
                    }
                    
                    document.querySelectorAll('.trackmant-highlight').forEach(el => el.classList.remove('trackmant-highlight'));
                    window.sendSelectorToPython(selector);
                }, true);
            }

            if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', initTrackmant); }
            else { initTrackmant(); }
            new MutationObserver(() => { if (!document.getElementById('trackmant-toolbar')) initTrackmant(); })
                .observe(document.documentElement, { childList: true, subtree: true });
        })();
        """
        await page.add_init_script(selection_js)
        
        print(f"Opening site: {url}")
        try:
            await page.goto(url, timeout=45000, wait_until="domcontentloaded")
        except Exception as e:
            print(f"Error: {e}")
        
        try:
            while True:
                await asyncio.sleep(1)
                if not browser.is_connected(): break
        except: pass

if __name__ == "__main__":
    asyncio.run(run_picker())
