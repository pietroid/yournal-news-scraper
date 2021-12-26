echo 'Installing Python dependencies'
python3 -m venv lib/
source lib/bin/activate
pip3 install -r requirements.txt