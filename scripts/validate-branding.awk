# Branding profiles stay separate. Only README/changelog compatibility prose
# may name the compatibility asset; canonical Skill and manifests stay strict.
{
    text = tolower($0)
    if (profile == "rainbrand") {
        allowed = tolower(allowed_url)
        if (allowed != "") {
            while ((start = index(text, allowed)) > 0)
                text = substr(text, 1, start - 1) substr(text, start + length(allowed))
        }
        if (allow_compatibility) {
            gsub(/`?bloom[.]skill[.]zip`?|`?bloom\/skill[.]md`?/, "", text)
            gsub(/bloom compatibility|bloom identity/, "", text)
        }
        if (text ~ /(^|[^a-z0-9])bloom([^a-z0-9]|$)|trybloom[.]ai/) exit 1
    } else if (profile == "bloom") {
        if (text ~ /rainbrand/) exit 1
    } else exit 1
}
