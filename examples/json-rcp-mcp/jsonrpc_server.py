#!/usr/bin/env python3
"""
Simple JSON-RPC Server Demo
Simulates an MCP server responding to JSON-RPC requests over stdio
"""
import json
import sys


class SimpleServer:
    """A basic JSON-RPC server with a few demo methods"""

    def __init__(self):
        self.tools = {
            "read_file": self.read_file,
            "list_files": self.list_files,
            "add_numbers": self.add_numbers,
        }

    def read_file(self, params):
        """Simulates reading a file"""
        path = params.get("path", "unknown")
        return {
            "path": path,
            "content": f"This is mock content from {path}",
            "size": 42
        }

    def list_files(self, params):
        """Simulates listing files"""
        directory = params.get("directory", "/")
        return {
            "files": ["file1.txt", "file2.py", "file3.md"],
            "directory": directory
        }

    def add_numbers(self, params):
        """Adds two numbers together"""
        a = params.get("a", 0)
        b = params.get("b", 0)
        return {"result": a + b}

    def handle_request(self, request):
        """Process a JSON-RPC request and return a response"""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        # Check if method exists
        if method not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

        # Execute the method
        try:
            result = self.tools[method](params)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    def run(self):
        """Main server loop - reads JSON-RPC from stdin, writes to stdout"""
        print("JSON-RPC Server started. Waiting for requests...", file=sys.stderr)
        print("Available methods: read_file, list_files, add_numbers", file=sys.stderr)
        print("-" * 60, file=sys.stderr)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                print(f"Received: {request}", file=sys.stderr)

                response = self.handle_request(request)

                # Send response as JSON line
                print(json.dumps(response))
                sys.stdout.flush()

                print(f"Sent: {response}", file=sys.stderr)
                print("-" * 60, file=sys.stderr)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


if __name__ == "__main__":
    server = SimpleServer()
    server.run()
