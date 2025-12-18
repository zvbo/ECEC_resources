#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
touch .env
echo "GOOGLE_API_KEY=your_key_here" >> .env
echo "DOCS_DIR=/path/to/docs" >> .env
echo "Environment setup complete. Please edit .env with your API Key and Doc path."
