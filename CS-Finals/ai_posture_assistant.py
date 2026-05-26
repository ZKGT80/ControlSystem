import serial
import requests
import time

# =========================
# SERIAL SETUP
# =========================

esp32 = serial.Serial('COM11', 115200)

time.sleep(2)

print("Connected to ESP32")
print("AI Posture Assistant Running...\n")

# =========================
# VARIABLES
# =========================

last_state = ""
last_ai_time = 0

AI_COOLDOWN = 8   # seconds

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        # -------------------------
        # READ DISTANCE
        # -------------------------

        raw = esp32.readline().decode(errors='ignore').strip()

        try:
            distance = float(raw)
        except:
            continue

        print(f"Distance: {distance:.2f} cm")

        # -------------------------
        # DETERMINE STATE
        # -------------------------

        if distance < 15:
            state = "too close"

        elif distance <= 40:
            state = "good posture"

        else:
            state = "too far"

        # -------------------------
        # CHECK IF STATE CHANGED
        # -------------------------

        current_time = time.time()

        if state != last_state and (current_time - last_ai_time > AI_COOLDOWN):

            last_state = state
            last_ai_time = current_time

            print("\nPOSTURE CHANGED")
            print("State:", state)

            # -------------------------
            # CREATE PROMPT
            # -------------------------

            prompt = f"""
            User posture status: {state}

            Give one complete and friendly posture advice sentence.
            Keep the answer under 20 words.
            """

            try:

                # -------------------------
                # SEND TO LM STUDIO
                # -------------------------

                response = requests.post(
                    "http://localhost:1234/v1/chat/completions",
                    json={

                        # USE YOUR EXACT MODEL NAME
                        "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",

                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],

                        "temperature": 0.2,
                        "max_tokens": 35
                    },

                    timeout=15
                )

                data = response.json()

                if "choices" in data:

                    reply = data["choices"][0]["message"]["content"]

                    print("\nAI Advice:")
                    print(reply)
                    print()

                else:

                    print("\nLM Studio Error:")
                    print(data)
                    print()

            except Exception as ai_error:

                print("\nAI Error:")
                print(ai_error)
                print()

    except Exception as e:

        print("System Error:", e)