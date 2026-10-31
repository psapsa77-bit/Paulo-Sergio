"""Gera o avatar de corpo inteiro em pixel art (32x64), de terno."""
import sys
from PIL import Image
from gerar_avatar import PALETA, SPRITE

CORES = dict(PALETA)
CORES.update({
    "J": (44, 52, 74),    # terno
    "j": (66, 76, 104),   # realce do terno
    "d": (30, 36, 52),    # vinco da calça
    "C": (238, 238, 240), # camisa
    "R": (150, 30, 45),   # gravata
    "Y": (200, 165, 90),  # botão
    "O": (16, 16, 18),    # sapato
    "o": (70, 70, 78),    # brilho do sapato
    "G": (190, 160, 90),  # relógio
})

# Metade esquerda do corpo (16 colunas); a direita é espelhada.
CORPO = [
    "........KJJJKCCR",
    "......KJJJJJJKCR",
    "....KJJJJJJJJKCR",
    "...KJJJJJJJJJKCR",
    "..KJJKJJJJJJJKCR",
    "..KJJKJJJJJJJjKR",
    "..KJJKJJJJJJJJjK",
    "..KJJKJJJJJJJJJY",
    "..KJJKJJJJJJJJJK",
    "..KJJKJjjjjJJJJK",
    "..KCCKJJJJJJJJJY",
    "..KSSKJJJJJJJJJK",
    "..KSSKJJJJJJJJJK",
    "...KKKJJJJJJJJJK",
    "......KKKKKKKKKK",
    "......KJJJJJJJJJ",
    "......KJJJJJJJJJ",
    "......KJJJJJJJJK",
] + ["......KJJdJJJJK."] * 12 + [
    ".......KJdJJJJK.",
    ".......KJdJJJJK.",
    ".......KJJJJJJK.",
    ".....KOOOOOOOOK.",
    "....KOoOOOOOOOK.",
    "....KKKKKKKKKKK.",
]

LINHAS = SPRITE[:23] + [m + m[::-1] for m in CORPO]
LINHAS += ["." * 32] * (64 - len(LINHAS))
# relógio no pulso esquerdo (lado esquerdo da imagem, como no espelho)
LINHAS[33] = LINHAS[33][:3] + "GG" + LINHAS[33][5:]

CHAO = 50


def fundo(x, y):
    if y < CHAO - 1:  # parede
        v = 222 - y // 8
        return (v, v, v + 4)
    if y == CHAO - 1:  # rodapé
        return (245, 245, 245)
    base = (214, 192, 152) if (x * 7 + y * 3) % 5 else (196, 174, 134)  # tapete felpudo
    if 54 <= y <= 59 and 4 <= x <= 27:  # sombra sob os pés
        return tuple(int(c * 0.85) for c in base)
    return base


def gerar(escala=12):
    img = Image.new("RGB", (32, 64))
    for y, linha in enumerate(LINHAS):
        assert len(linha) == 32, (y, len(linha))
        for x, c in enumerate(linha):
            img.putpixel((x, y), fundo(x, y) if c == "." else CORES[c])
    return img.resize((32 * escala, 64 * escala), Image.NEAREST)


if __name__ == "__main__":
    saida = sys.argv[1] if len(sys.argv) > 1 else "."
    gerar().save(f"{saida}/avatar_terno.png")
