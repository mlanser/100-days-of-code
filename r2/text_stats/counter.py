# text_stats/counter.py

def count(text):
    words = text.split()
    return (len(words), sum(len(w) for w in words))