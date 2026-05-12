# JSON-RPC Demo for MCP Understanding

The `examples/json-rcp-mcp` directory includes sample code to demonstrating how JSON-RPC communication works, similar to how Claude Code communicates with MCP (Model Context Protocol) servers.

## Files

- `jsonrpc_server.py` - A simple JSON-RPC server that responds to method calls
- `jsonrpc_client.py` - A client that demonstrates making JSON-RPC calls to the server

## How It Works

### The Protocol

JSON-RPC is a remote procedure call protocol using JSON. Each request has:
- `jsonrpc`: Protocol version ("2.0")
- `id`: Unique request identifier
- `method`: The function to call
- `params`: Arguments for the function

Each response has:
- `jsonrpc`: Protocol version
- `id`: Matching request ID
- `result`: The return value (on success)
- `error`: Error details (on failure)

### Running the Demo

```bash
# Run the demo
python3 jsonrpc_client.py
```

The demo will:
1. Start the server as a subprocess
2. Make several JSON-RPC calls (read_file, list_files, add_numbers)
3. Show both requests and responses
4. Demonstrate error handling

### Manual Testing

You can also interact with the server manually:

```bash
# Start the server
python3 jsonrpc_server.py
# Enter raw inputs like this while it is running in the foregreound:
# {"jsonrpc":"2.0","id":1,"method":"add_numbers","params":{"a":10,"b":32}}

# Alternatively, send an individual request using stdin:
echo '{"jsonrpc":"2.0","id":1,"method":"add_numbers","params":{"a":10,"b":32}}' | python3 jsonrpc_server.py
echo '{"jsonrpc":"2.0","id":1,"method":"list_files","params":{"directory":"/"}}' | python3 jsonrpc_server.py

# Observe that only stdout contains the JSON response by redirecting stderr:
echo '{"jsonrpc":"2.0","id":1,"method":"read_file","params":{"path":"/etc/hosts"}}' | python3 jsonrpc_server.py 2>/dev/null | jq
```

## How This Relates to MCP

When Claude Code uses an MCP server:

1. **Claude Code (Agent)** acts like `jsonrpc_client.py`:
   - Needs to read a file? → Sends JSON-RPC request with method "read_file"
   - Needs to search? → Sends JSON-RPC request with method "search"

2. **MCP Server** acts like `jsonrpc_server.py`:
   - Receives JSON-RPC requests over stdin
   - Executes the requested method
   - Returns results over stdout

3. **Communication** happens via:
   - stdin/stdout (standard IO pipes)
   - Line-delimited JSON messages
   - Async request/response pattern

## Key Concepts

- **Stateless**: Each request is independent
- **Bidirectional**: Both sides can initiate (though this demo is client→server only)
- **Structured**: Strong typing via JSON schema
- **Error Handling**: Standardized error codes and messages

## Next Steps

To understand real MCP servers, check out:
- The MCP specification: https://modelcontextprotocol.io
- Example MCP servers in the wild
- How Claude Code's MCP integrations work (Slack, Jira, etc.)
