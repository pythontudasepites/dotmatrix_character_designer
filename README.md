# Pontmátrix karakterek tervezésére és megjelenítésére szolgáló alkalmazás

A _designer_ modul _DotMatrixCharDesigner_ osztályának példánya pontmárix formában megjelenő karakterek tervezését lehetővé tevő alkalmazás.

Az osztály példányosításakor meg kell adni egy fájlt a _charset_filepath_ paraméternek, amelybe a megtervezett karakterek és pontmátrix leírásuk kerül JSON objektumként. Ha a megadott fájl egy létező pontmátrixleíró JSON fájl, akkor ennek tartalma beolvasásra kerül feltéve, hogy az nincs ellentmondásban a tervezendő pontmátrix sor- és/vagy oszlopméretével, amelyet a _rowcount_ és _columncount_ argumentumokkal lehet meghatározni.

Sikeres beolvasás után a fájl tartalma megjelenik a jobb oldali címkézett keretben, ami segít megállapítani, hogy mely karakterek vannak már megtervezve. Ha pedig egy már elmentett karaktert szerkeszteni akarunk, akkor megadva a karaktert a bal alsó beviteli mezőben, a "Betölt" gomb megnyomásával a hozzá tartozó pontmátrix betölthető és megjeleníthető a tervezőrácsban.

A tervezőrácsban bal egérgomb kattintással lehet a mátrixpontokat ki/be kapcsolni, és így a fekete színű cellákkal a karakter formáját kialakítani.

Akár új karaktert, akár egy már meglévőt szerkesztünk a rácsban, ha befejeztük, akkor a "MENTÉS" gomb megnyomásával el kell menteni a tervezés, illetve szerkesztés eredményét.

Ha egy karaktert a készletből ki akarunk törölni, akkor a karakter beviteli mezőbe történő írása után az "Eltávolítás" gombra kell kattintani.

A műveletekről a szerkesztőrács feletti üzenetsorban visszajelzést kapunk, vagy hiba esetén hibaüzenetet.

Az alkalmazás felületének képernyőképe:

<img src="https://github.com/pythontudasepites/dotmatrix_character_designer/blob/main/dotmxchar_designer_gui.png" width="720" height="420">

A _dotmatrixstring_widget_ modulban található _DotMatrixString_ osztály egy példánya az inicializáláskor a _string_to_display_ paraméternek átadott karakterláncot pontmátrix formában jeleníti meg egy Frame objektumon úgy, hogy az egyes karakterek egymást követően lehelyezett Canvas elemeken vannak kirajolva.

Azt, hogy hogyan jelenjenek meg a karakterek a _filepath_ argumentumban megadott pontmátrix-leíró JSON fájl tartalma határozza meg.

Az inicializáláskor az _fg_ és _bg_ opcionális argumentumokkal megadható a szöveg- és háttérszín, valamint az, hogy a mátrixpontok körrel vagy négyzettel legyenek megjelenítve. Ha négyzettel, akkor a _marker_ paraméternek a "rectangle", ha körrel, akkor a "circle" értéket kell adni. Ez utóbbi az alapértelmezett.

A karakterek alapértelmezésben a beolvasott pontmátrix leíró fájlban szereplő sor- és oszlopszám szerinti pixel méretben jelennek meg (pl. 5x12 pixel), de ennek egész számú többszörösére nagyíthatók a scale_factor beállításával.

Az alábbi kép a modulban látható tesztsorok eredményét mutatja:

<img src="https://github.com/pythontudasepites/dotmatrix_character_designer/blob/main/dotmxchar_widget_application.png" width="720" height="125">


Az alkalmazás működéséhez Python 3.10+ verzió szükséges.
