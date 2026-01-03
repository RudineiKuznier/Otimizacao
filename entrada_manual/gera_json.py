import json

COL_START = ["Z", "AV", "BR", "CN", "DJ", "EF", "FB", "FX", "GT"]
FIM_ESTREITO = ["AB", "AX", "BT", "CP", "DL", "EH", "FD", "FZ", "GV"]
FIM_LARGO = ["AN", "BJ", "CF", "DB", "DX", "ET", "FP", "GL", "HH"]

COLUMN_MAP = list(zip(COL_START, FIM_ESTREITO, FIM_LARGO))

BASE_SUPPLIERS = [
    ("P(Reorder)", 3, 5), ("P(Estado da arte)", 8, 10), ("Reorder", 13, 15),
    ("Var(Var(d))", 18, 20), ("Var(Var(Cap))", 23, 25), ("CV", 28, 30),
    ("Planned Stock", 33, 35), ("Variance coeff - z(S2nd)", 38, 40),
    ("demand", 43, 45), ("Média(E(RLT))", 48, 50), ("Cap", 53, 55),
    ("Var(d-cap)", 58, 60), ("Desvpad(Var(S2nd))", 63, 65),
    ("DesvPad(Var(E(RLT)))", 68, 70), ("Média(d-Cap)", 73, 75),
    ("DesvPad(Var(d-cap))", 78, 80), ("LB", 83, 85), ("DesvPad(ND*ELT)", 88, 90),
    ("DesvPad(Cap)", 93, 95), ("z(RLT)", 98, 100), ("Aleatória S2nd", 103, 105),
    ("Radicand", 108, 110), ("SQRT", 113, 115), ("ND*ELT", 118, 120),
    ("Aleatória RLT", 123, 125), ("ActualRotw", 128, 130),
    ("vMaxNumOfCyclesw", 133, 135), ("DesvPad(demand)", 138, 140),
    ("DesvPad(E(RLT))", 143, 145), ("DesvPad(D*E(RLT))", 148, 150),
    ("Média(D*E(RLT))", 153, 155), ("Reorder(Estado da arte)", 158, 160),
    ("Erro > 0,01%", 163, 165), ("DesvPad(D*ELT)", 6802, 6804)
]

BASE_FACTORIES = [
    ("P(Reorder)", 168, 170), ("P(Estado da arte)", 173, 175), ("Reorder", 178, 180),
    ("Var(Var(d))", 183, 185), ("Var(Var(Cap))", 188, 190), ("CV", 193, 195),
    ("Planned Stock", 198, 200), ("Variance coeff - z(S2nd)", 203, 205),
    ("demand", 208, 210), ("Média(E(RLT))", 213, 215), ("Cap", 218, 220),
    ("Var(d-cap)", 223, 225), ("Desvpad(Var(S2nd))", 228, 230),
    ("DesvPad(Var(E(RLT)))", 233, 235), ("Média(d-Cap)", 238, 240),
    ("DesvPad(Var(d-cap))", 243, 245), ("LB", 248, 250), ("DesvPad(ND*ELT)", 253, 255),
    ("DesvPad(Cap)", 258, 260), ("z(RLT)", 263, 265), ("Aleatória S2nd", 268, 270),
    ("Radicand", 273, 275), ("SQRT", 278, 280), ("ND*ELT", 283, 285),
    ("Aleatória RLT", 288, 290), ("ActualRotw", 293, 295),
    ("vMaxNumOfCyclesw", 298, 300), ("DesvPad(demand)", 303, 305),
    ("DesvPad(E(RLT))", 308, 310), ("DesvPad(D*E(RLT))", 313, 315),
    ("Média(D*E(RLT))", 318, 320), ("Reorder(Estado da arte)", 323, 325),
    ("Erro > 0,01%", 328, 330), ("DesvPad(D*ELT)", 6807, 6809)
]

