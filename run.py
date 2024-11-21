# run.py
from app.app import app

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port=8050)
    