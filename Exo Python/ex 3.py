p = []
while (p[-1] != 0) if len(p) else True: p.append(float(input("Price: ")))
print(f"Total: {sum(p)}€\nVAT: {round(sum(p) * 0.2, 2)}€\nTotal VAT included: {round(sum(p) * 1.2, 2)}€")