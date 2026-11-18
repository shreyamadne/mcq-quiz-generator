# AI-Powered MCQ Quiz Generator

An AI-powered application that automatically generates multiple-choice questions from study material using Google's Gemini API.

## Features

- Generate MCQs from pasted chapter text.
- Choose the number of questions.
- Select difficulty: Easy, Medium, or Hard.
- Four options for every question.
- Submit answers and calculate your score.
- View correct answers and explanations.

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- python-dotenv

## Installation and Setup

1. Clone this repository:

   `git clone https://github.com/shreyamadne/mcq-quiz-generator.git`

2. Open the project folder:

   `cd mcq-quiz-generator`

3. Create a virtual environment:

   `python -m venv venv`

4. Activate it on Windows:

   `venv\Scripts\activate`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Create a `.env` file in the project folder and add your own Gemini API key:

   `GEMINI_API_KEY=your_api_key_here`

7. Run the application:

   `streamlit run app.py`

## Security

Never upload your `.env` file or share your API key publicly.

## Author

Shreya Madne