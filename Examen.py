import gi, conexionBD

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table

class VentanaAlbaran(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Albaran")
        self.set_size_request(400,300)

        CajaP = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing = 4)
        CajaCmb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 2)
        CajaTV = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing =2)

        bbdd = conexionBD.ConexionBD("modelosClasicos.dat")
        bbdd.conectaBD()
        bbdd.creaCursor()

        modelo = Gtk.ListStore(int,str,int,float,int)
        self.filtrado_albaran = 0
        filtro = modelo.filter_new()
        filtro.set_visible_func(self.filtro_albaran)



        vista = Gtk.TreeView(model=filtro)
        for i, titulo in enumerate (["NumAlbaran","CodProducto", "Cantidad", "PrecioUnidad", "NumLinea"]):
            celda = Gtk.CellRendererText()
            columna = Gtk.TreeViewColumn(titulo,celda,text = i)
            vista.append_column(columna)

        self.lblAlbaran = Gtk.Label(label = "Numero Albaran")
        self.cmbNumeroA = Gtk.ComboBoxText()
        self.btnInforme = Gtk.Button(label="Generar Informe")
        self.cmbNumeroA.connect("changed", self.on_cmbNumeroA_changed, filtro,modelo)
        self.btnInforme.connect("clicked", self.on_btnInforme_clicked,bbdd)

        nAlbaranes = bbdd.consultaSenParametros("select numeroAlbaran from ventas")
        dAlbaranes = bbdd.consultaSenParametros("select * from main.detalleVentas where numeroAlbaran in (select numeroAlbaran from ventas)")
        print(nAlbaranes)
        print(dAlbaranes)
        for albaran in nAlbaranes:
            self.cmbNumeroA.append_text(str(albaran[0]))
        self.cmbNumeroA.append_text(str(0))

        for dAlbaran in dAlbaranes:
            modelo.append(dAlbaran)

        CajaCmb.pack_start(self.lblAlbaran, False, False, 5)
        CajaCmb.pack_start(self.cmbNumeroA, False, False, 5)
        CajaTV.pack_start(vista, True, True, 5)

        CajaP.pack_start(CajaCmb, False, False, 5)
        CajaP.pack_start(CajaTV, False, False, 5)
        CajaP.pack_start(self.btnInforme, False, False,5)

        self.add(CajaP)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def filtro_albaran(self, modelo, fila, datos):
        if (self.filtrado_albaran is None or self.filtrado_albaran==0):
            return True
        else:
            #print("NumeroAlbaran: %d" % (modelo[fila][0] == self.filtrado_albaran))
            return modelo[fila][0] == self.filtrado_albaran

    def on_cmbNumeroA_changed(self, combo, filtro, modelo):
        seleccion = combo.get_active_iter()
        if seleccion is not None:
            cmbModelo = combo.get_model()
            numero = cmbModelo[seleccion][0]
            self.filtrado_albaran = int(numero)
            print("Numero Seleccionado: %d" % self.filtrado_albaran)
        if seleccion is None:
            self.filtrado_albaran=0
        filtro.refilter()

    def on_btnInforme_clicked(self, boton, bd):
        doc = []
        hojaEstilo = getSampleStyleSheet()
        listaVenta = bd.consultaSenParametros("select * from ventas")
        listaDetalles = bd.consultaSenParametros("select * from main.detalleVentas where numeroAlbaran in(select numeroAlbaran from ventas)")


        cabecera = hojaEstilo['Heading1']
        cabecera.pageBreakBefore = 0
        cabecera.keepWithNext = 1
        parrafo = Paragraph("Ventas:", cabecera)
        doc.append(parrafo)
        doc.append(Spacer(0, 20))

        cuerpoTexto = hojaEstilo['BodyText']
        cuerpoTexto.keepWithNext = 0

        cabecera_al = hojaEstilo['Heading4']
        cuerpoTexto.keepWithNext = 0

        cadena = str()
        fila = []
        cabecera_tabla = ["codProducto", "cantidad", "precioUnitario", "numeroLinea"]
        ctabla = Table(cabecera_tabla)
        for venta in listaVenta:
            parrafo = Paragraph("Albaran: " + str(venta[0]) + "       Fecha: " + str(venta[1]) + "    Cliente: " + str(venta[3]), cabecera_al)
            doc.append(parrafo)
            fila.append(cabecera_tabla)
            for detalles in listaDetalles:
                if venta[0] == detalles[0]:
                    fila.append(detalles[1:])

            tabla = Table(fila)
            doc.append(tabla)
            fila.clear()
            cadena = cadena + "\n"
            parrafo = Paragraph(cadena, cuerpoTexto)
            doc.append(parrafo)
            cadena = ""

        informe = SimpleDocTemplate("informe.pdf", pagesize=A4, showBoundary=0)
        informe.build(doc)

if __name__ == "__main__":

    VentanaAlbaran()

    Gtk.main()