import subprocess
import os
import tempfile

# Text to speak in Persian
text = "سلام من استیو هستم"
print(f"Speaking: {text}")

# Output file path
output_file = "/workspace/persian_speech.wav"

# Use espeak directly to generate Persian speech
try:
    # Generate speech with Persian voice and save to file
    cmd = [
        'espeak', 
        '-v', 'fa',  # Use Persian voice
        '-s', '150',  # Speech rate
        '-w', output_file,  # Write to file
        text
    ]
    
    print("Generating speech with espeak...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Audio saved successfully to: {output_file}")
        
        # Also speak it directly
        speak_cmd = ['espeak', '-v', 'fa', '-s', '150', text]
        print("Speaking text...")
        subprocess.run(speak_cmd)
        
        # Check if file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"Audio file size: {file_size} bytes")
            
            # Try to play the audio file
            print("Attempting to play audio file...")
            
            # Try different audio players
            players = [
                ['aplay', output_file],
                ['paplay', output_file], 
                ['ffplay', '-nodisp', '-autoexit', output_file],
                ['play', output_file]
            ]
            
            played = False
            for player_cmd in players:
                try:
                    # Check if player exists
                    check_cmd = ['which', player_cmd[0]]
                    if subprocess.run(check_cmd, capture_output=True).returncode == 0:
                        print(f"Playing with {player_cmd[0]}...")
                        play_result = subprocess.run(player_cmd, capture_output=True)
                        if play_result.returncode == 0:
                            print("Audio played successfully!")
                            played = True
                            break
                        else:
                            print(f"Failed to play with {player_cmd[0]}")
                except Exception as e:
                    print(f"Error trying {player_cmd[0]}: {e}")
            
            if not played:
                print("Could not play audio file, but it was saved successfully.")
        else:
            print("Error: Audio file was not created")
    else:
        print(f"Error generating speech: {result.stderr}")
        
except Exception as e:
    print(f"Error: {e}")

print("Voice test completed!")