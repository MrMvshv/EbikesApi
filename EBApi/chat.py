from langchain.memory import ConversationTokenBufferMemory
from langchain.schema import HumanMessage, AIMessage
import json
#from dotenv import load_dotenv
from .twilio import send_message_to_client, send_message_to_rider
from django.db.models import Q
from .models import Rider, Location, Order, User, ClientMemory, RiderMemory

# load_dotenv()


# LLM setup
from .gpt_model import model

# Import your LangChain chains
from .client_request import client_chain, location_chain
from .rider_request import riders_chain, riders_acceptance_chain, delivery_completion_chain
from .chat_functions import post_order_from_chat, update_order_status, get_rider_by_phone, check_order, get_order_id


# # Dictionary to store ConversationBufferMemory for each user
# client_memories = {}
# # Dictionary to store ConversationBufferMemory for each rider
# rider_memories = {}

# # Dictionary to store the previous delivery request for each user
previous_delivery_requests = {}


# def get_client_memory(session_id: str):
#     if session_id not in client_memories:
#         client_memories[session_id] = ConversationTokenBufferMemory(max_token_limit=1000, llm=model, return_messages=True)
#     print(f"\n\n\n\nClient memory object gotten.: {client_memories[session_id]}\n\n\n\n")
#     return client_memories[session_id]

# def get_rider_memory(session_id: str):
#     if session_id not in rider_memories:
#         rider_memories[session_id] = ConversationTokenBufferMemory(max_token_limit=1000, llm=model, return_messages=True)
#     print(f"\n\n\n\nClient memory object gotten.: {rider_memories[session_id]}\n\n\n\n")
#     return rider_memories[session_id]

# Function to convert a message object to a serializable dictionary
def message_to_dict(message):
    if isinstance(message, HumanMessage):
        return {"type": "human", "content": message.content}
    elif isinstance(message, AIMessage):
        return {"type": "ai", "content": message.content}
    else:
        return {"type": "unknown", "content": str(message)}

# Function to convert a list of message objects to a JSON-compatible format
def conversation_to_json(conversation_history):
    return [message_to_dict(message) for message in conversation_history]

def dict_to_message(message_dict):
    if message_dict['type'] == 'human':
        return HumanMessage(content=message_dict['content'])
    elif message_dict['type'] == 'ai':
        return AIMessage(content=message_dict['content'])
    else:
        raise ValueError("Unknown message type: {}".format(message_dict['type']))

def deserialize_messages(json_data):
    message_dicts = json.loads(json_data)  # Deserialize from JSON
    return [dict_to_message(msg_dict) for msg_dict in message_dicts]
   
# Function to get rider memory from MySQL
def get_rider_memory(rider_id: str):
    try:
        # Try to retrieve the memory from the database
        rider_memory_obj = RiderMemory.objects.get(rider_id=rider_id)
        conversation_history = deserialize_messages(rider_memory_obj.conversation_history)  
        print(f"\n\n\n\n\nin get rider memory, convhist: {conversation_history}\n\n\n")
    except RiderMemory.DoesNotExist:
        # If no memory is found, initialize an empty memory
        conversation_history = []

    # Create the memory object for the rider (with loaded conversation)
    rider_memory = ConversationTokenBufferMemory(
        max_token_limit=1000,
        llm=model,
        return_messages=True,
    )

    for message in conversation_history:
        print(f"\n\n\n\n\nadding message: \n{message}\n\n\n")
        if isinstance(message, HumanMessage):
            rider_memory.chat_memory.add_message(HumanMessage(content=message.content))
        elif isinstance(message, AIMessage):
            rider_memory.chat_memory.add_message(AIMessage(content=message.content))

    print(f"\n\n\nrider memory object gotten: {rider_memory}\n\n\n\n")
    return rider_memory

