"""Master script to run the demo scenario: seeds baseline data and triggers an anomaly."""

import os
import subprocess


def main():
    print("=== TrialPulse Demo Scenario Runner ===")

    scripts_dir = os.path.dirname(os.path.abspath(__file__))

    print("\n1. Seeding past check-in sessions and symptoms...")
    subprocess.run(
        ["uv", "run", "python", os.path.join(scripts_dir, "seed_demo_data.py")], check=True
    )

    print(
        "\n2. Generating baseline wearable data for the past 14 days and triggering an anomaly today..."
    )
    subprocess.run(
        [
            "uv",
            "run",
            "python",
            os.path.join(scripts_dir, "generate_wearable_data.py"),
            "--anomaly",
        ],
        check=True,
    )

    print("\n=== Demo Data Successfully Injected ===")
    print("You can now open the Dashboard to see the populated Patient List and their Risk Scores.")


if __name__ == "__main__":
    main()
