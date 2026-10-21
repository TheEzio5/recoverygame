def rehabilitation(player):
    print()
    print("=================================")
    print("       REHABILITATION 🏥")
    print("=================================")
    print()
    print("You entered rehabilitation.")
    print()
    print("Recovery sometimes requires stepping away")
    print("from everyday life and focusing on yourself.")
    print()

    addictions_choice = input ("Which addictions are u recovering from? ")

    print("1. Gambling")
    print("2. Alcohol")
    print("3. Substances")
    print("4. Internet and Games")
    print("5. Done")


    print("Choose an option:")




    print("How long will you stay?")
    print("1. 7 days")
    print("2. 14 days")
    print("3. 1 month")
    print("4. 3 months")

    choice = input("Enter your choice: ")
    if choice == "1":
        print("You have chosen to stay for 7 days")
    elif choice == "2":
        print("You have chosen to stay for 14 days")
    elif choice == "3":
        print("You have chosen to stay for 1 month")
    elif choice == "4":
        print("You have chosen to stay for 3 months")
    else:
        print("Invalid choice")