# Function to get client memory from MySQL
def get_client_memory(client_id: str):
    print(f"Loading memory for client ID: {client_id}")
    
    try:
        # Try to retrieve the memory from the database
        client_memory_obj = ClientMemory.objects.get(client_id=client_id)
        
        # Load the conversation history from JSON
        conversation_history = deserialize_messages(client_memory_obj.conversation_history)  
        print(f"Conversation history loaded: {conversation_history}")
        #chat_memory = InMemoryChatMessageHistory(messages=conversation_history)
    except ClientMemory.DoesNotExist:
        # If no memory is found, initialize an empty memory
        conversation_history = []
        print("No existing conversation history found. Initializing empty memory.")

    except json.JSONDecodeError:
        # Handle JSON decoding errors if the stored data is not in the expected format
        print("Error: Failed to decode conversation history from JSON. Initializing empty memory.")
        conversation_history = []

    # Create the memory object for the client (with loaded conversation)
    client_memory = ConversationTokenBufferMemory(
        max_token_limit=1000,
        llm=model,
        return_messages=True,
    )

       # Load messages into the memory's chat history
    for message in conversation_history:
        print(f"\n\n\n\n\nadding message: \n{message}\n\n\n")
        if isinstance(message, HumanMessage):
            client_memory.chat_memory.add_message(HumanMessage(content=message.content))
        elif isinstance(message, AIMessage):
            client_memory.chat_memory.add_message(AIMessage(content=message.content))

    print(f"\n\n\n\nClient memory object gotten.: {client_memory}\n\n {client_memory.chat_memory.messages}\n\n")
    return client_memory


# Function to save or append client memory
def save_client_memory(client_id: str, conversation_history):
    print(f"convo history client:, {conversation_history}, {type(conversation_history)}")
    
    # Convert new conversation history to a JSON-compatible format
    new_conversation_history = conversation_to_json(conversation_history)
    
    # Check if the memory already exists for the client
    try:
        # Get the existing memory from the database
        client_memory_obj = ClientMemory.objects.get(client_id=client_id)
        
        # Load the existing conversation history from JSON
        existing_history_json = client_memory_obj.conversation_history
        existing_history = json.loads(existing_history_json) if existing_history_json else []
        
        # Append the new conversation history to the existing one
        updated_conversation_history = existing_history + new_conversation_history
    except ClientMemory.DoesNotExist:
        # If no memory exists, start with the new conversation history
        updated_conversation_history = new_conversation_history

        # Create a new record if none exists
        client_memory_obj = ClientMemory(client_id=client_id)
    
    updated_conversation_history = updated_conversation_history[-5:]
    
    # Convert the updated conversation history to a JSON string
    conversation_history_json = json.dumps(updated_conversation_history)

    # Update the object and save it to the database
    client_memory_obj.conversation_history = conversation_history_json
    client_memory_obj.save()

# Function to save or append rider memory
def save_rider_memory(rider_id: str, conversation_history):
    print(f"convo history rider:, {conversation_history}, {type(conversation_history)}")
    
    # Convert new conversation history to a JSON-compatible format
    new_conversation_history = conversation_to_json(conversation_history)
    
    # Check if the memory already exists for the client
    try:
        # Get the existing memory from the database
        rider_memory_obj = RiderMemory.objects.get(rider_id=rider_id)
        
        # Load the existing conversation history from JSON
        existing_history_json = rider_memory_obj.conversation_history
        existing_history = json.loads(existing_history_json) if existing_history_json else []
        
        # Append the new conversation history to the existing one
        updated_conversation_history = existing_history + new_conversation_history
    except RiderMemory.DoesNotExist:
        # If no memory exists, start with the new conversation history
        updated_conversation_history = new_conversation_history

        # Create a new record if none exists
        rider_memory_obj = RiderMemory(rider_id=rider_id)
    
    updated_conversation_history = updated_conversation_history[-5:]
    
    # Convert the updated conversation history to a JSON string
    conversation_history_json = json.dumps(updated_conversation_history)

    # Update the object and save it to the database
    rider_memory_obj.conversation_history = conversation_history_json
    rider_memory_obj.save()

