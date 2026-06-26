
import asyncio
from playwright.async_api import async_playwright
import os

async def verify_flows():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # Get absolute path to purebite.html
        path = os.path.abspath("purebite.html")
        await page.goto(f"file://{path}")

        print("--- VERIFYING SUBSCRIPTION FLOW (WEEKLY SIANG) ---")
        # 1. Click Susun Piringmu
        await page.click("button:has-text('Susun Piringmu')")

        # 2. Select Mingguan
        await page.click("h3:has-text('Mingguan')", force=True)
        await asyncio.sleep(1) # Wait for modal transition

        # 3. Select Paket Siang
        await page.click("h3:has-text('Paket Siang')", force=True)
        await asyncio.sleep(1) # Wait for view transition

        # 4. Click Lanjut Susun Piring Hari Pertama
        await page.click("button:has-text('Lanjut Susun Piring Hari Pertama')", force=True)
        await asyncio.sleep(1)

        # 5. Check initial price in builder (should be 250.000)
        price_text = await page.inner_text("#stat-price")
        print(f"Initial Subscription Price: Rp{price_text}")
        if "250.000" not in price_text:
            print(f"FAILED: Expected 250.000, got {price_text}")

        # 6. Add items (Nasi Merah 15k, Ayam Sambal 35k, Brokoli 15k = 65k total if calculated by item)
        await page.click("li:has-text('Nasi Merah')", force=True)
        await page.click("li:has-text('Ayam Sambal')", force=True)
        await page.click("li:has-text('Brokoli')", force=True)
        await page.click("li:has-text('Telur')", force=True) # +12k = 77k

        # 7. Check price again (should STILL be 250.000)
        price_text_after = await page.inner_text("#stat-price")
        print(f"Subscription Price after items: Rp{price_text_after}")
        if "250.000" not in price_text_after:
            print(f"FAILED: Expected 250.000, got {price_text_after}")

        # 8. Go to delivery
        await page.click("button:has-text('Lanjut ke Pengiriman')", force=True)
        await asyncio.sleep(1)

        # 9. Fill details
        await page.fill("#zip-input", "12345")
        await page.fill("#email-input", "test@example.com")
        await page.click("button:has-text('Verifikasi & Bayar')", force=True)
        await asyncio.sleep(1)

        # 10. Check receipt metadata and price
        receipt_commitment = await page.inner_text("#receipt-commitment")
        receipt_package = await page.inner_text("#receipt-package")
        receipt_subtotal = await page.inner_text("#receipt-subtotal")
        receipt_discount = await page.inner_text("#receipt-discount-amount")
        receipt_total = await page.inner_text("#receipt-total")

        print(f"Receipt Commitment: {receipt_commitment}")
        print(f"Receipt Package: {receipt_package}")
        print(f"Receipt Subtotal: {receipt_subtotal}")
        print(f"Receipt Discount: {receipt_discount}")
        print(f"Receipt Total: {receipt_total}")

        # Subtotal 250k, Discount 10% (25k), Total 225k
        if "250.000" not in receipt_subtotal: print("FAILED subtotal")
        if "25.000" not in receipt_discount: print("FAILED discount")
        if "225.000" not in receipt_total: print("FAILED total")

        await page.screenshot(path="verification_subscription.png")

        # --- VERIFYING ONE-TIME FLOW ---
        print("\n--- VERIFYING ONE-TIME FLOW ---")
        await page.goto(f"file://{path}") # Reset to home

        # 1. Click Susun Piringmu
        await page.click("button:has-text('Susun Piringmu')")

        # 2. Select Satu Kali
        await page.click("h3:has-text('Satu Kali')", force=True)
        await asyncio.sleep(1)

        # 3. Select Paket Siang
        await page.click("h3:has-text('Paket Siang')", force=True)
        await asyncio.sleep(1)

        # Initial price should be 0 (no items)
        price_text_one = await page.inner_text("#stat-price")
        print(f"Initial One-time Price: Rp{price_text_one}")

        # Add items (Nasi Merah 15k, Ayam Sambal 35k, Brokoli 15k = 65k)
        await page.click("li:has-text('Nasi Merah')", force=True)
        await page.click("li:has-text('Ayam Sambal')", force=True)
        await page.click("li:has-text('Brokoli')", force=True)

        price_text_one_after = await page.inner_text("#stat-price")
        print(f"One-time Price after items: Rp{price_text_one_after}")
        if "65.000" not in price_text_one_after:
            print(f"FAILED: Expected 65.000, got {price_text_one_after}")

        # Go to delivery
        await page.click("button:has-text('Lanjut ke Pengiriman')", force=True)
        await asyncio.sleep(1)
        await page.fill("#zip-input", "12345")
        await page.fill("#email-input", "test@example.com")
        await page.click("button:has-text('Verifikasi & Bayar')", force=True)
        await asyncio.sleep(1)

        # Check receipt for One-time
        receipt_subtotal_one = await page.inner_text("#receipt-subtotal")
        receipt_total_one = await page.inner_text("#receipt-total")
        print(f"One-time Receipt Subtotal: {receipt_subtotal_one}")
        print(f"One-time Receipt Total: {receipt_total_one}")

        if "65.000" not in receipt_subtotal_one: print("FAILED one-time subtotal")

        await page.screenshot(path="verification_onetime.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_flows())