BASE_DISTRIBUTORS = [
    ("P(Reorder)", 333, 334), ("P(Estado da arte)", 337, 338), ("Reorder", 341, 342),
    ("Var(Var(d))", 345, 346), ("Var(Var(Cap))", 349, 350), ("CV", 353, 354),
    ("Planned Stock", 357, 358), ("Variance coeff - z(S2nd)", 361, 362),
    ("demand", 365, 366), ("Média(E(RLT))", 369, 370), ("Cap", 373, 374),
    ("Var(d-cap)", 377, 378), ("Desvpad(Var(S2nd))", 381, 382),
    ("DesvPad(Var(E(RLT)))", 385, 386), ("Média(d-Cap)", 389, 390),
    ("DesvPad(Var(d-cap))", 393, 394), ("LB", 397, 398), ("DesvPad(ND*ELT)", 401, 402),
    ("DesvPad(Cap)", 405, 406), ("z(RLT)", 409, 410), ("Aleatória S2nd", 413, 414),
    ("Radicand", 417, 418), ("SQRT", 421, 422), ("ND*ELT", 425, 426),
    ("Aleatória RLT", 429, 430), ("ActualRotw", 433, 434),
    ("vMaxNumOfCyclesw", 438, 439), ("DesvPad(demand)", 442, 443),
    ("DesvPad(E(RLT))", 446, 447), ("DesvPad(D*E(RLT))", 450, 451),
    ("Média(D*E(RLT))", 454, 455), ("Reorder(Estado da arte)", 458, 459),
    ("Erro > 0,01%", 462, 463), ("DesvPad(D*ELT)", 6812, 6813)
]

BASE_RETAILERS = [
    ("P(Reorder)", 466, 655), ("P(Estado da arte)", 658, 847), ("Reorder", 850, 1039),
    ("Var(Var(d))", 1042, 1231), ("Var(Var(Cap))", 1234, 1423), ("CV", 1426, 1615),
    ("Planned Stock", 1618, 1807), ("Variance coeff - z(S2nd)", 1810, 1999),
    ("demand", 2002, 2191), ("Média(E(RLT))", 2194, 2383), ("Cap", 2386, 2575),
    ("Var(d-cap)", 2578, 2767), ("Desvpad(Var(S2nd))", 2770, 2959),
    ("DesvPad(Var(E(RLT)))", 2962, 3151), ("Média(d-Cap)", 3154, 3343),
    ("DesvPad(Var(d-cap))", 3346, 3535), ("LB", 3538, 3727), ("DesvPad(ND*ELT)", 3730, 3919),
    ("DesvPad(Cap)", 3922, 4111), ("z(RLT)", 4114, 4303), ("Aleatória S2nd", 4306, 4495),
    ("Radicand", 4498, 4687), ("SQRT", 4690, 4879), ("ND*ELT", 4882, 5071),
    ("Aleatória RLT", 5074, 5263), ("ActualRotw", 5266, 5455),
    ("vMaxNumOfCyclesw", 5458, 5647), ("DesvPad(demand)", 5650, 5839),
    ("DesvPad(E(RLT))", 5842, 6031), ("DesvPad(D*E(RLT))", 6034, 6223),
    ("Média(D*E(RLT))", 6226, 6415), ("Reorder(Estado da arte)", 6418, 6607),
    ("Erro > 0,01%", 6610, 6799), ("DesvPad(D*ELT)", 6816, 7005)
]

def generate(grupo, base):
    data = []
    for tabela, (c_start, c_narrow, c_wide) in enumerate(COLUMN_MAP, start=1):
        for var, r0, r1 in base:
            c_end = c_wide if grupo == "Suppliers" else c_narrow
            data.append({
                "grupo": grupo,
                "tabela": tabela,
                "variavel": var,
                "range": f"{c_start}{r0}:{c_end}{r1}"
            })
    return data

if __name__ == "__main__":
    all_tables = []
    all_tables += generate("Suppliers", BASE_SUPPLIERS)
    all_tables += generate("Factories", BASE_FACTORIES)
    all_tables += generate("Distributors", BASE_DISTRIBUTORS)
    all_tables += generate("Retailers", BASE_RETAILERS)

    with open("entrada_completa.txt", "w", encoding="utf-8") as f:
        json.dump(all_tables, f, ensure_ascii=False, indent=4)