#clear rider memory after order complete
def clear_rider_memory(rider_id: str):
    try:
        # Get the rider memory object from the database
        rider_memory_obj = RiderMemory.objects.get(rider_id=rider_id)
        
        # Clear the conversation history
        rider_memory_obj.conversation_history = json.dumps([])  # Empty conversation history
        rider_memory_obj.save()
        
        print(f"Rider memory cleared successfully for rider ID: {rider_id}")
    
    except RiderMemory.DoesNotExist:
        print(f"No memory found for rider ID: {rider_id}")

# Function to send rider notifications and handle follow-ups
def handle_rider_conversation(sender_id, message, order_id=0):
    # Get or create memory for the rider
    print(f'\n Order Id: {order_id} \n')
    rider_memory = get_rider_memory(sender_id)
    print(f"\nwhole rider memory from db\n\n: {rider_memory}")
    # Retrieve conversation history
    memory_data = rider_memory.load_memory_variables({})
    chat_history = memory_data.get('history', [])

    # Ensure chat_history is a list, even if empty
    if isinstance(chat_history, str):
        chat_history = []  # Initialize as empty list if it's an empty string

    print(f'\n Chat history: {chat_history}')

    # Prepare the input for the rider chain 
    riders_input = {
        "input": message,
        "conversation_history": chat_history
    }
    
    # Invoke the LangChain model to generate the response for the rider
    response = riders_chain.invoke(riders_input)
    
    # Store the conversation in the rider's memory
    rider_memory.save_context({"input": message}, {"output": response})

    # Save the conversation history to MySQL
    print(f"\n\nbefore saving, {rider_memory}")
    save_rider_memory(sender_id, chat_history)
    print("\n\nafter, rider_memory")
    #print('\n', sender_id, '\n')
    # Send the notification to the rider
    send_message_to_rider(sender_id, response)
    #print(f"\n{sender_id}\n")

    # Check if rider accepts delivery
    delivery_acceptance = riders_acceptance_chain.invoke(riders_input)
    #print(f"\n\nDelivery Acceptance 1 Order Id: {delivery_acceptance['order_id']}\n\n")
    
    #print('\n', delivery_acceptance, '\n')
    #print(f'\n Delivery Acceptance: {delivery_acceptance}\n')

    print(f'\n\nOrder ID from Riders side: {order_id}\n\n')
    # Send message to client to rider accepts request
    if delivery_acceptance['acceptance'] == 'Yes' and delivery_acceptance['phone_number'] != " ":
        if check_order(delivery_acceptance['order_id']):
            send_message_to_rider(sender_id, 'Order has already been taken')
        else:
            message = f"The delivery has been accepted and the rider can be contacted at {sender_id}"
            handle_client_conversation(f"whatsapp:{delivery_acceptance['phone_number']}", message, "notification")
            #print(f"\n\nDelivery Acceptance, should return Yes or No: {delivery_acceptance['acceptance']}\n\n")
            #print(f'\n\nOrder ID from Riders side on the if statement: {order_id}\n\n')

            rider_id = get_rider_by_phone(sender_id)

            #print(f"\n\nDelivery Acceptance 2 Order Id: {delivery_acceptance['order_id']}\n\n")

            update_order_status(delivery_acceptance['order_id'], 'active', rider_id)
            print('\n\nDone\n\n')
    
    delivery_completed = delivery_completion_chain.invoke(riders_input)
    print('\nDelivery Completed: ', delivery_completed, '\n')
    if delivery_completed['completed'] == 'Yes':
        rider_id = get_rider_by_phone(sender_id)
        completed_order_id = get_order_id(sender_id)
        update_order_status(completed_order_id, 'completed', rider_id)
        clear_rider_memory(rider_id)



