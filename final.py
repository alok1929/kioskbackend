import openai
import sounddevice as sd
import soundfile as sf
import numpy as np

# OpenAI API key
client = openai.OpenAI(
    api_key='')

# Store items
store_items = [
    {"name": "dosa", "description": "A thin pancake originating from South India"},
    {"name": "upma", "description": "A breakfast dish made from semolina"},
    {"name": "idli", "description": "A type of savoury rice cake"},
    {"name": "vada", "description": "A savoury fried snack"},
    {"name": "lemon rice", "description": "Rice with lemon flavor"},
    {"name": "curd rice", "description": "Rice mixed with curd"}
]

# Parameters for recording
duration = 10  # seconds
samplerate = 44100  # Hertz

# Function to record audio and return the file path


def record_audio(duration, samplerate):
    print("Recording...")
    audio_data = sd.rec(int(duration * samplerate),
                        samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")

    # Convert float32 array to int16
    audio_data_int = (audio_data * 32767).astype(np.int16)

    # Define the name and path of the permanent audio file
    permanent_audio_file = "recorded_audio.wav"

    # Save audio data to the permanent WAV file
    sf.write(permanent_audio_file, audio_data_int,
             samplerate, subtype='PCM_16')

    return permanent_audio_file

# Search store items


def search_store_items(query):
    for item in store_items:
        if query.lower() in item['name'].lower():
            return item
    return None

# Function to ask for feedback


def ask_for_feedback():
    return "Thank you for your order. We would love to hear your feedback on your experience. Please let us know if there is anything we can improve or if everything was perfect."

# Process and analyze the feedback


def process_feedback(feedback):
    with open('feedback_log.txt', 'a') as f:
        f.write(feedback + "\n")


try:
    # Record audio and get the file path
    audio_file_path = record_audio(duration, samplerate)

    # Transcribe the audio file
    print("Transcribing...")
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    transcribed_text = response.text
    print("Transcribed Text:", transcribed_text)

    # Search for the item
    searched_item = search_store_items(transcribed_text)

    # Generate the prompt based on the search result
    if searched_item:
        item_name = searched_item['name']
        item_description = searched_item['description']
        order_prompt = f"The customer said: '{transcribed_text}'. I found the item: {item_name} - {item_description}. Would you like to have any specifications with that? If yes, would you like to send it as a recording itself, or would you just directly like to tell the specifications?"
    else:
        order_prompt = f"The customer said: '{transcribed_text}'. I couldn't find the exact item. Can you please repeat or specify your order? The available items are: {', '.join([item['name'] for item in store_items])}."

    # Use the OpenAI API to generate a response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
                "content": """You are a helpful assistant at a South Indian store, after the order is placed, it should tell ask if there is anything else you like to say about
             the order, if no then place the order, and give your own prices including gst for all items on
             the menu."""},
            {"role": "user", "content": order_prompt}
        ]
    )

    # Print the AI response
    print(response.choices[0].message.content.strip())

    # Generate and print feedback request
    feedback_prompt = ask_for_feedback()
    feedback_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
                "content": "You are a helpful assistant at a South Indian store."},
            {"role": "user", "content": feedback_prompt}
        ]
    )
    print(feedback_response.choices[0].message.content.strip())

    # Capture and store user feedback
    user_feedback = input("Please provide your feedback: ")
    process_feedback(user_feedback)

except Exception as e:
    print(f"An error occurred: {str(e)}")

