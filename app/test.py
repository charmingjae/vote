from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as current_app
from flask import Flask

from modules import db


test = Flask(__name__)


@test.route('/', methods=['GET'])
def index():
    return render_template('dbTest.html',
                           result=None,
                           resultData=None,
                           resultUPDATE=None)


# INSERT 함수 예제
@test.route('/insert', methods=['GET'])
def insert():
    db_class = db.Database()

    sql = "INSERT INTO testDB.testTable(test) \
                VALUES('%s')" % ('testData')
    db_class.execute(sql)
    db_class.commit()

    return render_template('dbTest.html',
                           result='insert is done!',
                           resultData=None,
                           resultUPDATE=None)


# SELECT 함수 예제
@test.route('/select', methods=['GET'])
def select():
    db_class = db.Database()

    sql = "SELECT idx, test \
                FROM testDB.testTable"
    row = db_class.executeAll(sql)

    print(row)

    return render_template('dbTest.html',
                           result=None,
                           resultData=row[0],
                           resultUPDATE=None)


# UPDATE 함수 예제
@test.route('/update', methods=['GET'])
def update():
    db_class = db.Database()

    sql = "UPDATE testDB.testTable \
                SET test='%s' \
                WHERE test='testData'" % ('update_Data')
    db_class.execute(sql)
    db_class.commit()

    sql = "SELECT idx, test \
                FROM testDB.testTable"
    row = db_class.executeAll(sql)

    return render_template('dbTest.html',
                           result=None,
                           resultData=None,
                           resultUPDATE=row[0])


if __name__ == '__main__':
    test.run(debug=True)
