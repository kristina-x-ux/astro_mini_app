from varga_engine import *

TEST_POINTS = {
    "Солнце": 31.15,
    "Луна": 250.32,
    "Марс": 63.11,
    "Меркурий": 41.45,
    "Юпитер": 353.53,
    "Венера": 4.54,
    "Сатурн": 235.53,
}

result = calculate_all_vargas(TEST_POINTS)

print("\n========== VARGA TEST ==========\n")

for planet, data in result.items():

    print(f"\n{planet}")

    for varga, value in data.items():

        if "part" in value:
            print(
                f"{varga}: {value['sign']} "
                f"(часть {value['part']})"
            )
        else:
            print(f"{varga}: {value['sign']}")
