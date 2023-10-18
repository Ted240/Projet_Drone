def hauteur_parcourue(n_marches: int, h_marches: float) -> None:
    print(f"Il va parcourir un total de {7 * 5 * 2 * n_marches * h_marches / 100}m")

hauteur_parcourue(*tuple(map(float, [input(f"{x} ? ") for x in ["Nombre de marches", "Hauteur d\'une marche (cm)"]])))
