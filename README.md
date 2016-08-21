# transaction-service (Python + Flask)

A RESTful web service implementation that stores transactions (in memory) and returns information about those transactions. The transactions to be stored have a type and an amount. The service supports returning all transactions of a type. Also, transactions can be linked to each other (using a ”parent id”) and supports getting the total amount involved for all transactions linked to a particular transaction.

API Spec:
-----------
  1. PUT /transactionservice/transaction/$transaction_id
      <br>Body:
        { "amount":double,"type":string,"parent_id":long }
      where:
      <br>• transaction id is a long specifying a new transaction
      <br>• amount is a double specifying the amount
      <br>• type is a string specifying a type of the transaction.
      <br>• parent id is an optional long that may specify the parent transaction of this transaction.

  2. GET /transactionservice/transaction/$transaction_id
      <br>Returns: { "amount":double,"type":string,"parent_id":long }

  3. GET /transactionservice/types/$type
      <br>Returns: [long, long, ... ]
      <br>A json list of all transaction ids that share the same type $type.

  4. GET /transactionservice/sum/$transaction_id
      <br>Returns: { "sum": double }
      <br>A sum of all transactions that are transitively linked by their parent_id to $transaction_id.

Assumptions:
------------
  1. Transaction type is open-ended. That is, there is really no invalid transaction type.
  2. There cannot be circular dependency of transactions. Ideally, the first transaction that gets created will not(or cannot) have a parent id. This also means parent id cannot be the same as current transaction's id.

Asymptotic analysis:
--------------------
  - Both PUT and GET /transactionservice/transaction/$transaction_id deal with only one transaction at a time and the operations have a constant running time.
  - GET /transactionservice/types/$type iterates through the list of all available transactions to get the type, compare with the requested type and return. Hence, this runs in O(n), where n is the number of transactions in-memory.
  - GET /transactionservice/sum/$transaction_id recursively computes the sum based on transitive dependency of transactions. This runs in O(n2) with the best case of O(n). For example, if there are 2 transactions, t1 and t2 with t1 being the parent of t2 and sum of t1 is asked, then-
    1. go over the transactions once to find transactions who have parents as t1 - O(n)
    2. go over the transactions again for each transaction found in #1 (in this case 1 transaction). = O(n)+O(n)+..... = number of transaction ids from #1 * O(n)
  Running time = O(n).m*O(n) = O(n2)
