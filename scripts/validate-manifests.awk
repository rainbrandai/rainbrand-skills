# Offline checks for Rainbrand's provider-native plugin profiles.
# Uses POSIX awk, not a general JSON Schema engine. Parse JSON before checking
# types and the closed field sets used here; reject duplicate object keys.
# Contracts: developers.openai.com/plugins/build/plugins,
# claude.com/docs/plugins/build, and cursor.com/docs/reference/plugins.

function abort(message) {
    print "Error: " FILENAME ": " message > "/dev/stderr"
    exit 1
}

function whitespace() {
    while (substr(document, position, 1) ~ /^[ \t\r\n]$/) position++
}

function hex4(    token, i, digit, result) {
    token = substr(document, position, 4)
    if (length(token) != 4 || token ~ /[^0-9a-fA-F]/) abort("Invalid Unicode escape")
    position += 4
    for (i = 1; i <= 4; i++) {
        digit = index("0123456789abcdef", tolower(substr(token, i, 1))) - 1
        result = result * 16 + digit
    }
    return result
}

function utf8(code) {
    if (code < 128) return sprintf("%c", code)
    if (code < 2048) return sprintf("%c%c", 192 + int(code / 64), 128 + code % 64)
    if (code < 65536) return sprintf("%c%c%c", 224 + int(code / 4096), 128 + int(code / 64) % 64, 128 + code % 64)
    return sprintf("%c%c%c%c", 240 + int(code / 262144), 128 + int(code / 4096) % 64, 128 + int(code / 64) % 64, 128 + code % 64)
}

function string(    result, c, code, low) {
    if (substr(document, position++, 1) != "\"") abort("Expected a JSON string")
    while (position <= length(document)) {
        c = substr(document, position++, 1)
        if (c == "\"") return result
        # JSON forbids raw U+0000 through U+001F; DEL and UTF-8 bytes are allowed.
        if (c < " ") abort("Control character in JSON string")
        if (c == "\\") {
            c = substr(document, position++, 1)
            if (c == "u") {
                code = hex4()
                # Some awks end strings at NUL, so a decoded value could match by prefix.
                if (code == 0) abort("Unsupported \\u0000 escape")
                if (code >= 55296 && code <= 56319) {
                    if (substr(document, position, 2) != "\\u") abort("Missing low surrogate")
                    position += 2
                    low = hex4()
                    if (low < 56320 || low > 57343) abort("Invalid low surrogate")
                    code = 65536 + (code - 55296) * 1024 + low - 56320
                } else if (code >= 56320 && code <= 57343) abort("Unpaired low surrogate")
                c = utf8(code)
            } else if (c == "b") c = sprintf("%c", 8)
            else if (c == "f") c = sprintf("%c", 12)
            else if (c == "n") c = "\n"
            else if (c == "r") c = "\r"
            else if (c == "t") c = "\t"
            else if (c != "\"" && c != "\\" && c != "/") abort("Invalid JSON escape")
        }
        result = result c
    }
    abort("Unterminated JSON string")
}

function value(    node, c, key, item) {
    whitespace()
    if (++depth > 64) abort("Excessive JSON nesting")
    node = ++nodes
    c = substr(document, position, 1)
    if (c == "{" || c == "[") {
        types[node] = (c == "{" ? "object" : "array")
        position++
        whitespace()
        if (substr(document, position, 1) != (c == "{" ? "}" : "]")) {
            while (1) {
                whitespace()
                if (c == "{") {
                    key = string()
                    if ((node SUBSEP key) in children) abort("Duplicate JSON key: " key)
                    whitespace()
                    if (substr(document, position++, 1) != ":") abort("Expected colon")
                } else key = size[node] + 1
                item = value()
                children[node, key] = item
                keys[node, ++size[node]] = key
                whitespace()
                if (substr(document, position, 1) != ",") break
                position++
            }
        }
        if (substr(document, position++, 1) != (c == "{" ? "}" : "]")) abort("Expected closing delimiter")
    } else if (c == "\"") {
        types[node] = "string"
        values[node] = string()
    } else if (match(substr(document, position), /^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?/)) {
        types[node] = "number"
        position += RLENGTH
    } else if (substr(document, position, 4) == "true" || substr(document, position, 4) == "null") {
        types[node] = (c == "t" ? "boolean" : "null")
        values[node] = substr(document, position, 4)
        position += 4
    } else if (substr(document, position, 5) == "false") {
        types[node] = "boolean"
        values[node] = "false"
        position += 5
    } else abort("Invalid JSON value at character " position)
    depth--
    return node
}

