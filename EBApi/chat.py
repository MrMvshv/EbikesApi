from langchain.memory.buffer_window import ConversationBufferWindowMemory
from dotenv import load_dotenv
from .twilio import send_message_to_client, send_message_to_rider

load_dotenv()


# LLM setup
from .gpt_model import model

# Import your LangChain chains
from .client_request import client_chain, location_chain
from .rider_request import riders_chain, riders_acceptance_chain


# Dictionary to store ConversationBufferMemory for each user
client_memories = {}
# Dictionary to store ConversationBufferMemory for each rider
rider_memories = {}

# Dictionary to store the previous delivery request for each user
previous_delivery_requests = {}


def get_client_memory(session_id: str):
    if session_id not in client_memories:
        client_memories[session_id] = ConversationBufferWindowMemory(return_messages=True, k=8)
    return client_memories[session_id]

def get_rider_memory(session_id: str):
    if session_id not in rider_memories:
        rider_memories[session_id] = ConversationBufferWindowMemory(return_messages=True, k=8)
    return rider_memories[session_id]
    

# Function to send rider notifications and handle follow-ups
def handle_rider_conversation(sender_id, message):
    # Get or create memory for the rider
    rider_memory = get_rider_memory(sender_id)
    # Retrieve conversation history
    memory_data = rider_memory.load_memory_variables({})
    chat_history = memory_data.get('history', [])

    # Ensure chat_history is a list, even if empty
    if isinstance(chat_history, str):
        chat_history = []  # Initialize as empty list if it's an empty string

    # Prepare the input for the rider chain 
    riders_input = {
        "input": message,
        "conversation_history": chat_history
    }
    
    # Invoke the LangChain model to generate the response for the rider
    response = riders_chain.invoke(riders_input)
    
    # Store the conversation in the rider's memory
    rider_memory.save_context({"input": message}, {"output": response})
    
    # Send the notification to the rider
    send_message_to_rider(sender_id, response)

    # Check if rider accepts delivery
    delivery_acceptance = riders_acceptance_chain.invoke({"input": message, 'announcement': response})
    
    # Send message to client to rider accepts request
    if delivery_acceptance['acceptance'] == 'Yes' and delivery_acceptance['phone_number'] != " ":
        message = f"Notify the client that the delivery has been accepted and the rider can be contacted at {sender_id}"
        handle_client_conversation(f"whatsapp:{delivery_acceptance['phone_number']}", message)
    

# Function to send client notifications and handle follow-ups
def handle_client_conversation(sender_id, message):
    # Get or create ConversationBufferMemory for the sender
    client_memory = get_client_memory(sender_id)
    # Retrieve conversation history
    memory_data = client_memory.load_memory_variables({})
    chat_history = memory_data.get('history', [])

    # Ensure chat_history is a list, even if empty
    if isinstance(chat_history, str):
        chat_history = []  # Initialize as empty list if it's an empty string

    # Format input for the chatbot
    input_data = {
        "input": message,
        "conversation_history": chat_history
    }

    # Invoke the LangChain chatbot model (remove await if not async)
    response = client_chain.invoke(input_data)

    # Store the new message in memory
    client_memory.save_context({"input": message}, {"output": response})

    # Send the chatbot's response back via WhatsApp
    send_message_to_client(sender_id, response)

    # Get delivery request (pickup and dropoff locations)
    delivery_request = location_chain.invoke(chat_history)
    delivery_request['phone_number'] = sender_id

    # Retrieve the previous delivery request if available, else initialize with empty values
    previous_request = previous_delivery_requests.get(sender_id, {'pickup_location': 'None', 'dropoff_location': 'None'})

    # Check if the pickup and dropoff locations have changed and if both locations are provided
    if (delivery_request['pickup_location'] != "None" and delivery_request['dropoff_location'] != "None") and \
    has_locations_changed(delivery_request, previous_request):
        message = (
            f"Order assigned by {delivery_request['phone_number']}. For new order, client has a delivery from {delivery_request['pickup_location']} to {delivery_request['dropoff_location']}." 
            f"For updates, pickup location changed to {delivery_request['pickup_location']} or dropoff location changed to {delivery_request['dropoff_location']}."
            f"Avoid using courteous phrases like 'Thank you for reaching out'; just focus on providing the necessary information to the riders."
        )

        handle_rider_conversation('whatsapp:+254747694839', message)

        # Update the previous delivery request to the current one
        previous_delivery_requests[sender_id] = delivery_request


# Function to check if the pickup or dropoff locations have changed
def has_locations_changed(current_request, previous_request):
    current_pickup = current_request.get('pickup_location', 'None')
    current_dropoff = current_request.get('dropoff_location', 'None')
    previous_pickup = previous_request.get('pickup_location', 'None')
    previous_dropoff = previous_request.get('dropoff_location', 'None')

    return (current_pickup != previous_pickup or current_dropoff != previous_dropoff)

