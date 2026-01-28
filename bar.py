import time
from tqdm import tqdm


for i in tqdm(range(50), desc="Processing"):
    time.sleep(0.1)
