# Test Scenario Generator - User Guide

## Introduction
The Test Scenario Generator is an AI-powered web application designed to assist testers and QA professionals in creating comprehensive test scenarios. It analyzes documents (Word, PDF, text files, and images) to generate scenarios that adhere to the IEEE 829 standard. This guide will walk you through the main features and how to use the application effectively.

## Getting Started
1. Open your web browser and navigate to the Test Scenario Generator application URL.
2. You'll see the main interface with the CGI logo, input areas, buttons, and a scenario history section.

## Creating a New Scenario
1. Click the "Create New Scenario" button at the top of the page.
2. The scenario name input, criteria input, and file upload button will become enabled.
3. A default name (e.g., "Scenario 1") will be automatically assigned. You can change this if desired.

## Entering Criteria
1. In the criteria text area, enter the requirements, user stories, or any other relevant information for your test scenario.
2. You can modify this information at any time before generating the scenario.

## Uploading Files
1. Click the "Upload Document" button.
2. Select a file (supported formats: DOC, DOCX, PDF, TXT, PNG, JPG, JPEG).
3. The application will analyze the file and extract relevant information.
4. Extracted information will be automatically added to the criteria text area.
5. If any errors occur during file analysis, you'll see a warning message with details.

## Customizing Prompts and Context Window
1. Click the "Edit System Prompt" button to edit the system prompt used for scenario generation.
2. Click the "Edit Scenario Prompt" button to customize the scenario prompt template for generation.
3. Click the "Edit Context Window" button to select the context window size (4096 or 8192 tokens).

## Generating a Test Scenario
1. After entering criteria and uploading files, click the "Generate Scenario" button.
2. The application will process your input using a local LLM server and generate a test scenario.
3. The generated scenario will appear in real-time in the large text area on the right side of the page.
4. You can stop the generation at any time by clicking the "Stop Generation" button.
5. The scenario will be automatically saved to the database and appear in the scenario history.

## Exporting Scenarios
1. After a scenario is generated, the "Export Scenario" button will turn green.
2. Click the "Export Scenario" button to download the generated scenario as a text file.

## Viewing Scenario History
1. The bottom of the page displays a list of previously generated scenarios.
2. Click on any scenario in the list to view its details, including the name, criteria, and generated scenario.
3. The selected scenario's information will be loaded into the main interface for viewing or further editing.

## Clearing Scenario History
1. To clear all scenario history, click the "Clear History" button at the top of the scenario history section.
2. Confirm the action when prompted. Note that this action cannot be undone.

## Tips for Best Results
- Provide clear and specific criteria for more accurate scenario generation.
- Include relevant documents that describe the functionality you want to test.
- Review and adjust the automatically extracted information from uploaded files if necessary.
- Experiment with different system prompts and scenario prompts to fine-tune the output.
- Adjust the context window size if you need to generate longer scenarios.

## Troubleshooting
- If file analysis fails, ensure the file is not corrupted and is in a supported format.
- Check the browser console for any error messages or issues.
- Verify that all required dependencies are properly installed and configured on the server.
- Ensure that the local LLM server is running and accessible at http://localhost:1234.
- If scenario generation seems stuck, try stopping and restarting the generation process.

For technical issues or further assistance, please refer to the developer documentation or contact the development team.
