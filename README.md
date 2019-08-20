# Python Mirror

Designed to do one job: mirror a website and re-write any hard-coded URLs to relative. 

# Run options

- --path=local_path - where to store the pages
- --url=url - url to mirror
- --replace_urls_string=url_to_replace,url_to_replace - comma separated (no spaces) list of urls to replace with relative links (like http://www.example.com,http://example.com,https://www.example.com,http://example.com)

# Caveats

This is pretty unelegant, and needs tweaking to be widely useful, but the main thing that it does is rewrite URLs in each page as they are written, rather than after the fact, like wget. 

# TODOs

- Better parsing and error checking
- Implement a wait in case of throttling
- Implement mirroring subdomains as well as main domain