import matplotlib.pyplot as plt
import numpy as np

# 1. Create Data
categories = ["AI Tools", "Cloud Storage", "Consulting", "Hardware", "Software"]
sales_2024 = [40, 55, 30, 80, 60]
sales_2025 = [60, 70, 45, 90, 75]

x = np.arange(len(categories))
width = 0.35

# 2. Build the Chart
fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width / 2, sales_2024, width, label="2024", color="#A9A9A9")
rects2 = ax.bar(x + width / 2, sales_2025, width, label="2025", color="#4F8BF9")

# 3. Add Labels & Style
ax.set_ylabel("Revenue ($k)")
ax.set_title("Global Tech Sales Performance (2024 vs 2025)")
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# 4. Save it
plt.tight_layout()
plt.savefig("test_chart.png", dpi=300)
print("✅ Success! 'test_chart.png' has been created.")
