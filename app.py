from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/docs/<framework>')
def framework_docs(framework):
    return render_template(f'docs_{framework}.html')

@app.route('/docs/<framework>/<page>')
def doc_page(framework, page):
    return render_template(f'docs_{framework}_{page}.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
