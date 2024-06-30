import openai
import sounddevice as sd
import soundfile as sf
import numpy as np

# OpenAI API key
client = openai.OpenAI(
    api_key='')

# Store items
store_items = [
    {"name": "dosa", "description": "A thin pancake originating from South India", "price": 50},
    {"name": "upma", "description": "A breakfast dish made from semolina", "price": 40},
    {"name": "idli", "description": "A type of savoury rice cake", "price": 30},
    {"name": "vada", "description": "A savoury fried snack", "price": 35},
    {"name": "lemon rice", "description": "Rice with lemon flavor", "price": 45},
    {"name": "curd rice", "description": "Rice mixed with curd", "price": 40}
]

# Parameters for recording
duration = 10  # seconds
samplerate = 44100  # Hertz


def record_audio(duration, samplerate):
    print("Recording...")
    audio_data = sd.rec(int(duration * samplerate),
                        samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")

    audio_data_int = (audio_data * 32767).astype(np.int16)
    permanent_audio_file = "recorded_audio.wav"
    sf.write(permanent_audio_file, audio_data_int,
             samplerate, subtype='PCM_16')
    return permanent_audio_file


def transcribe_audio(audio_file_path):
    print("Transcribing...")
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    return response.text


def search_store_items(query):
    found_items = []
    for item in store_items:
        if item['name'].lower() in query.lower():
            found_items.append(item)
    return found_items


def get_order(transcribed_text):
    order_items = []
    items = transcribed_text.split(',')

    for item_name in items:
        item = search_store_items(item_name.strip())
        if item:
            order_items.extend(item)  # Append all found items

    if order_items:
        bill = calculate_bill(order_items)
        return f"Order placed successfully! Here is your bill:\n{bill}"
    else:
        return f"The items you ordered are not available. Please check the available items and order again. The available items are: {', '.join([item['name'] for item in store_items])}."


def calculate_bill(order_items):
    total = 0
    gst_rate = 0.05  # 5% GST
    print("\nOrder Summary:")
    for item in order_items:
        price = item['price']
        gst = price * gst_rate
        total += price + gst
        print(f"Item: {item['name']}")
        print(f"Specifications: {item.get('specifications', 'N/A')}")
        print(f"Price: ₹{price:.2f}")
        print(f"GST (5%): ₹{gst:.2f}")
        print(f"Subtotal: ₹{price + gst:.2f}")
        print("--------------------")

    print(f"Total Bill: ₹{total:.2f}")


try:
    print("Chatbot: Hello! Welcome to our South Indian restaurant.")
    audio_file = record_audio(duration, samplerate)
    transcribed_text = transcribe_audio(audio_file)
    order_items = get_order(transcribed_text)
    print(order_items)  # Added this line to see the order items structure
    if order_items:
        calculate_bill(order_items)
    else:
        print("Chatbot: Thank you for visiting. Have a great day!")

except Exception as e:
    print(f"An error occurred: {str(e)}")
