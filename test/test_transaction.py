#!/usr/bin/python
from ..transaction import app
import unittest
import json

class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.test_app = app.test_client()
        self.test_data = [ { "transaction_id" : 12341,
                             "data"           : {"amount": 100.00, "type": "conference"},
                           },
                           { "transaction_id" : 12342,
                             "data"           : {"amount": 200.00, "type": "conference"},
                           },
                           { "transaction_id" : 12343,
                             "data"           : {"amount": 300.00, "type": "grocery", "parent_id":12342}
                           },
                           { "transaction_id" : 12344,
                             "data"           : {"amount": 400.00, "type": "grocery", "parent_id":12342}
                           },
                           { "transaction_id" : 12345,
                             "data"           : {"amount": 500.00, "type": "maintainence", "parent_id":12343}
                           },
                           { "transaction_id" : 12346,
                             "data"           : {"amount": 600.00, "type": "gym", "parent_id":12343}
                           },
                           { "transaction_id" : 12347,
                             "data"           : {"type": "gym"}
                           },
                           { "transaction_id" : 12348,
                             "data"           : {"amount": 800.00}
                           } ]
        self.error_not_found      = {"error": "Not found"}
        self.error_invalid_txn_id = {"error": "Invalid transaction id"}
        self.message_status_ok    = {"status": "ok"}

    _get_missing_param_error   = lambda self, param: {"error": "%s is required" % param}
    _get_duplicate_txn_error   = lambda self, txn_id: {"error": "Transaction with id %s already exists. Choose another id" % txn_id}
    _get_transaction_path      = lambda self, txn_id: '/transactionservice/transaction/%s' % txn_id
    _get_transaction_type_path = lambda self, txn_type: '/transactionservice/types/%s' % txn_type
    _get_transaction_sum_path  = lambda self, txn_id: '/transactionservice/sum/%s' % txn_id

    def _create_transaction(self, txn_id, data):
        response = self.test_app.post(self._get_transaction_path(txn_id),
                                             data=json.dumps(data),
                                             headers={"content-type": "application/json"})
        return response

    def test_create_transaction(self):
        data   = self.test_data[0]["data"]
        txn_id = self.test_data[0]["transaction_id"]

        expected_response = json.dumps(self.message_status_ok)
        actual_response   = self._create_transaction(txn_id, data)
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_create_transaction_missing_amount(self):
        data   = self.test_data[6]["data"]
        txn_id = self.test_data[6]["transaction_id"]

        expected_response = json.dumps(self._get_missing_param_error("amount"))
        actual_response   = self._create_transaction(txn_id, data)
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_create_transaction_missing_type(self):
        data   = self.test_data[7]["data"]
        txn_id = self.test_data[7]["transaction_id"]

        expected_response = json.dumps(self._get_missing_param_error("type"))
        actual_response   = self._create_transaction(txn_id, data)
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_get_transaction(self):
        data   = self.test_data[1]["data"]
        txn_id = self.test_data[1]["transaction_id"]
        self._create_transaction(txn_id, data)

        data   = self.test_data[2]["data"]
        txn_id = self.test_data[2]["transaction_id"]
        self._create_transaction(txn_id, data)

        expected_response = json.dumps(data)
        actual_response   = self.test_app.get(self._get_transaction_path(txn_id), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_get_transaction_fail(self):
        data   = self.test_data[1]["data"]
        txn_id = self.test_data[1]["transaction_id"]
        self._create_transaction(txn_id, data)

        data   = self.test_data[1]["data"]
        txn_id = self.test_data[1]["transaction_id"]
        actual_response   = self._create_transaction(txn_id, data)
        expected_response = json.dumps(self._get_duplicate_txn_error(txn_id))
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_get_transaction_invalid(self):
        import time
        actual_response   = self.test_app.get(self._get_transaction_path(int(time.time())), content_type="application/json")
        expected_response = json.dumps(self.error_invalid_txn_id)
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_get_transaction_by_type(self):
        data   = self.test_data[1]["data"]
        txn_id = self.test_data[1]["transaction_id"]
        self._create_transaction(txn_id, data)

        data   = self.test_data[2]["data"]
        txn_id = self.test_data[2]["transaction_id"]
        self._create_transaction(txn_id, data)

        data   = self.test_data[3]["data"]
        txn_id = self.test_data[3]["transaction_id"]
        self._create_transaction(txn_id, data)

        expected_response = json.dumps([txn_id, self.test_data[2]["transaction_id"]])
        actual_response   = self.test_app.get(self._get_transaction_type_path(data["type"]), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_get_transaction_sum(self):
        data1   = self.test_data[1]["data"]
        txn_id1 = self.test_data[1]["transaction_id"]
        self._create_transaction(txn_id1, data1)

        data2   = self.test_data[2]["data"]
        txn_id2 = self.test_data[2]["transaction_id"]
        self._create_transaction(txn_id2, data2)

        data3   = self.test_data[3]["data"]
        txn_id3 = self.test_data[3]["transaction_id"]
        self._create_transaction(txn_id3, data3)

        data4   = self.test_data[4]["data"]
        txn_id4 = self.test_data[4]["transaction_id"]
        self._create_transaction(txn_id4, data4)

        data5   = self.test_data[5]["data"]
        txn_id5 = self.test_data[5]["transaction_id"]
        self._create_transaction(txn_id5, data5)

        expected_response = '{"sum" : 2000.0}'
        actual_response   = self.test_app.get(self._get_transaction_sum_path(txn_id1), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))

        expected_response = '{"sum" : 1400.0}'
        actual_response   = self.test_app.get(self._get_transaction_sum_path(txn_id2), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))

        expected_response = '{"sum" : 400.0}'
        actual_response   = self.test_app.get(self._get_transaction_sum_path(txn_id3), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))

        expected_response = '{"sum" : 500.0}'
        actual_response   = self.test_app.get(self._get_transaction_sum_path(txn_id4), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))

        expected_response = '{"sum" : 600.0}'
        actual_response   = self.test_app.get(self._get_transaction_sum_path(txn_id5), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


    def test_not_found(self):
        expected_response = json.dumps(self.error_not_found)

        actual_response   = self.test_app.get(self._get_transaction_path(""), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))

        actual_response   = self.test_app.get(self._get_transaction_type_path(""), content_type="application/json")
        self.assertEquals(json.loads(actual_response.data), json.loads(expected_response))


if __name__ == '__main__':
    unittest.main()
