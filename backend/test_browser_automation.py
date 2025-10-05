"""
Browser Automation Test for PsychNow Frontend
Tests the actual UI at http://localhost:3000
Requires: pip install playwright
Then run: playwright install
"""
import asyncio
import time
from playwright.async_api import async_playwright, Page, expect

FRONTEND_URL = "http://localhost:3000"

class BrowserTester:
    """Automated browser testing for PsychNow"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.page = None
        
    async def setup(self):
        """Start browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        await self.page.goto(FRONTEND_URL)
        print(f"🌐 Opened browser at {FRONTEND_URL}")
        
    async def teardown(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            print("🔒 Browser closed")
    
    async def wait_for_ava_response(self, timeout: int = 10000):
        """Wait for Ava to finish responding"""
        # Wait for the typing indicator to disappear
        await self.page.wait_for_selector('text="Ava is thinking..."', state="hidden", timeout=timeout)
        await asyncio.sleep(0.5)  # Small buffer
    
    async def type_message(self, message: str):
        """Type and send a message to Ava"""
        print(f"👤 Typing: {message}")
        
        # Find input field and type
        input_field = self.page.locator('input[placeholder*="Type your response"]')
        await input_field.fill(message)
        
        # Click Send button
        send_button = self.page.locator('button:has-text("Send")')
        await send_button.click()
        
        # Wait for Ava's response
        await self.wait_for_ava_response()
        await asyncio.sleep(1)
    
    async def click_button_option(self, option_text: str):
        """Click a button option (like screener answers)"""
        print(f"🖱️  Clicking button: {option_text}")
        button = self.page.locator(f'button:has-text("{option_text}")')
        await button.click()
        await self.wait_for_ava_response()
        await asyncio.sleep(0.5)
    
    async def take_screenshot(self, name: str):
        """Take a screenshot"""
        filename = f"screenshot_{name}_{int(time.time())}.png"
        await self.page.screenshot(path=filename)
        print(f"📸 Screenshot saved: {filename}")
    
    async def get_latest_ava_message(self) -> str:
        """Get Ava's latest message from the chat"""
        # Get all chat bubbles
        chat_bubbles = self.page.locator('[class*="bg-blue-50"]')
        count = await chat_bubbles.count()
        if count > 0:
            last_bubble = chat_bubbles.nth(count - 1)
            text = await last_bubble.inner_text()
            return text.strip()
        return ""
    
    async def has_button_options(self) -> bool:
        """Check if there are button options available"""
        buttons = self.page.locator('button[class*="bg-white border"]')
        count = await buttons.count()
        return count > 0
    
    async def get_button_options(self) -> list:
        """Get all available button options"""
        buttons = self.page.locator('button[class*="bg-white border"]')
        count = await buttons.count()
        options = []
        for i in range(count):
            text = await buttons.nth(i).inner_text()
            options.append(text.strip())
        return options
    
    async def smart_response(self, question: str) -> str:
        """Generate appropriate response based on question type"""
        question_lower = question.lower()
        
        # Name question
        if "name" in question_lower and "what" in question_lower:
            return "John Doe"
        
        # Chief complaint
        if "bring" in question_lower or "help" in question_lower:
            return "I've been feeling really depressed and anxious lately"
        
        # Duration questions
        if "how long" in question_lower or "when did" in question_lower:
            return "About 3 weeks"
        
        # Severity/intensity
        if "severity" in question_lower or "intense" in question_lower or "scale" in question_lower:
            return "It's pretty moderate, maybe 6 out of 10"
        
        # Sleep questions
        if "sleep" in question_lower:
            return "I've been having trouble falling asleep and I wake up a lot during the night"
        
        # Appetite questions
        if "appetite" in question_lower or "eating" in question_lower:
            return "I'm eating less than usual and have lost some weight"
        
        # Energy questions
        if "energy" in question_lower or "tired" in question_lower or "fatigue" in question_lower:
            return "My energy is very low, I feel exhausted most of the time"
        
        # Concentration questions
        if "concentration" in question_lower or "focus" in question_lower:
            return "It's hard to concentrate on anything"
        
        # Work/daily life impact
        if "work" in question_lower or "job" in question_lower:
            return "It's affecting my work performance, I'm having trouble completing tasks"
        
        # Relationships impact
        if "relationship" in question_lower or "friends" in question_lower or "family" in question_lower:
            return "I've been isolating myself from friends and family"
        
        # Self-care impact
        if "self-care" in question_lower or "hygiene" in question_lower:
            return "I'm struggling with basic self-care"
        
        # Medical conditions
        if "medical" in question_lower or "health condition" in question_lower:
            return "No major medical conditions"
        
        # Medication questions
        if "medication" in question_lower or "medicine" in question_lower:
            return "Not currently taking any medications"
        
        # Treatment history
        if "treatment" in question_lower or "therapy" in question_lower or "counseling" in question_lower:
            return "I haven't tried therapy before"
        
        # Substance use
        if "alcohol" in question_lower or "drug" in question_lower or "substance" in question_lower:
            return "Occasionally drink but nothing excessive"
        
        # Family history
        if "family history" in question_lower:
            return "My mother struggled with depression"
        
        # Living situation
        if "living" in question_lower or "housing" in question_lower:
            return "I live alone in an apartment"
        
        # Support system
        if "support" in question_lower:
            return "I have some friends but haven't been reaching out to them"
        
        # Ready for screeners
        if "ready" in question_lower or "begin" in question_lower:
            return "yes"
        
        # Default response
        return "yes"
    
    async def test_anonymous_assessment(self):
        """Test full anonymous assessment flow with intelligent responses"""
        print("\n" + "="*60)
        print("🎬 TEST: Full Automated Assessment Flow")
        print("="*60 + "\n")
        
        # Navigate to intake
        print("📍 Navigating to /patient-intake")
        await self.page.goto(f"{FRONTEND_URL}/patient-intake")
        await asyncio.sleep(3)
        
        # Wait for Ava's greeting
        await self.wait_for_ava_response(timeout=15000)
        await self.take_screenshot("01_greeting")
        
        question_count = 0
        screenshot_count = 2
        max_questions = 100  # Safety limit
        
        while question_count < max_questions:
            question_count += 1
            
            # Check if assessment is complete
            page_content = await self.page.content()
            if "Assessment complete" in page_content or "Download PDF" in page_content:
                print("\n✅ Assessment completed!")
                await self.take_screenshot(f"{screenshot_count:02d}_report_generated")
                break
            
            # Check for button options first
            if await self.has_button_options():
                options = await self.get_button_options()
                print(f"\n🎯 Button options detected: {options}")
                
                # Handle screener options
                if any(opt in options for opt in ["Not at all", "Several days", "More than half the days", "Nearly every day"]):
                    print("📋 Completing screener question...")
                    # Choose "Several days" for moderate symptoms
                    if "Several days" in options:
                        await self.click_button_option("Several days")
                    else:
                        await self.click_button_option(options[1] if len(options) > 1 else options[0])
                
                elif any(opt in options for opt in ["Yes", "No"]):
                    print("🚨 Safety question detected...")
                    # Answer "No" to safety questions
                    await self.click_button_option("No")
                
                else:
                    # Click first option for other multiple choice
                    await self.click_button_option(options[0])
                
                await self.take_screenshot(f"{screenshot_count:02d}_after_option")
                screenshot_count += 1
                continue
            
            # Get Ava's latest question
            ava_message = await self.get_latest_ava_message()
            if not ava_message:
                await asyncio.sleep(1)
                continue
            
            print(f"\n🤖 Ava: {ava_message[:100]}...")
            
            # Check if it's asking for text input
            input_field = self.page.locator('input[placeholder*="Type your response"]')
            if await input_field.count() > 0 and await input_field.is_enabled():
                response = await self.smart_response(ava_message)
                print(f"👤 Response: {response}")
                await self.type_message(response)
                await self.take_screenshot(f"{screenshot_count:02d}_after_response")
                screenshot_count += 1
            else:
                # Wait a bit for Ava to continue
                await asyncio.sleep(2)
        
        if question_count >= max_questions:
            print(f"\n⚠️  Reached max question limit ({max_questions})")
        
        # Check for PDF download button
        pdf_button = self.page.locator('button:has-text("Download PDF")')
        if await pdf_button.count() > 0:
            print("✅ PDF Download button found!")
            await self.take_screenshot("99_final_pdf_button")
        else:
            print("⚠️  PDF Download button not found - trying :finish command")
            await self.type_message(":finish")
            await asyncio.sleep(10)
            await self.take_screenshot("99_after_finish_command")
        
        print("\n✅ Assessment flow complete!")
    
    async def test_authenticated_assessment(self):
        """Test authenticated user flow"""
        print("\n" + "="*60)
        print("🎬 TEST: Authenticated User Assessment")
        print("="*60 + "\n")
        
        # Go to sign-in (assuming we need to sign in first)
        print("📍 Note: This test requires manual sign-in setup")
        print("   For now, testing anonymous flow instead")
        await self.test_anonymous_assessment()
    
    async def test_pause_resume(self):
        """Test pause and resume functionality"""
        print("\n" + "="*60)
        print("🎬 TEST: Pause and Resume Flow")
        print("="*60 + "\n")
        
        # Start assessment
        await self.page.goto(f"{FRONTEND_URL}/patient-intake")
        await asyncio.sleep(2)
        await self.wait_for_ava_response(timeout=15000)
        
        # Provide name
        await self.type_message("Test User")
        await self.type_message("I need help with anxiety")
        
        # Pause the session
        print("\n⏸️  Pausing session...")
        pause_button = self.page.locator('button:has-text("Take a Break")')
        await pause_button.click()
        await asyncio.sleep(2)
        await self.take_screenshot("10_paused")
        
        # Go to dashboard
        dashboard_button = self.page.locator('button:has-text("Dashboard")')
        await dashboard_button.click()
        await asyncio.sleep(2)
        await self.take_screenshot("11_dashboard_with_paused")
        
        # Resume assessment
        print("\n▶️  Resuming assessment...")
        resume_button = self.page.locator('button:has-text("Resume Assessment")')
        if await resume_button.count() > 0:
            await resume_button.click()
            await asyncio.sleep(3)
            await self.take_screenshot("12_resumed")
            print("✅ Resume successful!")
        else:
            print("⚠️  Resume button not found")


async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Browser automation tests for PsychNow")
    parser.add_argument(
        "--test",
        choices=["anonymous", "authenticated", "pause", "all"],
        default="anonymous",
        help="Which test to run"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no window)"
    )
    
    args = parser.parse_args()
    
    tester = BrowserTester(headless=args.headless)
    
    try:
        await tester.setup()
        
        if args.test == "anonymous" or args.test == "all":
            await tester.test_anonymous_assessment()
        
        if args.test == "pause" or args.test == "all":
            await tester.test_pause_resume()
        
        if args.test == "authenticated":
            await tester.test_authenticated_assessment()
        
        # Keep browser open for a moment to see results
        if not args.headless:
            print("\n⏳ Keeping browser open for 10 seconds...")
            await asyncio.sleep(10)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.teardown()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║       PsychNow Browser Automation Tester                  ║
║                                                            ║
║  Prerequisites:                                            ║
║    1. pip install playwright                               ║
║    2. playwright install                                   ║
║    3. Frontend running on http://localhost:3000            ║
║    4. Backend running on http://localhost:8000             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())

