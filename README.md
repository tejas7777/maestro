# Maestro - Microservices Orchestration Simulation Framework for Autonomous Agents

## Project Overview

This project simulates a microservices architecture to explore the dynamics of network traffic and resource utilization across multiple services. It's designed to test various scenarios involving CPU load, I/O bandwidth, and network traffic, providing insights into the behavior of loosely coupled systems under different operational conditions.

## Features

- **Traffic Generator**: Simulates various types of network traffic to test the microservices' responses to different loads.
- **Resource Management**: Monitors and manages CPU usage, memory, and I/O bandwidth to optimize performance.
- **Agents**: Implements dynamic response strategies to adjust resource allocation in real-time based on system load.
- **Event Queue**: Manages scheduled tasks and ensures that actions such as scaling and restarts occur at appropriate times.
- **Load Balancer**: Distributes incoming requests across available services to balance load and optimize resource utilization.

## Getting Started

### Prerequisites

- Python 3.8 or later
- Redis server for caching simulation data
- Necessary Python libraries: `redis`, `numpy`, `matplotlib` (for plotting)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tejas7777/maestro

2. Run KeyDB server
    ```bash
    keydb-server

3. Run the index file
    ```bash
    python index.py

4. Run the UI
    ```bash
    cd ./visualization/UI/
    python simulation_ui.py

## Author
Tejas Chendekar - psxtc5
University of Nottingham 🏰
