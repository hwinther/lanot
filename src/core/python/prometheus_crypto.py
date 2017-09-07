import sys
import gc
import os
import time
from prometheus_servers import Server, UdpSocketServer, TcpSocketServer
if sys.platform in ['esp8266', 'esp32', 'WiPy']:
    from urandom import randrange
else:
    from random import randrange

__version__ = '0.1.2b'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


local_key_path = 'prometheus.localkey'
key_registry_path = 'prometheus.keys'

# TODO: RSA socket
# client & server must support request for public key (respond with public key)
# client & server should keep received public key replies locally
# client & server have to generate a local key in init if none exist
# request over protocol should be:
# <command encrypted with remote ends public key> -> encrypted again with local private key for ident verification
# (server) decrypts with remote public key, and then decrypts with local private key
# do something after first decrypt to see that it failed at that step (static padding)
# concider adding time.time() to the command format (at end, split away after recv?), so it cant be replayed


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
    try:
        plain = [chr(pow(char, key, n)) for char in ciphertext]
    except OverflowError as e:
        raise
    # Return the array of bytes as a string
    return ''.join(plain)


def get_random_prime():
    page = randrange(0, 8365)
    f = open('primes.src', 'r')
    i = 0
    line = '0'
    while i != page:
        line = f.readline()
        if line == '':
            break
        i += 1
    gc.collect()
    return int(line.replace('\r', '').replace('\n', ''))


def get_or_create_local_keys():
    """
    :type: () -> ((int, int), (int, int))
    :return: public key, private key
    """
    st = None
    try:
        st = os.stat(local_key_path)
    except OSError as e:
        if e.args[0] != 2:
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

    # p = 961241
    # q = 18341
    p = get_random_prime()
    q = get_random_prime()
    print('Got %d for p and %d for q' % (p, q))
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
                break
            if line.find('\t') != -1:
                ip, pub0, pub1 = line.split('\t')
                d[ip] = (int(pub0), int(pub1))
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


def eratosthenes():
    # Yields the sequence of prime numbers via the Sieve of Eratosthenes.
    D = {}  # map composite integers to primes witnessing their compositeness
    q = 2  # first integer to test for primality
    while 1:
        if q not in D:
            yield q  # not marked composite, must be prime
            D[q * q] = [q]  # first multiple of q not already marked
        else:
            for p in D[q]:  # move each witness to its next multiple
                D.setdefault(p + q, []).append(p)
            del D[q]  # no longer need D[q], free memory
        q += 1


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
    def __init__(self, instance, clientencrypt=False):
        UdpSocketServer.__init__(self, instance)
        self.public_key, self.private_key = get_or_create_local_keys()
        self.clientencrypt = clientencrypt
        self.key_registry = get_local_key_registry()

    def handle_data(self, command, source=None, **kwargs):
        # override specific commands
        if command == 'pubkey':
            # TODO: only permit this 30s after reset for instance
            msg = '%d\t%d' % (self.public_key[0], self.public_key[1])
            print('returning public key')
            self.reply(msg, source=source, encrypt=False, **kwargs)
            return

        print('command=%s' % repr(command))
        if command.count('\t') == 3:
            remote_key = command.split('\t\t\t')
            remote_key = (int(remote_key[0]), int(remote_key[1]))
            print('storing received key')
            self.key_registry[source[0]] = remote_key
            # save changes
            set_local_key_registry(self.key_registry)
            return

        if self.clientencrypt and source[0] not in self.key_registry.keys():
            # poorly attached reverse key resolving :)
            print('could not find %s in %s' % (source[0], self.key_registry.keys()))
            print('requesting remote key')
            self.reply('pubkey', source=source, encrypt=False, **kwargs)
            return

        # decrypt command before handling
        if self.clientencrypt and source[0] in self.key_registry.keys():
            decrypted = decrypt_packet(command, self.private_key, self.key_registry[source[0]])
        else:
            decrypted = decrypt_packet(command, self.private_key)
        if decrypted is not None:
            command = decrypted

        UdpSocketServer.handle_data(self, command, source=source, **kwargs)

    def reply(self, return_value, source=None, encrypt=True, **kwargs):
        if encrypt:
            if self.clientencrypt and source[0] in self.key_registry.keys():
                return_value = encrypt_packet(return_value, self.private_key, self.key_registry[source[0]])
            else:
                return_value = encrypt_packet(return_value, self.private_key)

        UdpSocketServer.reply(self, return_value, source, **kwargs)


def decrypt_packet(ciphertext, private_key, public_key=None):
    """
    :type ciphertext: bytes
    :type private_key: (int, int)
    :type public_key: (int, int)
    :rtype: str
    :param ciphertext: encrypted bytes
    :param private_key: private key
    :param public_key: public key
    :return: cleartext
    """
    print('decrypt_packet')
    if type(ciphertext) == str:
        ciphertext = ciphertext.encode('ascii')
    if ciphertext is None or ciphertext.count(b'\x00') < 5:
        return None
        # not encrypted?
    cipher = list()
    for x in ciphertext.split(b'\x00'):
        s = b''
        try:
            for y in x:
                s += b'%02d' % y
            if s == '':
                s = 0
            else:
                s = int(s)
        except ValueError:
            print('ValueError')
            break
        cipher.append(s)
    if len(cipher) == 0:
        # nothing to decrypt
        return None
    else:
        ciphertext = decrypt(private_key, cipher)
        # print(repr(ciphertext))
        t, ciphertext = ciphertext.split('\t', 1)
    return ciphertext


def encrypt_packet(cleartext, public_key, private_key=None):
    """
    :type cleartext: bytes
    :type private_key: (int, int)
    :type public_key: (int, int)
    :rtype: str
    :param cleartext: encrypted bytes
    :param private_key: private key
    :param public_key: public key
    :return: cleartext
    """
    print('encrypt_packet')
    if type(cleartext) == str:
        cleartext = cleartext.encode('ascii')
    cleartext = b'%s\t%s' % (chr(time.localtime()[5]).encode('ascii'), cleartext)
    encrypted = encrypt(public_key, cleartext.decode('ascii'))
    # yields list[str]
    ciphertext = b''
    # print('repr(encrypted)=%s' % repr(encrypted))
    for i in encrypted:
        # sacrificing performance for smaller packet size..
        if i == 0:
            # skip this, the delimiter will mark its existance
            s = ''
        elif len(str(i)) < 11:
            s = '%010d' % i
        else:
            s = '%012d' % i
        if len(ciphertext) != 0:
            ciphertext += b'\x00'
        ciphertext += b''.join([chr(int(s[i:i + 2])).encode('ascii') for i in range(0, len(s), 2)])
    print('sending %d encrypted bytes' % len(ciphertext))
    return ciphertext
