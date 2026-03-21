from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Test if .or_ works
        try:
            loc1 = page.locator("div")
            loc2 = page.get_by_text("hello")
            combined = loc1.or_(loc2)
            print("✅ combined.or_ absolute works")
        except AttributeError as e:
            print(f"❌ combined.or_ failed: {e}")
            
        # Test if or_ operator works
        try:
            combined = page.locator("div") | page.get_by_text("hello")
            print("✅ | operator works")
        except Exception as e:
             print(f"❌ | operator failed: {e}")

        browser.close()

test()
