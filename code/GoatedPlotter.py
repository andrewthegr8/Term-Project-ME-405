import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import os
import pandas as pd
from datetime import datetime


def clean_outliers(arr, threshold=5.0):
    """
    Replace outlier points (those deviating > threshold×median absolute deviation)
    with the average of their previous and next valid values.
    Returns a cleaned numpy array.
    """
    if len(arr) < 3:
        return arr

    arr = np.array(arr, dtype=float)
    median = np.median(arr)
    mad = np.median(np.abs(arr - median)) + 1e-9  # avoid division by zero
    deviation = np.abs(arr - median) / mad

    # Mark outliers (huge deviations)
    mask = deviation > threshold
    cleaned = arr.copy()
    for i in np.where(mask)[0]:
        if i == 0 or i == len(arr) - 1:
            cleaned[i] = median
        else:
            cleaned[i] = 0.5 * (cleaned[i - 1] + cleaned[i + 1])

    return cleaned


def GoatedPlotter(d, go_plot):
    state = 0
    while True:
        if state == 0:
            if go_plot.is_set():
                state = 1
            else:
                sleep(0.005)

        elif state == 1:
            print("Plotting...")
            try:
                np.array(d.get("time_L", []))[0]  # Check and make sure there's some data to plot
            except Exception:
                print('No data was saved :(')
                go_plot.clear()
                state = 0
                continue

            # Clean wild outliers
            for key, val in d.items():
                arr = np.array(val, dtype=float)
                d[key] = clean_outliers(arr)

            # --- 1. Export CSV ---
            os.makedirs('test_data', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join('test_data', f"romi_data_{timestamp}.csv")

            try:
                df = pd.DataFrame(d)
                df.to_csv(csv_path, index=False)
                print(f"[INFO] Data exported to {csv_path}")
            except Exception as e:
                print(f"[WARN] Could not save CSV: {e}")

            # --- Pre-process ---
            tL = np.array(d.get("time_L", []))
            if tL.size:
                # t_start = 0 and convert from ms to s
                tL = (tL - tL[0]) / 1000.0

            tR = np.array(d.get("time_R", []))
            if tR.size:
                tR = (tR - tR[0]) / 1000.0

            # Convert all numeric data safely
            velo_L  = np.array(d.get("velo_L", []))
            velo_R  = np.array(d.get("velo_R", []))
            p_v_L   = np.array(d.get("p_v_L", []))
            p_v_R   = np.array(d.get("p_v_R", []))

            # Displacement data still saved to CSV, but not plotted
            pos_L   = np.array(d.get("pos_L", []))
            pos_R   = np.array(d.get("pos_R", []))
            p_pos_L = np.array(d.get("p_pos_L", []))
            p_pos_R = np.array(d.get("p_pos_R", []))

            # Heading (read but unused right now; kept for future use)
            RAD2DEG = 57.2958
            Eul_head = np.array(d.get("Eul_head", [])) * RAD2DEG
            p_head   = np.array(d.get("p_head", []))   * RAD2DEG

            # Robot X/Y path (world coordinates)
            X_pos = np.array(d.get("X_pos", []))
            Y_pos = np.array(d.get("Y_pos", []))

            # Velocity setpoint data
            velo_set = np.array(d.get("velo_set", []))

            cmd_L = np.array(d.get("cmd_L", []))
            cmd_R = np.array(d.get("cmd_R", []))

            # --- Path setpoints (in inches) ---
            X_SP = np.array([
                33.46456692913386,
                51.181102362204726,
                55.118110236220474,
                49.21259842519685,
                27.559055118110237,
                13.779527559055119,
                2.952755905511811,
                0.0,
                15.748031496062993,
                15.748031496062993,
                -0.984251968503937,
            ])
            Y_SP = np.array([
                14.763779527559056,
                0.0,
                11.811023622047244,
                27.559055118110237,
                24.606299212598426,
                24.606299212598426,
                24.606299212598426,
                6.889763779527559,
                11.811023622047244,
                0.0,
                -0.984251968503937,
            ])

            # --- Mirror path and setpoints about the +Y axis for the path plot: X -> -X, Y unchanged ---
            X_plot = -X_pos
            Y_plot = Y_pos

            X_SP_plot = -X_SP
            Y_SP_plot = Y_SP

            # --- Determine checkpoint hit times (in order of X_SP) based on X_pos vs time ---
            checkpoint_times = []
            if tL.size and X_pos.size:
                n_pose = min(len(tL), len(X_pos))
                t_pose = tL[:n_pose]
                X_pose = X_pos[:n_pose]

                start_idx = 0
                for xsp in X_SP:
                    if start_idx >= len(X_pose):
                        break
                    segment = X_pose[start_idx:]
                    if segment.size == 0:
                        break
                    # Find index of closest X to this setpoint, after previous checkpoint
                    rel_idx = int(np.argmin(np.abs(segment - xsp)))
                    idx = start_idx + rel_idx
                    checkpoint_times.append(t_pose[idx])
                    start_idx = idx + 1  # ensure next checkpoint occurs later in time

            # --- Layout: 2×2 grid (4 plots) ---
            fig, axes = plt.subplots(2, 2, figsize=(16, 9))
            axes = axes.ravel()

            # Make full screen if possible
            try:
                mgr = plt.get_current_fig_manager()
                try:
                    mgr.full_screen_toggle()
                except Exception:
                    try:
                        mgr.window.showMaximized()
                    except Exception:
                        pass
            except Exception:
                pass

            # --- [0] Left Wheel Velocity + Command ---
            ax = axes[0]
            ax2 = ax.twinx()  # second y-axis
            if tL.size and velo_L.size:
                ax.plot(tL[:len(velo_L)], velo_L, label="Left Velocity (True)", color="tab:blue")
            if tL.size and p_v_L.size:
                ax.plot(tL[:len(p_v_L)], p_v_L, label="Left Velocity (Pred)", color="tab:orange")
            if tL.size and cmd_L.size:
                ax2.plot(tL[:len(cmd_L)], cmd_L, label="Left Cmd (%)", color="tab:red")
            ax.set_title("Left Wheel Velocity + Command")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Velocity (in/s)")
            ax2.set_ylabel("Cmd (%)")
            # Combine legends from both axes
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            if lines or lines2:
                ax.legend(lines + lines2, labels + labels2, loc="best")
            ax.grid(True)

            # --- [1] Right Wheel Velocity + Command (restored) ---
            ax = axes[1]
            ax2 = ax.twinx()
            if tR.size and velo_R.size:
                ax.plot(tR[:len(velo_R)], velo_R, label="Right Velocity (True)", color="tab:blue")
            if tR.size and p_v_R.size:
                ax.plot(tR[:len(p_v_R)], p_v_R, label="Right Velocity (Pred)", color="tab:orange")
            if tR.size and cmd_R.size:
                ax2.plot(tR[:len(cmd_R)], cmd_R, label="Right Cmd (%)", color="tab:red")
            ax.set_title("Right Wheel Velocity + Command")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Velocity (in/s)")
            ax2.set_ylabel("Cmd (%)")
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            if lines or lines2:
                ax.legend(lines + lines2, labels + labels2, loc="best")
            ax.grid(True)

            # --- [2] Velocity Setpoint vs Time with checkpoint lines + labels + final time textbox ---
            ax = axes[2]
            if tL.size and velo_set.size:
                n_vs = min(len(tL), len(velo_set))
                ax.plot(tL[:n_vs], velo_set[:n_vs], label="Velocity Setpoint")

            ax.set_title("Velocity Setpoint vs Time")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Velocity (in/s)")

            # Vertical lines and time labels at checkpoint times
            if checkpoint_times:
                # Get y-limits after plotting velo_set
                ymin, ymax = ax.get_ylim()
                y_text = ymin + 0.02 * (ymax - ymin)
                for t_cp in checkpoint_times:
                    ax.axvline(x=t_cp, color="red", linestyle="--", linewidth=0.8)
                    ax.text(
                        t_cp,
                        y_text,
                        f"{t_cp:.2f}s",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        rotation=90,
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="red", alpha=0.7),
                    )

            if ax.get_legend_handles_labels()[0]:
                ax.legend()
            ax.grid(True)

            # Add textbox with max time in seconds (last tL value)
            if tL.size:
                t_end = tL[-1]
                textstr = f"t_end = {t_end:.2f} s"
                ax.text(
                    0.98, 0.02, textstr,
                    transform=ax.transAxes,
                    ha="right", va="bottom",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.7)
                )

            # --- [3] XY Path with Setpoints (mirrored) ---
            ax = axes[3]
            if X_plot.size and Y_plot.size:
                ax.plot(X_plot, Y_plot, label="Path")
            # Setpoints as red dots (mirrored)
            ax.scatter(X_SP_plot, Y_SP_plot, color="red", s=30, label="Setpoints")

            ax.set_title("Robot Path (Mirrored about +Y Axis)")
            ax.set_xlabel("X (in)")
            ax.set_ylabel("Y (in)")

            # Equal scaling for X/Y (so path isn't distorted)
            ax.set_aspect("equal", adjustable="box")

            if ax.get_legend_handles_labels()[0]:
                ax.legend()
            ax.grid(True)

            fig.tight_layout()

            # --- Save PNG of the full figure in ./plots with name as date+time ---
            os.makedirs("plots", exist_ok=True)
            png_path = os.path.join("plots", f"{timestamp}.png")
            try:
                fig.savefig(png_path, dpi=300, bbox_inches="tight")
                print(f"[INFO] Plot image saved to {png_path}")
            except Exception as e:
                print(f"[WARN] Could not save plot PNG: {e}")

            # Show the figure
            plt.show()

            # Clear out the recorded_data dictionary
            for k in d.keys():
                d[k] = []
            go_plot.clear()
            state = 0
