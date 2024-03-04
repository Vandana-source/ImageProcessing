import xmlrpc.client

# Create an XML-RPC client
client = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'tiff'}


# Function to display available operations
def display_available_operations():
    print("Available operations:")
    print("1. Rotate")
    print("2. Flip")
    print("3. Resize")
    print("4. Generate Thumbnail")
    print("5. Convert to Grayscale")
    print("6. Rotate Left/Right")
    print("")


# Read the image file as binary data
image_path = input("Enter the path to the image file: ")
if not image_path.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
    print("Invalid file type. Allowed file types are: ", ALLOWED_EXTENSIONS)
    exit()
    
with open(image_path, 'rb') as f:
    image_data = xmlrpc.client.Binary(f.read())

# Initialize an empty list to store operations
operations = []

# Display available operations
display_available_operations()

# Ask the user for operations until they choose to stop
while True:
    operation_choice = input("Enter the number corresponding to the operation you want to perform (or type 'done' to "
                             "finish): ")
    if operation_choice.lower() == 'done':
        break

    operation = {}
    if operation_choice == '1':
        operation["name"] = 'rotate'
        degrees = int(input("Enter the degrees to rotate (-10000 to +10000): "))
        if -10000 <= degrees <= 10000:
            operation["degrees"] = degrees
        else:
            print("Invalid value. Rotation degrees must be within the range -10000 to +10000.")
            continue
    elif operation_choice == '2':
        operation["name"] = 'flip'
        operation["axis"] = input("Enter the axis to flip (horizontal or vertical): ")
    elif operation_choice == '3':
        operation["name"] = 'resizing'
        percentage = int(input("Enter the percentage to resize (-95% to +500%): "))
        if -95 <= percentage <= 500:
            operation["percentage"] = percentage
        else:
            print("Invalid value. Resize percentage must be within the range -95% to +500%.")
            continue
    elif operation_choice == '4':
        operation["name"] = 'thumbnail'
        operation["thumb"] = (200, 200)
    elif operation_choice == '5':
        operation["name"] = 'grayscale'
        operation["scale"] = input("Convert to grayscale (yes or no): ")
    elif operation_choice == '6':
        operation["name"] = 'rotate_left_right'
        operation["side"] = input("Enter the side to rotate (left or right): ")

    # Add the operation to the list
    operations.append(operation)

print("Operations to be performed: ", operations)

# Call the server's process_image method and pass the image data and operations
result = client.process_image(image_data, operations)

# Check if it's a single value (no thumbnail)
if isinstance(result, xmlrpc.client.Binary):
    processed_image_data = result
    thumbnail_image_data = None
    error_message = None
else:
    # Unpack as usual if both data are present
    thumbnail_image_data, processed_image_data, error_message = result

    # Write the processed image data to a file
    processed_output_path = 'processed_image.jpg'
    thumbnail_image_path = 'thumbnail.jpg'
    if thumbnail_image_data:
        with open(thumbnail_image_path, "wb") as handle:
            handle.write(thumbnail_image_data.data)
        print("Thumbnail image saved to:", thumbnail_image_path)

    if processed_image_data:
        with open(processed_output_path, 'wb') as handle:
            handle.write(processed_image_data.data)
        print("Processed image saved to:", processed_output_path)

    if error_message:
        print("Only first thumbnail is processed as the system does not support multiple thumbnail operations")
