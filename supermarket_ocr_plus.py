#!/usr/bin/env python3
# supermarket_text_parser_fixed_mobile.py
#
# Final solution for Pydroid3:
# - END ends input (not blank line)
# - Accepts your exact real format:
#   name
#   price
#   next name
#   ...
# - Ignores subtotal lines (like "12,60")
# - Ignores initial quantity in product line (e.g., '1 ' in '1 BASE PIZZA')

import os
import csv
import re
from datetime import datetime

# Rutas de archivos
BASE_CSV = "/storage/emulated/0/Documents/Pythor/CSVs"
SUP_DB = os.path.join(BASE_CSV, "supermarkets_db.csv")
PROD_DB = os.path.join(BASE_CSV, "supermarket_products_db.csv")
TICKETS_DB = os.path.join(BASE_CSV, "supermarket_ticket_history.csv")

os.makedirs(BASE_CSV, exist_ok=True)

# Mapeo de Repartos FINAL Y REORDENADO
# Nuevo Mapeo según tus reglas (Am, Ams, As, A, M, S, Ms):
# La numeración no es secuencial pero el orden de presentación sí sigue el solicitado.
SPLIT_MAP = {
    # Am
    "1": ("A♡M", ["A","M"]),
    # Ams
    "2": ("A&M&S", ["A","M","S"]),
    "3": ("M&S", ["M","S"]),
    "4": ("S", ["S"]),
    "5": ("A", ["A"]),
    "6": ("M", ["M"]),
    "7": ("A&S", ["A","S"])
}

# ------------------ FUNCIONES DE ARCHIVO ------------------
def ensure_csv(path, header):
    if not os.path.exists(path):
        with open(path,"w",encoding="utf-8",newline="") as f:
            csv.writer(f).writerow(header)

