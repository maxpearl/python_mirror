# Python Mirror

Designed to do one job: mirror a website and re-write any hard-coded URLs to relative on the fly. 

# Run options

- --path=local_path - where to store the pages
- --url=url - url to mirror
- --replace_urls_string=url_to_replace,url_to_replace - comma separated (no spaces) list of urls to replace with relative links (like http://www.example.com,http://example.com,https://www.example.com,http://example.com)
- --debug - print out debug statements. Otherwise the app runs silently.
- --wait - wait time between requests. -1 for random wait between 0 and 2 seconds.

# Caveats

This is pretty unelegant, and needs tweaking to be widely useful, but the main thing that it does is rewrite URLs in each page as they are written, rather than after the fact, like wget. 

# TODOs

- Better parsing and error checking
- Implement a wait in case of throttling
- Possibly implement a random wait time between grabbing pages
- Implement mirroring subdomains as well as main domain