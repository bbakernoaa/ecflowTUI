# ecFlow Examples

This directory contains example ecFlow suite definitions and utilities to help you get started with `ectop`.

## Contents

- `tutorial_suite.py`: A simple suite definition used for the basic tutorial.
- `ectop_demo.py`: A comprehensive demonstration suite designed to exercise all features of `ectop`, including limits, triggers, and automated script generation.

## Running the Demo Suite

The `ectop_demo.py` script is the best way to test `ectop`'s capabilities. It creates a suite with various states (active, queued, complete, aborted, suspended) and generates the necessary script files.

### Prerequisites

- An ecFlow server must be running.
- The `ecflow` Python API must be installed.

### Usage

1. **Start a local ecFlow server** (if not already running):
   ```bash
   ecflow_server --port 3141
   ```

2. **Generate scripts and load the suite**:
   ```bash
   python ectop_demo.py --load --port 3141 --home ./ectop_demo_home
   ```

3. **Start ectop**:
   ```bash
   ectop --port 3141
   ```

### Command Line Options for `ectop_demo.py`

- `--host`: ecFlow server host (default: localhost)
- `--port`: ecFlow server port (default: 3141)
- `--home`: Directory where scripts and logs will be stored (default: ./ectop_demo_home)
- `--load`: Load the suite into the server and begin playback.

## Tutorial Suite

The `tutorial_suite.py` script creates a `tutorial.def` file.

```bash
python tutorial_suite.py
```

This will create `tutorial.def` in the current directory, which can then be loaded into an ecFlow server using `ecflow_client`.
