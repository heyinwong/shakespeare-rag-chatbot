import re

def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower())