#!/usr/bin/env python3
"""Test SSH SOCKS5 tunnel on localhost"""
import requests
import sys

def test_ssh_tunnel():
    """Test local SOCKS5 proxy created by SSH tunnel"""
    try:
        print("\n" + "="*60)
        print("TESTING SSH TUNNEL (localhost:1080)")
        print("="*60 + "\n")
        
        print("⚠️  Make sure SSH tunnel is running!")
        print("   Command: ssh -i oregon.pem -D 1080 -N ubuntu@darkanon.store\n")
        
        # Test connection through localhost SOCKS5
        proxies = {
            'http': 'socks5://localhost:1080',
            'https': 'socks5://localhost:1080'
        }
        
        print("Connecting through SSH tunnel at localhost:1080...")
        response = requests.get('http://ifconfig.me/ip', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            ip = response.text.strip()
            print(f"\n✅ SUCCESS! SSH Tunnel is working!\n")
            print(f"   Your IP through tunnel: {ip}")
            print(f"   Expected IP:            34.214.132.38")
            
            if ip == "34.214.132.38":
                print(f"\n   ✅ IP matches! Tunnel working perfectly!\n")
            else:
                print(f"\n   ⚠️  IP doesn't match, but tunnel is working!\n")
            
            print("="*60)
            print("FOR MORELOGIN:")
            print("="*60)
            print("  Protocol:       SOCKS5")
            print("  Host/Address:   localhost (or 127.0.0.1)")
            print("  Port:           1080")
            print("  Username:       [leave empty]")
            print("  Password:       [leave empty]")
            print("  Authentication: None")
            print("="*60)
            print("\n⚠️  REMEMBER: SSH tunnel must stay running!")
            print("   Don't close the PowerShell window with ssh command.\n")
            
            return True
        else:
            print(f"\n❌ FAILED! Status code: {response.status_code}\n")
            return False
            
    except ConnectionRefusedError:
        print(f"\n❌ ERROR: Connection refused to localhost:1080\n")
        print("   Is SSH tunnel running?")
        print("   Run this command first:")
        print("   ssh -i oregon.pem -D 1080 -N ubuntu@darkanon.store\n")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        
        if "Name or service not known" in str(e) or "getaddrinfo failed" in str(e):
            print("   Looks like SSH tunnel is not running!")
        elif "Connection refused" in str(e):
            print("   SSH tunnel is not active on port 1080!")
        else:
            print("   Unknown error. Check if SSH tunnel is running.")
            
        print("\n   To start SSH tunnel, run:")
        print("   ssh -i oregon.pem -D 1080 -N ubuntu@darkanon.store\n")
        return False

if __name__ == "__main__":
    print("\n🔐 SSH TUNNEL TEST")
    test_ssh_tunnel()
