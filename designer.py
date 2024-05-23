from __future__ import annotations
from itertools import product
from pathlib import Path
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from util import read_dotmatrix_charset_json, save_dotmatrix_charset_json


class DesignerGrid(tk.LabelFrame):
    """Tervezőrácsot megvalósító és megjelenítő osztály"""

    def __init__(self, master: DotMatrixCharDesigner, rowcount, columncount):
        super().__init__(master)
        self.config(text='Karaktertervező rács', labelanchor='n', bg='gray98', font=('Consolas', 12, 'bold'))
        # A tervezőrács celláit egy-egy négyzet alakú Frame grafikus elem valósítja meg. E cella színe a
        # bal egérgomb minden egyes lenyomásakor fehér vagy fekete lesz. A fekete jelenti, hogy a cella a
        # pontmátrixban kijelölt.
        cell_size = 50  # Egy rácscellát reprezentáló keret mérete.
        for ri, ci in product(range(rowcount), range(columncount)):
            cell_frame = tk.Frame(self, name='cell' + '{}{}'.format(ri, ci),
                                  width=cell_size, height=cell_size, bg='white',
                                  highlightthickness=cell_size * 0.04)

            cell_frame.grid(row=ri, column=ci, sticky='news')
            # A bal egérgomb lenyomása esemény és a színváltást megvalósító eseménykezelő cellákhoz rendelése.
            cell_frame.bind('<Button 1>', self.toggle_cell_color)

    def toggle_cell_color(self, event):
        """A tervezőrács egy adott, az eseménnyel érintett cellája színváltását megvalósító eseménykezelő."""
        widget: tk.Frame = event.widget
        widget.config(bg='black' if widget.cget('bg') == 'white' else 'white')

    def clear(self):
        """Törli a tervezőrács tartalmát, vagyis minden cellát fehér színűre állít."""
        for cell_frame in self.winfo_children():
            cell_frame.config(bg='white')


class FileContentViewer(tk.LabelFrame):
    """Az aktuális karakterkészlet pontmátrix definícióit hordozó fájl tartalmának megtekinthetőségét megvalósító osztály"""

    def __init__(self, master: DotMatrixCharDesigner):
        super().__init__(master)
        self.config(text='Fájltartalom', labelanchor='n', bg='gray98', font=('Consolas', 12, 'bold'))
        # A fájltartalmat egy függőleges görgetősávval ellátott Text típusú grafikus elemmel jelenítjük meg, amit a
        # a tkinter modulban rendelkezésre álló ScrolledText osztállyal valósítunk meg.
        self.filecontent = ScrolledText(self, bg='gray98', font=('Consolas', 10), width=115)
        self.filecontent.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=5, pady=5)
        # Az aktuális karakterkészletet tartalmazó szótár kulcs-értékpárjait írjuk egymás alá a ScrolledText elemben.
        txt = '\n'.join([f'{key}:{value}' for key, value in master.charset.items()])
        self.filecontent.insert('1.0', txt)


class ToolBar(tk.Frame):
    def __init__(self, master: DotMatrixCharDesigner):
        super().__init__(master)
        common_configs = dict(font=('Consolas', 14, 'bold'))  # A grafikus elemek azonos konfigurációs paraméterei.
        # A megtervezni kívánt karakter beviteli mezője a hozzárendelt kontrollváltozóval.
        self.char = tk.StringVar(self, '')
        tk.Entry(self, textvariable=self.char, width=3, justify=tk.CENTER, font=('Consolas', 24, 'bold'))
        # Nyomógomb a beviteli mezőben megadott karakter pontmátrix képének tervezőrácsban történő megjelenítéséhez.
        tk.Button(self, text='Betölt', **common_configs,
                  command=lambda: master.show_char_in_designer_grid(self.char.get()))
        # Nyomógomb a tervezőrács tartalmának törléséhez, ami a cellák fehérre váltását jelenti.
        tk.Button(self, text='Rácstörlés', **common_configs, command=master.designer_grid.clear)
        # Nyomógomb a beviteli mezőben megadott karakter karakterkészletből történő eltávolítására.
        tk.Button(self, text='Eltávolítás', **common_configs, command=lambda: master.remove(self.char.get()))
        # Nyomógomb a beviteli mezőben megadott karakter és a tervezőrácsban szereplő pontmátrix definíciójának
        # karakterkészletbe történő felvételére és fájlba mentése.
        tk.Button(self, text='MENTÉS', **common_configs, command=master.update_and_save_charset)
        # A fenti grafikus elemek lehelyezése azonos paraméterekkel.
        for widget in self.winfo_children():
            widget.pack(side=tk.LEFT, padx=(2, 2), pady=5)

        # A karakterkészletet tároló fájl útvonalának és nevének megadására szolgáló beviteli mező.
        filepath_ebx = tk.Entry(self, textvariable=master.filepath, width=40, justify=tk.LEFT, font=('Consolas', 18))
        filepath_ebx.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5), pady=7)