def read_rows(path):
    if not os.path.exists(path): return []
    with open(path,"r",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def append_row(path, row):
    rows = read_rows(path)
    if not rows:
        with open(path,"w",encoding="utf-8",newline="") as f:
            w = csv.DictWriter(f, fieldnames=row.keys())
            w.writeheader()
            w.writerow(row)
        return
    
    valid_keys = [k for k in rows[0].keys() if k is not None and k in row]

    with open(path,"a",encoding="utf-8",newline="") as f:
        csv.writer(f).writerow([row[k] for k in valid_keys])


ensure_csv(SUP_DB, ["id","name"])
ensure_csv(PROD_DB, ["product_name","default_split_idx","last_price"])
ensure_csv(TICKETS_DB, ["timestamp","supermarket","buyer","product","price","split_idx"])


# Expresión para detectar el precio con coma o punto
price_re = re.compile(r"^\s*\d+[.,]\d+\s*$")
# Expresión para limpiar la cantidad inicial (ej: '1 ' o '4 ')
quantity_re = re.compile(r"^\s*\d+\s+") 

def is_price(line):
    return price_re.search(line) is not None

def norm_price(p):
    return float(p.replace(",",".").strip())


# ------------------ PARSER MODIFICADO (IGNORAR CANTIDAD) ------------------
def parse_ticket(lines):
    items=[]
    product_name=None

    for line in lines:
        line=line.strip()

        if line == "":
            continue

        if is_price(line):
            # Es un precio
            if product_name:
                price = norm_price(line)
                items.append({"product": product_name, "price": price})
                product_name = None
        else:
            # No es un precio, es un nombre de producto.
            # 💡 Aplicar la limpieza para ignorar la cantidad inicial (ej. "4 SET ANTIHUMEDAD" -> "SET ANTIHUMEDAD")
            product_name = quantity_re.sub('', line).strip()
            # Asegurarse de que no queda vacío después de la limpieza
            if not product_name: 
                continue 

    return items


# ------------------ SPLITS ------------------
def ask_split(name):
    print(f"\nNo se encontró regla de reparto para '{name}':")
    # Mostrar el SPLIT_MAP en el orden definido
    for k in SPLIT_MAP:
        v = SPLIT_MAP[k]
        print(f"{k}: {v[0]}")
    c=""
    # El bucle de elección se asegura que la opción exista en el diccionario
    while c not in SPLIT_MAP:
        c=input("Elige una opción: ").strip()
    return c

def get_product(name):
    for r in read_rows(PROD_DB):
        if r["product_name"].lower()==name.lower():
            return r
    return None

def save_product(name, split_idx, price):
    rows=read_rows(PROD_DB)
    found=False
    for r in rows:
        if r["product_name"].lower()==name.lower():
            r["default_split_idx"]=split_idx
            r["last_price"]=f"{price:.2f}"
            found=True
            break
    if not found:
        rows.append({
            "product_name": name,
            "default_split_idx": split_idx,
            "last_price": f"{price:.2f}"
        })
    with open(PROD_DB,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f, fieldnames=["product_name","default_split_idx","last_price"])
        w.writeheader()
        w.writerows(rows)


# ------------------ MAIN ------------------
def choose_supermarket():
    sups=read_rows(SUP_DB)
    print("\nSupermarkets:")
    for r in sups:
        print(f"{r['id']}: {r['name']}")
    x=input("Selecciona ID o ENTER para nuevo: ").strip()
    if x=="":
        name=""
        while name=="":
            name=input("Nuevo nombre: ").strip()
        new_id=str(max([int(r["id"]) for r in sups], default=0)+1)
        append_row(SUP_DB, {"id":new_id,"name":name})
        return name
    for r in sups:
        if r["id"]==x:
            return r["name"]
    name=""
    while name=="":
        name=input("ID inválida. Nuevo nombre: ").strip()
    new_id=str(max([int(r["id"]) for r in sups], default=0)+1)
    append_row(SUP_DB, {"id":new_id,"name":name})
    return name


def main():
    print("\nPega tu ticket de Mercadona.")
    print("Usa el formato EXACTO que pegas normalmente.")
    print("Cuando termines, escribe: END\n")

    lines=[]
    while True:
        t=input()
        if t.strip().upper()=="END":
            break
        lines.append(t)

    items=parse_ticket(lines)

    if not items:
        print("\n❌ No se detectaron productos.\n")
        return

    supermarket=choose_supermarket()

    buyer=""
    while buyer not in ("A","M","S"):
        buyer=input("¿Quién pagó? (A/M/S): ").strip().upper()

    final=[]
    for it in items:
        name=it["product"]
        price=it["price"]

        info=get_product(name)
        if info and info["default_split_idx"]:
            idx=info["default_split_idx"]
        else:
            # Pregunta por el reparto si es un producto nuevo
            idx=ask_split(name)
            save_product(name, idx, price)

        final.append({
            "product":name,
            "price":price,
            "split_idx":idx
        })

    total=sum(i["price"] for i in final)

    print("\n--- Resumen del Ticket ---")
    for it in final:
        split_desc, _ = SPLIT_MAP[it['split_idx']]
        print(f"- {it['product']} ({split_desc}): {it['price']:.2f}€")
    print(f"\nTOTAL: {total:.2f}€")

    # Calculo y muestro el reparto final por persona
    split_totals = {"A": 0.0, "M": 0.0, "S": 0.0}
    for item in final:
        price = item['price']
        _, people = SPLIT_MAP[item['split_idx']]
        # Cálculo de reparto igualitario
        share = price / len(people) 
        for person in people:
            split_totals[person] += share

    print("\n--- Reparto Final ---")
    print(f"Total pagado por {buyer}: {total:.2f}€")
    for person in sorted(split_totals.keys()):
        print(f"{person} debe pagar: {split_totals[person]:.2f}€")

    # Calculo y muestro quién debe a quién
    debt = {}
    for person in ("A", "M", "S"):
        if person == buyer:
            debt[person] = total - split_totals[person]
        else:
            debt[person] = -split_totals[person]

    print("\n--- Balance (Quién debe a quién) ---")
    for person, amount in debt.items():
        if amount > 0:
            print(f"✅ {person} debe recibir: {amount:.2f}€")
        elif amount < 0:
            # Deuda
            print(f"❌ {person} debe a {buyer}: {abs(amount):.2f}€")
        else:
            print(f"⚖️ {person} no debe ni recibe nada.")


    ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for it in final:
        append_row(TICKETS_DB,{
            "timestamp":ts,
            "supermarket":supermarket,
            "buyer":buyer,
            "product":it["product"],
            "price":f"{it['price']:.2f}",
            "split_idx":it["split_idx"]
        })

    print("\n✓ Guardado.\n")


if __name__ == "__main__":
    main()
