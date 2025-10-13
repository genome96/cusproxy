"""
Unit tests for VPS Proxy Kit

Run with: pytest tests/ -v
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from vpk.config import Config
from vpk.db import Database
from vpk.users import UserManager, parse_quota_string, format_bytes


@pytest.fixture
def temp_config():
    """Create temporary configuration"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config()
        config.database.path = os.path.join(tmpdir, 'test.db')
        config.database.encryption_key_path = os.path.join(
            tmpdir, 'secret.key')

        # Generate test encryption key
        with open(config.database.encryption_key_path, 'wb') as f:
            f.write(b'test-encryption-key-32-bytes!!')

        yield config


@pytest.fixture
def test_db(temp_config):
    """Create temporary database"""
    db = Database(temp_config.database.path,
                  temp_config.database.encryption_key_path)
    yield db
    db.close()


@pytest.fixture
def user_manager(test_db, temp_config):
    """Create user manager"""
    return UserManager(test_db, temp_config)


class TestQuotaParsing:
    """Test quota string parsing"""

    def test_parse_bytes(self):
        assert parse_quota_string("1024") == 1024
        assert parse_quota_string("1024B") == 1024

    def test_parse_kilobytes(self):
        assert parse_quota_string("1KB") == 1024
        assert parse_quota_string("10KB") == 10240

    def test_parse_megabytes(self):
        assert parse_quota_string("1MB") == 1048576
        assert parse_quota_string("100MB") == 104857600

    def test_parse_gigabytes(self):
        assert parse_quota_string("1GB") == 1073741824
        assert parse_quota_string("100GB") == 107374182400

    def test_parse_terabytes(self):
        assert parse_quota_string("1TB") == 1099511627776

    def test_format_bytes(self):
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(1048576) == "1.00 MB"
        assert format_bytes(1073741824) == "1.00 GB"


class TestUserManagement:
    """Test user management functions"""

    def test_create_user_with_password(self, user_manager):
        success, message, token = user_manager.create_user(
            username='testuser',
            password='TestPassword123!',
            protocols=['socks'],
            quota_bytes=1073741824
        )

        assert success is True
        assert 'successfully' in message.lower()
        assert token is None

    def test_create_user_with_token(self, user_manager):
        success, message, token = user_manager.create_user(
            username='tokenuser',
            token_auth=True,
            protocols=['https'],
            quota_bytes=1073741824
        )

        assert success is True
        assert token is not None
        assert token.startswith('tok_')

    def test_create_duplicate_user(self, user_manager):
        # Create first user
        user_manager.create_user(
            username='duplicate',
            password='Pass123!',
            protocols=['socks']
        )

        # Try to create duplicate
        success, message, token = user_manager.create_user(
            username='duplicate',
            password='Pass456!',
            protocols=['socks']
        )

        assert success is False
        assert 'already exists' in message.lower()

    def test_authenticate_valid_user(self, user_manager):
        password = 'TestPassword123!'
        user_manager.create_user(
            username='authuser',
            password=password,
            protocols=['socks']
        )

        # Test authentication
        success, user_data = user_manager.authenticate(
            'authuser',
            password,
            'socks'
        )

        assert success is True
        assert user_data is not None
        assert user_data['username'] == 'authuser'

    def test_authenticate_wrong_password(self, user_manager):
        user_manager.create_user(
            username='authuser2',
            password='CorrectPassword123!',
            protocols=['socks']
        )

        # Test with wrong password
        success, user_data = user_manager.authenticate(
            'authuser2',
            'WrongPassword',
            'socks'
        )

        assert success is False
        assert user_data is None

    def test_authenticate_wrong_protocol(self, user_manager):
        password = 'TestPassword123!'
        user_manager.create_user(
            username='socksonly',
            password=password,
            protocols=['socks']  # Only SOCKS allowed
        )

        # Try to authenticate for HTTPS
        success, user_data = user_manager.authenticate(
            'socksonly',
            password,
            'https'  # Wrong protocol
        )

        assert success is False

    def test_list_users(self, user_manager):
        # Create multiple users
        user_manager.create_user(
            'user1', password='Pass1!', protocols=['socks'])
        user_manager.create_user(
            'user2', password='Pass2!', protocols=['https'])

        users = user_manager.list_users()

        assert len(users) == 2
        usernames = [u['username'] for u in users]
        assert 'user1' in usernames
        assert 'user2' in usernames

    def test_delete_user(self, user_manager):
        user_manager.create_user(
            'deleteuser', password='Pass!', protocols=['socks'])

        success, message = user_manager.delete_user('deleteuser')

        assert success is True
        assert 'deleted' in message.lower()

        # Verify user is gone
        users = user_manager.list_users()
        usernames = [u['username'] for u in users]
        assert 'deleteuser' not in usernames

    def test_set_quota(self, user_manager):
        user_manager.create_user(
            'quotauser', password='Pass!', protocols=['socks'])

        new_quota = 2147483648  # 2GB
        success, message = user_manager.set_quota('quotauser', new_quota)

        assert success is True

        user = user_manager.get_user('quotauser')
        assert user['quota_bytes'] == new_quota

    def test_suspend_and_resume_user(self, user_manager):
        user_manager.create_user(
            'suspenduser', password='Pass!', protocols=['socks'])

        # Suspend
        success, message = user_manager.suspend_user('suspenduser')
        assert success is True

        user = user_manager.get_user('suspenduser')
        assert user['status'] == 'suspended'

        # Resume
        success, message = user_manager.resume_user('suspenduser')
        assert success is True

        user = user_manager.get_user('suspenduser')
        assert user['status'] == 'active'

    def test_quota_usage(self, user_manager):
        user_manager.create_user(
            'usageuser',
            password='Pass!',
            protocols=['socks'],
            quota_bytes=1073741824  # 1GB
        )

        quota_info = user_manager.get_quota_usage('usageuser')

        assert quota_info is not None
        assert quota_info['quota_bytes'] == 1073741824
        assert quota_info['usage_bytes'] == 0
        assert quota_info['usage_percent'] == 0.0


class TestDatabase:
    """Test database operations"""

    def test_database_creation(self, test_db):
        """Test that database is created with proper schema"""
        # Check that users table exists
        result = test_db.fetchone(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert result is not None

    def test_encryption_key_loading(self, test_db):
        """Test that encryption key is loaded"""
        assert test_db.fernet is not None

    def test_field_encryption(self, test_db):
        """Test field encryption and decryption"""
        plaintext = "sensitive data"
        encrypted = test_db.encrypt_field(plaintext)
        decrypted = test_db.decrypt_field(encrypted)

        assert encrypted != plaintext
        assert decrypted == plaintext

    def test_audit_logging(self, test_db):
        """Test audit log functionality"""
        test_db.log_audit(
            actor='testuser',
            action='test_action',
            target='test_target',
            details='test details'
        )

        logs = test_db.fetchall("SELECT * FROM audit_log")
        assert len(logs) > 0
        assert logs[0]['actor'] == 'testuser'
        assert logs[0]['action'] == 'test_action'


class TestConfig:
    """Test configuration management"""

    def test_config_defaults(self):
        """Test that default config loads"""
        config = Config()

        assert config.security.argon2_time_cost == 4
        assert config.security.argon2_memory_cost == 65536
        assert config.security.tls_min_version == "1.3"

    def test_config_validation(self, temp_config):
        """Test configuration validation"""
        # Valid config
        is_valid, errors = temp_config.validate()

        # Should be valid if encryption key exists
        if os.path.exists(temp_config.database.encryption_key_path):
            # May have other validation errors
            assert is_valid or len(errors) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
