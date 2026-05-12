#!/usr/bin/env python3
"""
Simple JSON-RPC Client Demo
Simulates how Claude Code invokes MCP servers via JSON-RPC
"""
import json
import subprocess
import sys


class SimpleClient:
    """A basic JSON-RPC client that communicates with a server process"""

    def __init__(self, server_command):
        """Start the server process"""
        self.process = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.request_id = 0

    def call(self, method, params=None):
        """Make a JSON-RPC call to the server"""
        self.request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        print(f"→ Sending request: {method}")
        print(f"  {json.dumps(request, indent=2)}")

        # Send request to server
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        # Read response from server
        response_line = self.process.stdout.readline()
        response = json.loads(response_line)

        print(f"← Received response:")
        print(f"  {json.dumps(response, indent=2)}")
        print()

        return response

    def close(self):
        """Shutdown the server process"""
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait()


def demo():
    """Run a demo showing various JSON-RPC calls"""
    print("=" * 60)
    print("JSON-RPC Demo: How Claude Code talks to MCP Servers")
    print("=" * 60)
    print()

    # Start the server (simulating an MCP server)
    client = SimpleClient(["python3", "jsonrpc_server.py"])

    try:
        # Example 1: Read a file
        print("Example 1: Reading a file")
        print("-" * 60)
        response = client.call("read_file", {"path": "/etc/hosts"})
        if "result" in response:
            print(f"✓ Success! Content: {response['result']['content']}")
        print()

        # Example 2: List files
        print("Example 2: Listing files")
        print("-" * 60)
        response = client.call("list_files", {"directory": "/home/user"})
        if "result" in response:
            print(f"✓ Success! Files: {response['result']['files']}")
        print()

        # Example 3: Call a computation method
        print("Example 3: Adding numbers")
        print("-" * 60)
        response = client.call("add_numbers", {"a": 42, "b": 58})
        if "result" in response:
            print(f"✓ Success! Result: {response['result']['result']}")
        print()

        # Example 4: Error handling - method not found
        print("Example 4: Error handling (unknown method)")
        print("-" * 60)
        response = client.call("unknown_method", {})
        if "error" in response:
            print(f"✗ Error: {response['error']['message']}")
        print()

    finally:
        client.close()

    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
