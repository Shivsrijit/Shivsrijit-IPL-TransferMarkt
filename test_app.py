from flask import Flask, render_template
import os

app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'templates')))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True) 