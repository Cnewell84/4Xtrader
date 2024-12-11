import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from forex_env import ForexEnv  # Replace with the actual path to your custom environment

# Configuration
MODEL_SAVE_PATH = "ppo_forex_agent"
TOTAL_TIMESTEPS = 100000  # Adjust as needed

def main():
    # Initialize the custom Forex trading environment
    env = ForexEnv()
    
    # Optional: Check the environment for any issues
    check_env(env, warn=True)
    
    # Optionally, wrap the environment for better performance
    # from stable_baselines3.common.sb2_vec_env import DummyVecEnv
    # env = DummyVecEnv([lambda: env])
    
    # Initialize the PPO agent
    model = PPO(
        "MlpPolicy",  # You can choose other policies like "CnnPolicy" if applicable
        env,
        verbose=1,
        tensorboard_log="./ppo_forex_tensorboard/",
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
    )
    
    # Train the agent
    print("Starting training...")
    model.learn(total_timesteps=TOTAL_TIMESTEPS)
    print("Training completed.")
    
    # Save the trained model
    model.save(MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}.zip")
    
    # Optional: Save the environment (if needed)
    env.close()

if __name__ == "__main__":
    main() 