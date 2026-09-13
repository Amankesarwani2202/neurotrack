# NEUROTRACK - Cognitive & Motor Screening Application

A web-based suite of quick cognitive and motor micro-tests for screening purposes.

## Features

- **Reaction Time Test**: Measures response speed
- **Stroop Test**: Tests attention and cognitive flexibility
- **Memory Test**: Short-term numerical recall
- **Spiral Drawing Test**: Evaluates motor smoothness and tremor
- **PDF Report Generation**: Comprehensive analysis with risk scoring
- **Participant Data Collection**: Stores participant demographics, family-history response, and test scores in `participants.json`

## Deployment

This application is configured for deployment on Vercel.

### Quick Deploy

1. Push this repository to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Click "Deploy"

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open http://localhost:5000
```

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Analysis**: NumPy
- **PDF Generation**: ReportLab
- **Hosting**: Vercel (Serverless)

## Data Access

Participant records are written to `participants.json` by default. Set `NEUROTRACK_DATA_FILE` to choose another JSON path. The records can be read through `GET /participants`; test results are attached after `POST /analyze_all`. A response of “I do not know” stores the participant's test scores as `null`.

For persistent Vercel storage, configure these server-side environment variables:

- `GITHUB_TOKEN`: fine-grained token with Contents read/write access to the repository
- `GITHUB_REPOSITORY`: repository in `owner/name` form
- `GITHUB_DATA_PATH`: optional JSON path, default `participants.json`

When configured, the Flask server reads and commits the JSON file through GitHub's Contents API. Keep the token private and use a private repository for participant data. GitHub is file-backed storage rather than a database, so high-volume concurrent submissions may require a database instead.

The Cookie Theft image is “Interior view of an Indian kitchen in West Bengal” by Billjones94, used under CC BY-SA 4.0 from Wikimedia Commons.

## Disclaimer

This tool is for informational screening purposes only and is not a medical diagnostic device.

## License

MIT