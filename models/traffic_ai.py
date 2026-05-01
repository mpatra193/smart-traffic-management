import os
import torch
from .rl_agent import TrafficDQN, ACTION_SPACE

# Global cache for the RL model
_dqn_model = None

def _load_dqn_model():
    """Loads the pre-trained DQN weights into the model for inference only."""
    global _dqn_model
    if _dqn_model is not None:
        return _dqn_model

    weights_path = os.path.join(os.path.dirname(__file__), 'dqn_weights.pt')
    
    # Initialize the model structure
    model = TrafficDQN(input_dim=3, output_dim=4)
    
    if os.path.exists(weights_path):
        try:
            model.load_state_dict(torch.load(weights_path))
            model.eval() # Set to evaluation mode
            _dqn_model = model
            print("Successfully loaded DQN weights.")
            return model
        except Exception as e:
            print(f"Error loading DQN weights: {e}")
            return None
    else:
        print("DQN weights not found. Falling back to rule-based engine.")
        return None

def _rule_based_engine(ns_count, ew_count):
    """Fast, deterministic mathematical heuristic for low traffic scenarios."""
    total = ns_count + ew_count
    if total == 0:
        return {
            "green_ns": 25,
            "green_ew": 35,
            "mode": "🌿 LIGHT TRAFFIC (Rule-Based)",
            "wait_saved": 5
        }

    ratio = ns_count / (ew_count + 1)

    if ratio > 2.0:
        return {"green_ns": 50, "green_ew": 15, "mode": "🚦 NS HEAVY FLOW (Rule-Based)", "wait_saved": 15}
    elif ratio > 1.2:
        return {"green_ns": 40, "green_ew": 25, "mode": "🚗 NS MODERATE (Rule-Based)", "wait_saved": 10}
    elif ratio < 0.5:
        return {"green_ns": 15, "green_ew": 50, "mode": "🚦 EW HEAVY FLOW (Rule-Based)", "wait_saved": 15}
    else:
        return {"green_ns": 30, "green_ew": 30, "mode": "🌿 BALANCED FLOW (Rule-Based)", "wait_saved": 8}


def get_signal_timing(ns_count, ew_count, is_emergency=False):
    """
    Hybrid Signal Decision Engine
    - Emergency: Immediate override.
    - Low Traffic: Fast rule-based heuristic.
    - High Traffic: RL Deep Q-Network inference.
    """
    # 1. Emergency Override
    if is_emergency:
        return {
            "green_ns": 60,
            "green_ew": 10,
            "mode": "🚑 EMERGENCY OVERRIDE",
            "wait_saved": 45
        }

    total_traffic = ns_count + ew_count
    
    # 2. Hybrid Threshold check
    # If traffic is below 15 vehicles total, use simple rule-based logic to save compute
    if total_traffic < 15:
        return _rule_based_engine(ns_count, ew_count)

    # 3. RL Inference Mode for High Traffic
    model = _load_dqn_model()
    if model is not None:
        # Prepare state: [ns_vehicles, ew_vehicles, approximated_wait_time]
        approximated_wait_time = total_traffic # Proxy for queue wait time
        state = torch.FloatTensor([ns_count, ew_count, approximated_wait_time])
        
        with torch.no_grad():
            q_values = model(state)
            action_idx = torch.argmax(q_values).item()
            
        action = ACTION_SPACE[action_idx]
        
        # Add a simulated stat
        return {
            "green_ns": action["green_ns"],
            "green_ew": action["green_ew"],
            "mode": action["mode"],
            "wait_saved": int(total_traffic * 0.4) # Assume RL saves 40% of queue wait
        }
        
    # 4. Fallback if model fails to load
    return _rule_based_engine(ns_count, ew_count)