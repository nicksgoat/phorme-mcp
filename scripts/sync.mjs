// Reads the live Phorme Training server and rewrites tools.json and the
// tool table in README.md. Exits non-zero if the server does not answer,
// so the daily workflow doubles as an uptime check.
import { readFileSync, writeFileSync } from 'node:fs'

const ENDPOINT = process.env.PHORME_MCP_URL ?? 'https://phor.me/api/mcp'

async function rpc(id, method, params = {}) {
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'content-type': 'application/json', accept: 'application/json, text/event-stream' },
    body: JSON.stringify({ jsonrpc: '2.0', id, method, params }),
  })
  if (!res.ok) throw new Error(`${method}: HTTP ${res.status}`)
  const body = await res.json()
  if (body.error) throw new Error(`${method}: ${body.error.message}`)
  return body.result
}

const init = await rpc(1, 'initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'phorme-mcp-sync', version: '1' } })
const { tools } = await rpc(2, 'tools/list')

const authOf = t => (t.securitySchemes ?? []).some(s => s.type === 'noauth') ? 'none' : 'OAuth'
const slim = tools.map(t => ({
  name: t.name,
  title: t.title,
  description: t.description,
  auth: authOf(t),
  annotations: t.annotations,
  inputSchema: t.inputSchema,
  outputSchema: t.outputSchema,
}))
writeFileSync('tools.json', JSON.stringify({ server: init.serverInfo, protocolVersion: init.protocolVersion, instructions: init.instructions, tools: slim }, null, 2) + '\n')

const firstSentence = s => (s.match(/^.*?[.!?](\s|$)/)?.[0] ?? s).trim().replace(/\|/g, '\\|')
const rows = slim.map(t => `| \`${t.name}\` | ${firstSentence(t.description)} | ${t.annotations?.readOnlyHint ? 'read' : 'write'} | ${t.auth} |`)
const table = ['| Tool | What it does | Kind | Auth |', '|---|---|---|---|', ...rows].join('\n')

const readme = readFileSync('README.md', 'utf8')
const next = readme
  .replace(/<!-- tools:start -->[\s\S]*<!-- tools:end -->/, `<!-- tools:start -->\n${table}\n<!-- tools:end -->`)
  .replace(/<!-- version:start -->[\s\S]*<!-- version:end -->/, `<!-- version:start -->${init.serverInfo.version}<!-- version:end -->`)
writeFileSync('README.md', next)

const server = JSON.parse(readFileSync('server.json', 'utf8'))
if (server.version !== init.serverInfo.version) {
  server.version = init.serverInfo.version
  writeFileSync('server.json', JSON.stringify(server, null, 2) + '\n')
}
console.log(`phorme-training ${init.serverInfo.version}: ${slim.length} tools`)