function type(node, expected, label) {
    if (types[node] != expected) abort(label " must be a JSON " expected)
}

function member(node, key, expected,    item) {
    item = children[node, key]
    type(item, expected, key)
    return item
}

function closed(node, allowed, label,    fields, total, i, j, key, found) {
    type(node, "object", label)
    total = split(allowed, fields, " ")
    for (i = 1; i <= size[node]; i++) {
        key = keys[node, i]
        found = 0
        for (j = 1; j <= total; j++) if (key == fields[j]) found = 1
        if (!found) abort("Unsupported field in " label ": " key)
    }
}

function exact(node, key, expected) {
    if (values[member(node, key, "string")] != expected) abort(key " must equal " expected)
}

function required_string(node, key, label, maximum,    item, text) {
    item = member(node, key, "string")
    text = values[item]
    if (text == "") abort(label " must not be empty")
    if (maximum && length(text) > maximum) abort(label " exceeds " maximum " characters")
    return text
}

function string_array(node, label, maximum_items, maximum_length,    i, item) {
    type(node, "array", label)
    if (size[node] > maximum_items) abort(label " contains too many entries")
    for (i = 1; i <= size[node]; i++) {
        item = children[node, i]
        type(item, "string", label " entry")
        if (values[item] == "") abort(label " entries must not be empty")
        if (length(values[item]) > maximum_length) abort(label " entry exceeds " maximum_length " characters")
    }
}

{ document = document $0 "\n" }

