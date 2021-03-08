from flask import Flask, json, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["users"]


def genReturn(status, msg):
    retJson = {"staus": status, "msg": msg}
    return retJson


def UserExists(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True


class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExists(username):
            return jsonify(genReturn(301, "invalid username"))

        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        users.insert(
            {
                "username": username,
                "password": hashed_pw,
                "own": 0,
                "dept": 0,
            }
        )

        return jsonify(genReturn(200, "succesfully signed up to the API"))


def verifyPassword(username, password):
    if not UserExists(username):
        return False

    hashed_pw = users.find({"username": username})[0]["password"]

    if bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def cashWithUser(username):
    cash = users.find({"username": username})[0]["own"]
    return cash


def debtWithUser(username):
    debt = users.find({"username": username})[0]["debt"]
    return debt


def verifyCredentials(username, password):
    if not UserExists(username):
        return genReturn(301, "invalid username"), True

    correct_pw = verifyPassword(username, password)
    if not correct_pw:
        return genReturn(302, "incorrect password"), True

    return None, False


def updateAccount(username, balance):
    users.update({"username": username}, {"$set": {"own": balance}})


def updateDebt(username, balance):
    users.update({"username": username}, {"$set": {"debt": balance}})


class Add(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        retJson, error = verifyCredentials(username, password)

        if error:
            return jsonify(retJson)

        if amount <= 0:
            return jsonify(genReturn(304, "the amount entered must be greater then 0"))

        cash = cashWithUser(username)
        fee = amount / 100
        amount = fee * 99
        bank_cash = cashWithUser("BANK")
        updateAccount("BANK", bank_cash + fee)
        updateAccount(username, cash + amount)

        return jsonify(200, "the amount has been deposited succesfully")


class Transfer(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        to = postedData["to"]
        amount = postedData["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(username)
        if cash < amount:
            return jsonify(genReturn(304, "not enough money on your account"))

        if not UserExists(to):
            return genReturn(301, "receriver username is invalid")

        cash_from = cashWithUser(username)
        cash_to = cashWithUser(to)
        cash_bank = cashWithUser("BANK")

        fee = amount / 100
        amount = fee * 99

        updateAccount("BANK", cash_bank + fee)
        updateAccount(username, cash_from - amount)
        updateAccount(to, cash_to + amount)

        return jsonify(genReturn(200, "transaction complete"))


class Balance(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        balanceJson = users.find({"username": username}, {"password": 0, "_id": 0})[0]

        return jsonify({"status": 200, "msg": balanceJson})


class TakeLoan(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(username)
        debt = debtWithUser(username)

        updateAccount(username, cash + amount)
        updateDebt(username, debt + amount)

        return jsonify(genReturn(200, "succesfully added the loan to your account"))


class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(username)
        debt = debtWithUser(username)

        if cash < amount:
            return jsonify(genReturn(303, "not enough money on your account"))

        updateAccount(username, cash - amount)
        updateDebt(username, debt - amount)

        return jsonify(genReturn(200, "succesfully payed your loan to the bank"))


api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(TakeLoan, "/takeloan")
api.add_resource(PayLoan, "/payloan")

if __name__ == "__main__":
    app.run(host="0.0.0.0")