"""
Simple test script for intake conversation
Tests the chat endpoint with OpenAI integration
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"


def test_intake_flow():
    """Test complete intake flow"""
    
    print("🚀 Testing PsychNow Intake Flow\n")
    print("=" * 60)
    
    # Step 1: Start session
    print("\n📝 Step 1: Starting intake session...")
    response = requests.post(f"{BASE_URL}/intake/start", json={"patient_id": None})
    
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.text}")
        return
    
    session_data = response.json()
    session_token = session_data["session_token"]
    print(f"✅ Session created: {session_token}\n")
    
    # Step 2: Get initial greeting
    print("💬 Step 2: Getting Ava's greeting...")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/intake/chat",
        json={"session_token": session_token, "prompt": ""},
        stream=True
    )
    
    if response.status_code != 200:
        print(f"❌ Chat failed: {response.text}")
        return
    
    # Parse SSE stream
    full_greeting = ""
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]  # Remove 'data: ' prefix
                try:
                    message = json.loads(data_str)
                    content = message.get('content', '')
                    full_greeting += content
                    print(content, end='', flush=True)
                except json.JSONDecodeError:
                    pass
    
    print("\n" + "-" * 60)
    print(f"✅ Greeting received ({len(full_greeting)} characters)\n")
    
    # Step 3: Send patient response
    print("💬 Step 3: Patient responds...")
    print("-" * 60)
    print("Patient: I've been feeling really down and anxious lately. It's been hard to sleep and concentrate at work.")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/intake/chat",
        json={
            "session_token": session_token,
            "prompt": "I've been feeling really down and anxious lately. It's been hard to sleep and concentrate at work."
        },
        stream=True
    )
    
    print("\nAva: ", end='')
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    message = json.loads(line_str[6:])
                    print(message.get('content', ''), end='', flush=True)
                except:
                    pass
    
    print("\n" + "-" * 60)
    print("✅ Conversation is working!\n")
    
    # Step 4: Check session state
    print("📊 Step 4: Checking session state...")
    response = requests.get(f"{BASE_URL}/intake/session/{session_token}")
    
    if response.status_code == 200:
        session = response.json()
        print(f"✅ Session status: {session.get('status')}")
        print(f"✅ Current phase: {session.get('current_phase')}")
        print(f"✅ Messages: {len(session.get('conversation_history', []))}")
        print(f"✅ Symptoms detected: {session.get('symptoms_detected', {})}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETE!")
    print("\nNext Steps:")
    print("1. Continue conversation with more messages")
    print("2. Administer screeners (PHQ-9, GAD-7)")
    print("3. Type ':finish' to generate report")
    print("\nSession Token (save this):", session_token)


if __name__ == "__main__":
    try:
        test_intake_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Is it running on port 8000?")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

