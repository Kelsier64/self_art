from PIL import Image
from openai import OpenAI
import base64,os
from dotenv import load_dotenv
load_dotenv()
def crop_and_save(image_path, output_dir, index):
    try:
        # Open the image
        img = Image.open(image_path)
        width, height = img.size

        # Calculate the coordinates for the 16 parts
        part_width = width // 4
        part_height = height // 4
        parts = [
            (x * part_width, y * part_height, (x + 1) * part_width, (y + 1) * part_height)
            for y in range(4) for x in range(4)
        ]

        # Ensure the index is valid
        if index < 1 or index > 16:
            raise ValueError("Index must be between 1 and 16")

        # Crop and save the selected part
        selected_box = parts[index - 1]
        cropped_img = img.crop(selected_box)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the cropped image in the specified directory
        output_path = os.path.join(output_dir, f"{index}.jpg")
        cropped_img.save(output_path)
        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
for i in range(1, 17):
    crop_and_save("me.jpg", "static/images", i)


# prompt = "把圖片變成Cyberpuck風格"

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# result = client.images.edit(
#     model="gpt-image-1",
#     image=open("me.jpg", "rb"),
#     size="1024x1024",
#     quality="low",
#     prompt=prompt
# )

# image_base64 = result.data[0].b64_json
# image_bytes = base64.b64decode(image_base64)

# # Save the image to a file
# with open("result.jpg", "wb") as f:
#     f.write(image_bytes)

