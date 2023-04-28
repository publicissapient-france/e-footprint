import numpy as np

from footprint_model.constants.physical_elements import PhysicalElements
from footprint_model.constants.units import u


def plot_emissions(ax, input_dicts, legend_labels, title, rounding_value):
    elements = [element.value for element in PhysicalElements]

    index = np.arange(len(elements))
    bar_width = 0.4

    total_emissions_in_kg = 0
    for input_dict in input_dicts:
        total_emissions_in_kg += sum(input_dict.values()).to(u.kg).magnitude

    for i, input_dict in enumerate(input_dicts):
        values = [input_dict.get(element, 0 * u.kg).to(u.kg).magnitude for element in elements]

        proportions = [(value / total_emissions_in_kg) * 100 for value in values]

        # Plot the values with proportions as secondary scale
        rects = ax.bar(index + i * bar_width, values, bar_width, label=legend_labels[i])

        # Add labels to bars
        for rect, proportion in zip(rects, proportions):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, f"{proportion:.0f}%", ha="center", va="bottom")

    ax.set_xlabel("Physical Elements")
    ax.set_ylabel("kg CO2 emissions / year")
    ax.set_title(title, fontsize=24, fontweight="bold", y=1.12)
    if total_emissions_in_kg < 501:
        unit = "kg"
        dividing_number = 1
    else:
        unit = "ton"
        dividing_number = 1000
    rounded_sum = round(total_emissions_in_kg / dividing_number, rounding_value)
    if rounding_value == 0:
        rounded_sum = int(rounded_sum)
    ax.text(0.5, 1.1, f"CO2 emissions (total {rounded_sum} {unit})",
            transform=ax.transAxes, fontsize=12, va="top", ha="center")
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(elements, rotation=45, ha="right")

    ax2 = ax.twinx()
    max_value = max([max(input_dict.values()) for input_dict in input_dicts]).to(u.kg).magnitude
    ax2.set_ylim(0, 100 * (max_value / total_emissions_in_kg) * (ax.get_ylim()[1] / max_value))
    ax2.set_ylabel("Proportions (%)")

    ax.legend()


if __name__ == "__main__":
    fabrication_dict = {
                PhysicalElements.SMARTPHONE: 6337.6 * u.kg,
                PhysicalElements.LAPTOP: 8474.3 * u.kg,
                PhysicalElements.BOX: 1853.8 * u.kg,
                PhysicalElements.SCREEN: 2411.9 * u.kg,
                PhysicalElements.SERVER: 4.3 * u.kg,
                PhysicalElements.SSD: 320.0 * u.kg}
    energy_emissions_dict = {
                PhysicalElements.SMARTPHONE: 50.0 * u.kg,
                PhysicalElements.LAPTOP: 2500.0 * u.kg,
                PhysicalElements.BOX: 750.0 * u.kg,
                PhysicalElements.SCREEN: 300.0 * u.kg,
                PhysicalElements.MOBILE_NETWORK: 111.6 * u.kg,
                PhysicalElements.WIFI_NETWORK: 139.5 * u.kg,
                PhysicalElements.SERVER: 8.1 * u.kg,
                PhysicalElements.SSD: 3.3 * u.kg,
            }

    plot_emissions([fabrication_dict, energy_emissions_dict], ["Fabrication", "Electricity consumption"])
