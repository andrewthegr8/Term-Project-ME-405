#!/usr/bin/env python3
import os

import matplotlib
matplotlib.use("Agg")  # no GUI backend
import matplotlib.pyplot as plt


def render_equation_to_svg(tex, output_path, fontsize=20, padding=0.2):
    """
    Render a LaTeX-style math expression to an SVG file using matplotlib's mathtext.

    Parameters
    ----------
    tex : str
        The LaTeX math expression WITHOUT the surrounding $...$.
    output_path : str
        Path to the output SVG file.
    fontsize : int
        Font size for the rendered math.
    padding : float
        Extra figure size (in inches) around the text.
    """
    # Create directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Initial tiny figure
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)

    # Add the math text (centered)
    text = fig.text(
        0.5,
        0.5,
        f"${tex}$",
        ha="center",
        va="center",
        fontsize=fontsize,
    )

    # Draw once to get bounding box
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = text.get_window_extent(renderer=renderer)

    # Compute size in inches
    width_in = bbox.width / fig.dpi + padding
    height_in = bbox.height / fig.dpi + padding

    # Resize figure to tightly fit the text
    fig.set_size_inches(width_in, height_in)

    # Keep text centered
    text.set_position((0.5, 0.5))

    # Save as SVG
    fig.savefig(
        output_path,
        format="svg",
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.01,
    )
    plt.close(fig)


def main():
    # LaTeX-ish expression for your speed control law
    # (use \mathrm instead of \text to keep mathtext happy)
    tex = (
        r"\mathrm{speed}"
        r" = \mathrm{base\_speed}_i + "
        r"\frac{\max\left("
        r"\mathrm{FULLTHROTTLE}"
        r" + \mathrm{SLOWDOWN\_ON\_APPROACH}\,(E - \mathrm{brake\_dist}_i),"
        r" 0\right)}{1 + \mathrm{head\_weight}\,|\alpha|}"
    )

    # Output path for the SVG (relative to this script)
    output_path = os.path.join("images", "speed_law.svg")

    render_equation_to_svg(tex, output_path)

    # Print RST snippet to stdout so you can copy-paste it
    print("Generated:", output_path)
    print()
    print("Use this in your .rst file:")
    print()
    print(".. figure:: images/speed_law.svg")
    print("   :align: center")
    print("   :width: 60%")
    print()
    print("   Speed control law used for Romi's waypoint approach and alignment.")


if __name__ == "__main__":
    main()
