
class CodeFactory:
    CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    MAX_CODES = 36**4
    MULTIPLIER = 1234567

    @classmethod
    def int_to_code(cls, n: int) -> str:
        n = n % cls.MAX_CODES
        scrambled = (n * cls.MULTIPLIER) % cls.MAX_CODES

        code = ""
        for _ in range(4):
            code = cls.CHARS[scrambled % 36] + code
            scrambled //= 36

        return code

    @classmethod
    def code_to_int(cls, code: str) -> int:
        scrambled = 0
        for char in code:
            scrambled = scrambled * 36 + cls.CHARS.index(char)

        inv_multiplier = cls._mod_inverse(cls.MULTIPLIER, cls.MAX_CODES)
        original = (scrambled * inv_multiplier) % cls.MAX_CODES

        return original

    @staticmethod
    def _mod_inverse(a: int, m: int) -> int:
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            m, a = a % m, m
            x0, x1 = x1 - q * x0, x0
        return x1 + m0 if x1 < 0 else x1