# Function to send client notifications and handle follow-ups
def handle_client_conversation(sender_id, message, type):
    if type == "notification":
        send_message_to_client(sender_id, message)
    else:
        # Get or create ConversationBufferMemory for the sender
        client_memory = get_client_memory(sender_id)
        print(f"\n\n client memory from db: {client_memory}")
        # Retrieve conversation history
        memory_data = client_memory.load_memory_variables({})
        chat_history = memory_data.get('history', [])

        # Ensure chat_history is a list, even if empty
        if isinstance(chat_history, str):
            chat_history = []  # Initialize as empty list if it's an empty string

        print(f"client chat history: {chat_history}")

        # Format input for the chatbot
        input_data = {
            "input": message,
            "conversation_history": chat_history
        }

        # Invoke the LangChain chatbot model (remove await if not async)
        response = client_chain.invoke(input_data)

        # Store the new message in memory
        client_memory.save_context({"input": message}, {"output": response})

        # Save the conversation history to MySQL
        print(f"\n\nbefore saving, {client_memory}")
        save_client_memory(sender_id, chat_history)
        print("\nafter, client memory.")

        # Send the chatbot's response back via WhatsApp
        send_message_to_client(sender_id, response)

        print(f'\n\n after saving, Chat History: {chat_history}')

        # Get delivery request (pickup and dropoff locations)
        delivery_request = location_chain.invoke(chat_history)
        delivery_request['phone_number'] = sender_id
        delivery_request['Notes'] = message

        # Retrieve the previous delivery request if available, else initialize with empty values
        previous_request = previous_delivery_requests.get(sender_id, {'pickup_location': 'None', 'dropoff_location': 'None'})

        #print(f'\nDelivery Request: {delivery_request}\n')
        #print(f'\nPrevious Request: {previous_request}\n')
        
        # Check if the pickup and dropoff locations have changed and if both locations are provided
        if (delivery_request['pickup_location'] != "None" and delivery_request['dropoff_location'] != "None") and \
        has_locations_changed(delivery_request, previous_request):
            order_id = post_order_from_chat(delivery_request['pickup_location'], delivery_request['dropoff_location'], sender_id, delivery_request['Notes'])

            message = (
                f"Order Id: {order_id} has been assigned by {delivery_request['phone_number']}. For new order, client has a delivery from {delivery_request['pickup_location']} to {delivery_request['dropoff_location']}." 
                f"For updates, pickup location changed to {delivery_request['pickup_location']} or dropoff location changed to {delivery_request['dropoff_location']}."
                f"Avoid using courteous phrases like 'Thank you for reaching out'; just focus on providing the necessary information to the riders."
                f"Make sure the client phone number has been mentioned."
            )   

            print(f"\nDelivery request: {delivery_request}\n")
            print(f"\nPrevious request: {previous_request}\n")

            #print(f'\n Order Id 2: {order_id} \n')
            # Get riders who don't have any order with status 'active'
            riders_without_pending_orders = Rider.objects.exclude(
                id__in=Order.objects.filter(status='active').values('rider_id')
            )

            # To get only the IDs of those riders
            rider_ids = riders_without_pending_orders.values_list('id', flat=True)
            # Now, get the phone numbers of the riders with these IDs
            phone_numbers = Rider.objects.filter(id__in=rider_ids).values_list('phone_number', flat=True)

            # Convert the QuerySet to a list, if needed
            phone_numbers = list(phone_numbers)
            # Check if the phone numbers list is empty
            print(f"attempting to send notification to rider: { phone_numbers } \n")
            if not phone_numbers:
                print("No phone numbers to process.")
                #TO DO: alert dispatch of pending order without rider
            else:
                for phone_number in phone_numbers:
                    # Check if the phone number starts with '0' and convert it to 'whatsapp:+254' format
                    if phone_number.startswith('0'):
                        converted_phone_number = 'whatsapp:+254' + phone_number[1:]
                    else:
                        # Handle the case where the phone number is already in the correct format
                        converted_phone_number = phone_number

                    # Call the handle_rider_conversation with the converted phone number
                    print(f"attempting to send notification to rider: { converted_phone_number }, { message }, { order_id } \n")
                    handle_rider_conversation(converted_phone_number, message, order_id)



# Function to check if the pickup or dropoff locations have changed
def has_locations_changed(current_request, previous_request):
    current_pickup = current_request.get('pickup_location', 'None')
    current_dropoff = current_request.get('dropoff_location', 'None')
    previous_pickup = previous_request.get('pickup_location', 'None')
    previous_dropoff = previous_request.get('dropoff_location', 'None')

    return (current_pickup != previous_pickup or current_dropoff != previous_dropoff)

