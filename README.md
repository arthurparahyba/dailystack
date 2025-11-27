# DevFlashcards

A desktop application for developers to learn new concepts via daily flashcards.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

## Packaging

To create a standalone Windows executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Generate the executable:

   **Option A: Release Build (No Debug Console)**
   This uses the default configuration in `build.spec`.
   ```bash
   python -m PyInstaller build.spec
   ```

   **Option B: Debug Build (With Console)**
   To see print statements and debug information, run:
   ```bash
   python -m PyInstaller --debug=all --console --add-data "web;web" --name DevFlashcards_Debug app.py
   ```
   *Note: On Windows, use `;` as separator for `--add-data`. On Linux/Mac use `:`.*

3. The executable will be in the `dist` folder.

## Configuration

The application currently uses mock data. To connect to a real LLM:
1. Update `backend/api.py` with the real API URL.
2. Ensure the API returns the expected JSON format.
