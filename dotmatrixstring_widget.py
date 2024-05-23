import tkinter as tk
from util import read_dotmatrix_charset_json


class DotMatrixString(tk.Frame):
    """Az osztály egy példánya az inicializáláskor a string_to_display paraméternek átadott karakterláncot pontmátrix
    formában jeleníti meg egy Frame objektumon úgy, hogy az egyes karakterek egymást követően lehelyezett Canvas
    elemeken vannak kirajolva. Azt, hogy hogyan jelenjenek meg a karakterek a filepath argumentumban megadott
    pontmátrix-leíró JSON fájl tartalma határozza meg.
    Az inicializáláskor az fg és bg opcionális argumentumokkal megadható a szöveg- és háttérszín, valamint az, hogy
    a mátrixpontok körrel vagy négyzettel legyenek megjelenítve. Ha négyzettel, akkor a marker paraméternek a
    "rectangle", ha körrel, akkor a "circle" értéket kell adni. Ez utóbbi az alapértelmezett.
    A karakterek alapértelmezésben a beolvasott pontmátrix leíró fájlban szereplő sor- és oszlopszám szerinti pixel
    méretben jelennek meg (pl. 5x12 pixel), de ennek egész számú többszörösére nagyíthatók a scale_factor beállításával.
    """

    def __init__(self, master, string_to_display: str, filepath: str, bg='white', fg='black', scale_factor=1,
                 marker='circle'):
        super().__init__(master)

        # Beolvassuk a megadott JSON fájlból a pontmátrix karakterkészletet egy szótárba, ahol a kulcsok az egyes
        # karakterek, a kulcsokhoz tartozó értékek pedig egy-egy lista, amely a karakter pontmátrix leírását
        # tartalmazza '0' és '1' karakterekből álló karakterláncok formájában. Ezek száma a pontmátrix sorainak
        # számával egyenlő, a karakterláncok hossza pedig a pontmátrix oszlopainak számával egyezik.
        self.charset: dict = read_dotmatrix_charset_json(filepath)
        # A beolvasott szótár alapján meghatározzuk a karakterek méreteit, azaz a mátrix sor- és oszlopszámát.
        a_bitmx = self.charset[list(self.charset)[0]]
        self.rowcount, self.columncount = len(a_bitmx), len(a_bitmx[0])

        for char in string_to_display:
            # A megjelenítendő karakterlánc egyes karaktereit egy-egy vászon elemen kirajzoljuk, és a vásznakat
            # egymást követően lehelyezzük a keretben.
            charmx: list[str] = self.charset.get(char, self.charset.get(chr(0xfffd)))
            canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            for ri, bitstring in enumerate(charmx):
                bitstring: str  # Az egy sorban levő '0' vagy '1' tartalmú karakterlánc.
                for ci, bitchar in enumerate(bitstring):
                    if bitchar == '1':
                        x0, y0 = ci, ri
                        x1, y1 = x0 + 1, y0 + 1
                        # Az argumentumban megadottnak megfelelően a mátrixpontokat körrel vagy négyzettel jelenítítjük meg.
                        if marker == 'rectangle':
                            canvas.create_rectangle((x0, y0), (x1, y1), tags='dot', fill=fg)
                        if marker == 'circle':
                            canvas.create_oval((x0, y0), (x1, y1), tags='dot', fill=fg)

            pdx, pdy = 1, 0
            # A sor- és oszlopszámhoz igazítjuk a vászon méretét.
            canvas.config(width=self.columncount + pdx, height=self.rowcount + pdy)
            # Minden karakterpontot felnagyítunk a megadott mértékkel, és a vászon méretét is ehhez igazítjuk.
            scalefactor = scale_factor
            canvas.scale('dot', 0, 0, scalefactor, scalefactor)
            canvas.config(width=scalefactor * int(canvas.cget('width')),
                          height=scalefactor * int(canvas.cget('height')))


if __name__ == '__main__':
    # TESZT
    root = tk.Tk()
    dotmxfilepath = 'dotmxfonts5x12.json'

    DotMatrixString(root, 'A tanulás tudás. "A tudás hatalom." (Sir Francis Bacon)',
                    dotmxfilepath, fg='black', bg='light cyan', scale_factor=3, marker='rectangle')

    DotMatrixString(root, 'PYTHON TUDÁSÉPÍTÉS LÉPÉSRŐL LÉPÉSRE',
                    dotmxfilepath, fg='blue', bg='white', scale_factor=5, marker='circle')

    DotMatrixString(root, """Az alapoktól az első asztali alkalmazásig.""",
                    dotmxfilepath, fg='red', bg='lightyellow', scale_factor=4, marker='rectangle')

    for w in root.winfo_children():
        w.pack(fill=tk.BOTH, padx=3)

    root.mainloop()
