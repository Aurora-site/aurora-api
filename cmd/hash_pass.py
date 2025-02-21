import hashlib
import os
import sys


def hash_new_password(password: str) -> tuple[str, str]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex(), pw_hash.hex()


if __name__ == "__main__":
    if not sys.argv[1:]:
        print("Usage: hash_pass.py <password>")
        sys.exit(1)
    s, h = hash_new_password(sys.argv[1])
    print(f"salt: {s}")
    print(f"hash: {h}")
