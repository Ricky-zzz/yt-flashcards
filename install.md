git clone https://github.com/Ricky-zzz/yt-flashcards.git
cd yt-flashcards
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python tests/pipeline_test.py "https://youtu.be/<VIDEO_ID>"