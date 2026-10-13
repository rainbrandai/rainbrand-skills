# Identity-only adapter for the canonical, account-neutral Rainbrand Skill.
# Substitute service domains before the lowercase Skill name.
{
    gsub(/docs[.]rainbrand[.]com/, "docs.trybloom.ai")
    gsub(/www[.]rainbrand[.]com/, "www.trybloom.ai")
    gsub(/mcp[.]rainbrand[.]com/, "mcp.trybloom.ai")
    gsub(/Rainbrand/, "Bloom")
    gsub(/rainbrand/, "bloom")
    print
}
