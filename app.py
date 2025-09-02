from flask import Flask, render_template

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
    app.run(debug=True)
