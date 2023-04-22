import io
import os
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import PIL.Image
from PIL import UnidentifiedImageError
from flask import Flask, render_template, request, send_from_directory, send_file
from .prompts_service import generate_images


# Create a Flask application object
app = Flask(__name__, template_folder = "../templates/", static_folder = "../static/")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process_text", methods = ["POST"])
def process_text():

    text = request.form["text"]
    design = request.form["dropdownMenuButton"]
    images = generate_images(text, design)


    if images == -1:
        return render_template("index.html", error_message = "No images to display. "
                                                           "Try a new prompt or again the same one.")
    if "The system is currently under maintenance." in images:
        return render_template("index.html", error_message = "A problem occured. " \
                                                            "Please try again in a few minutes.")
    filenames = os.listdir(app.static_folder)
    for filename in filenames:
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            os.remove(os.path.join(app.static_folder, filename))

    image_paths = []
    for i, image_bytes in enumerate(images):
        # Create a filename for the image
      try:
        filename = f"image_{i}.jpg"
        # Create the full path to the file
        path = os.path.join(app.static_folder, filename)
        # Create an Image instance from the byte array
        image = PIL.Image.open(io.BytesIO(image_bytes))
        # Save the image to the static folder as a JPEG
        image.save(path, "JPEG")
        # Add the path to the list of image paths
        image_paths.append(filename)
      except UnidentifiedImageError as e:
        continue

    # Render the template with the list of image paths
    loading = False
    return render_template("index.html", zip_file = image_paths)


@app.route("/aboutme")
def aboutme():
    return render_template("aboutme.html")

@app.route("/faq")
def faq():
    filepath = "../frontend/images/methodology.pdf"
    return send_file(filepath, download_name="methodology.pdf")


@app.route("/demo")
def demo():
    return render_template("demo.html")


@app.route("/download_zip")
def download_zip():
    image_paths = request.args.getlist("zip_file")

    if not image_paths:
        return "No images to download"

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w", compression=ZIP_DEFLATED) as zip_file:
        for image_path in image_paths:
            # Read the image from the static folder
            path = os.path.join(app.static_folder, image_path)
            with open(path, "rb") as image_file:
                # Write the image to the zip file
                zip_file.writestr(image_path, image_file.read())

    zip_buffer.seek(0)

    # delete static imgaes in the folder. do stylistics and multiple options. responsive design.
    return send_file(zip_buffer, download_name="images.zip",
                     as_attachment=True, mimetype="application/zip")



# endpoint for frontend folder. For accessing the css files.
@app.route('/frontend/<path:path>')
def serve_frontend(path):
    return send_from_directory('../frontend', path)



# Start the app
if __name__ == '__main__':
    app.run()
