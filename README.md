# NEUROTRACK - Cognitive & Motor Screening Application

A web-based suite of quick cognitive and motor micro-tests for screening purposes.

## Features

- **Reaction Time Test**: Measures response speed
- **Stroop Test**: Tests attention and cognitive flexibility
- **Memory Test**: Short-term numerical recall
- **Spiral Drawing Test**: Evaluates motor smoothness and tremor
- **PDF Report Generation**: Comprehensive analysis with risk scoring

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

## Disclaimer

This tool is for informational screening purposes only and is not a medical diagnostic device.

## License

MIT