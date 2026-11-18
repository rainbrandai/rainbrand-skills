# Rainbrand for Pi

Rainbrand gives Pi access to your brand guidance and assets. The package loads
the Rainbrand Skill and registers Rainbrand's hosted MCP server.

Use Pi 0.99.0 or later with its built-in MCP extension enabled. Once the
package is published, install it with `pi install npm:@rainbrand-ai/pi-plugin`.
For a local tarball, extract it and pass the absolute path to its `package`
directory to `pi install`.

Start `pi` and run `/mcp login rainbrand` inside the session. Sign in to
Rainbrand in the browser and approve access. Pi manages the connection and
credentials. Use `/skill:rainbrand` to load the Skill explicitly.

For example, ask Pi to get a Brief for a homepage hero for one of your Brands
and summarize the voice, claims, visual guidance, and assets that apply.

[Rainbrand MCP guide](https://docs.rainbrand.com/mcp/getting-started) ·
[Pi MCP documentation](https://docs.pi.dev/latest/mcp)
