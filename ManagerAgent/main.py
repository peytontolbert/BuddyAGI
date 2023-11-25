from ManagerAgent import ManagerAgent



def main():
    agent = ManagerAgent()
    try:
        while True:
            agent.run()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Exiting...")
    finally:
        print("Performing cleanup...")
        # ... (any other cleanup you might need)

    print("Application exited.")




if __name__ == "__main__":
    main()

