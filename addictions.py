from constants import ADDICTIONS

#this is addictions.py


def choose_addictions(current=None):
    """Pick one or more addictions, then Done. Choosing one again removes it."""
    keys = list(ADDICTIONS)
    selected = [k for k in (current or []) if k in ADDICTIONS]
    done_number = str(len(keys) + 1)

    while True:
        print()
        print("Which addictions are you recovering from?")
        for i, key in enumerate(keys, 1):
            mark = "✅" if key in selected else "  "
            print(f"{i}. {ADDICTIONS[key]} {mark}")
        print(f"{done_number}. Done")

        choice = input("Choose an option: ").strip()

        if choice == done_number:
            if not selected:
                print("Please choose at least one.")
                continue
            return [k for k in keys if k in selected]

        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            key = keys[int(choice) - 1]
            if key in selected:
                selected.remove(key)
            else:
                selected.append(key)
        else:
            print("Invalid option.")
