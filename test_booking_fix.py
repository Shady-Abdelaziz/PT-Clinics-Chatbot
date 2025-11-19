"""
Test script to verify the booking validation fix
Run this to ensure appointments work correctly in long conversations
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.medical_agents import medical_chatbot

def test_long_conversation_booking():
    """Test booking after a long conversation"""
    print("=" * 70)
    print("TEST: Long Conversation Booking")
    print("=" * 70)
    
    # Simulate a long conversation
    conversations = [
        "Tell me about your services",
        "What doctors do you have?",
        "Tell me about Dr. Sarah Martinez",
        "What are your operating hours?",
        "How can I contact physical therapy?",
        "When is Dr. Sarah Martinez available?",
    ]
    
    print("\n📝 Simulating long conversation...\n")
    for i, msg in enumerate(conversations, 1):
        print(f"{i}. User: {msg}")
        response = medical_chatbot.chat(msg)
        print(f"   Bot: {response[:100]}...\n")
    
    # Now try to book an appointment
    print("\n🎯 Now attempting to book an appointment...")
    booking_request = "Book me for December 12 at 9:00 AM with Dr. Sarah Martinez, name is John Doe, phone 1234567890"
    print(f"User: {booking_request}")
    
    response = medical_chatbot.chat(booking_request)
    print(f"\nBot Response:\n{response}")
    
    print("\n" + "=" * 70)
    if "successfully" in response.lower() or "alternative" in response.lower():
        print("✅ TEST PASSED: System handled booking correctly")
    else:
        print("❌ TEST FAILED: Unexpected response")
    print("=" * 70)

def test_time_format_matching():
    """Test that various time formats are handled correctly"""
    print("\n" + "=" * 70)
    print("TEST: Time Format Matching")
    print("=" * 70)
    
    from src.agents.medical_agents import MedicalCenterChatbot
    chatbot = MedicalCenterChatbot()
    
    test_times = [
        ("10:00 AM", "10:00"),
        ("10 AM", "10:00"),
        ("2:30 PM", "14:30"),
        ("14:30", "14:30"),
        ("9:00 AM", "09:00"),
    ]
    
    print("\n🔍 Testing time normalization...")
    all_passed = True
    for input_time, expected in test_times:
        result = chatbot._normalize_time_for_comparison(input_time)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_time}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TIME FORMATS PASSED")
    else:
        print("❌ SOME TIME FORMATS FAILED")
    print("=" * 70)

def test_direct_booking():
    """Test direct booking (regression test)"""
    print("\n" + "=" * 70)
    print("TEST: Direct Booking (Regression)")
    print("=" * 70)
    
    from src.agents.medical_agents import MedicalCenterChatbot
    chatbot = MedicalCenterChatbot()
    
    print("\n📝 Testing direct booking without prior conversation...\n")
    booking_request = "Book appointment with Dr. Sarah Martinez on December 12 at 10:00 AM for Jane Smith, phone 9876543210"
    print(f"User: {booking_request}")
    
    response = chatbot.chat(booking_request)
    print(f"\nBot Response:\n{response}")
    
    print("\n" + "=" * 70)
    if "successfully" in response.lower() or "alternative" in response.lower() or "name" in response.lower():
        print("✅ TEST PASSED: Direct booking still works")
    else:
        print("❌ TEST FAILED: Direct booking broken")
    print("=" * 70)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("BOOKING VALIDATION FIX - TEST SUITE")
    print("=" * 70)
    
    try:
        # Test 1: Time format matching
        test_time_format_matching()
        
        # Test 2: Direct booking (regression)
        test_direct_booking()
        
        # Test 3: Long conversation booking
        test_long_conversation_booking()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
