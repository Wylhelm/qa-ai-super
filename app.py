from flask import Flask, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import docx2txt
import PyPDF2
from PIL import Image
import pytesseract
import requests
import json
import base64
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

# Add this line to print the API key (remove in production)
logger.info(f"API Key: {os.getenv('OPENAI_API_KEY')}")

app = Flask(__name__, static_folder='static', static_url_path='/static')
logger.info("Flask app initialized with static folder")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scenarios.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for system prompt, scenario prompt, and context window size
SYSTEM_PROMPT = "You are a test scenario generator that creates comprehensive test scenarios based on given criteria."
CONTEXT_WINDOW_SIZE = 4096
SCENARIO_PROMPT = """Generate a test scenario based on the following criteria:

{criteria}

Please provide a comprehensive test scenario that includes:

1. Ignore all filenames and add the Test Scenario ID and Name
2. Test Case Objective
3. Preconditions
4. Test Steps (including inputs and expected results)
5. Post-conditions
6. Test Data Requirements
7. Environmental Needs
8. Any special procedural requirements
9. Inter-case dependencies (if applicable)
10. Actions and expected results
11. At the end write "Created by CGI Innovation and Immersive Systems Community"

Ensure the scenario adheres to the IEEE 829 standard for test documentation."""

class TestScenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    criteria = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    statistics = db.Column(db.Text)
    uploaded_files = db.Column(db.Text)

def init_db():
    with app.app_context():
        db.create_all()

init_db()

def process_file(file):
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.endswith('.docx'):
            content = docx2txt.process(filepath)
        elif filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ' '.join([page.extract_text() for page in reader.pages])
        elif filename.endswith('.txt'):
            with open(filepath, 'r') as f:
                content = f.read()
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            content = analyze_image(filepath)
        else:
            content = ''

        return {'filename': filename, 'content': content}
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return {'filename': filename, 'content': ''}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

def analyze_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "Error: OpenAI API key not found in environment variables"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": os.getenv('OPENAI_MODEL', 'gpt-4o'),  # Use the model from .env, fallback to gpt-4o if not set
            "messages": [
                {
                    "role": "user",
                    "content": f"Provide a detailed description of the following text extracted from an image: {text}"
                }
            ],
            "max_tokens": 1000  # Increase max tokens to capture more detailed responses
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            return response_data['choices'][0]['message']['content']
        else:
            print(f"Error analyzing image: {response_data}")
            return "Error analyzing image"
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return "Error processing image"

def generate_scenario(criteria):
    global SYSTEM_PROMPT, CONTEXT_WINDOW_SIZE
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": SCENARIO_PROMPT.format(criteria=criteria)}
        ],
        "max_tokens": CONTEXT_WINDOW_SIZE
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "Error generating scenario"

@app.route('/')
def index():
    try:
        logger.info("Attempting to render index.html")
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Template folder: {app.template_folder}")
        logger.debug(f"Static folder: {app.static_folder}")
        print("Rendering index.html")  # Add this line
        return render_template('index.html', scenario_name='', scenario_description='', scenario_statistics='')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}", exc_info=True)
        return f"Error rendering index.html: {str(e)}", 500

@app.route('/debug')
def debug():
    return "Debug route is working"

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload endpoint hit")
        if 'files' not in request.files:
            return jsonify({'error': 'No file part'})
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No selected file'})
        results = []
        for file in files:
            result = process_file(file)
            results.append(result)
        return jsonify({'results': results})
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500

from flask import Response, stream_with_context

