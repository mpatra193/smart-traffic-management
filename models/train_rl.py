import torch
import torch.nn as nn
import torch.optim as optim
import random
import os
import numpy as np
from collections import deque
from rl_agent import TrafficDQN

# Environment
class MockTrafficEnv:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.ns = random.randint(0, 50)
        self.ew = random.randint(0, 50)
        self.wait_time = self.ns + self.ew
        return [self.ns, self.ew, self.wait_time]
        
    def step(self, action):
        if action == 0: g_ns, g_ew = 60, 15
        elif action == 1: g_ns, g_ew = 40, 25
        elif action == 2: g_ns, g_ew = 25, 40
        else: g_ns, g_ew = 15, 60
            
        # Vehicles cleared (approx 1 per 2 seconds of green)
        ns_cleared = min(self.ns, g_ns // 2)
        ew_cleared = min(self.ew, g_ew // 2)
        
        self.ns -= ns_cleared
        self.ew -= ew_cleared
        
        # New vehicles arrive
        self.ns += random.randint(0, 15)
        self.ew += random.randint(0, 15)
        
        # Update wait time proxy
        self.wait_time = self.ns + self.ew
        
        # Reward: penalize large queues
        reward = -self.wait_time
        
        # Random episode termination (simulating end of peak hour)
        done = random.random() < 0.05
        
        return [self.ns, self.ew, self.wait_time], reward, done

def train():
    env = MockTrafficEnv()
    model = TrafficDQN(input_dim=3, output_dim=4)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    memory = deque(maxlen=2000)
    
    epochs = 500
    gamma = 0.95
    epsilon = 1.0
    epsilon_min = 0.01
    epsilon_decay = 0.99
    batch_size = 32
    
    print("Starting Offline Pre-training of TrafficDQN...")
    for e in range(epochs):
        state = torch.FloatTensor(env.reset())
        total_reward = 0
        
        for time in range(100):
            # Epsilon-greedy action selection
            if np.random.rand() <= epsilon:
                action = random.randrange(4)
            else:
                with torch.no_grad():
                    q_values = model(state)
                    action = torch.argmax(q_values).item()
                    
            next_state_list, reward, done = env.step(action)
            next_state = torch.FloatTensor(next_state_list)
            
            memory.append((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward
            
            if done:
                break
                
            # Replay and learn
            if len(memory) > batch_size:
                minibatch = random.sample(memory, batch_size)
                
                states = torch.stack([m[0] for m in minibatch])
                actions = torch.tensor([m[1] for m in minibatch])
                rewards = torch.tensor([m[2] for m in minibatch], dtype=torch.float32)
                next_states = torch.stack([m[3] for m in minibatch])
                dones = torch.tensor([m[4] for m in minibatch], dtype=torch.float32)
                
                current_q = model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
                with torch.no_grad():
                    max_next_q = model(next_states).max(1)[0]
                target_q = rewards + (gamma * max_next_q * (1 - dones))
                
                loss = criterion(current_q, target_q)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay
            
        if (e+1) % 100 == 0:
            print(f"Epoch: {e+1}/{epochs}, Epsilon: {epsilon:.2f}, Total Reward: {total_reward}")

    # Save weights
    save_path = os.path.join(os.path.dirname(__file__), 'dqn_weights.pt')
    torch.save(model.state_dict(), save_path)
    print(f"Training complete. Weights saved to {save_path}")

if __name__ == "__main__":
    train()
