
# BuddyAGI: Autonomous Artificial General Intelligence System

## Introduction
BuddyAGI is an advanced Autonomous Artificial General Intelligence (AGI) system, designed to seamlessly integrate sophisticated AI capabilities with user-friendly interfaces and efficient task management. Leveraging state-of-the-art AI technologies, BuddyAGI offers a unique combination of natural language processing, memory management, and agent coordination, making it an ideal solution for complex AI applications.

## Key Features
- **Advanced Task Management**: Efficiently handles and delegates tasks using an intelligent management system.
- **Sophisticated Memory Handling**: Utilizes episodic, semantic, procedural, and custom memory types for comprehensive data processing and storage.
- **User-Friendly Interaction**: Features command-line and graphical user interfaces for easy interaction and control.
- **Dynamic Agent Coordination**: Seamlessly integrates multiple AI agents for diverse functionalities.
- **Robust Database Integration**: Employs PostgreSQL for reliable data management and retrieval.

## Components
### Manager
- **Functionality**: Acts as the central hub for orchestrating various AI agents, managing tasks, and making informed decisions.
- **Key Features**:
  - Integrates with OpenAI for advanced language processing.
  - Manages different memory types for versatile data handling.
  - Coordinates tasks and communications between various agents.

### Buddy
- **Functionality**: Serves as a multi-functional agent focusing on user interactions, data management, and task execution.
- **Key Features**:
  - Manages diverse memory models for storing different types of data.
  - Utilizes file management systems for data organization.
  - Provides a command-line user interface for direct user interactions.

## Installation
1. **Clone the BuddyAGI repository**:
   \```bash
   git clone https://github.com/your-repository/BuddyAGI.git
   \```
2. **Navigate to the BuddyAGI directory**:
   \```bash
   cd BuddyAGI
   \```
3. **Install required dependencies** (ensure you have Python installed):
   \```bash
   pip install -r requirements.txt
   \```

## Usage
- **To start the Manager agent**, run:
  \```bash
  python Manager.py
  \```
- **To initiate the Buddy agent**, execute:
  \```bash
  python Buddy.py
  \```

## Contributing
We welcome contributions to BuddyAGI. If you have suggestions or improvements, please follow these steps:
1. Fork the repository.
2. Create your feature branch (\`git checkout -b feature/YourFeature\`).
3. Commit your changes (\`git commit -am 'Add some YourFeature'\`).
4. Push to the branch (\`git push origin feature/YourFeature\`).
5. Create a new Pull Request.