@app.route('/generate', methods=['POST'])
def generate():
    try:
        print("Generate endpoint hit")
        data = request.json
        name = data.get('name')
        criteria = data.get('criteria')
        is_regenerate = data.get('is_regenerate', False)

        if is_regenerate:
            if "(Regenerated)" not in name:
                name = f"{name} (Regenerated)"

        def generate_stream():
            nonlocal name
            scenario = ""
            statistics = ""
            for chunk in generate_scenario_stream(criteria):
                if chunk.startswith("\n\nInference Statistics:"):
                    statistics = chunk.split("\n\nInference Statistics:\n")[1]
                else:
                    scenario += chunk
                yield chunk
    
            uploaded_files = ", ".join(request.json.get('uploaded_files', []))
            if is_regenerate:
                name = f"{name} (Regenerated)"
            new_scenario = TestScenario(name=name, criteria=criteria, scenario=scenario, statistics=statistics, uploaded_files=uploaded_files)
            db.session.add(new_scenario)
            db.session.commit()

        return Response(stream_with_context(generate_stream()), content_type='text/plain')
    except Exception as e:
        print(f"Error in generate: {str(e)}")
        return "Error generating scenario", 500

import time

def generate_scenario_stream(criteria):
    global SYSTEM_PROMPT, CONTEXT_WINDOW_SIZE, SCENARIO_PROMPT
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": SCENARIO_PROMPT.format(criteria=criteria)}
        ],
        "max_tokens": CONTEXT_WINDOW_SIZE,
        "stream": True
    }
    
    start_time = time.time()
    input_tokens = len(SYSTEM_PROMPT.split()) + len(SCENARIO_PROMPT.format(criteria=criteria).split())
    output_tokens = 0
    scenario = ""
    
    response = requests.post(url, headers=headers, json=data, stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                try:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        json_str = line_text[6:]  # Remove 'data: ' prefix
                        json_object = json.loads(json_str)
                        if 'choices' in json_object and len(json_object['choices']) > 0:
                            delta = json_object['choices'][0]['delta']
                            if 'content' in delta:
                                content = delta['content']
                                output_tokens += len(content.split())
                                scenario += content
                                yield content
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {line_text}")
                except Exception as e:
                    print(f"Error processing line: {str(e)}")
        
        end_time = time.time()
        generation_time = end_time - start_time
    else:
        scenario = f"Error generating scenario: HTTP {response.status_code}"
        generation_time = 0
    
    statistics = f"Input Tokens: {input_tokens}\nOutput Tokens: {output_tokens}\nGeneration Time: {generation_time:.2f} seconds"
    yield f"\n\nInference Statistics:\n{statistics}"

@app.route('/scenarios', methods=['GET'])
def get_scenarios():
    if db.engine.has_table('test_scenario'):
        scenarios = TestScenario.query.all()
        return jsonify([{'id': s.id, 'name': s.name, 'criteria': s.criteria, 'scenario': s.scenario, 'statistics': s.statistics, 'uploaded_files': s.uploaded_files} for s in scenarios])
    else:
        return jsonify([])  # Return an empty list if the table doesn't exist

@app.route('/get_system_prompt', methods=['GET'])
def get_system_prompt():
    global SYSTEM_PROMPT
    return jsonify({'prompt': SYSTEM_PROMPT})

@app.route('/set_system_prompt', methods=['POST'])
def set_system_prompt():
    global SYSTEM_PROMPT
    data = request.json
    SYSTEM_PROMPT = data.get('prompt')
    return jsonify({'success': True})

@app.route('/get_context_window', methods=['GET'])
def get_context_window():
    global CONTEXT_WINDOW_SIZE
    return jsonify({'size': CONTEXT_WINDOW_SIZE})

@app.route('/set_context_window', methods=['POST'])
def set_context_window():
    global CONTEXT_WINDOW_SIZE
    data = request.json
    size = data.get('size')
    if size in [4096, 8192]:
        CONTEXT_WINDOW_SIZE = size
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid context window size'})

@app.route('/get_scenario_prompt', methods=['GET'])
def get_scenario_prompt():
    global SCENARIO_PROMPT
    return jsonify({'prompt': SCENARIO_PROMPT})

@app.route('/set_scenario_prompt', methods=['POST'])
def set_scenario_prompt():
    global SCENARIO_PROMPT
    data = request.json
    SCENARIO_PROMPT = data.get('prompt')
    return jsonify({'success': True})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        TestScenario.query.delete()
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(debug=True)
    logger.info("Flask application has stopped")
