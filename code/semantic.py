import random
import matplotlib.pyplot as plt

import habitat
from habitat.config import read_write

env = habitat.Env(
    config=habitat.get_config("benchmark/nav/pointnav/pointnav_habitat_test.yaml")
)
def print_scene_recur(scene, limit_output=10):
    
    count = 0
    for level in scene.levels:
        print(
            f"Level id:{level.id}, center:{level.aabb.center},"
            f" dims:{level.aabb.sizes}"
        )
        for region in level.regions:
            print(
                f"Region id:{region.id}, category:{region.category.name()},"
                f" center:{region.aabb.center}, dims:{region.aabb.sizes}"
            )
            for obj in region.objects:
                print(
                    f"Object id:{obj.id}, category:{obj.category.name()},"
                    f" center:{obj.aabb.center}, dims:{obj.aabb.sizes}"
                )
                count += 1
                if count >= limit_output:
                    return None

# Print semantic annotation information (id, category, bounding box details)
# for the current scene in a hierarchical fashion
scene = env.sim.semantic_annotations()
print_scene_recur(scene, limit_output=15)

env.close()
import numpy as np
from PIL import Image
from habitat_sim.utils.common import d3_40_colors_rgb
from habitat.config.default import get_agent_config
from habitat.config.default_structured_configs import HabitatSimSemanticSensorConfig

def display_sample(rgb_obs, semantic_obs, depth_obs):
    rgb_img = Image.fromarray(rgb_obs, mode="RGB")

    semantic_img = Image.new("P", (semantic_obs.shape[1], semantic_obs.shape[0]))
    semantic_img.putpalette(d3_40_colors_rgb.flatten())
    semantic_img.putdata((semantic_obs.flatten() % 40).astype(np.uint8))
    semantic_img = semantic_img.convert("RGBA")

    depth_img = Image.fromarray((depth_obs * 255).astype(np.uint8), mode="L")

    arr = [rgb_img, semantic_img, depth_img]

    titles = ['rgb', 'semantic', 'depth']
    plt.figure(figsize=(12 ,8))
    for i, data in enumerate(arr):
        ax = plt.subplot(1, 3, i+1)
        ax.axis('off')
        ax.set_title(titles[i])
        plt.imshow(data)
    plt.show()

config=habitat.get_config("benchmark/nav/pointnav/pointnav_habitat_test.yaml")
with read_write(config):
    config.habitat.dataset.split = "val"
    agent_config = get_agent_config(sim_config=config.habitat.simulator)
    agent_config.sim_sensors.update(
        {"semantic_sensor": HabitatSimSemanticSensorConfig(height=256, width=256)}
    )
    config.habitat.simulator.turn_angle = 30

env = habitat.Env(config=config)
env.episodes = random.sample(env.episodes, 2)

max_steps = 4

action_mapping = {
    0: 'stop',
    1: 'move_forward',
    2: 'turn left',
    3: 'turn right'
}

for i in range(len(env.episodes)):
    observations = env.reset()

    display_sample(observations['rgb'], observations['semantic'], np.squeeze(observations['depth']))

    count_steps = 0
    while count_steps < max_steps:
        action = random.choice(list(action_mapping.keys()))
        print(action_mapping[action])
        observations = env.step(action)
        display_sample(observations['rgb'], observations['semantic'], np.squeeze(observations['depth']))

        count_steps += 1
        if env.episode_over:
            break

env.close()
