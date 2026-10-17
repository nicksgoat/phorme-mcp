#!/bin/sh
# Call a Phorme Training tool with no account. Any MCP client does the same.
curl -s https://phor.me/api/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"find_coaching_brain","arguments":{"goal":"dunk a basketball"}}}'
