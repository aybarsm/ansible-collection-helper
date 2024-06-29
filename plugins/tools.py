import hashlib
import uuid

class Tools:

    @staticmethod
    def hash_md5(content):
        return hashlib.md5(str(content).encode()).hexdigest()