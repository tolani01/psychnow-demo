"""
Manual Interactive Intake Test
Allows you to have a real conversation with Ava and test the full intake flow
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"


class Colors:
    """ANSI color codes for terminal"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")


def send_message(session_token: str, prompt: str) -> bool:
    """
    Send a message to Ava and print response
    
    Returns:
        True if successful, False if error
    """
    try:
        response = requests.post(
            f"{BASE_URL}/intake/chat",
            json={"session_token": session_token, "prompt": prompt},
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print_colored(f"\n❌ Error: {response.text}", Colors.RED)
            return False
        
        print_colored("\nAva: ", Colors.BLUE, end='')
        
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
                        
                        # Check if this is the final report
                        if message.get('done'):
                            print_colored("\n\n✅ REPORT GENERATED!", Colors.GREEN)
                            # Pretty print the JSON report
                            try:
                                report = json.loads(full_response)
                                print_colored("\n📋 INTAKE REPORT:", Colors.BOLD)
                                print(json.dumps(report, indent=2))
                            except:
                                pass
                    except:
                        pass
        
        print("\n")
        return True
    
    except requests.exceptions.Timeout:
        print_colored("\n❌ Request timed out. Ava might be thinking too long.", Colors.RED)
        return False
    except requests.exceptions.ConnectionError:
        print_colored("\n❌ Cannot connect to server. Is it running on port 8000?", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", Colors.RED)
        return False


def main():
    """Main interactive intake session"""
    print_colored("="*70, Colors.BOLD)
    print_colored("🧠 PsychNow - Manual Intake Test", Colors.BOLD)
    print_colored("="*70, Colors.BOLD)
    
    print("\nThis will guide you through a complete intake conversation with Ava.")
    print("You'll play the role of a patient and respond to Ava's questions.")
    print("\nCommands:")
    print("  - Type your responses naturally")
    print("  - Type 'quit' to exit")
    print("  - Type ':finish' when ready to generate report")
    print("\n" + "-"*70 + "\n")
    
    # Start session
    print_colored("📝 Starting new intake session...", Colors.YELLOW)
    response = requests.post(f"{BASE_URL}/intake/start", json={"patient_id": None})
    
    if response.status_code != 200:
        print_colored(f"❌ Failed to start session: {response.text}", Colors.RED)
        return
    
    session_data = response.json()
    session_token = session_data["session_token"]
    
    print_colored(f"✅ Session created: {session_token[:8]}...\n", Colors.GREEN)
    
    # Get initial greeting
    if not send_message(session_token, ""):
        return
    
    # Interactive loop
    message_count = 0
    while True:
        # Get user input
        print_colored("\nYou: ", Colors.GREEN, end='')
        try:
            user_input = input().strip()
        except KeyboardInterrupt:
            print_colored("\n\n⏸️  Intake paused. Session saved.", Colors.YELLOW)
            print(f"Session token: {session_token}")
            print("To resume later, use this token with the API.")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print_colored("\n👋 Ending intake session.", Colors.YELLOW)
            print(f"Session token: {session_token}")
            break
        
        # Send message to Ava
        if not send_message(session_token, user_input):
            print_colored("Error sending message. Try again or type 'quit'.", Colors.RED)
            continue
        
        message_count += 1
        
        # Check if report was generated
        if user_input.strip() == ":finish":
            print_colored("\n🎉 Intake complete! Report generated above.", Colors.GREEN)
            break
    
    print("\n" + "="*70)
    print_colored(f"✅ Session complete! Total messages: {message_count}", Colors.GREEN)
    print(f"Session token: {session_token}")
    print("="*70 + "\n")


def print_colored(text, color, end='\n'):
    """Print colored text with optional end character"""
    print(f"{color}{text}{Colors.END}", end=end)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()

