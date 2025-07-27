# IPL Analytics System

A comprehensive analytics platform for IPL cricket data, providing insights for fans, players, and team owners.

## Features

- 🔍 Advanced search functionality for players and teams
- 👥 Role-based access (Normal Users, Team Owners)
- 📊 Interactive dashboards with detailed statistics
- 📈 Performance analytics and trends
- 💰 Financial analysis for team owners
- 🔄 Real-time data updates

## Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML/CSS/JavaScript with Chart.js
- **Data Collection**: Web Scraping (BeautifulSoup/Selenium)
- **Visualization**: Plotly/Dash

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up MySQL database and update configuration
5. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

```
ipl_analytics/
├── app/
│   ├── static/          # CSS, JS, images
│   ├── templates/       # HTML templates
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   └── utils/          # Helper functions
├── scraper/            # Web scraping scripts
├── tests/              # Unit tests
├── config.py           # Configuration
├── app.py             # Application entry point
└── requirements.txt    # Dependencies
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 