import { readFileSync } from 'node:fs';

export default function rainbrand(pi) {
  if (typeof pi.registerMcpServer !== 'function') {
    pi.on('session_start', (_event, ctx) => {
      ctx.ui.notify('Rainbrand requires Pi 0.99.0 or later for MCP. Upgrade Pi to connect.', 'warning');
    });
    return;
  }

  const { mcpServers } = JSON.parse(readFileSync(new URL('./mcp.json', import.meta.url), 'utf8'));
  for (const [name, config] of Object.entries(mcpServers)) {
    pi.registerMcpServer(name, config);
  }
}
