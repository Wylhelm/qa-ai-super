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

app = Flask(__name__)
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

1. Test Scenario ID and Name
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

with app.app_context():
    db.create_all()

def process_file(file):
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.endswith('.docx'):
            return docx2txt.process(filepath)
        elif filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return ' '.join([page.extract_text() for page in reader.pages])
        elif filename.endswith('.txt'):
            with open(filepath, 'r') as f:
                return f.read()
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            return pytesseract.image_to_string(Image.open(filepath))
        else:
            return ''
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return ''
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

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
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        content = process_file(file)
        return jsonify({'content': content})

from flask import Response, stream_with_context

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    name = data.get('name')
    criteria = data.get('criteria')

    def generate_stream():
        scenario = ""
        for chunk in generate_scenario_stream(criteria):
            scenario += chunk
            yield chunk

        new_scenario = TestScenario(name=name, criteria=criteria, scenario=scenario)
        db.session.add(new_scenario)
        db.session.commit()

    return Response(stream_with_context(generate_stream()), content_type='text/plain')

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
                                yield content
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {line_text}")
                except Exception as e:
                    print(f"Error processing line: {str(e)}")
        
        end_time = time.time()
        generation_time = end_time - start_time
        yield f"\n\nInference Statistics:\nInput Tokens: {input_tokens}\nOutput Tokens: {output_tokens}\nGeneration Time: {generation_time:.2f} seconds"
    else:
        yield f"Error generating scenario: HTTP {response.status_code}"

@app.route('/scenarios', methods=['GET'])
def get_scenarios():
    scenarios = TestScenario.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'criteria': s.criteria, 'scenario': s.scenario} for s in scenarios])

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
    app.run(debug=True)
