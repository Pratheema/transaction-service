#!/usr/bin/python
"""
This module implements transaction service APIs and exposes them for RESTful access.

The idea here is to store transactions (in-memory) and return information about
those transactions.

API Spec:
    1.  PUT /transactionservice/transaction/$transaction_id
        
        Body: { "amount":double,"type":string,"parent_id":long }
        where:
            - transaction_id is a long specifying a new transaction
            - amount is a double specifying the amount
            - type is a string specifying a type of the transaction.
            - parent_id is an optional long that may specify the parent transaction of this transaction.

    2.  GET /transactionservice/transaction/$transaction_id
        
        Returns: { "amount":double,"type":string,"parent_id":long }

    3.  GET /transactionservice/types/$type
        
        Returns: [long, long, ... ]
        
        A json list of all transaction ids that share the same type $type.

    4.  GET /transactionservice/sum/$transaction_id
        
        Returns: { "sum": double }
        
        A sum of all transactions that are transitively linked by their parent_id to $transaction_id.

@author: Pratheema Raman <pratheema5@gmail.com>
"""
from flask import Flask, request, jsonify, abort, make_response, render_template

app = Flask(__name__)

# Keys as per the transaction service spec
TRANSACTION_ID        = "transaction_id"
TRANSACTION_TYPE      = "type"
TRANSACTION_AMOUNT    = "amount"
TRANSACTION_PARENT_ID = "parent_id"

# Types as per transaction service spec
param_types = { TRANSACTION_ID        : long,
                TRANSACTION_TYPE      : str,
                TRANSACTION_AMOUNT    : float,
                TRANSACTION_PARENT_ID : long
              }

# Required keys for a transaction
required_keys = [TRANSACTION_AMOUNT, TRANSACTION_TYPE]

SUM         = "sum"
MESSAGE     = "message"
BAD_REQUEST = "Bad Request"
VALUE_ERROR = "Value Error: %s"
STATUS_OK   = {"status": "ok"}
REQUIRED_PARAM_ERROR        = "%s is required"
INVALID_TRANSACTION_ERROR   = "Invalid transaction id"
INVALID_PARENT_ERROR        = "Invalid parent id"
DUPLICATE_TRANSACTION_ERROR = "Transaction with id %s already exists. Choose another id"

# Transactions stored in-memory
transactions = {}

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': error.description['message']}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def _get_typed_attr(attr, attr_val):
    attr_type = param_types[attr]
    try:
        return param_types[attr](attr_val)
    except ValueError:
        abort(400, {MESSAGE: VALUE_ERROR % attr})


def _sanitize_data(**request_data):
    """
    Sanitizes and validates input data

    @param request_data:
        input data as keyword arguments
    @return:
        Input data sanitized and validated
    """
    request_data = dict([(str(k), str(v)) for k, v in request_data.items()])

    # Check if required params - "type" or "amount" is missing from request data
    for attr in required_keys:
        if attr not in request_data:
            abort(400, {MESSAGE: REQUIRED_PARAM_ERROR % attr})

    for attr in request_data.keys():
        # Check if required params is empty
        if not len(request_data[attr]):
            # Parent ID can be empty
            if attr != TRANSACTION_PARENT_ID:
                abort(400, {MESSAGE: REQUIRED_PARAM_ERROR % attr})
            request_data.pop(attr)
        else:
            # Enforce type. Fail if there is type conversion error
            request_data[attr] = _get_typed_attr(attr, request_data[attr])

    # Validate parent id
    if TRANSACTION_PARENT_ID in request_data and request_data[TRANSACTION_PARENT_ID] not in transactions:
        abort(400, {MESSAGE: INVALID_PARENT_ERROR})
    return request_data


@app.route("/transactionservice/transaction/<transaction_id>", methods=['GET', 'POST'])
def transaction(transaction_id):
    """
    Creates a new transaction (if POST) or returns an exisiting transaction (if GET)

    @param transaction_id:
        Id of the transaction to be added or returned
    """
    if request.method == 'POST':
        transaction_id = _get_typed_attr(TRANSACTION_ID, transaction_id)
        # Transaction ID must be unique. Do not allow over-writing
        if transaction_id in transactions:
            abort(400, {MESSAGE: DUPLICATE_TRANSACTION_ERROR % transaction_id})

        request_data = request.get_json()
        if not request_data:
            abort(400, {MESSAGE: BAD_REQUEST})

        transactions[transaction_id] = _sanitize_data(**request_data)

        return jsonify(STATUS_OK)

    transaction_id = _get_typed_attr(TRANSACTION_ID, transaction_id)
    if transaction_id not in transactions:
        abort(400, {MESSAGE: INVALID_TRANSACTION_ERROR})
    transaction = transactions[transaction_id]
    return jsonify(transaction)


@app.route('/transactionservice/types/<string:txn_type>')
def get_transaction_type(txn_type):
    """
    Get transaction ids of a type

    @param txn_type:
        Type of transaction to filter on
    @return:
        List of transaction ids filtered by L{txn_type}
    """
    filtered_by_type = [txn_id for txn_id, txn_values in transactions.iteritems()
                        if TRANSACTION_TYPE in txn_values and txn_values[TRANSACTION_TYPE] == txn_type]
    return jsonify(filtered_by_type)


@app.route('/transactionservice/sum/<parent_id>')
def get_transaction_sum(parent_id):
    """
    Get sum of all transactions that are transitively linked by their parent id to transaction id

    @param parent_id:
        Parent ID by which transactions are linked
    @return:
        Sum of transactions
    """
    def _get_sum(filtered_txns, attr, value):
        """Recursively compute sum of all transactions transitively linked by parent-id"""
        for txn_id, txn_values in transactions.iteritems():
            if attr in txn_values and txn_values[attr] == value:
                filtered_txns.append(txn_id)
                _get_sum(filtered_txns, attr, txn_id)

    parent_id = _get_typed_attr(TRANSACTION_PARENT_ID, parent_id)
    # Validate parent id
    if parent_id not in transactions:
        abort(400, {MESSAGE: INVALID_PARENT_ERROR})

    filtered_txns = [parent_id]
    _get_sum(filtered_txns, TRANSACTION_PARENT_ID, parent_id)
    return jsonify({SUM: sum([transactions[tid][TRANSACTION_AMOUNT] for tid in filtered_txns])})


@app.route('/')
def index():
    return jsonify(transactions)

if __name__ == "__main__":
    app.run()
