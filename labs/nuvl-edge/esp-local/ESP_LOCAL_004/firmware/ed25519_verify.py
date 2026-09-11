MASK64 = (1 << 64) - 1

K = (
    0x428a2f98d728ae22, 0x7137449123ef65cd,
    0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019,
    0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe,
    0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1,
    0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
    0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483,
    0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210,
    0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725,
    0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926,
    0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8,
    0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001,
    0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910,
    0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53,
    0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
    0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60,
    0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9,
    0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207,
    0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6,
    0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493,
    0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a,
    0x5fcb6fab3ad6faec, 0x6c44198c4a475817,
)

H_INIT = (
    0x6a09e667f3bcc908,
    0xbb67ae8584caa73b,
    0x3c6ef372fe94f82b,
    0xa54ff53a5f1d36f1,
    0x510e527fade682d1,
    0x9b05688c2b3e6c1f,
    0x1f83d9abfb41bd6b,
    0x5be0cd19137e2179,
)

Q = 2 ** 255 - 19
L = 2 ** 252 + 27742317777372353535851937790883648493


def ror64(x, n):
    return ((x >> n) | (x << (64 - n))) & MASK64


def sha512(data):
    msg = bytearray(data)
    bit_len = len(msg) * 8

    msg.append(0x80)

    while (len(msg) % 128) != 112:
        msg.append(0)

    msg.extend(b"\x00" * 8)

    for shift in range(56, -1, -8):
        msg.append((bit_len >> shift) & 0xFF)

    h = list(H_INIT)

    for offset in range(0, len(msg), 128):
        w = [0] * 80
        block = msg[offset:offset + 128]

        for i in range(16):
            value = 0
            start = i * 8

            for j in range(8):
                value = (value << 8) | block[start + j]

            w[i] = value

        for i in range(16, 80):
            x = w[i - 15]
            s0 = ror64(x, 1) ^ ror64(x, 8) ^ (x >> 7)

            x = w[i - 2]
            s1 = ror64(x, 19) ^ ror64(x, 61) ^ (x >> 6)

            w[i] = (
                w[i - 16]
                + s0
                + w[i - 7]
                + s1
            ) & MASK64

        a, b, c, d, e, f, g, hh = h

        for i in range(80):
            s1 = (
                ror64(e, 14)
                ^ ror64(e, 18)
                ^ ror64(e, 41)
            )

            ch = (e & f) ^ ((~e) & g)

            temp1 = (
                hh
                + s1
                + ch
                + K[i]
                + w[i]
            ) & MASK64

            s0 = (
                ror64(a, 28)
                ^ ror64(a, 34)
                ^ ror64(a, 39)
            )

            maj = (a & b) ^ (a & c) ^ (b & c)

            temp2 = (s0 + maj) & MASK64

            hh = g
            g = f
            f = e
            e = (d + temp1) & MASK64
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & MASK64

        h[0] = (h[0] + a) & MASK64
        h[1] = (h[1] + b) & MASK64
        h[2] = (h[2] + c) & MASK64
        h[3] = (h[3] + d) & MASK64
        h[4] = (h[4] + e) & MASK64
        h[5] = (h[5] + f) & MASK64
        h[6] = (h[6] + g) & MASK64
        h[7] = (h[7] + hh) & MASK64

    out = bytearray()

    for value in h:
        for shift in range(56, -1, -8):
            out.append((value >> shift) & 0xFF)

    return bytes(out)


def inv(x):
    return pow(x, Q - 2, Q)


D = (-121665 * inv(121666)) % Q
I = pow(2, (Q - 1) // 4, Q)


def xrecover(y):
    xx = ((y * y - 1) * inv(D * y * y + 1)) % Q
    x = pow(xx, (Q + 3) // 8, Q)

    if (x * x - xx) % Q != 0:
        x = (x * I) % Q

    if x & 1:
        x = Q - x

    return x


BY = (4 * inv(5)) % Q
BX = xrecover(BY)
BASE = (BX, BY)


def is_on_curve(point):
    x, y = point

    return (
        -x * x
        + y * y
        - 1
        - D * x * x * y * y
    ) % Q == 0


def edwards_add(p, q):
    x1, y1 = p
    x2, y2 = q

    t = (D * x1 * x2 * y1 * y2) % Q

    x3 = (
        (x1 * y2 + x2 * y1)
        * inv(1 + t)
    ) % Q

    y3 = (
        (y1 * y2 + x1 * x2)
        * inv(1 - t)
    ) % Q

    return x3, y3


def scalar_mult(point, scalar):
    result = (0, 1)
    addend = point

    while scalar > 0:
        if scalar & 1:
            result = edwards_add(result, addend)

        addend = edwards_add(addend, addend)
        scalar >>= 1

    return result


def decode_int(data):
    value = 0

    for i in range(len(data) - 1, -1, -1):
        value = (value << 8) | data[i]

    return value


def decode_point(data):
    if len(data) != 32:
        raise ValueError("point_length")

    y = decode_int(data) & ((1 << 255) - 1)
    sign = (data[31] >> 7) & 1

    if y >= Q:
        raise ValueError("point_noncanonical")

    x = xrecover(y)

    if (x & 1) != sign:
        x = Q - x

    point = (x, y)

    if not is_on_curve(point):
        raise ValueError("point_not_on_curve")

    return point


def hint(data):
    return decode_int(sha512(data))


def verify(public_key, message, signature):
    if len(public_key) != 32:
        return False

    if len(signature) != 64:
        return False

    try:
        r_encoded = signature[:32]
        s = decode_int(signature[32:])

        if s >= L:
            return False

        r_point = decode_point(r_encoded)
        a_point = decode_point(public_key)

        h = hint(r_encoded + public_key + message) % L

        left = scalar_mult(BASE, s)
        right = edwards_add(
            r_point,
            scalar_mult(a_point, h),
        )

        return left == right

    except Exception:
        return False
