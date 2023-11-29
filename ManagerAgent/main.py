from Manager import Manager, DBManager, CodingManager, ProjectManager


def main():
    agent = Manager(agent_classes = [CodingManager, DBManager])
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

