from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/vote')
def hellohtml():
    return render_template('vote.html')


@app.route('/vote/finish', methods=['POST'])
def finish_vote():
    candidate = request.form['candidate']

    response = '선정 된 후보자 : ' + candidate
    return render_template('fin.html', response=response)


if __name__ == '__main__':
    app.run(debug=True)
