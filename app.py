from RIS import app
import os

if __name__ == '__main__':
    port = os.environ.get('PORT')
    app.run(debug=True, port=port)