from flask import Flask, request, render_template, jsonify, redirect, session, escape, url_for
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
import threading
from operator import itemgetter
import numpy as np
import datetime
from modules import db


# Block chain
class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # print("\n=======================\n")
            # print(f'{last_block}')
            # print(f'{block}')
            # print("\n=======================\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:

                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            # 'timestamp': time(),
            'timestamp': str(datetime.datetime.now()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, candidate):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'candidate': candidate,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(
            block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @ staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


app = Flask(__name__)


def getUserVote(username):
    db_class = db.Database()
    sql = "SELECT voteWT FROM user WHERE userid = '%s'" % username
    row = db_class.executeAll(sql)
    if row[0]['voteWT'] == 'NO':
        return 0
    else:
        return 1


@app.route('/')
def helloIndex():
    if "username" in session:
        print(session)
        return render_template('index.html', userSession=session["username"], userAuth=session["userauth"])
    else:
        return render_template('index.html')


@app.route('/vote')
def hellohtml():
    if "username" in session:
        # 1. 투표 여부 가져오기
        res = getUserVote(session["username"])
        # 2. 투표 한 사람이면 '이미 투표를 완료했습니다.' alert 띄우기
        if res:
            response = '''alert(' %s님은 이미 투표를 완료했습니다.');''' % session["username"]
            return render_template('index.html', response=response, userSession=session["username"], userAuth=session['userauth'])
        else:
            db_class = db.Database()
            sql = "SELECT * FROM candidate"
            row = db_class.executeAll(sql)

            sql = "SELECT auth FROM user WHERE userid = %s" % session["username"]
            userAuth = db_class.executeAll(sql)
            return render_template('vote.html', response=row, userSession=session["username"], userAuth=userAuth[0]['auth'])
    else:
        return render_template('login.html', response=None)


# 투표 마지막 페이지로 이동
@ app.route('/vote/finish', methods=['POST'])
def finish_vote():
    candidate = request.form['candidate']

    response = '선정 된 후보자 : ' + candidate
    if "username" in session:
        return render_template('fin.html', response=response, userSession=session["username"], userAuth=session['userauth'])
    else:
        return render_template('fin.html', response=response)


# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# add Transaction


@ app.route('/tran/new', methods=['POST'])
def new_tran():

    res = getUserVote(session["username"])

    if res:
        response = '''alert(' %s님은 이미 투표를 완료했습니다.');''' % session["username"]
        return render_template('index.html', response=response, userSession=session["username"], userAuth=session['userauth'])
    else:
        print("session : ", session["username"])
        candidate = request.form['candidate']
        # jsonObj = json.dumps({'location': loc, 'name': name,
        #                       'phone': phone}, ensure_ascii=False)
        jsonObj = json.dumps({'candidate': candidate}, ensure_ascii=False)
        jsonObj = json.loads(jsonObj)
        # required = ['location', 'name', 'phone']
        required = ['candidate']
        if not all(k in jsonObj for k in required):
            return 'Missing values', 400

        # Create a new Transaction
        # index = blockchain.new_transaction(
        #     jsonObj['location'], jsonObj['name'], jsonObj['phone'])
        index = blockchain.new_transaction(
            jsonObj['candidate'])

        db_class = db.Database()

        sql = "UPDATE user SET voteWT = 'YES' WHERE userid = '%s'" % (
            session["username"])
        print(sql)
        db_class.execute(sql)
        db_class.commit()
        # response = {'message': f'Transaction will be added to Block {index}'}
        response = '''alert('🥳 투표해주셔서 감사합니다. 🥳');'''
        # return jsonify(response), 201
        if "username" in session:
            return render_template('index.html', response=response, userSession=session["username"], userAuth=session['userauth'])
        else:
            return render_template('index.html', response=response)


# mine new block
# @ app.route('/mine/new', methods=['GET'])
def new_mine():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        print(':: Our chain was replaced ::')
        # 'new_chain': blockchain.chain

    else:
        print(':: Our chain is representative ::')

    # 노드 검증
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    # response = {
    #     'message': "New Block Forged",
    #     'index': block['index'],
    #     'transactions': block['transactions'],
    #     'proof': block['proof'],
    #     'previous_hash': block['previous_hash'],
    # }

    # response = '''alert('%s번째 블록이 생성되었습니다. proof=%s');''' % (
    #     block['index'], block['proof'])
    response = '''[ NOTICE ] %s번째 블록이 생성되었습니다. | proof=%s | transaction Length=%s |''' % (
        block['index'], block['proof'], len(block['transactions']))

    print(response)
    threading.Timer(5, new_mine).start()
    # if "username" in session:
    #     print(response)
    #     return render_template('index.html', response=response, userSession=session["username"])
    # else:
    #     return render_template('index.html', response=response)


@ app.route('/new_mines', methods=['GET'])
def new_mines():
    # blockchain.resolve_conflicts()

    # 노드 검증
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    # response = {
    #     'message': "New Block Forged",
    #     'index': block['index'],
    #     'transactions': block['transactions'],
    #     'proof': block['proof'],
    #     'previous_hash': block['previous_hash'],
    # }

    # response = '''alert('%s번째 블록이 생성되었습니다. proof=%s');''' % (
    #     block['index'], block['proof'])
    response = '''[ NOTICE ] %s번째 블록이 생성되었습니다. | proof=%s | transaction Length=%s |''' % (
        block['index'], block['proof'], len(block['transactions']))

    print(response)
    # threading.Timer(5, new_mine).start()
    # if "username" in session:
    #     print(response)
    #     return render_template('index.html', response=response, userSession=session["username"])
    # else:
    #     return render_template('index.html', response=response)
    return render_template('index.html')


@ app.route('/chain', methods=['GET'])
def full_chain():
    userid = session["username"]
    db_class = db.Database()
    sql = "SELECT auth FROM user WHERE userid = '%s'" % userid
    row = db_class.executeAll(sql)
    userAuth = row[0]['auth']

    if userAuth == 'admin':
        # # 노드 검증
        # replaced = blockchain.resolve_conflicts()

        # if replaced:
        #     print(':: Our chain was replaced ::')
        #     # 'new_chain': blockchain.chain

        # else:
        #     print(':: Our chain is representative ::')
        # sort block by index - descending

        # chains = sorted(blockchain.chain, key=(lambda x: x['index']), reverse=True)
        chains = blockchain.chain
        response = {
            # 'chain': blockchain.chain,
            'chain': chains,
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200
        # return json.dumps(response), 200
    else:
        return render_template('index.html', authflag='''alert('접근할 수 없는 권한입니다.');location.href='/';''')


@ app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@ app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        print(':: Our chain was replaced ::')
        # 'new_chain': blockchain.chain

    else:
        print(':: Our chain is representative ::')
        # 'chain': blockchain.chain

    # return jsonify(response), 200
    if "username" in session:
        return render_template('index.html')
    else:
        return render_template('index.html')


@ app.route('/total')
# AUTO_INCREMENT를 반드시 1로 수정하고 진입해야 한다. 아니면 리스트 오류 걸림
def getTotal():
    # 현재 블록체인 길이
    chainLength = len(blockchain.chain)

    # 데이터베이스에서 현재 후보자 수 가져오기
    db_class = db.Database()
    sql = "SELECT COUNT(*) FROM candidate"
    row = db_class.executeAll(sql)

    if row[0]['COUNT(*)'] == 0:
        flag = False
        if "username" in session:
            return render_template('total.html', flag=flag, userSession=session["username"], userAuth=session['userauth'])
        else:
            return render_template('total.html', flag=flag)
    else:
        flag = True
        # USE row[0]['COUNT(*)']
        candArr = []
        for i in range(0, row[0]['COUNT(*)']):
            candArr.append(0)
        print(candArr)

        total_len = 0

        for blockLength in range(chainLength):
            total_len = total_len + \
                len(blockchain.chain[blockLength]['transactions'])
            for tranLength in range(len(blockchain.chain[blockLength]['transactions'])):
                candNum = int(blockchain.chain[blockLength]
                              ['transactions'][tranLength]['candidate'])
                print(candArr)
                print(candArr[candNum-1])
                candArr[candNum-1] = candArr[candNum-1]+1

        print(candArr)
        print('총 투표자 수 : ', total_len)

        max = candArr[0]
        maxIdx = 0
        superiority = ''
        for i in range(1, len(candArr)):
            if max < candArr[i]:
                max = candArr[i]
                maxIdx = i+1
                superiority = str(maxIdx)+'번 후보자가 우세!'
            elif max == candArr[i]:
                superiority = '박빙!'

        if "username" in session:
            return render_template('total.html', flag=flag, chainLength=chainLength, candData=candArr, total_len=total_len, superiority=superiority, userSession=session["username"], userAuth=session['userauth'])
        else:
            return render_template('total.html', flag=flag, chainLength=chainLength, candData=candArr, total_len=total_len, superiority=superiority)


@ app.route('/signup')
def goSignup():
    return render_template('signup.html')


@ app.route('/signup/progress', methods=['POST'])
def signupProg():
    # 폼 데이터 가져오기
    userid = request.form['userid']
    print('USER MAJOR : ', userid)
    userpw = request.form['userpw']
    print('USER MAJOR : ', userpw)
    usermajor = request.form['usermajor']
    print('USER MAJOR : ', usermajor)

    # 데이터베이스 생성자
    db_class = db.Database()

    # 1. 테이블에 데이터가 이미 있는지 확인하기
    sql = "SELECT COUNT(*) FROM user WHERE userid = '%s'" % userid
    row = db_class.executeAll(sql)
    if row[0]['COUNT(*)'] == 1:
        response = '''alert('이미 존재하는 아이디입니다.');'''
    else:
        # 2. 없으면 테이블에 인서트 하기
        sql = "INSERT INTO user(userid, userpw, major) VALUES('%s','%s','%s');" % (
            userid, userpw, usermajor)

        db_class.execute(sql)
        db_class.commit()
        response = '''alert('회원가입 완료!');'''

    return render_template('index.html', response=response)


@ app.route('/login')
def goLogin():
    return render_template('login.html')


app.secret_key = "ABCDEFG"


@ app.route('/login/progress', methods=['POST'])
def loginProg():
    # 폼 데이터 가져오기
    userid = request.form['userid']
    userpw = request.form['userpw']

    db_class = db.Database()

    sql = "SELECT COUNT(*) FROM user WHERE userid = '%s' and userpw = '%s'" % (userid, userpw)
    row = db_class.executeAll(sql)
    sql = "SELECT auth FROM user WHERE userid = '%s'" % (userid)
    row2 = db_class.executeAll(sql)
    print(row2)
    if row[0]['COUNT(*)'] == 1:
        session["username"] = userid
        session["userauth"] = row2[0]['auth']
        response = '''location.href='/';'''
        return render_template('index.html', response=response, userSession=session["username"], userAuth=session['userauth'])
    else:
        response = '''alert('입력 정보를 확인하세요.');'''
        return render_template('login.html', response=response)


@ app.route('/logout')
def logout():
    session.clear()
    return redirect("/", code=302)


@ app.route('/freshUser')
def fresh():
    if session['userauth'] == 'admin':
        db_class = db.Database()
        sql = "UPDATE user SET voteWT = 'NO'"
        db_class.execute(sql)
        db_class.commit()
        response = '''alert('초기화 완료!')'''
        if "username" in session:
            return render_template('index.html', response=response, userSession=session["username"], userAuth=session['userauth'])
        else:
            return render_template('index.html', response=response)
    else:
        return render_template('index.html', response=None, userSession=session["username"], userAuth=session['userauth'], authflag='''alert('접근할 수 없는 권한입니다.'); location.href='/';''')


@app.route('/scope')
def scope():
    # 노드 검증
    # replaced = blockchain.resolve_conflicts()

    # if replaced:
    #     print(':: Our chain was replaced ::')
    #     # 'new_chain': blockchain.chain

    # else:
    #     print(':: Our chain is representative ::')
    # data = sorted(blockchain.chain, key=(
    #     lambda x: x['index']), reverse=True)
    data = []
    # data = np.array(np.arange(1, len(blockchain.chain)+1))
    for i in range(1, len(blockchain.chain)+1):
        data.append(i)
    data_sort = data.sort(reverse=True)
    print(data_sort)
    chains = blockchain.chain
    if "username" in session:
        return render_template('scope.html', data=data, userSession=session["username"], chain=chains, userAuth=session['userauth'])
    else:
        return render_template('scope.html', data=data, chain=chains)


@app.route('/start')
def start():
    new_mine()
    return render_template('index.html')


@app.route('/scope/<index>')
def scope_index(index):
    index = int(index)
    response = '''
        {0} <br/> {1} <br/> {2} <br/> {3}
    '''.format(blockchain.chain[index-1]['timestamp'], blockchain.chain[index-1]['proof'], blockchain.chain[index-1]['transactions'], blockchain.chain[index-1]['previous_hash'])
    return "{}".format(response)


@app.route('/regCandidate')
def register_candidate():
    return render_template('regCandidate.html', userSession=session["username"], userAuth=session['userauth'])


@app.route('/regCandidate/progress', methods=['POST'])
def reg_candidate_progress():
    lst_candName = request.form.getlist('candidate_name')
    lst_candDep = request.form.getlist('stuPresident_dep')
    cand_msg = request.form['msgCandidate']
    print(lst_candName)
    print(lst_candDep)
    print(cand_msg)
    # 데이터베이스 생성자
    db_class = db.Database()
    sql = "INSERT INTO candidate(cand1, cand1_dep, cand2, cand2_dep, cand3, cand3_dep, candMsg) VALUES('%s','%s','%s', '%s','%s','%s','%s');" % (
        lst_candName[0], lst_candDep[0], lst_candName[1], lst_candDep[1], lst_candName[2], lst_candDep[2], cand_msg)

    db_class.execute(sql)
    db_class.commit()

    return render_template('index.html', userSession=session['username'], userAuth=session['userauth'])


@app.route('/manageCandidate')
def manage():
    db_class = db.Database()
    sql = "SELECT * FROM candidate"
    row = db_class.executeAll(sql)

    return render_template('manage.html', data=row, userSession=session["username"], userAuth=session['userauth'])


@app.route('/manageCandidate/progress', methods=['GET'])
def manage_process():
    num = int(request.args.get('candNum'))
    print('num : ', num)
    activity = int(request.args.get('act'))
    print('activity : ', activity)
    if activity == 1:
        # delete
        db_class = db.Database()
        sql = "DELETE FROM candidate where idx = %s" % num
        print(sql)
        db_class.execute(sql)
        db_class.commit()
        return redirect('/manageCandidate?flag=1')
    if activity == 2:
        return redirect('/modCandidate/mod/'+str(num))


@app.route('/modCandidate/mod/<candNum>')
def modify_candidate(candNum):
    db_class = db.Database()
    sql = "SELECT * FROM candidate where idx = %s" % candNum
    row = db_class.executeAll(sql)
    print(row)
    return render_template('modCandidate.html', data=row, userSession=session["username"], userAuth=session['userauth'])


@app.route('/modCandidate/progress', methods=['POST'])
def mod_candidate_progress():
    candNum = request.form.get('candNum')
    lst_candName = request.form.getlist('candidate_name')
    lst_candDep = request.form.getlist('stuPresident_dep')
    cand_msg = request.form['msgCandidate']
    print(candNum)
    print(lst_candName)
    print(lst_candDep)
    print(cand_msg)
    # 데이터베이스 생성자
    db_class = db.Database()
    sql = "UPDATE candidate SET cand1='%s', cand1_dep='%s', cand2='%s', cand2_dep='%s', cand3='%s', cand3_dep='%s', candMsg='%s' WHERE idx='%s';" % (
        lst_candName[0], lst_candDep[0], lst_candName[1], lst_candDep[1], lst_candName[2], lst_candDep[2], cand_msg, candNum)
    print(sql)

    db_class.execute(sql)
    db_class.commit()

    return render_template('index.html', userSession=session['username'], userAuth=session['userauth'])


@app.route('/indexReset')
def indexReset():
    try:
        db_class = db.Database()
        sql = "alter table candidate auto_increment=1;"
        db_class.execute(sql)
        db_class.commit()
        authflag = '''alert('인덱스 초기화 완료!');location.href='/';'''
        return render_template('index.html', userSession=session['username'], userAuth=session['userauth'], authflag=authflag)
    except:
        print('예외 발생')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    new_mine()
    app.run(host='0.0.0.0', port=port, debug=True,
            use_reloader=False, threaded=True)
