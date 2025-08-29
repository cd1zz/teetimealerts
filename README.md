# TeeTime Alerts Preferences Manager

A Python command-line tool for managing golf tee time preferences and alerts through the TeeTimeAlerts.io API. This script allows golfers to automatically update their tee time preferences for specific courses, dates, times, and party sizes.

## Features

- 🏌️ Interactive golf course selection based on ZIP code
- 📅 Flexible date and time preferences
- 👥 Configurable party size (1-4 players)
- 💾 Persistent local configuration storage
- 🔐 Secure authentication via Google Identity Toolkit
- ✅ Input validation and error handling

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. Create a `.env` file in the project directory with your TeeTimeAlerts credentials:
   ```
   EMAIL=your_email@example.com
   PASSWORD=your_password
   ```

2. Run the script for the first time to set up your default courses:
   ```bash
   python teetimealerts.py --start_time 6 --end_time 10 --date 2025-09-01 --num_players 2
   ```

   The first run will prompt you to:
   - Enter your ZIP code
   - Select golf courses from your area

## Usage

### Basic Command

```bash
python teetimealerts.py --start_time <hour> --end_time <hour> --date <YYYY-MM-DD> --num_players <1-4>
```

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--start_time` | Start time hour in 24hr format (0-23) | `6` (for 6 AM) |
| `--end_time` | End time hour in 24hr format (0-23) | `12` (for 12 PM) |
| `--date` | Date in YYYY-MM-DD format | `2025-09-01` |
| `--num_players` | Number of players (1-4) | `2` |

### Examples

```bash
# Set preferences for morning tee times on September 1st for 2 players
python teetimealerts.py --start_time 6 --end_time 10 --date 2025-09-01 --num_players 2

# Set preferences for afternoon tee times on September 15th for 4 players
python teetimealerts.py --start_time 12 --end_time 17 --date 2025-09-15 --num_players 4

# Early morning tee time for a single player
python teetimealerts.py --start_time 5 --end_time 8 --date 2025-10-01 --num_players 1
```

## Configuration

### Course Selection

On first run, the script will:
1. Ask for your ZIP code
2. Search for golf courses within 50 miles
3. Present an interactive list for selection
4. Save your preferences locally

Your course preferences are stored in `~/.teetimealerts/config.json` and will be reused for subsequent runs.

### Resetting Courses

To change your default courses, when prompted "Use these courses?", type `reset` to go through the course selection process again.

## File Structure

```
teetimealerts/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── teetimealerts.py         # Main script
├── CLAUDE.md                # Developer documentation
└── .env                     # Credentials (create this file)
```

## Dependencies

- **requests** (2.31.0) - HTTP library for API calls
- **python-dotenv** (1.0.0) - Environment variable management

## How It Works

1. **Authentication**: Uses Google Identity Toolkit to authenticate with your TeeTimeAlerts account
2. **Course Discovery**: Searches for golf courses by ZIP code within a configurable radius
3. **Preference Updates**: Sends your time, date, and course preferences to the TeeTimeAlerts API
4. **Local Storage**: Saves your course selections for future use

## Security Notes

- Credentials are stored in a local `.env` file (not committed to version control)
- The script uses secure HTTPS connections for all API calls
- Authentication tokens are used only for the current session

## Error Handling

The script includes comprehensive error handling for:
- Invalid time ranges and date formats
- Missing or incorrect credentials
- Network connectivity issues
- API response errors
- Invalid course selections

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your EMAIL and PASSWORD in the `.env` file
   - Check that your TeeTimeAlerts account is active

2. **No Courses Found**
   - Verify your ZIP code is correct
   - The search radius is set to 50 miles by default

3. **Invalid Date/Time**
   - Ensure date is in YYYY-MM-DD format
   - Start time must be before end time
   - Times are in 24-hour format (0-23)

### Reset Configuration

To reset your saved course preferences, delete the configuration file:
```bash
rm ~/.teetimealerts/config.json
```

## Contributing

This is a personal automation script. Feel free to fork and modify for your own use.

## License

This project is for personal use. Please respect TeeTimeAlerts.io's terms of service when using this tool.
