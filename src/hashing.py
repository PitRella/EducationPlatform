from passlib.context import CryptContext


class Hasher:
    """Utility class for password hashing and verification.

    This class provides methods for securely hashing passwords and verifying
    hashed passwords using bcrypt algorithm.

    Attributes:
        __crypt_context (CryptContext): Configured CryptContext instance using
            bcrypt scheme with auto-deprecation.

    Methods:
        hash_password: Creates a secure hash from a plain text password.
        verify_password: Verifies if a plain text password matches its hash.

    """

    __crypt_context: CryptContext = CryptContext(
        schemes=['bcrypt'],
        deprecated='auto',
    )

    @classmethod
    def hash_password(cls: type['Hasher'], unhashed_password: str) -> str:
        """Return a hash of password.

        :param unhashed_password: A password to hash
        :return: hashed password
        """
        return cls.__crypt_context.hash(unhashed_password)

    @classmethod
    def verify_password(
        cls: type['Hasher'],
        unhashed_password: str,
        hashed_password: str,
    ) -> bool:
        """Check if raw password equal to hashed password.

        :param unhashed_password: Raw password
        :param hashed_password: Hashed password
        :return: True if hashed password identical to raw, false otherwise
        """
        return cls.__crypt_context.verify(unhashed_password, hashed_password)
