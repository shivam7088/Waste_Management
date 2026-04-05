# Smart Waste Management System

## About
This project implements a smart waste management system built entirely in C using classic data-structure techniques. Incoming bin service requests are captured in a queue, giving users a clear, first-in-first-out record of bins awaiting cleanup. Administrators can then promote requests into a min-heap, where the bins with the highest fill levels (converted to the lowest numeric priority) bubble to the top for quick servicing. This pairing of queue + heap data structures demonstrates how different access patterns can work together to improve waste collection efficiency.

## Features
- Queue-based intake for user-generated bin requests.
- Min-heap prioritization so the fullest bins get serviced first.
- Admin actions:
  - View the entire queue.
  - Filter queue entries by area (case-insensitive).
  - Move pending requests from the queue into the heap.
  - View or automatically clean the most urgent bin from the heap.
  - Manually select a bin to clean by ID.
- Input validation for duplicate IDs and fill-level bounds.

## Project Structure
```
WASTE-MANAGEMENT-SYSTEM/
├── Waste_main.c      // Entry point containing the CLI menus
├── functions.c       // Queue + heap implementations and helpers
└── functions.h       // Shared type and function declarations
```

## Building & Running
```bash
cd dsa/WASTE-MANAGEMENT-SYSTEM
gcc Waste_main.c functions.c -o waste
./waste
```

## Usage
1. Launch the program and choose whether to log in as **Admin** or **User**.
2. Users create new bin requests by supplying an ID, area, and fill percentage. Requests stay in the queue until the admin promotes them.
3. Admins can display or filter the queue, transfer requests into the heap, and then either auto-clean the most urgent bin (extract-min) or pick one manually by ID.

## Future Ideas
- Persist requests to disk to retain state between runs.
- Introduce authentication or multiple admin roles.
- Extend the heap to consider other metrics (distance, bin size, etc.).
- Add reporting dashboards to visualize service frequency by area.
