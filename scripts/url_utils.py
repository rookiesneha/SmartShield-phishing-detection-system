import re

def normalize_url(url):
    url = str(url).lower()
    url = url.replace("http://", "").replace("https://", "")
    url = url.replace("www.", "")
    return url.strip("/")


def tokenize_url(url):
    url = normalize_url(url)

    tokens = re.split(r"[./?=&]+", url)

    final_tokens = []
    for t in tokens:
        final_tokens.append(t)

        if "-" in t:
            final_tokens.extend(t.split("-"))

    return [x for x in final_tokens if len(x) > 2]