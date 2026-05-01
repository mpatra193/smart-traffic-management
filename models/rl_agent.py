import torch
import torch.nn as nn
import torch.nn.functional as F

class TrafficDQN(nn.Module):
    """
    A simple Deep Q-Network for Traffic Signal Control.
    State: [ns_vehicles, ew_vehicles, approximated_wait_time]
    Action: 4 discrete signal phases.
    """
    def __init__(self, input_dim=3, output_dim=4):
        super(TrafficDQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# Discrete Action Space Mapping
ACTION_SPACE = {
    0: {"green_ns": 60, "green_ew": 15, "mode": "🚦 NS HEAVY FLOW (RL Opt)"},
    1: {"green_ns": 40, "green_ew": 25, "mode": "🚗 NS MODERATE (RL Opt)"},
    2: {"green_ns": 25, "green_ew": 40, "mode": "🚗 EW MODERATE (RL Opt)"},
    3: {"green_ns": 15, "green_ew": 60, "mode": "🚦 EW HEAVY FLOW (RL Opt)"}
}
