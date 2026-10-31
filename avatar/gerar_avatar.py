"""Gera o avatar em pixel art (32x32) e uma versão pixelizada da foto."""
import sys
from PIL import Image

PALETA = {
    "K": (26, 18, 16),    # contorno
    "H": (35, 25, 21),    # cabelo
    "h": (68, 50, 40),    # brilho do cabelo
    "E": (30, 21, 18),    # sobrancelha
    "S": (201, 142, 106), # pele
    "s": (168, 113, 79),  # sombra da pele
    "W": (240, 230, 220), # branco do olho
    "P": (59, 34, 20),    # íris
    "B": (40, 29, 23),    # barba
    "b": (74, 55, 44),    # barba clara
    "M": (196, 118, 106), # lábios
    "T": (22, 22, 26),    # camiseta
    "t": (48, 48, 58),    # costura/realce
    "w": (242, 242, 242), # lobo
}

F = "......"
SPRITE = [
    "................................",
    "...........KKKKKKKKKK...........",
    ".........KKHHHHHHHHHHKK.........",
    "........KHHHHHHHHHHhhHHK........",
    ".......KHHHHHHHHHhhHHHHHK.......",
    ".......KHHHHHHHhhHHHHHHHK.......",
    "......KHHHHHHhhHHHHHHHHHHK......",
    "......KHHHHHhSSSHHHHHHHHHK......",
    "......KHHHSSSSSSSSSHHHHHHK......",
    ".....KKHHSSSSSSSSSSSSSHHHKK.....",
    F + "KHSEEEEESSSSEEEEESHK" + F,
    F + "KSSSSEESSSSSSEESSSSK" + F,
    ".....K" + "sSSKWPPWSSSSWPPWKSSs" + "K.....",
    ".....K" + "sSSSssSSSSSSSSssSSSs" + "K.....",
    F + "KSSSSSSSSssSSSSSSSSK" + F,
    F + "KBSSSSSSssssSSSSSSBK" + F,
    F + "KBBSSSBBBBBBBBSSSBBK" + F,
    F + "KBBBBBBMMMMMMBBBBBBK" + F,
    F + "KBBBBBBBbbbbBBBBBBBK" + F,
    F + ".KBBBBBBBbbBBBBBBBK." + F,
    F + "..KBBBBBBBBBBBBBBK.." + F,
    F + "...KKBBBBBBBBBBKK..." + F,
    "..........KsSSSSSSSSsK..........",
    "....TTTTTTtsSSSSSSSSstTTTTTT....",
    "..TTTTTTTTTttSSSSSSttTTTTTTTTT..",
    ".TTTTTTTTTTTTttttttTTTTTTTTTTTT.",
    "TTTwTTTTTwTTTTTTTTTTTTTTTTTTTTTT",
    "TTTwwTTTwwTTTTTTTTTTTTTTTTTTTTTT",
    "TTTwTwwwTwTTTTTTTTTTTTTTTTTTTTTT",
    "TTTwTTwTTwTTTTTTTTTTTTTTTTTTTTTT",
    "TTTTwTTTwTTTTTTTTTTTTTTTTTTTTTTT",
    "TTTTTwwwTTTTTTTTTTTTTTTTTTTTTTTT",
]


def ceu(y, total):
    # degradê do céu: azul mais forte em cima, mais claro embaixo
    t = y / (total - 1)
    topo, base = (88, 160, 222), (176, 220, 245)
    return tuple(round(a + (b - a) * t) for a, b in zip(topo, base))


def avatar(escala=16):
    n = len(SPRITE)
    img = Image.new("RGB", (32, n))
    for y, linha in enumerate(SPRITE):
        assert len(linha) == 32, (y, len(linha))
        for x, c in enumerate(linha):
            img.putpixel((x, y), ceu(y, n) if c == "." else PALETA[c])
    return img.resize((32 * escala, n * escala), Image.NEAREST)


def foto_pixelizada(caminho, lado=64, cores=24, escala=8):
    foto = Image.open(caminho).convert("RGB")
    w, h = foto.size
    # recorte quadrado centrado no rosto
    topo = int(h * 0.15)
    foto = foto.crop((0, topo, w, topo + w))
    pequena = foto.resize((lado, lado), Image.BOX)
    pequena = pequena.quantize(colors=cores, method=Image.MEDIANCUT).convert("RGB")
    return pequena.resize((lado * escala, lado * escala), Image.NEAREST)


if __name__ == "__main__":
    saida = sys.argv[1] if len(sys.argv) > 1 else "."
    avatar().save(f"{saida}/avatar_pixel_art.png")
    if len(sys.argv) > 2:
        foto_pixelizada(sys.argv[2]).save(f"{saida}/foto_pixelizada.png")
