import os
from PIL import Image

def convert_images(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Loop through all files in the input folder
    img_counter = 1
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.jpg'):
            # Open the image file
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            
            # Convert to webp and rename
            webp_filename = f'img{img_counter}.webp'
            webp_path = os.path.join(output_folder, webp_filename)
            img.save(webp_path, 'webp')
            
            print(f"Converted {filename} to {webp_filename}")
            img_counter += 1

# Define the input and output folders
input_folder = "Your-path"
output_folder = "Your-path"

# Run the conversion
convert_images(input_folder, output_folder)
