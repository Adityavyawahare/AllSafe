import hashlib
from AES.constants import *


def pad(text):
    """CMS (Cryptographic Message Syntax).
    This pads with the same value as the number of padding bytes.
     Defined in RFC 5652, PKCS#5, PKCS#7 (X.509 certificate) and RFC 1423 PEM."""
    pad_length = 16 - (len(text) % 16)
    padding = ""
    for i in range(1, pad_length + 1):
        padding += bytes([i]).decode()
    return text + padding


def unpad(text):
    x = ord(text[-1])
    y = x
    count = 0
    if x > len(text):
        return text
    for i in range(0, x):
        if y == ord(text[-1 - i]):
            count += 1
        else:
            return text
        y -= 1
    return text[0:len(text) - x]


def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])


def bytes_to_matrix(text):
    # Converts text to 4X4 matrix
    lst = []
    for i in range(0, len(text), 4):
        lst.append([bytes([lol]) for lol in text[i:i + 4]])
    return lst


def matrix_to_bytes(matrix):
    """ Converts a 4x4 matrix into a 16-byte array.  """
    s = "".encode()
    for i in range(4):
        for j in range(4):
            s += matrix[i][j]
    return s


def matrix_to_int(matrix):
    for i in range(4):
        for j in range(4):
            matrix[i][j] = int.from_bytes(matrix[i][j], "big")


def bytes_to_matrix_32bit(text):
    # Converts 32bit key to 4X4 matrix
    lst = []
    for i in range(0, 4):
        lst.append([bytes([int(text[i * 8 + j:i * 8 + j + 2], 16)]) for j in range(0, 8, 2)])
    return lst


def transpose(text):
    # Converts text to 4X4 matrix Column Major Order
    lst = []
    for i in range(0, 4):
        lst.append([text[j][i] for j in range(0, 4)])
    return lst


def add_round_key(byte_matrix, key_matrix):
    for i in range(0, 4):
        for j in range(0, 4):
            byte_matrix[j][i] = xor_bytes(byte_matrix[j][i], key_matrix[j][i])


def sub_bytes(byte_matrix):
    for i in range(0, 4):
        for j in range(0, 4):
            byte_matrix[j][i] = bytes([SUB_BOX[int.from_bytes(byte_matrix[j][i], "big")]])


def inv_sub_bytes(byte_matrix):
    for i in range(0, 4):
        for j in range(0, 4):
            byte_matrix[j][i] = bytes([INV_SUB_BOX[int.from_bytes(byte_matrix[j][i], "big")]])


def shift_bytes(byte_matrix):
    for i in range(0, 4):
        for j in range(0, i):
            byte_matrix[i].append(byte_matrix[i].pop(0))


def inv_shift_bytes(byte_matrix):
    for i in range(0, 4):
        for j in range(0, i):
            byte_matrix[i].insert(0, byte_matrix[i].pop())


xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)


def mix_single_column(a):
    # see Sec 4.1.2 in The Design of Rijndael
    t = xor_bytes(xor_bytes(a[0], a[1]), xor_bytes(a[2], a[3]))
    u = int.from_bytes(a[0], "big")
    a[0] = xor_bytes(a[0], xor_bytes(t, bytes([xtime(int.from_bytes(a[0], "big") ^ int.from_bytes(a[1], "big"))])))
    a[1] = xor_bytes(a[1], xor_bytes(t, bytes([xtime(int.from_bytes(a[1], "big") ^ int.from_bytes(a[2], "big"))])))
    a[2] = xor_bytes(a[2], xor_bytes(t, bytes([xtime(int.from_bytes(a[2], "big") ^ int.from_bytes(a[3], "big"))])))
    a[3] = xor_bytes(a[3], xor_bytes(t, bytes([xtime(int.from_bytes(a[3], "big") ^ u)])))


def mix_columns(byte_matrix):
    for i in range(4):
        mix_single_column(byte_matrix[i])
    byte_matrix = transpose(byte_matrix)
    return byte_matrix


def inv_mix_columns(s):
    for i in range(4):
        u = xtime(xtime(int.from_bytes(s[i][0], "big") ^ int.from_bytes(s[i][2], "big")))
        v = xtime(xtime(int.from_bytes(s[i][1], "big") ^ int.from_bytes(s[i][3], "big")))
        s[i][0] = xor_bytes(s[i][0], bytes([u]))
        s[i][1] = xor_bytes(s[i][1], bytes([v]))
        s[i][2] = xor_bytes(s[i][2], bytes([u]))
        s[i][3] = xor_bytes(s[i][3], bytes([v]))

    s = mix_columns(s)
    return s


def split_bytes(text):
    return [text[i:i + 16] for i in range(0, len(text), 16)]


def split_bytes_32bit(text):
    return [text[i:i + 32] for i in range(0, len(text), 32)]


