"""
Automated Conversation Tester for Ava
Tests the full intake flow including screeners and report generation
"""
import asyncio
import httpx
import json
import time
from typing import Dict, List, Optional

# API Configuration
API_BASE = "http://127.0.0.1:8000"

# Test conversation scenarios
SCENARIOS = {
    "depression": {
        "name": "John Doe",
        "chief_complaint": "feeling depressed",
        "duration": "about 3 weeks",
        "severity": "moderate",
        "sleep": "having trouble sleeping",
        "appetite": "eating less than usual",
        "energy": "very low energy",
        "concentration": "hard to focus",
        "phq9_answers": [2, 2, 1, 2, 1, 1, 0, 0, 0],  # Moderate depression
        "cssrs_answers": ["No"],  # No suicidal ideation
        "gad7_answers": [1, 1, 0, 1, 1, 0, 1],  # Mild anxiety
    },
    "anxiety": {
        "name": "Jane Smith",
        "chief_complaint": "feeling very anxious",
        "duration": "2 months",
        "severity": "severe",
        "worry": "worry about everything",
        "restless": "can't sit still",
        "sleep": "trouble falling asleep",
        "concentration": "mind goes blank",
        "phq9_answers": [1, 1, 0, 1, 0, 0, 0, 0, 0],  # Mild depression
        "gad7_answers": [3, 3, 2, 3, 2, 2, 2],  # Moderate-severe anxiety
        "cssrs_answers": ["No"],
    },
    "high_risk": {
        "name": "Alex Johnson",
        "chief_complaint": "feeling hopeless",
        "duration": "1 month",
        "severity": "very severe",
        "sleep": "barely sleeping",
        "appetite": "no appetite",
        "energy": "no energy",
        "thoughts": "thoughts of harming myself",
        "phq9_answers": [3, 3, 3, 3, 3, 2, 2, 2, 2],  # Severe depression
        "cssrs_answers": ["Yes", "Yes", "No"],  # Suicidal ideation present
        "gad7_answers": [3, 3, 3, 2, 2, 2, 2],  # Severe anxiety
    }
}


