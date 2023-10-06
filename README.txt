

We use port number: 12345 (non-priviledged port number as non-admin can also run on this)
NACK is represent by 1000


Run for sender : python3.9 sendergbn.py -s machine1 -p 12345 -l 512 -r 10 -n 20 -w 3 -b 1
Run for receiver: python3.9 receivergbn.py -p 12345 -n 20 -e 0.00001
