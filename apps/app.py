from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/hello')
def hellohtml():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)
