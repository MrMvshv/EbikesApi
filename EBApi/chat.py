from langchain.memory import ConversationTokenBufferMemory
from dotenv import load_dotenv
from .twilio import send_message_to_client, send_message_to_rider

load_dotenv()


# LLM setup
from .gpt_model import model

# Import your LangChain chains
from .client_request import client_chain, location_chain
from .rider_request import riders_chain, riders_acceptance_chain, delivery_completion_chain
from .chat_functions import post_order_from_chat, update_order_status


# Dictionary to store ConversationBufferMemory for each user
client_memories = {}
# Dictionary to store ConversationBufferMemory for each rider
rider_memories = {}

# Dictionary to store the previous delivery request for each user
previous_delivery_requests = {}


def get_client_memory(session_id: str):
    if session_id not in client_memories:
        client_memories[session_id] = ConversationTokenBufferMemory(max_token_limit=1000, llm=model, return_messages=True)
    return client_memories[session_id]

def get_rider_memory(session_id: str):
    if session_id not in rider_memories:
        rider_memories[session_id] = ConversationTokenBufferMemory(max_token_limit=1000, llm=model, return_messages=True)
    return rider_memories[session_id]
    

# Function to send rider notifications and handle follow-ups
def handle_rider_conversation(sender_id, message, order_id=0):
    # Get or create memory for the rider
    print(f'\n Order Id: {order_id} \n')
    rider_memory = get_rider_memory(sender_id)
    # Retrieve conversation history
    memory_data = rider_memory.load_memory_variables({})
    chat_history = memory_data.get('history', [])

    print(chat_history)

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
    print('\n', sender_id, '\n')
    # Send the notification to the rider
    send_message_to_rider(sender_id, response)
    print(f"\n{sender_id}\n")

    # Check if rider accepts delivery
    delivery_acceptance = riders_acceptance_chain.invoke(riders_input)
    
    print('\n', delivery_acceptance, '\n')
    print(f'\n Delivery Acceptance: {delivery_acceptance}\n')
    # Send message to client to rider accepts request
    if delivery_acceptance['acceptance'] == 'Yes' and delivery_acceptance['phone_number'] != " ":
        message = f"Notify the client that the delivery has been accepted and the rider can be contacted at {sender_id}"
        handle_client_conversation(f"whatsapp:{delivery_acceptance['phone_number']}", message)
        print(f"\n\nDelivery Acceptance, shoulld return Yes or No: {delivery_acceptance['acceptance']}\n\n")
        update_order_status(order_id, 'active')
        print('\n\nDone\n\n')
    
    delivery_completed = delivery_completion_chain.invoke(riders_input)
    print('\nDelivery Completed: ', delivery_completed, '\n')
    if delivery_completed == 'Yes':
        update_order_status(order_id, 'completed')


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

    print(chat_history)

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

    print(f'\n\n Chat History: {chat_history}')

    # Get delivery request (pickup and dropoff locations)
    delivery_request = location_chain.invoke(chat_history)
    delivery_request['phone_number'] = sender_id
    delivery_request['Notes'] = message

    # Retrieve the previous delivery request if available, else initialize with empty values
    previous_request = previous_delivery_requests.get(sender_id, {'pickup_location': 'None', 'dropoff_location': 'None'})

    print(f'\nDelivery Request: {delivery_request}\n')
    print(f'\nPrevious Request: {previous_request}\n')
    
    # Check if the pickup and dropoff locations have changed and if both locations are provided
    if (delivery_request['pickup_location'] != "None" and delivery_request['dropoff_location'] != "None") and \
    has_locations_changed(delivery_request, previous_request):
        order_id = post_order_from_chat(delivery_request['pickup_location'], delivery_request['dropoff_location'], sender_id, delivery_request['Notes'])

        message = (
            f"Order Id: {order_id} has been assigned by {delivery_request['phone_number']}. For new order, client has a delivery from {delivery_request['pickup_location']} to {delivery_request['dropoff_location']}." 
            f"For updates, pickup location changed to {delivery_request['pickup_location']} or dropoff location changed to {delivery_request['dropoff_location']}."
            f"Avoid using courteous phrases like 'Thank you for reaching out'; just focus on providing the necessary information to the riders."
        )   

        print(f"\nDelivery request: {delivery_request}\n")
        print(f"\nPrevious request: {previous_request}\n")

        print(f'\n Order Id 2: {order_id} \n')
        handle_rider_conversation('whatsapp:+254701638574', message, order_id)

        # Update the previous delivery request to the current one
        previous_delivery_requests[sender_id] = delivery_request



# Function to check if the pickup or dropoff locations have changed
def has_locations_changed(current_request, previous_request):
    current_pickup = current_request.get('pickup_location', 'None')
    current_dropoff = current_request.get('dropoff_location', 'None')
    previous_pickup = previous_request.get('pickup_location', 'None')
    previous_dropoff = previous_request.get('dropoff_location', 'None')

    return (current_pickup != previous_pickup or current_dropoff != previous_dropoff)

