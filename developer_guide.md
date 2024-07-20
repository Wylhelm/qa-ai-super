# Test Scenario Generator - Developer Guide

## Project Overview 
The Test Scenario Generator is a Flask-based web application that leverages AI to analyze documents (Word, PDF, text files, and images) to automatically generate comprehensive test scenarios. It uses a local Large Language Model (LLM) to create scenarios adhering to the IEEE 829 standard.

## Project Structure
- `app.py`: Main application file containing Flask routes and core functionality
- `templates/index.html`: HTML template for the main user interface
- `static/`: Directory for static files (CSS, JavaScript, images)
- `.env`: Environment variables file (not in version control)
- `requirements.txt`: List of Python dependencies
- `README.md`: Project overview and setup instructions
- `user_guide.md`: User guide for the application
- `developer_guide.md`: This file, containing development details

## Setup and Dependencies
1. Ensure Python 3.7+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up a local LLM server (e.g., using LM Studio) accessible at http://localhost:1234.
4. Create a `.env` file with necessary environment variables (see `.env` section in this guide).

## Key Components

### Flask Application (app.py)
- Implements the main application logic and API endpoints.
- Handles file uploads, scenario generation, and database operations.
- Manages system prompt, scenario prompt, and context window size.
- Implements streaming scenario generation with abort functionality.
- Integrates with OpenAI API for image analysis.

### Database Model (app.py)
- Uses SQLAlchemy to define the TestScenario model.
- Handles database operations for storing and retrieving scenarios.

### File Processing (app.py)
- Processes various file types (DOCX, PDF, TXT, PNG, JPG, JPEG) using libraries like docx2txt, PyPDF2, and pytesseract.
- Implements image analysis using OpenAI's API for PNG, JPG, and JPEG files.

### AI Integration (app.py)
- Communicates with a local LLM server to generate test scenarios.
- Manages system prompt, scenario prompt, and context window size for scenario generation.
- Implements streaming response handling for real-time scenario generation.
- Uses OpenAI API for image analysis.

### User Interface (templates/index.html)
- Provides a responsive web interface for user interactions.
- Implements client-side functionality using JavaScript.
- Handles real-time scenario generation display and abort functionality.
- Manages customization of system prompt, scenario prompt, and context window size.
- Implements file upload with multiple file support.

## Environment Variables (.env)
The application uses the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key for image analysis
- `OPENAI_MODEL`: The OpenAI model to use (default: gpt-4o)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URI`: SQLite database URI
- `LOCAL_LLM_SERVER_URL`: URL of the local LLM server
- `DEBUG`: Debug mode flag (True/False)

## Workflow
1. User creates a new scenario with an automatically assigned name.
2. Documents are uploaded and processed by the server.
3. Extracted information is added to the criteria input.
4. User can modify the criteria if needed.
5. User can customize system prompt, scenario prompt, and context window size.
6. Server generates a test scenario based on criteria and processed files using the local LLM server.
7. Generated scenario is displayed in real-time, with the option to stop generation.
8. Completed scenario is saved to the database and can be exported.
9. Inference statistics are displayed after generation.

## Extending the Application
- To add new file types for processing, extend the `process_file` function in `app.py`.
- To modify the UI, update the `index.html` template and associated JavaScript.
- To change the database schema, update the `TestScenario` model in `app.py` and perform necessary migrations.
- To add new features, create new routes in `app.py` and corresponding UI elements in `index.html`.

## Best Practices
- Follow PEP 8 style guidelines for Python code.
- Write unit tests for new features (use `unittest` or `pytest`).
- Document new methods and functions using docstrings.
- Handle exceptions appropriately and provide user-friendly error messages.
- Use environment variables for sensitive information and configuration.
- Implement proper error handling for asynchronous operations in the frontend.
- Regularly update dependencies and check for security vulnerabilities.

## Troubleshooting
- Ensure the local LLM server is running and accessible at http://localhost:1234.
- Check the server logs for error messages and stack traces.
- Ensure all required dependencies are installed and up to date.
- Verify that the context window size is appropriate for the chosen LLM model.
- Debug frontend issues using browser developer tools and console logs.
- For OpenAI API issues, check your API key and quota.

## Recent Improvements
- Added real-time scenario generation with stop functionality.
- Implemented customizable scenario prompt.
- Added clear history functionality.
- Improved UI responsiveness and feedback.
- Integrated OpenAI API for image analysis.
- Added support for multiple file uploads.
- Implemented inference statistics display.

## Future Improvements
- Implement user authentication and multi-user support.
- Add support for more file formats and AI models.
- Enhance the UI with more interactive features and real-time updates.
- Implement a plugin system for easy extension of file processing capabilities.
- Add a feature to compare and merge multiple scenarios.
- Implement automated testing for both backend and frontend components.
- Improve error handling and user feedback for LLM server connection issues.
- Add support for different LLM providers and models.
- Implement a feature to save and load custom prompt templates.
- Add pagination for scenario history to improve performance with large datasets.
- Enhance the filtering and sorting system for scenarios with more options and better performance.

For any questions or contributions, please contact the project maintainers.
- Add support for more file formats and AI models.
- Enhance the UI with more interactive features and real-time updates.
- Implement a plugin system for easy extension of file processing capabilities.
- Add a feature to compare and merge multiple scenarios.
- Implement automated testing for both backend and frontend components.
- Improve error handling and user feedback for LLM server connection issues.
- Add support for different LLM providers and models.
- Implement a feature to save and load custom prompt templates.
- Add pagination for scenario history to improve performance with large datasets.
- Enhance the filtering and sorting system for scenarios with more options and better performance.
- Implement a progress indicator for scenario generation.
- Add a feature to edit and regenerate parts of a scenario.

For any questions or contributions, please contact the project maintainers.
