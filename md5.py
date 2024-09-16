import hashlib
import time

# Function to calculate MD5 hash
def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# Function to calculate the signature based on the password and current time
def calculate_signature(password):
    # Get the current Unix timestamp
    current_time = str(int(time.time()))
    
    # Calculate the double MD5 hash
    intermediate_hash = md5_hash(password)
    final_signature = md5_hash(intermediate_hash + current_time)
    
    return final_signature, current_time

# Example usage with the password "123456"
signature, current_time = calculate_signature("Bikes23")
#signature, current_time = calculate_signature("123456")
print("Signature:", signature)
print("Timestamp:", current_time)