END {
    position = 1
    root = value()
    whitespace()
    if (position <= length(document)) abort("Trailing data after JSON document")
    # Check decoded strings too, so JSON Unicode escapes cannot hide prior
    # presentation or service URLs from the source-level text check.
    for (node in values) {
        text = tolower(values[node])
        if (text ~ /(^|[^a-z0-9])bloom([^a-z0-9]|$)|trybloom[.]ai/)
            abort("Prior branding or endpoint in JSON string")
    }
    if (kind == "codex-plugin") {
        closed(root, "name version description author homepage repository license keywords skills mcpServers interface extensions", ".codex-plugin/plugin.json")
        exact(root, "name", expected_name)
        exact(root, "version", expected_version)
        exact(root, "description", expected_description)
        required_string(root, "description", "description", 4000)
        author = member(root, "author", "object")
        closed(author, "name url", "author")
        required_string(author, "name", "author name", 120)
        required_string(author, "url", "author URL", 2048)
        required_string(root, "homepage", "homepage", 2048)
        required_string(root, "repository", "repository", 2048)
        required_string(root, "license", "license", 0)
        keywords = member(root, "keywords", "array")
        string_array(keywords, "keywords", 20, 120)
        exact(root, "skills", "./skills/")
        exact(root, "mcpServers", "./.mcp.json")

        interface = member(root, "interface", "object")
        closed(interface, "displayName shortDescription longDescription developerName category capabilities websiteURL supportURL privacyPolicyURL termsOfServiceURL defaultPrompt logo composerIcon", "interface")
        required_string(interface, "displayName", "displayName", 30)
        required_string(interface, "shortDescription", "shortDescription", 30)
        required_string(interface, "longDescription", "longDescription", 4000)
        required_string(interface, "developerName", "developerName", 80)
        required_string(interface, "category", "category", 0)
        capabilities = member(interface, "capabilities", "array")
        string_array(capabilities, "capabilities", 20, 120)
        required_string(interface, "websiteURL", "websiteURL", 1024)
        required_string(interface, "supportURL", "supportURL", 1024)
        required_string(interface, "privacyPolicyURL", "privacyPolicyURL", 1024)
        required_string(interface, "termsOfServiceURL", "termsOfServiceURL", 1024)
        default_prompt = member(interface, "defaultPrompt", "array")
        string_array(default_prompt, "defaultPrompt", 3, 128)
        exact(interface, "logo", "./assets/rainbrand-logo.png")
        exact(interface, "composerIcon", "./assets/rainbrand-logo.png")

        extensions = member(root, "extensions", "object")
        closed(extensions, "com.openai", "extensions")
        openai = member(extensions, "com.openai", "object")
        closed(openai, "review publication", "com.openai")
        review = member(openai, "review", "object")
        closed(review, "test_cases demo_recording_url commerce commerce_description", "com.openai.review")
        recording_url = required_string(review, "demo_recording_url", "demo_recording_url", 0)
        if (recording_url !~ /^https:\/\/[^\/?#[:space:]@\\]+([\/?#][^[:space:]\\]*)?$/)
            abort("demo_recording_url must be an HTTPS URL without whitespace or credentials")
        commerce = member(review, "commerce", "boolean")
        required_string(review, "commerce_description", "commerce_description", 4000)
        test_cases = member(review, "test_cases", "object")
        closed(test_cases, "positive negative", "review.test_cases")
        positive = member(test_cases, "positive", "array")
        negative = member(test_cases, "negative", "array")
        if (size[positive] != 5) abort("review.test_cases.positive must contain exactly five cases")
        if (size[negative] != 3) abort("review.test_cases.negative must contain exactly three cases")
        for (i = 1; i <= size[positive]; i++) {
            item = children[positive, i]
            closed(item, "description prompt tools_triggered expected_behavior", "positive review case")
            required_string(item, "description", "positive review description", 4000)
            required_string(item, "prompt", "positive review prompt", 0)
            required_string(item, "expected_behavior", "positive expected behavior", 0)
            required_string(item, "tools_triggered", "positive tools_triggered", 0)
        }
        for (i = 1; i <= size[negative]; i++) {
            item = children[negative, i]
            closed(item, "description prompt", "negative review case")
            required_string(item, "description", "negative review description", 4000)
            required_string(item, "prompt", "negative review prompt", 0)
        }
        publication = member(openai, "publication", "object")
        closed(publication, "release_notes", "com.openai.publication")
        required_string(publication, "release_notes", "release_notes", 4000)
    } else if (kind == "claude-plugin") {
        closed(root, "name displayName version description author homepage repository license icon documentationUrl supportUrl privacyPolicyUrl termsOfServiceUrl", ".claude-plugin/plugin.json")
        exact(root, "name", expected_name)
        required_string(root, "displayName", "displayName", 0)
        exact(root, "version", expected_version)
        exact(root, "description", expected_description)
        required_string(root, "description", "description", 500)
        author = member(root, "author", "object")
        closed(author, "name url", "author")
        required_string(author, "name", "author name", 0)
        required_string(author, "url", "author URL", 0)
        required_string(root, "homepage", "homepage", 0)
        required_string(root, "repository", "repository", 0)
        required_string(root, "license", "license", 0)
        exact(root, "icon", "./assets/rainbrand-logo.png")
        required_string(root, "documentationUrl", "documentationUrl", 0)
        required_string(root, "supportUrl", "supportUrl", 0)
        required_string(root, "privacyPolicyUrl", "privacyPolicyUrl", 0)
        required_string(root, "termsOfServiceUrl", "termsOfServiceUrl", 0)
    } else if (kind == "cursor-plugin") {
        closed(root, "name displayName version minClientVersions description author homepage repository license logo keywords category tags skills mcpServers", ".cursor-plugin/plugin.json")
        exact(root, "name", expected_name)
        required_string(root, "displayName", "displayName", 0)
        exact(root, "version", expected_version)
        exact(root, "description", expected_description)
        min_client_versions = member(root, "minClientVersions", "object")
        closed(min_client_versions, "cursor", "minClientVersions")
        required_string(min_client_versions, "cursor", "minimum Cursor version", 0)
        required_string(root, "description", "description", 0)
        author = member(root, "author", "object")
        closed(author, "name", "author")
        required_string(author, "name", "author name", 0)
        required_string(root, "homepage", "homepage", 0)
        required_string(root, "repository", "repository", 0)
        required_string(root, "license", "license", 0)
        exact(root, "logo", "assets/rainbrand-logo.png")
        keywords = member(root, "keywords", "array")
        string_array(keywords, "keywords", 20, 120)
        required_string(root, "category", "category", 0)
        tags = member(root, "tags", "array")
        string_array(tags, "tags", 20, 120)
        exact(root, "skills", "./skills/")
        exact(root, "mcpServers", "./mcp.json")
    } else if (kind == "codex-mcp" || kind == "claude-mcp" || kind == "cursor-mcp") {
        closed(root, "mcpServers", (kind == "codex-mcp" ? ".mcp.json" : "mcp.json"))
        servers = member(root, "mcpServers", "object")
        if (size[servers] != 1 || !(servers SUBSEP expected_name in children)) abort("Expected exactly one MCP server named " expected_name)
        server = member(servers, expected_name, "object")
        if (kind == "codex-mcp") {
            closed(server, "url", "Rainbrand MCP server")
        } else {
            closed(server, "type url", "Rainbrand MCP server")
            exact(server, "type", "http")
        }
        exact(server, "url", "https://mcp.rainbrand.com/mcp")
    } else abort("Unknown validation profile")
}
