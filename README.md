# Google Calendar Schedule Management App

## Overview

This Python application retrieves events from Google Calendar and uses AI to propose and visualize daily schedules.

## Key Features

1. Fetch events from Google Calendar
2. Generate schedule proposals using Gemini AI
3. Visualize schedules
4. Save and load data

## Requirements

- Python 3.7 or higher
- Python libraries:
  - tkinter
  - matplotlib
  - google-auth-oauthlib
  - google-auth
  - google-api-python-client
  - google.generativeai
  - japanize-matplotlib
  - python-dotenv

## Setup

1. Clone or download the repository.
2. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
3. Create a project in Google Cloud Platform and enable the Calendar API and Gemini API.
4. Create an OAuth 2.0 client ID and save it as `credentials.json` in the project's root directory.
5. Obtain a Gemini API key and add it to a `.env` file as follows:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

1. Run `main.py` to start the application:
   ```
   python main.py
   ```
2. Enter the year, month, and day, then click the "Fetch Events" button.
3. Events from Google Calendar will be retrieved, and an AI-generated schedule proposal will be displayed.
4. A visualization of the schedule will appear on the right side.

## File Structure

- `main.py`: Application entry point
- `calendar_app.py`: Main application logic
- `google_calendar_api.py`: Google Calendar API integration
- `gemini_integration.py`: Gemini AI integration
- `schedule_parser.py`: Schedule text parsing
- `schedule_visualizer.py`: Schedule visualization

## Notes

- Google account authentication is required on first run.
- Schedule data is saved in `calendar_data.json`.

## License

This project is released under the MIT License. See the `LICENSE` file for details.