class MessageBar(tk.Frame):
    """A tájékoztató vagy hibaüzeneteket megjelenítő sávot megvalósító osztály."""

    def __init__(self, master: DotMatrixCharDesigner):
        super().__init__(master)
        # A kiírandó szövegek egy Label típusú grafikus elemen jelennek meg, amelyhez egy, az aktuális szöveget
        # tartalmazó kontrollváltozó van társítva.
        self.message = tk.StringVar(self, '')
        lbl_msg = tk.Label(self, textvariable=self.message, bg='gray95', fg='red', font=('Consolas', 12, 'bold'))
        lbl_msg.pack(fill=tk.BOTH)


class DotMatrixCharDesigner(tk.Tk):
    """Pontmárix karakterek tervezésére szolgáló alkalmazás.
    A példányosításkor meg kell adni egy fájlt a charset_filepath paraméternek, amelybe a megtervezett karakterek és
    pontmátrix leírásuk JSON objektumként kerül. Ha a megadott fájl egy létező pontmátrixleíró JSON fájl, akkor ennek
    tartalma beolvasásra kerül feltéve, hogy az nincs ellentmondásban a tervezendő pontmátrix sor- és/vagy
    oszlopméretével, amelyet a rowcount és columncount argumentumokkal lehet meghatározni. Sikeres beolvasás után a
    fájl tartalma megjelenik a jobb oldali keretben, ami segít megállapítani, hogy mely karakterek vannak már megtervezve.
    Ha pedig egy karaktert szerkeszteni akarunk, akkor megadva a karaktert a bal alsó beviteli mezőben, a hozzá tartozó
    pontmátrix betölthető és megjeleníthető a tervezőrácsban a "Betölt" gomb megnyomásával.
    A tervezőrácsban a bal egérgomb kattintással lehet a mátrixpontokat ki/be kapcsolni.
    Akár új karaktert, akár meglévőt szerkesztünk a rácsban, ha befejeztük, akkor a "MENTÉS" gomb megnyomásával el kell
    menteni a tervezés eredményét. Ha pedig egy karaktert a készletből ki akarunk törölni, akkor a karakter beviteli mezőbe
    írása után az "Eltávolítás" gombra kell kattintani.
    """

    def __init__(self, charset_filepath: str, rowcount: int = 12, columncount: int = 5):
        super().__init__()
        self.title('Karaktertervező alkalmazás')
        self.resizable(tk.NO, tk.NO)
        self.rowcount, self.columncount = rowcount, columncount
        # A karaktereket és a megtervezett pontmátrixukat mint kulcs-érték párokat egy szótártárban tartjuk nyilván.
        self.charset = dict()
        # Ha a megadott fájlútvonalon érvényes pontmátrixleíró fájl van, akkor annak tartalmát beolvassuk a szótárba.
        # Ha a fájl nem létezik, akkor a megtervezett karakterek e fájlba fognak mentődni.
        self.filepath = tk.StringVar(self, charset_filepath)
        if Path(self.filepath.get()).exists():
            self.read_dotmatrixcharset()
            a_bitmx = self.charset[list(self.charset)[0]]
            if not (self.rowcount, self.columncount) == (len(a_bitmx), len(a_bitmx[0])):
                raise ValueError(
                    'A fájlban szereplő karaktermátrix dimenziója nem egyezik a megadott sor és oszlopszámmal')

        # A grafikus felület felépítése a komponens keretekből, és ezek lehelyezése a főablakban.
        self.message_bar = MessageBar(self)
        self.designer_grid = DesignerGrid(self, rowcount, columncount)
        self.toolbar = ToolBar(self)
        self.file_content_viewer = FileContentViewer(self)

        self.message_bar.grid(row=0, column=0, sticky='wens', columnspan=2)
        self.designer_grid.grid(row=1, column=0, sticky='wens')
        self.file_content_viewer.grid(row=1, column=1, sticky='wens', padx=5)
        self.toolbar.grid(row=2, column=0, columnspan=2, sticky='wens')

        # Ahhoz, hogy a korábbi tájékoztató üzenet törlődjön, ha a felületen a bal egérgombbal kattintunk.
        self.bind_all('<Button 1>', lambda e: self.message_bar.message.set(''))

    def read_dotmatrixcharset(self):
        """Az aktuális fájlból beolvassa egy szótárba a karakterkészletet. A szótár kulcsai a karakterek, a kulcsokhoz
        tartozó értékek a karakter pontmátrixleírását tartalmazó listák.
        """
        self.charset: dict = read_dotmatrix_charset_json(Path(self.filepath.get()))

    def remove(self, char: str):
        """Az argumentumban megadott karaktert törli a karakterkészletből."""
        try:
            del self.charset[char]
            save_dotmatrix_charset_json(dict(sorted(self.charset.items())), Path(self.filepath.get()))
            self.file_content_viewer.filecontent.delete('1.0', tk.END)
            self.file_content_viewer.filecontent.insert('1.0', '\n'.join([f'{key}:{value}'
                                                                          for key, value in
                                                                          dict(sorted(self.charset.items())).items()]))
            self.message_bar.message.set(f'A "{char}" karakter törölve lett a karakterkészletből.')
            self.toolbar.char.set('')
        except KeyError:
            self.message_bar.message.set(f'Eltávolítás nem lehetséges, mert a "{char}" karakter nincs definiálva.')
        self.designer_grid.clear()

    def show_char_in_designer_grid(self, char: str):
        """Az argumentumban megadott karakter pontmátrix képét jeleníti meg a tervezőrácsban."""
        if len(char) != 1:
            self.message_bar.message.set('Csak egyetlen, nem üres karakter adható meg!')
            return
        # Az eddig elmentett karakterkészlet beolvasása az aktuálisan megadott fájlból.
        try:
            self.read_dotmatrixcharset()
        except FileNotFoundError:
            self.message_bar.message.set(f'A fájl nem létezik: {self.filepath.get()}')
            self.charset.clear()
            self.file_content_viewer.filecontent.delete('1.0', tk.END)
            return
        try:
            # Az aktuális karakterkészletből a megadott karakter mátrixának kikérése.
            dotmx: list[str] = self.charset[char]
        except KeyError:
            # Ha nincs még ilyen karakter a készletben, akkor töröljük a tervezőrács tartalmát, és visszatérünk.
            self.designer_grid.clear()
            self.message_bar.message.set('Még nincs ilyen karakter. Ha kell, akkor tervezd meg most.')
            return
        # Ha van a karakterkészletben az argumentumban megadott karakter, és így megkaptuk a mátrixát, akkor
        # a tervezőrács celláit a mátrix értékeinek megfelelő színnel jelenítjük meg.
        for cell_frame in self.designer_grid.winfo_children():
            ri, ci = cell_frame.grid_info()['row'], cell_frame.grid_info()['column']
            cell_color = 'black' if dotmx[ri][ci] == '1' else 'white'
            cell_frame.config(bg=cell_color)

    def cells_to_matrix(self) -> list[str]:
        """A tervezőrács tartalmának megfelelő mátrixot hoz létre, amely egy olyan lista, amelynek elemei olyan
        karakterláncok, amelyek csak '0' vagy '1' karaktereket tartalmaznak aszerint, hogy a tervezőrács adott
        cellája fehér vagy fekete színű.
        """
        mx: list = [''] * self.rowcount
        bitstring = ''  # Csak '0' vagy '1' karaktereket tartalmazó karakterlánc.
        for ri, ci in product(range(self.rowcount), range(self.columncount)):
            row_cells: list = self.designer_grid.grid_slaves(ri)
            for cell_frame in reversed(row_cells):
                bitstring += '1' if cell_frame.cget('bg') == 'black' else '0'
            mx[ri] = bitstring
            bitstring = ''
        return mx

    def update_and_save_charset(self):
        """A beviteli mezőben megadott karaktert és annak a tervezőrácsban szereplő pontmátrix leírását felveszi a
        karakterkészletbe és elmenti az aktuálisan megadott fájlba.
        """
        if len(self.toolbar.char.get()) == 1:
            self.charset.update({self.toolbar.char.get(): self.cells_to_matrix()})
            # A szótárat egy JSON fájlba mentjük.
            save_dotmatrix_charset_json(dict(sorted(self.charset.items())), Path(self.filepath.get()))
            # A fájltartalom megjelenítését aktualizáljuk.
            self.file_content_viewer.filecontent.delete('1.0', tk.END)
            content_text = '\n'.join([f'{key}:{value}' for key, value in dict(sorted(self.charset.items())).items()])
            self.file_content_viewer.filecontent.insert('1.0', content_text)
            # Tájékoztató üzenet az elmentésről.
            self.message_bar.message.set(f'A "{self.toolbar.char.get()}" karakter el lett mentve.')
        else:
            self.message_bar.message.set('Csak egyetlen, nem üres karakter menthető!')

    def run(self):
        self.mainloop()


if __name__ == '__main__':
    designer = DotMatrixCharDesigner('dotmxfonts5x12.json')
    designer.run()

