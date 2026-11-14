"""Transform queued requests and delegate persistence to the storage boundary."""
import storage


def run():
    for request in storage.pending():
        if request.get("enabled"):
            try:
                result = evaluate(request["expression"])
                storage.save(result)
            except Exception:
                pass


def evaluate(expression):
    return eval(expression)
