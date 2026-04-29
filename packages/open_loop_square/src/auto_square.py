import time
import subprocess

# ===============================
# SIT310 Task 4.1P - Open Loop Square
# Student: Naman Jain
# ===============================

ROBOT = "mybota002822"

# Function to send key command to Duckiebot
def send_command(key, duration):
    print(f"Sending command: {key} for {duration} seconds")

    # Start keyboard control process
    process = subprocess.Popen(
        ["dts", "duckiebot", "keyboard_control", ROBOT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        start_time = time.time()

        while time.time() - start_time < duration:
            process.stdin.write(key)
            process.stdin.flush()
            time.sleep(0.2)

    finally:
        process.terminate()
        time.sleep(1)


# ===============================
# TUNE THESE VALUES
# ===============================

FORWARD_TIME = 3.0   # adjust for 1 meter
TURN_TIME = 1.0      # adjust for 90 degree


# ===============================
# MAIN LOGIC
# ===============================

print("Starting Open Loop Square...")

for i in range(4):
    print(f"Side {i+1}")

    # Move forward
    send_command("w", FORWARD_TIME)

    # Turn right
    send_command("d", TURN_TIME)

print("Square Completed!")
