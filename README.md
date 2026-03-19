YouTube Analyzer

YouTube Analyzer is a Python OSINT tool designed to analyze public YouTube channels, extract video statistics, interactions, and generate a JSON report for further analysis. The project uses the YouTube API and requires a secure API key.

 ====Features:====

Search and analyze a YouTube channel by name.

Retrieve key information: subscribers, videos, total views.

Analyze the latest 20 videos (likes, comments, video views).

Extract the top 5 most active users (frequent commenters).

Export results in JSON format.

Secure API key usage via environment variable (YT_API_KEY).

 ====Requirements:====

Python 3.10+

Python modules:

pip install google-api-python-client

YouTube API key with access to the YouTube Data API v3.

Set the environment variable:

export YT_API_KEY="YOUR_API_KEY"

 ====Installation:====

Clone the repository:

git clone git@github.com:Soum59/youtube-analyzer.git

Navigate into the project folder:

cd youtube-analyzer

Create and activate a Python virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install google-api-python-client

Set your API key as an environment variable:

export YT_API_KEY="YOUR_API_KEY"
 Usage:

Analyze a YouTube channel:

python3 project.py --target "ChannelName"

Available options:

--target "ChannelName" : Name of the channel to analyze.

--output : Export results to a JSON report.

--max-videos N : Maximum number of videos to analyze (default 20).

====Example:====

python3 project.py --target "Name_Of_The_Analyzed_Channel" --output --max-videos 30
 Project Structure:
youtube-analyzer/
├── project.py          # Main script
├── README.md           # Project documentation
├── venv/               # Python virtual environment
├── sessions/           # (optional) sessions if used
└── report_<channel>.json # JSON reports generated after analysis
 Security:

Never include the API key in the code or on GitHub.

Always use an environment variable to store the key.

Do not share the project.py file containing the key in plaintext.

 Sample Output:
Channel: Name_Of_The_Analyzed_Channel
Subscribers: 123,456
Videos analyzed: 20
Total views: 1,234,456

Top commenters:
- @user1
- @user2
- @user3
- @user4
- @user5

 Technologies:

Python 3.10+
Google API Client for Python
YouTube Data API v3
