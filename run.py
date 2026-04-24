from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app
from config import DevelopmentConfig

# Create flask app
app = create_app(DevelopmentConfig)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=False)
