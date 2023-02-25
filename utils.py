import hashlib
import random, string

def hash(text):
    h = hashlib.new('sha256')
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def rand_hex(length):
    letters = string.ascii_letters + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))