from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from PIL import Image
import base64
from openai import OpenAI
import os

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Track the current puzzle index
current_index = 7
prompts = ["none"] * 16

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

# 動態提供圖片
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/')
def index():
    # 假設圖片存放在 uploads 資料夾中
    image_folder = 'uploads'
    images = sorted(
        [f'uploads/{img}' for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg'))],
        key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
    )
    # 確保最多顯示16張圖片
    images = images[:16]
    return render_template('index.html', images=images)

@app.route('/generate', methods=['POST'])
def generate_image():
    global current_index
    global prompts
    try:
        # Get the prompt from the form
        prompt = request.form['prompt']
        
        # Call the OpenAI API to generate an image
        result = client.images.edit(
            model="gpt-image-1",
            image=open("me.jpg", "rb"),
            size="1024x1024",
            quality="low",
            prompt=prompt
        )

        # Decode the generated image
        prompts[current_index - 1] = prompt
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Save the generated image
        generated_image_path = f"generated/{current_index}.jpg"
        with open(generated_image_path, "wb") as f:
            f.write(image_bytes)

        # Crop and replace the current puzzle piece
        crop_and_save(generated_image_path, "uploads", current_index)

        # Update the current index for the next submission
        current_index = (current_index % 16) + 1

        return redirect(url_for('index'))
    except Exception as e:
        return redirect(url_for('index'))

@app.route('/puzzle/<int:image_id>')
def puzzle(image_id):
    # Render the puzzle page with the selected image ID
    if prompts[image_id - 1] :
        prompt = prompts[image_id - 1] 
    return render_template('puzzle.html', prompt=prompt, image_id=image_id)

@app.route('/reveal', methods=['POST'])
def reveal():
    try:
        # Get the image ID and password from the form
        image_id = int(request.form['image_id'])
        password = request.form['password']

        # Check if the password is correct (for simplicity, using a hardcoded password)
        if password == 'secret':
            # Return the original image from the server
            return send_from_directory('generated', f'{image_id}.jpg')
        else:
            return "Incorrect password", 403
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)