class AES:
    def __init__(self, master_key):
        self.no_of_rounds = ROUNDS
        self.expanded_key = self.expand_key(master_key)

    def expand_key(self, master_key):
        if len(master_key) == 16:
            key = bytes_to_matrix(master_key)
        else:
            key = bytes_to_matrix_32bit(master_key)

        i = 4
        while len(key) < (self.no_of_rounds + 1) * 4:
            temp = [k for k in key[-1]]
            if i % 4 == 0:
                # Right Circular Shift
                temp.append(temp.pop(0))
                # Substitution bytes
                temp = [bytes([SUB_BOX[int.from_bytes(it, "big")]]) for it in temp]
                # Adding Rcon
                temp[0] = xor_bytes(temp[0], bytes([R_CON[i // 4]]))
            key.append([xor_bytes(x, y) for x, y in zip(key[i - 4], temp)])
            i += 1
        return key

    def encrypt(self, message, iv="encryptionIntVec"):
        """This function encrypts in cbc mode"""
        message = pad(message)
        message_list = split_bytes(message)
        for i in range(0, len(message_list)):
            message_list[i] = message_list[i].encode()
        # message_list=[b'\x01#Eg\x89\xab\xcd\xef\xfe\xdc\xba\x98vT2\x10']
        # message_list = [[b'\x01', b'\x89', b'\xfe', b'\76'], [b'\23', b'\xab', b'\xdc', b'\x54'],
        #                 [b'\x45', b'\xcd', b'\xba', b'\x32'], [b'\x67', b'\xef', b'\x98', b'\x10']]
        previous_cipher = iv.encode()
        cipher = []
        for block in message_list:
            temp = self.encrypt_block(xor_bytes(previous_cipher, block))
            # temp=self.encrypt_block(block)
            cipher.append(temp)
            previous_cipher = temp
        s = ""
        for c in cipher:
            for i in c:
                s += bytes([i]).hex()
        return s

    def encrypt_block(self, plaintext):
        """
            Encrypts a single block of 16 byte long plaintext.
        """
        plaintext_matrix = bytes_to_matrix(plaintext)
        plaintext_matrix = transpose(plaintext_matrix)
        round_key = list(self.expanded_key[i] for i in range(0, 4))
        add_round_key(plaintext_matrix, transpose(round_key))
        for i in range(1, 10):
            sub_bytes(plaintext_matrix)
            shift_bytes(plaintext_matrix)
            plaintext_matrix = mix_columns(transpose(plaintext_matrix))
            add_round_key(plaintext_matrix, transpose(list(self.expanded_key[i * 4 + j] for j in range(0, 4))))
        i += 1
        sub_bytes(plaintext_matrix)
        shift_bytes(plaintext_matrix)
        round_key = transpose(list(self.expanded_key[i * 4 + j] for j in range(0, 4)))
        add_round_key(plaintext_matrix, round_key)

        # matrix_to_int(plaintext_matrix)
        # print(plaintext_matrix)
        plaintext = matrix_to_bytes(plaintext_matrix)
        return plaintext

    def decrypt(self, cipher_text, iv="encryptionIntVec"):
        cipher_temp_list = split_bytes_32bit(cipher_text)
        cipher_list = []
        s = "".encode()
        for i in range(0, len(cipher_temp_list)):
            s = "".encode()
            for j in range(0, len(cipher_temp_list[i]), 2):
                s += bytes([int(cipher_temp_list[i][j:j + 2], 16)])
            cipher_list.append(s)
        previous_cipher = iv.encode()
        plain_text_matrix = []
        for block in cipher_list:
            plain_text_matrix.append(xor_bytes(previous_cipher, self.decrypt_block(block)))
            previous_cipher = block
        s = ""
        for c in plain_text_matrix:
            for i in c:
                s += chr(i)
        s = unpad(s)
        return s

    def decrypt_block(self, ciphertext):
        ciphertext_matrix = bytes_to_matrix(ciphertext)
        x = transpose(list(self.expanded_key[i] for i in range(40, 44)))
        add_round_key(ciphertext_matrix, x)
        inv_shift_bytes(ciphertext_matrix)
        inv_sub_bytes(ciphertext_matrix)

        for i in range(9, 0, -1):
            add_round_key(ciphertext_matrix, transpose(list(self.expanded_key[i * 4 + j] for j in range(0, 4))))
            ciphertext_matrix = inv_mix_columns(transpose(ciphertext_matrix))
            inv_shift_bytes(ciphertext_matrix)
            inv_sub_bytes(ciphertext_matrix)
        add_round_key(ciphertext_matrix, transpose(list(self.expanded_key[i] for i in range(0, 4))))
        ciphertext_matrix = transpose(ciphertext_matrix)
        ciphertext = matrix_to_bytes(ciphertext_matrix)
        return ciphertext

    def display(self):
        for i in range(0, 44, 4):
            for j in self.expanded_key[i]:
                print(j, end=" ")
            for j in self.expanded_key[i + 1]:
                print(j, end=" ")
            for j in self.expanded_key[i + 2]:
                print(j, end=" ")
            for j in self.expanded_key[i + 3]:
                print(j, end=" ")
            print()


# key = input("Enter your password ")
# sha256=hashlib.sha256()
# sha256.update(key.encode())
# h=sha256.digest()
# key=h.hex()[:32]
# print(key)
# key = "0f1571c947d9e8590cb7add6af7f6798"
'''When hexadecimal key inserted'''
# if len(key) == 32:
#     aes = AES(key)
#     # aes.display()
# 
# elif len(key) == 16:
#     aes = AES(key.encode())
#     # aes.display()
# 
# message = input("Enter message: ")
# cipher = aes.encrypt(message)
# print(cipher)
# plaintext = aes.decrypt(cipher)
# print(plaintext)
# print(base64.b64decode(cipher))
# 1bD4k5nDa3Dgs8Sh
# 0f1571c947d9e8590cb7add6af7f6798
# b'\x01\x89\xfe>\x13\xab\xdcTE\xcd\xba2g\xef\x98\x10'
