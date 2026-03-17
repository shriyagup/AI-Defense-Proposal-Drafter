from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape_solicitation(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        links = []
        for a in soup.find_all("a", href=True):
            links.append(
                {
                    "text": a.get_text(strip=True),
                    "url": a["href"],
                }
            )

        return {
            "raw_page_text": text,
            "preview_text": text[:8000],
            "links": links[:20],
        }
    except Exception as e:
        return {"error": str(e)}