class AvaConversationTester:
    """Automated tester for Ava conversations"""
    
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
        self.session_token: Optional[str] = None
        self.conversation_log: List[Dict] = []
        
    async def start_session(self, user_name: Optional[str] = None) -> str:
        """Start a new intake session"""
        print("\n🚀 Starting new intake session...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_base}/api/v1/intake/start",
                json={
                    "patient_id": f"test_user_{int(time.time())}",
                    "user_name": user_name
                }
            )
            response.raise_for_status()
            data = response.json()
            self.session_token = data["session_token"]
            print(f"✅ Session started: {self.session_token[:8]}...")
            return self.session_token
    
    async def send_message(self, message: str, expect_options: bool = False) -> Dict:
        """Send a message to Ava and get response"""
        if not self.session_token:
            raise ValueError("No active session. Call start_session() first.")
        
        print(f"\n👤 You: {message}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.api_base}/api/v1/intake/chat",
                json={
                    "session_token": self.session_token,
                    "prompt": message
                }
            ) as response:
                response.raise_for_status()
                
                full_response = ""
                options = None
                pdf_report = None
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if data.get("content"):
                                content = data["content"]
                                
                                # Skip technical messages
                                if content.startswith("REPORT_ID:"):
                                    continue
                                
                                full_response += content
                            
                            if data.get("options"):
                                options = data["options"]
                            
                            if data.get("pdf_report"):
                                pdf_report = data["pdf_report"]
                        except json.JSONDecodeError:
                            pass
                
                print(f"🤖 Ava: {full_response[:200]}{'...' if len(full_response) > 200 else ''}")
                
                if options:
                    print(f"   Options: {[opt['label'] for opt in options]}")
                
                self.conversation_log.append({
                    "user": message,
                    "ava": full_response,
                    "options": options,
                    "has_pdf": pdf_report is not None
                })
                
                return {
                    "response": full_response,
                    "options": options,
                    "pdf_report": pdf_report
                }
    
    async def get_initial_greeting(self) -> str:
        """Get Ava's initial greeting"""
        print("\n🤖 Getting initial greeting...")
        result = await self.send_message("")
        return result["response"]
    
    async def click_option(self, option_value: str) -> Dict:
        """Click a button option"""
        print(f"\n🖱️  Clicking option: {option_value}")
        return await self.send_message(option_value)
    
    async def run_scenario(self, scenario_name: str):
        """Run a full test scenario"""
        if scenario_name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(SCENARIOS.keys())}")
        
        scenario = SCENARIOS[scenario_name]
        print(f"\n{'='*60}")
        print(f"🎬 Running scenario: {scenario_name.upper()}")
        print(f"{'='*60}")
        
        # Start session
        await self.start_session(user_name=scenario.get("name"))
        
        # Get greeting
        greeting = await self.get_initial_greeting()
        
        # If greeting asks for name, provide it
        if "name" in greeting.lower() and "What name" in greeting:
            await self.send_message(scenario["name"])
            await asyncio.sleep(1)
        
        # Answer "What brings you here?"
        await self.send_message(scenario["chief_complaint"])
        await asyncio.sleep(1)
        
        # Answer follow-up questions
        if "duration" in scenario:
            await self.send_message(scenario["duration"])
            await asyncio.sleep(1)
        
        if "severity" in scenario:
            await self.send_message(scenario["severity"])
            await asyncio.sleep(1)
        
        # Answer symptom questions
        for key in ["sleep", "appetite", "energy", "concentration", "worry", "restless", "thoughts"]:
            if key in scenario:
                await self.send_message(scenario[key])
                await asyncio.sleep(1)
        
        # Wait for screener introduction
        print("\n⏳ Waiting for screener introduction...")
        await self.send_message("yes")  # Ready to begin screeners
        await asyncio.sleep(1)
        
        # PHQ-9 (if present)
        if "phq9_answers" in scenario:
            print("\n📋 Completing PHQ-9...")
            for i, answer in enumerate(scenario["phq9_answers"], 1):
                options_map = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
                await self.click_option(options_map[answer])
                await asyncio.sleep(0.5)
        
        # C-SSRS (if present)
        if "cssrs_answers" in scenario:
            print("\n🚨 Completing C-SSRS...")
            for answer in scenario["cssrs_answers"]:
                await self.click_option(answer)
                await asyncio.sleep(0.5)
        
        # GAD-7 (if present)
        if "gad7_answers" in scenario:
            print("\n😰 Completing GAD-7...")
            for i, answer in enumerate(scenario["gad7_answers"], 1):
                options_map = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
                await self.click_option(options_map[answer])
                await asyncio.sleep(0.5)
        
        # Finish assessment
        print("\n🏁 Finishing assessment...")
        result = await self.send_message(":finish")
        
        if result.get("pdf_report"):
            print("\n✅ PDF Report Generated!")
        else:
            print("\n⚠️  No PDF report received")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Conversation Summary")
        print(f"{'='*60}")
        print(f"Total exchanges: {len(self.conversation_log)}")
        print(f"Scenario: {scenario_name}")
        print(f"✅ Test complete!")


async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Ava conversation flows")
    parser.add_argument(
        "scenario",
        nargs="?",
        default="depression",
        choices=list(SCENARIOS.keys()),
        help="Scenario to run"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios"
    )
    
    args = parser.parse_args()
    
    if args.all:
        print("\n🎬 Running ALL scenarios...\n")
        for scenario_name in SCENARIOS.keys():
            tester = AvaConversationTester()
            try:
                await tester.run_scenario(scenario_name)
                await asyncio.sleep(2)  # Pause between scenarios
            except Exception as e:
                print(f"\n❌ Error in scenario '{scenario_name}': {e}")
                import traceback
                traceback.print_exc()
    else:
        tester = AvaConversationTester()
        try:
            await tester.run_scenario(args.scenario)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

