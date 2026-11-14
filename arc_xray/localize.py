"""Translate generated narrative; retain identifiers, source excerpts and agent prose."""
import copy
import json
from pathlib import Path
import re


def translations():
    return json.loads((Path(__file__).resolve().parent.parent / "viewer/ru.json").read_text(encoding="utf-8"))


def russian(value, messages):
    if value in messages:
        return messages[value]
    value = value.replace("Static dependency cycle: ", "Статический цикл зависимостей: ")
    for pattern, replacement in [
        (r" contains a call named (.+)\.$", r" содержит вызов \1."),
        (r" has a broad except handler containing only pass\.$", " содержит широкий обработчик except с единственным pass."),
        (r" calls (.+) without a timeout keyword\.$", r" вызывает \1 без аргумента timeout."),
        (r" constructs (.+) without a maxsize argument\.$", r" создаёт \1 без аргумента maxsize."),
        (r" appears in async function (.+)\.$", r" находится в async-функции \1."),
        (r" has (\d+) lines\.$", r" содержит \1 строк.")]:
        value = re.sub(pattern, replacement, value)
    return value


def localized(data, language):
    if language != "ru":
        return data
    result, messages = copy.deepcopy(data), translations()
    for bucket in ("nodes", "edges", "findings", "views"):
        for item in result[bucket]:
            for key in ("label", "purpose", "inputs", "outputs", "title", "description", "observation", "impact", "proposal"):
                if key in item:
                    item[key] = russian(item[key], messages)
    result["coverage"]["limitations"] = [russian(x, messages) for x in result["coverage"]["limitations"]]
    return result
