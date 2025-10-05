"""
Full intake test - simulates complete patient conversation
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Replace this with your session token from the previous test
SESSION_TOKEN = "d21a68a6-4cbe-418e-bf1c-e12f3aef12d4"


def send_message(prompt: str):
    """Send a message and print Ava's response"""
    print(f"\n{'='*60}")
    print(f"Patient: {prompt}")
    print(f"{'-'*60}")
    print("Ava: ", end='', flush=True)
    
    response = requests.post(
        f"{BASE_URL}/intake/chat",
        json={"session_token": SESSION_TOKEN, "prompt": prompt},
        stream=True
    )
    
    full_response = ""
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    message = json.loads(line_str[6:])
                    content = message.get('content', '')
                    full_response += content
                    print(content, end='', flush=True)
                except:
                    pass
    
    print(f"\n{'-'*60}")
    return full_response


def main():
    print("🧪 Testing Full Intake Conversation")
    print(f"Session Token: {SESSION_TOKEN}\n")
    
    # Conversation flow
    send_message("You can call me Sarah. I've been struggling for about 3 months now, since my breakup. It started with trouble sleeping but now I feel sad most days.")
    
    time.sleep(1)
    
    send_message("Yes, it's gotten worse. At first it was just sadness, but now I'm anxious too. I worry about everything and can't seem to shut my brain off.")
    
    time.sleep(1)
    
    send_message("I wake up around 3am most nights and can't fall back asleep. During the day I'm exhausted but my mind is racing.")
    
    time.sleep(1)
    
    send_message("My appetite is down, I've lost maybe 10 pounds. And I used to love going to the gym but now I have zero energy or motivation.")
    
    time.sleep(1)
    
    send_message("Sometimes I feel like I'm worthless, like everyone would be better off without me. But I wouldn't actually hurt myself - I have my kids to think about.")
    
    time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Conversation complete!")
    print(f"Session Token: {SESSION_TOKEN}")
    print("\nAva should now recommend administering PHQ-9, GAD-7, and C-SSRS screeners.")
    print("\nTo finish and generate report, you can:")
    print("1. Continue chatting with more responses")
    print("2. Let Ava guide through screeners")
    print("3. Type ':finish' when complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

