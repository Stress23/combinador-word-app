# main_imagenes.py - APP MÓVIL CON IMÁGENES EN GRID 2 COLUMNAS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json
import threading


class ConfigPopup(Popup):
    """Popup para configurar IP del PC"""
    def __init__(self, ip_actual, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Configurar IP del PC"
        self.size_hint = (0.85, 0.4)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text="IP de tu PC:"))
        
        self.ip_input = TextInput(
            text=ip_actual,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.ip_input)
        
        btn_guardar = Button(
            text="Guardar",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_guardar.bind(on_press=self.guardar)
        layout.add_widget(btn_guardar)
        
        self.content = layout
    
    def guardar(self, instance):
        self.callback(self.ip_input.text.strip())
        self.dismiss()


class CombinadorVerdurasApp(App):
    def build(self):
        self.title = "Catálogo Verduras"
        self.ip_pc = "192.168.1.100"  # CAMBIAR por tu IP real
        self.job_id = None
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # ===== HEADER =====
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        title = Label(
            text="🥦 Catálogo de Semillas",
            size_hint_x=0.7,
            font_size='18sp',
            bold=True
        )
        
        btn_config = Button(
            text="⚙️",
            size_hint_x=0.15,
            font_size='16sp'
        )
        btn_config.bind(on_press=self.mostrar_config)
        
        btn_refresh = Button(
            text="🔄",
            size_hint_x=0.15,
            font_size='16sp'
        )
        btn_refresh.bind(on_press=self.cargar_lista_archivos)
        
        header.add_widget(title)
        header.add_widget(btn_config)
        header.add_widget(btn_refresh)
        main_layout.add_widget(header)
        
        # ===== IP =====
        self.ip_label = Label(
            text=f"PC: {self.ip_pc}",
            size_hint_y=None,
            height=25,
            font_size='11sp',
            color=(0.4, 0.4, 0.4, 1)
        )
        main_layout.add_widget(self.ip_label)
        
        # ===== BÚSQUEDA =====
        search_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        
        self.search_input = TextInput(
            hint_text='🔍 Buscar verdura...',
            multiline=False,
            size_hint_x=0.8
        )
        self.search_input.bind(text=self.buscar_verduras)
        
        btn_clear_search = Button(
            text="X",
            size_hint_x=0.2,
            size_hint_y=None,
            height=40
        )
        btn_clear_search.bind(on_press=self.limpiar_busqueda)
        
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_clear_search)
        main_layout.add_widget(search_box)
        
        # ===== CONTADOR =====
        self.contador_label = Label(
            text="Seleccionadas: 0/0",
            size_hint_y=None,
            height=25,
            font_size='12sp',
            color=(0.3, 0.5, 0.3, 1)
        )
        main_layout.add_widget(self.contador_label)
        
        # ===== GRID DE 2 COLUMNAS CON IMÁGENES =====
        scroll = ScrollView(bar_width=8)
        self.grid_verduras = GridLayout(
            cols=2,
            spacing=15,
            padding=15,
            size_hint_y=None
        )
        self.grid_verduras.bind(minimum_height=self.grid_verduras.setter('height'))
        scroll.add_widget(self.grid_verduras)
        main_layout.add_widget(scroll)
        
        # ===== BOTÓN GENERAR =====
        self.btn_generar = Button(
            text="📗 GENERAR CATÁLOGO",
            size_hint_y=None,
            height=60,
            background_color=(0.1, 0.7, 0.3, 1),
            font_size='14sp',
            bold=True
        )
        self.btn_generar.bind(on_press=self.enviar_a_pc)
        main_layout.add_widget(self.btn_generar)
        
        # ===== STATUS =====
        self.status_label = Label(
            text="Presiona 🔄 para cargar el catálogo",
            size_hint_y=None,
            height=30,
            font_size='11sp'
        )
        main_layout.add_widget(self.status_label)
        
        # Variables para búsqueda
        self.todas_verduras = []
        self.verduras_visibles = []
        self.checkboxes = {}
        
        # Cargar lista al iniciar
        Clock.schedule_once(lambda dt: self.cargar_lista_archivos(), 1)
        
        return main_layout
    
    def mostrar_config(self, instance):
        """Muestra popup de configuración"""
        popup = ConfigPopup(self.ip_pc, self.actualizar_ip)
        popup.open()
    
    def actualizar_ip(self, nueva_ip):
        """Actualiza la IP del PC"""
        self.ip_pc = nueva_ip.strip()
        self.ip_label.text = f"PC: {self.ip_pc}"
        self.actualizar_status("IP actualizada - Cargando catálogo...")
        self.cargar_lista_archivos()
    
    def actualizar_status(self, mensaje):
        """Actualiza el label de estado"""
        self.status_label.text = mensaje
    
    def actualizar_contador(self):
        """Actualiza el contador de selección"""
        seleccionados = sum(1 for check in self.checkboxes.values() if check.active)
        total = len(self.checkboxes)
        self.contador_label.text = f"Seleccionadas: {seleccionados}/{total}"
    
    def buscar_verduras(self, instance, texto):
        """Filtra la lista de verduras según búsqueda"""
        if not hasattr(self, 'todas_verduras'):
            return
            
        texto = texto.lower().strip()
        if not texto:
            # Mostrar todas
            self.verduras_visibles = self.todas_verduras.copy()
        else:
            # Filtrar
            self.verduras_visibles = [v for v in self.todas_verduras if texto in v.lower()]
        
        self.mostrar_lista_filtrada()
    
    def limpiar_busqueda(self, instance):
        """Limpia la búsqueda"""
        self.search_input.text = ""
        if hasattr(self, 'todas_verduras'):
            self.verduras_visibles = self.todas_verduras.copy()
            self.mostrar_lista_filtrada()
    
    def mostrar_lista_filtrada(self):
        """Muestra la lista filtrada de verduras con imágenes en grid"""
        self.grid_verduras.clear_widgets()
        
        for verdura_nombre in self.verduras_visibles:
            # ===== CELDA (FloatLayout) =====
            celda = FloatLayout(size_hint_y=None, height=220)
            
            # Imagen
            imagen = AsyncImage(
                source=f"http://{self.ip_pc}:5000/miniatura/{verdura_nombre}.png",
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 0.77),
                pos_hint={"x": 0, "top": 1}
            )
            celda.add_widget(imagen)
            
            # CheckBox
            checkbox = CheckBox(
                size_hint=(None, None),
                size=(32, 32),
                pos_hint={"center_x": 0.5, "y": 100},
                active=False
            )
            checkbox.bind(active=lambda inst, val, v=verdura_nombre: self.actualizar_contador())
            celda.add_widget(checkbox)
            
            # Nombre
            nombre = Label(
                text=verdura_nombre,
                size_hint=(1, None),
                height=40,
                pos_hint={"x": 0, "y": 0},
                halign="center",
                valign="middle",
                font_size="12sp",
                bold=True,
                color=(0.2, 0.5, 0.2, 1)
            )
            nombre.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            celda.add_widget(nombre)
            
            # Guardar referencia al checkbox
            self.checkboxes[verdura_nombre] = checkbox
            
            # Agregar celda al grid
            self.grid_verduras.add_widget(celda)
        
        self.actualizar_contador()
    
    def cargar_lista_archivos(self, instance=None):
        """Carga lista de verduras desde el PC"""
        self.actualizar_status("🔄 Cargando catálogo...")
        
        threading.Thread(target=self._cargar_lista_thread, daemon=True).start()
    
    def _cargar_lista_thread(self):
        """Hilo para cargar lista"""
        try:
            url = f"http://{self.ip_pc}:5000/archivos"
            
            def on_success(req, result):
                Clock.schedule_once(lambda dt: self._mostrar_verduras_ui(result))
            
            def on_error(req, error):
                Clock.schedule_once(lambda dt: self._error_ui("No se pudo conectar al PC"))
            
            UrlRequest(
                url,
                on_success=on_success,
                on_error=on_error,
                on_failure=on_error,
                timeout=10
            )
        except Exception as e:
            Clock.schedule_once(lambda dt: self._error_ui(f"Error: {str(e)}"))
    
    def _mostrar_verduras_ui(self, resultado):
        """Muestra verduras en UI"""
        if "archivos" in resultado and resultado["archivos"]:
            # Extraer solo los nombres de los archivos
            self.todas_verduras = sorted([doc["nombre"] for doc in resultado["archivos"]])
            self.verduras_visibles = self.todas_verduras.copy()
            self.mostrar_lista_filtrada()
            self.actualizar_status(f"✅ {len(self.todas_verduras)} verduras cargadas")
        else:
            self._error_ui("No hay archivos en el PC")
    
    def _error_ui(self, mensaje):
        """Muestra error en UI"""
        self.actualizar_status(f"❌ {mensaje}")
        self.grid_verduras.clear_widgets()
        error_label = Label(
            text=f"Error de conexión:\n{mensaje}\n\nVerifica:\n• IP correcta\n• Servidor activo\n• Misma red WiFi",
            size_hint_y=None,
            height=120,
            color=(0.8, 0.2, 0.2, 1),
            font_size='12sp'
        )
        self.grid_verduras.add_widget(error_label)
    
    def enviar_a_pc(self, instance):
        """Envía verduras seleccionadas al PC"""
        if not hasattr(self, 'checkboxes') or not self.checkboxes:
            self.mostrar_popup("Error", "Primero carga el catálogo")
            return
        
        seleccionados = [nombre for nombre, check in self.checkboxes.items() if check.active]
        
        if not seleccionados:
            self.mostrar_popup("Atención", "Selecciona al menos una verdura")
            return
        
        self.actualizar_status(f"📤 Enviando {len(seleccionados)} verduras...")
        
        threading.Thread(target=self._enviar_thread, args=(seleccionados,), daemon=True).start()
    
    def _enviar_thread(self, seleccionados):
        """Hilo para enviar verduras"""
        try:
            url = f"http://{self.ip_pc}:5000/combinar"
            datos = json.dumps({"archivos": seleccionados})
            
            def on_success(req, result):
                Clock.schedule_once(lambda dt: self._procesar_respuesta(result))
            
            def on_error(req, error):
                Clock.schedule_once(lambda dt: self.mostrar_popup("Error", "No se pudo conectar al PC"))
            
            UrlRequest(
                url,
                req_body=datos,
                req_headers={'Content-Type': 'application/json'},
                on_success=on_success,
                on_error=on_error,
                timeout=30
            )
        except Exception as e:
            Clock.schedule_once(lambda dt: self.mostrar_popup("Error", f"Error: {str(e)}"))
    
    def _procesar_respuesta(self, resultado):
        """Procesa respuesta del servidor"""
        if "job_id" in resultado:
            self.job_id = resultado["job_id"]
            self.actualizar_status("🔄 Generando catálogo...")
            # Iniciar seguimiento
            Clock.schedule_once(lambda dt: self._verificar_progreso(), 3)
        else:
            self.mostrar_popup("Error", resultado.get("error", "Error desconocido"))
    
    def _verificar_progreso(self):
        """Verifica progreso"""
        if not self.job_id:
            return
        
        threading.Thread(target=self._verificar_thread, daemon=True).start()
    
    def _verificar_thread(self):
        """Hilo para verificar progreso"""
        try:
            url = f"http://{self.ip_pc}:5000/estado/{self.job_id}"
            
            def on_success(req, result):
                Clock.schedule_once(lambda dt: self._actualizar_progreso_ui(result))
            
            UrlRequest(url, on_success=on_success)
        except:
            pass
    
    def _actualizar_progreso_ui(self, resultado):
        """Actualiza UI con progreso"""
        status = resultado.get("status")
        
        if status == "processing":
            progreso = resultado.get("progreso", 0)
            self.actualizar_status(f"🔄 Generando catálogo... ({progreso}%)")
            Clock.schedule_once(lambda dt: self._verificar_progreso(), 2)
        elif status == "done":
            self.actualizar_status("✅ Catálogo generado exitosamente!")
            self.mostrar_popup("Éxito", "🌱 Catálogo de verduras generado y guardado en tu PC")
        elif status == "error":
            self.actualizar_status("❌ Error al generar catálogo")
            self.mostrar_popup("Error", resultado.get("error", "Error desconocido"))
    
    def mostrar_popup(self, titulo, mensaje):
        """Muestra popup de mensaje"""
        popup = Popup(
            title=titulo,
            content=Label(text=mensaje),
            size_hint=(0.7, 0.4)
        )
        popup.open()


if __name__ == '__main__':
    CombinadorVerdurasApp().run()
