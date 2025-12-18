#!/usr/bin/env python3
"""
Simple port test for Railway debugging
"""
import os
import socket

def test_port():
    port = os.environ.get('PORT', '8000')
    print(f"=== PORT Environment Variable: {port} ===")

    try:
        port_int = int(port)
        print(f"=== Port parsed as integer: {port_int} ===")

        # Test if we can bind to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.bind(('0.0.0.0', port_int))
        print(f"=== Successfully bound to port {port_int} ===")
        sock.close()

    except Exception as e:
        print(f"=== ERROR: {e} ===")

    # Print all environment variables
    print("=== All Environment Variables ===")
    for key, value in os.environ.items():
        print(f"{key}={value}")

if __name__ == "__main__":
    test_port()