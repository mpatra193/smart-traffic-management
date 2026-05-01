## 🚦 Smart Traffic Route Optimizer  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)

> A real-time traffic route optimizer developed to reduce urban congestion using computer vision, adaptive signal control, and reinforcement learning.

## 🔍 Overview

Urban traffic congestion leads to increased travel time, pollution, and fuel consumption. This **Traffic Route Optimizer** leverages real-time computer vision (YOLO) and a hybrid AI decision engine to dynamically adjust traffic signal timings and optimize vehicle flow across intersections.

This solution aims to make city transportation smarter, safer, and more efficient using modern technologies such as **machine learning**, **Deep Q-Networks (RL)**, and **real-time interactive dashboards**.

---

## ✨ Features

✅ **Computer Vision Vehicle Detection**  
   - Uses YOLO models to accurately detect, classify, and count vehicles from live camera feeds, differentiating directional traffic flows.

✅ **Hybrid AI Signal Optimization**  
   - **Rule-Based Engine**: For low traffic, a highly efficient mathematical heuristic manages intersections.
   - **Reinforcement Learning**: For high traffic, a Deep Q-Network (DQN) agent dynamically calculates optimal green light durations to minimize wait times.

✅ **Emergency Vehicle "Green Wave" Preemption**  
   - Detects emergency vehicles (ambulances, fire engines) and instantly triggers a massive priority green light to clear the path.

✅ **City-Wide Dynamic Routing (Dijkstra + OSRM)**  
   - Simulates a city camera grid and calculates real-time congestion scores.
   - Uses Dijkstra's algorithm to actively route users around heavy traffic hotspots, drawing actual road geometries using OSRM.

✅ **Interactive Real-Time Dashboard**  
   - Powered by Streamlit, featuring live annotated feeds, decisive analytics for recommended signal times, traffic trend charts, and multi-language support (English, Hindi, Tamil).

---

## 🛠️ Tech Stack

| Component         | Technology Used                          |
|------------------|------------------------------------------|
| Frontend UI      | Streamlit, PyDeck, Pandas                |
| Computer Vision  | Ultralytics YOLO, OpenCV                 |
| Machine Learning | PyTorch (Deep Q-Network RL Agent)        |
| Routing Engine   | NetworkX (Dijkstra), OSRM API, Polyline  |
| Scripting        | Python 3                                 |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/puneetdhd/routing-ml.git
   cd routing-ml
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train the RL Agent (Optional but recommended)**
   ```bash
   python models/train_rl.py
   ```

5. **Run the Dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

---

## 🖼️ Project Structure
```
routing-ml/
│
├── dashboard/                # Streamlit Web UI
│   └── app.py                # Main Dashboard application
├── detector/                 # Computer Vision Logic
│   └── detector.py           # YOLO inference and frame processing
├── models/                   # ML models & training scripts
│   ├── traffic_ai.py         # Hybrid decision engine
│   ├── rl_agent.py           # DQN Architecture
│   └── train_rl.py           # Training script for the RL agent
├── utils/                    # Helper functions
│   └── stream_handler.py     # Video stream fallback and threading
├── data/                     # Offline video simulators and logs
│   ├── intersection.mp4
│   └── traffic_log.jsonl     # Persisted historical metrics
├── requirements.txt          # Dependencies
└── README.md
```

---

## 🎯 How It Works

1. **Input**: Live video feed from local MP4 simulations or direct CCTV.
2. **Detection**: OpenCV and YOLOv8 process the frames to identify vehicles per directional lane.
3. **Decision**: The Hybrid AI engine evaluates counts—relying on heuristics for light traffic or the PyTorch DQN agent for heavy queues.
4. **Output**: The Streamlit dashboard updates the suggested signal timing and plots visual traffic trends.
5. **Routing**: The system calculates the least congested city-wide route using Dijkstra and renders the actual road map via PyDeck and OSRM.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contribution Guidelines](CONTRIBUTING.md) before submitting a pull request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---


