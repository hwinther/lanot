import sys
import gc
import os
from prometheus_servers import Server, UdpSocketServer, TcpSocketServer
if sys.platform in ['esp8266', 'esp32', 'WiPy']:
    from urandom import randrange
else:
    from random import randrange

__version__ = '0.1.1'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


local_key_path = 'prometheus.localkey'
key_registry_path = 'prometheus.keys'


def gcd(a, b):
    # Euclid's algorithm for determining the greatest common divisor
    # Use iteration to make it faster for larger integers
    while b != 0:
        a, b = b, a % b
    return a


def multiplicative_inverse(a, b):
    # Euclid's extended algorithm for finding the multiplicative inverse of two numbers
    """Returns a tuple (r, i, j) such that r = gcd(a, b) = ia + jb
    """
    # r = gcd(a,b) i = multiplicitive inverse of a mod b
    #      or      j = multiplicitive inverse of b mod a
    # Neg return values for i or j are made positive mod b or a respectively
    # Iterateive Version is faster and uses much less stack space
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a  # Remember original a/b to remove
    ob = b  # negative values from return results
    while b != 0:
        q = a // b
        (a, b) = (b, a % b)
        (x, lx) = ((lx - (q * x)), x)
        (y, ly) = ((ly - (q * y)), y)
    if lx < 0:
        lx += ob  # If neg wrap modulo orignal b
    if ly < 0:
        ly += oa  # If neg wrap modulo orignal a
    # return a , lx, ly  # Return only positive values
    return lx


def is_prime(num):
    # Tests to see if a number is prime.
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num ** 0.5) + 2, 2):
        if num % n == 0:
            return False
    return True


def generate_keypair(p, q):
    """
    :param p: int
    :param q: int
    :return: :type (int, int), (int, int)
    """
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')
    # n = pq
    n = p * q

    # Phi is the totient of n
    phi = (p - 1) * (q - 1)

    # Choose an integer e such that e and phi(n) are coprime
    e = randrange(1, phi)

    # Use Euclid's Algorithm to verify that e and phi(n) are comprime
    g = gcd(e, phi)
    while g != 1:
        e = randrange(1, phi)
        g = gcd(e, phi)

    # Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, phi)

    # Return public and private keypair
    # Public key is (e, n) and private key is (d, n)
    return (e, n), (d, n)


def encrypt(pk, plaintext):
    # Unpack the key into it's components
    key, n = pk
    # Convert each letter in the plaintext to numbers based on the character using a^b mod m
    # cipher = [(ord(char) ** key) % n for char in plaintext]
    cipher = [pow(ord(char),key,n) for char in plaintext]
    # Return the array of bytes
    return cipher


def decrypt(pk, ciphertext):
    # Unpack the key into its components
    key, n = pk
    # Generate the plaintext based on the ciphertext and key using a^b mod m
    # plain = [chr((char ** key) % n) for char in ciphertext]
    plain = [chr(pow(char, key, n)) for char in ciphertext]
    # Return the array of bytes as a string
    return ''.join(plain)


def get_or_create_local_keys():
    st = None
    try:
        st = os.stat(local_key_path)
    except OSError as e:
        if e.errno != 2:
            # ignore errno 2 - ENOENT (doesnt exist)
            raise

    if st is not None:
        # return existing values
        keys = open(local_key_path).read()
        public, private = keys.split('\n')
        public = public.split('\t')
        private = private.split('\t')
        public[0] = int(public[0])
        public[1] = int(public[1])
        private[0] = int(private[0])
        private[1] = int(private[1])
        print('returning saved keys: pub=%d %d priv=%d %d' % (public[0], public[1], private[0], private[1]))
        return public, private

    p = 961241
    q = 18341
    public, private = generate_keypair(p, q)
    print("Your public key is %s and your private key is %s" % (repr(public), repr(private)))
    message = 'my test message'
    encrypted_msg = encrypt(private, message)
    print("Your encrypted message is:")
    print(''.join(map(lambda x: str(x), encrypted_msg)))
    print("Decrypting message with public key")
    print("Your message is:")
    print(decrypt(public, encrypted_msg))
    print('Saving keys to %s' % local_key_path)
    f = open(local_key_path, 'w')
    f.write('%d\t%d\n%d\t%d' % (public[0], public[1], private[0], private[1]))
    f.close()
    return public, private


def get_local_key_registry():
    st = None
    try:
        st = os.stat(key_registry_path)
    except OSError as e:
        if e.errno != 2:
            # ignore errno 2 - ENOENT (doesnt exist)
            raise

    if st is not None:
        d = dict()
        f = open(key_registry_path)
        while True:
            line = f.readline()
            if line == '':
                continue
            if line.find('\t') != -1:
                ip, pub0, pub1 = line.split('\t')
                d[ip] = (pub0, pub1)
        print('Loaded %d entries from key registry' % len(d))
        return d

    f = open(key_registry_path, 'w')
    f.close()
    return dict()


def set_local_key_registry(d):
    print('Writing %d entries to key registry' % len(d))
    f = open(key_registry_path, 'w')
    for key in d.keys():
        f.write('%s\t%d\t%d\n' % (key, d[key][0], d[key][1]))
    f.close()


def test():
    pub, priv = get_or_create_local_keys()
    message = 'another test'
    encrypted_msg = encrypt(priv, message)
    print("Your encrypted message is:")
    print(''.join(map(lambda x: str(x), encrypted_msg)))
    print("Decrypting message with public key")
    print("Your message is:")
    print(decrypt(pub, encrypted_msg))


class RsaUdpSocketServer(UdpSocketServer):
    def __init__(self, instance):
        UdpSocketServer.__init__(self, instance)
        self.public_key, self.private_key = get_or_create_local_keys()

    def handle_data(self, command, source=None, **kwargs):
        # override specific commands
        if command == 'pubkey':
            # TODO: only permit this 30s after reset for instance
            msg = '%d\t%d' % (self.public_key[0], self.public_key[1])
            print('returning public key')
            self.reply(msg, source=source, **kwargs)
            return
        else:
            # decrypt command before handling
            print('decrypting command data')
            cipher = list()
            for x in command.split('\t'):
                if x == '':
                    continue
                cipher.append(int(x))
            command = decrypt(self.private_key, cipher)

        Server.handle_data(self, command, source=source, **kwargs)
