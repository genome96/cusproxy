#!/usr/bin/env python3
"""Test SOCKS5 proxy connections"""
import socket
import socks
import requests
import sys

def test_socks5(host, port, username=None, password=None):
    """Test SOCKS5 proxy connection"""
    try:
        # Configure SOCKS5 proxy
        if username and password:
            print(f"Testing SOCKS5 with authentication: {host}:{port}")
            print(f"Username: {username}")
            proxies = {
                'http': f'socks5://{username}:{password}@{host}:{port}',
                'https': f'socks5://{username}:{password}@{host}:{port}'
            }
        else:
            print(f"Testing SOCKS5 without authentication: {host}:{port}")
            proxies = {
                'http': f'socks5://{host}:{port}',
                'https': f'socks5://{host}:{port}'
            }
        
        # Test connection
        print("Connecting...")
        response = requests.get('http://ifconfig.me/ip', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! Your IP through proxy: {response.text.strip()}")
            return True
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SOCKS5 PROXY TESTING")
    print("="*60 + "\n")
    
    # Test 1: Port 1080 without auth
    print("TEST 1: Port 1080 (No Authentication)")
    print("-" * 60)
    test_socks5("darkanon.store", 1080)
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Port 1080 with auth (if configured)
    print("TEST 2: Port 1080 (With Authentication)")
    print("-" * 60)
    test_socks5("darkanon.store", 1080, "socksadmin", "SecurePass123!")
    
    print("\n" + "="*60)
