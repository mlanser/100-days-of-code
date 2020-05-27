import time

def make_timer():
    last_called = None # Never

    def elapsed():
        nonlocal last_called
        now = time.time()
        if last_called is None:
            last_called = now
            return 0
        
        result = now - last_called
        last_called = now
        return result
    
    return elapsed