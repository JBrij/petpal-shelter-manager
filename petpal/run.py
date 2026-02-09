from app import create_app
from flask import send_from_directory
import os


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        os.path.join(os.getcwd(), "uploads"),
        filename
    )