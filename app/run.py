from flask import Flask, request, render_template, jsonify, redirect, session, escape
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
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
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
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
            'timestamp': time(),
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


@app.route('/')
def helloIndex():
    if "username" in session:
        return render_template('index.html', userSession=session["username"])
    else:
        return render_template('index.html')


@app.route('/vote')
def hellohtml():
    if "username" in session:
        return render_template('vote.html', response=None, userSession=session["username"])
    else:
        return render_template('vote.html', response=None)


# 투표 마지막 페이지로 이동
@app.route('/vote/finish', methods=['POST'])
def finish_vote():
    candidate = request.form['candidate']

    response = '선정 된 후보자 : ' + candidate
    if "username" in session:
        return render_template('fin.html', response=response, userSession=session["username"])
    else:
        return render_template('fin.html', response=response)


# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# add Transaction


@ app.route('/tran/new', methods=['POST'])
def new_tran():
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

    # response = {'message': f'Transaction will be added to Block {index}'}
    response = '🥳 투표해주셔서 감사합니다. 🥳'
    # return jsonify(response), 201
    if "username" in session:
        return render_template('fin.html', response=response, userSession=session["username"])
    else:
        return render_template('fin.html', response=response)


# mine new block
@ app.route('/mine/new', methods=['GET'])
def new_mine():
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

    response = '{0}번째 블록이 생성되었습니다. proof={1}'.format(
        block['index'], block['proof'])
    if "username" in session:
        return render_template('index.html', response=response, userSession=session["username"])
    else:
        return render_template('index.html', response=response)


@ app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


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
        response = ':: Our chain was replaced ::'
        # 'new_chain': blockchain.chain

    else:
        response = ':: Our chain is representative ::'
        # 'chain': blockchain.chain

    # return jsonify(response), 200
    if "username" in session:
        return render_template('index.html', response=response, userSession=session["username"])
    else:
        return render_template('index.html', response=response)


@app.route('/total')
def getTotal():
    chainLength = len(blockchain.chain)
    # test = blockchain.chain[2]['transactions']

    candidate_1 = 0
    candidate_2 = 0
    total_len = 0

    for blockLength in range(chainLength):
        total_len = total_len + \
            len(blockchain.chain[blockLength]['transactions'])
        for tranLength in range(len(blockchain.chain[blockLength]['transactions'])):
            if blockchain.chain[blockLength]['transactions'][tranLength]['candidate'] == '1':
                candidate_1 = candidate_1 + 1
            else:
                candidate_2 = candidate_2 + 1

    print('candidate 1 : ', candidate_1)
    print('candidate_2 : ', candidate_2)
    print('총 투표자 수 : ', total_len)

    if "username" in session:
        return render_template('total.html', chainLength=chainLength, candidate_1=candidate_1, candidate_2=candidate_2, total_len=total_len, userSession=session["username"])
    else:
        return render_template('total.html', chainLength=chainLength, candidate_1=candidate_1, candidate_2=candidate_2, total_len=total_len)


@app.route('/signup')
def goSignup():
    return render_template('signup.html')


@app.route('/signup/progress', methods=['POST'])
def signupProg():
    # 폼 데이터 가져오기
    userid = request.form['userid']
    userpw = request.form['userpw']

    # 데이터베이스 생성자
    db_class = db.Database()

    # 1. 테이블에 데이터가 이미 있는지 확인하기
    sql = "SELECT COUNT(*) FROM user WHERE userid = '%s'" % userid
    row = db_class.executeAll(sql)
    if row[0]['COUNT(*)'] == 1:
        response = '''alert('이미 존재하는 아이디입니다.');'''
    else:
        # 2. 없으면 테이블에 인서트 하기
        sql = "INSERT INTO user(userid, userpw) VALUES('%s','%s');" % (
            userid, userpw)

        db_class.execute(sql)
        db_class.commit()
        response = '''alert('회원가입 완료!');'''

    return render_template('index.html', response=response)


@app.route('/login')
def goLogin():
    return render_template('login.html')


app.secret_key = "ABCDEFG"


@app.route('/login/progress', methods=['POST'])
def loginProg():
    # 폼 데이터 가져오기
    userid = request.form['userid']
    userpw = request.form['userpw']

    db_class = db.Database()

    sql = "SELECT COUNT(*) FROM user WHERE userid = '%s' and userpw = '%s'" % (userid, userpw)
    row = db_class.executeAll(sql)
    if row[0]['COUNT(*)'] == 1:
        session["username"] = userid
        response = '''alert('로그인 성공! %s');''' % session["username"]
        userSession = session["username"]
        return render_template('index.html', response=response, userSession=session["username"])
    else:
        response = '''alert('입력 정보를 확인하세요.');'''
        return render_template('login.html', response=response)


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/", code=302)


if __name__ == '__main__':
    app.run(debug=True)
