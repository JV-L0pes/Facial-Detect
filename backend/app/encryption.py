from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from config import ENCRYPTION_KEY, AES_KEY_LENGTH


class EncryptionManager:
    def __init__(self):
        # Gerar chave AES a partir da chave de configuração
        self.key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()[:AES_KEY_LENGTH]

    def encrypt_data(self, data: str) -> str:
        """Criptografa dados usando AES-256"""
        try:
            # Converter string para bytes se necessário
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = data

            # Criar cipher
            cipher = AES.new(self.key, AES.MODE_CBC)

            # Criptografar dados
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)

            # Combinar IV + dados criptografados e codificar em base64
            encrypted_with_iv = cipher.iv + encrypted_data
            return base64.b64encode(encrypted_with_iv).decode("utf-8")

        except Exception as e:
            raise Exception(f"Erro na criptografia: {str(e)}")

    def decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografa dados usando AES-256"""
        try:
            # Decodificar base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))

            # Extrair IV e dados criptografados
            iv = encrypted_bytes[: AES.block_size]
            encrypted_bytes = encrypted_bytes[AES.block_size :]

            # Criar cipher
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

            # Descriptografar e remover padding
            decrypted_padded = cipher.decrypt(encrypted_bytes)
            decrypted_data = unpad(decrypted_padded, AES.block_size)

            return decrypted_data.decode("utf-8")

        except Exception as e:
            raise Exception(f"Erro na descriptografia: {str(e)}")

    def encrypt_embedding(self, embedding) -> str:
        """Criptografa embedding numpy array"""
        import numpy as np

        # Converter numpy array para string
        embedding_str = np.array2string(embedding, separator=",")
        return self.encrypt_data(embedding_str)

    def decrypt_embedding(self, encrypted_embedding: str):
        """Descriptografa embedding e converte de volta para numpy array"""
        import numpy as np

        decrypted_str = self.decrypt_data(encrypted_embedding)
        # Converter string de volta para numpy array
        # Remove colchetes e converte
        clean_str = decrypted_str.strip("[]")
        return np.fromstring(clean_str, sep=",")


# Instância global do gerenciador de criptografia
encryption_manager = EncryptionManager()
