import PIL.Image
import customtkinter as ctk
from latticegeometrylib.Generator import LatticeGenerator as LatticeGeometryLib
from View import CellViewer, LatticeViewer
import webbrowser
import os
from tkinter import filedialog as fd
from typing import ( Callable, Tuple, List, Dict, Any, Union)

class Appearance:
    def __init__(self,
                 width: int = 500,
                 height: int = 720,
                 spacing: int = 10,
                 radius: int = 5,
                 text_light: str = "#979DA2",
                 text_dark: str = 'black',
                 selected_color: str = '#B84245',
                 fg_dark: str = "#979DA2",
                 fg_light: str = '#F0F0F0'):
        self.spacing: int = spacing
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self.text_light = text_light
        self.text_dark = text_dark
        self.selected_color = selected_color
        self.fg_dark = fg_dark
        self.fg_light = fg_light


class Button( ctk.CTkButton ):
    def __init__( self, master: Any,
                  width: int,
                  height: int,
                  appearance: Appearance,
                  text:str,
                  command: Callable,
                  row: Tuple[int,int]=(0, 1),
                  column: Tuple[int,int]=(0, 1),
                  ):
        ctk.CTkButton.__init__(self,
                               master=master,
                               text=text,
                               command=command,
                               fg_color=appearance.fg_dark,
                               text_color='white',
                               width=width * appearance.spacing,
                               height=height*appearance.spacing,
                               hover_color= appearance.selected_color)
        self.grid(row=row[0], rowspan=row[1], column=column[0], columnspan=column[1], sticky='w', padx=appearance.spacing, pady=appearance.spacing)
        self.enabled = True

    def toggle(self, value: bool):
        if value:
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)


class CreateButton(Button):
    def __init__(self, master, command: Callable, a: Appearance, row: int, column:int, text="Erstellen" ):
        Button.__init__(self, master=master, text=text, command=command, appearance=a, width=14, height=3, row=(row,1),
                        column=(column,1) )


class DeleteButton(Button):
    def __init__(self, master, command: Callable, a: Appearance, row: int, column:int, text="Löschen" ):
        Button.__init__(self, master=master, text=text, command=command, appearance=a, width=14, height=3, row=(row,1),
                        column=(column,1) )


class SaveButton(Button):
    def __init__(self, master, command: Callable, a: Appearance, row: int, column:int, text="Speichern"):
        Button.__init__(self, master=master, text=text, command=command, appearance=a, width=14, height=3,row=(row,1),
                        column=(column,1) )

class ButtonBar:
    def __init__( self, master, commands: Dict[ str, Callable ], appearance: Appearance, row: int ):
        self.create = CreateButton( master=master, command= commands["Erstellen"], a=appearance,row=row, column=0 )
        self.delete = DeleteButton( master=master, command= commands["Löschen"], a=appearance,row=row, column=1 )
        self.export = SaveButton( master=master, command= commands["Speichern"], a=appearance,row=row, column=2 )

    def toggle(self, name: str, value: bool) -> None:
        if name == "Erstellen":
            self.create.toggle( value )
        elif name == "Löschen":
            self.delete.toggle( value )
        elif name == "Speichern":
            self.export.toggle( value )


class ImageWindow( ctk.CTkFrame ):
    def __init__(self,
                 master,
                 path: Union[ str, List[ str ] ],
                 width: int,
                 height: int,
                 row: Tuple[ int, int ],
                 column: Tuple[ int, int ],
                 appearance: Appearance,
                 pad = 1):
        super().__init__( master=master,
                          width= width * appearance.spacing,
                          height= height*appearance.spacing,
                          corner_radius=appearance.radius,
                          border_width= 2,
                          border_color=appearance.fg_dark,
                          fg_color='white')

        self.grid( row=row[ 0 ], rowspan=row[ 1 ], column=column[ 0 ], columnspan=column[ 1 ], padx=appearance.spacing * pad,
                   pady=appearance.spacing * pad, sticky='w' )

        self.image = None
        self.current = None

        self.container = ctk.CTkLabel(
            master = self,
            width = (width - 2)* appearance.spacing,
            height= (height - 2) * appearance.spacing,
            fg_color='white',
            text=""
        )
        self.container.grid(row= 0, column=0,padx=appearance.spacing, pady=appearance.spacing)

        self.hint = ctk.CTkLabel(
            master=self,
            height=1*appearance.spacing,
            width=10*appearance.spacing,
            fg_color=appearance.fg_dark,
            text_color='white',
            text="Symbolbild",
            corner_radius=appearance.radius
        )
        self.hint.grid(row= 0, column=0,padx=appearance.spacing, pady=appearance.spacing, sticky='nw')

        def _image( filepath: str ) -> ctk.CTkImage:
            image = PIL.Image.open( filepath )
            w, h = image.size
            return ctk.CTkImage( light_image= image, size=( appearance.spacing * w // h * height, appearance.spacing * height )  )

        if type( path ) is list:
            self.image = [ _image( p ) for p in path ]
            self.container.configure( image = self.image[ 0 ] )
            self.current = 0
        elif type( path ) is str:
            self.image = _image( path )
            self.container.configure( image=self.image )

    def change(self) -> None:

        def _next():
            self.current += 1
            if self.current == len( self.image ):
                self.current = 0

        if not self.current is None:
            _next()
            self.container.configure(image=self.image[self.current])


class StepTitle( ctk.CTkLabel ):
    def __init__( self, master, text: str, width: int, appearance: Appearance, row: Tuple[ int, int], column: Tuple[ int, int ], pad = 1):
        super().__init__( master= master, width=width*appearance.spacing, height=appearance.spacing,
                          corner_radius=appearance.radius, fg_color='white', text=text, anchor='w',
                          text_color=appearance.fg_dark )

        self.activated = False
        self.appearance = appearance
        self.grid( row= row[ 0 ], rowspan= row[ 1 ], column = column[ 0 ], columnspan = column[ 1 ],
                   padx = appearance.spacing * pad, pady = appearance.spacing * pad )

    def toggle(self, value: bool):
        if value:
            self.configure(text_color=self.appearance.selected_color)
        else:
            self.configure(text_color=self.appearance.fg_dark)


class LatticeGeometryUI(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)

        self.appearance = Appearance()

        self.geometry( str(self.appearance.width + 2* self.appearance.spacing)+'x'+str(self.appearance.height + 2* self.appearance.spacing) )
        self.title("LatticeGeometryUI")
        self.iconbitmap("./images/iwf.ico")
        self.protocol("WM_DELETE_WINDOW", self.quit_program)
        self.configure( fg_color="#D0D0D0")
        self.lib = LatticeGeometryLib()
        self.resizable(False, False)
        self.toolbar_frame = ctk.CTkFrame(
            master = self,
            fg_color=self.appearance.fg_dark,
            corner_radius=self.appearance.radius,
            border_color=self.appearance.fg_dark
        )

        self.toolbar_spacing = ctk.CTkLabel(
            master = self.toolbar_frame,
            text='',
            height=0,
            width=self.appearance.width,
            fg_color=self.appearance.fg_dark
        )

        self.toolbar_spacing.pack()

        self.toolbar = ctk.CTkSegmentedButton(
            master = self.toolbar_frame,
            width=self.appearance.width,
            height=self.appearance.spacing,
            values=['Hilfe', 'Beenden'],
            corner_radius=self.appearance.radius,
            fg_color=self.appearance.fg_dark,
            command=self.toolbar_events,
            selected_color=self.appearance.selected_color,
            selected_hover_color=self.appearance.selected_color,
            unselected_hover_color=self.appearance.selected_color
        )
        self.toolbar.pack(anchor='w', padx=self.appearance.spacing)
        self.toolbar_frame.grid(row=0, column=0, padx=self.appearance.spacing, sticky='w')

        self.workflow_tabview = ctk.CTkTabview(master=self,
                                                  width=self.appearance.width,
                                                  height=self.appearance.spacing*57,
                                                  corner_radius=self.appearance.radius,
                                                  border_width=2,
                                                  border_color=self.appearance.fg_dark,
                                                  fg_color=self.appearance.fg_light,
                                                  segmented_button_selected_hover_color=self.appearance.selected_color,
                                                  segmented_button_selected_color=self.appearance.selected_color

        )

        self.workflow_tabview.grid(row=1, column=0, padx= self.appearance.spacing, pady=self.appearance.spacing)

        self.workflow_tabview.add("    1 >    ")

        self.initial_model_label = StepTitle(
            master = self.workflow_tabview.tab("    1 >    "),
            text = " Einladen des Modells",
            width = 46,
            appearance = self.appearance,
            row = ( 0, 1 ),
            column= ( 0, 3 )
        )

        self.initial_model_selectType = ctk.CTkOptionMenu(master=self.workflow_tabview.tab("    1 >    "),
                                                          width=self.appearance.spacing*14,
                                                          height=3 * self.appearance.spacing,
                                                          values= ["Vollkörper", "Schale"],
                                                          button_color=self.appearance.fg_dark,
                                                          dropdown_fg_color=self.appearance.fg_dark,
                                                          text_color="white",
                                                          fg_color=self.appearance.fg_dark,
                                                          corner_radius=self.appearance.radius,
                                                          command=self.onSelectModel,
                                                          button_hover_color=self.appearance.selected_color,
                                                          dropdown_hover_color=self.appearance.selected_color)

        self.initial_model_selectType.grid(row=2, column=0, sticky="w", padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.initial_model_import_button = CreateButton(
            master = self.workflow_tabview.tab("    1 >    "),
            command=self.onImportModel,
            a=self.appearance,
            column=1,
            row=2,
            text = "Datei auswählen"
        )

        self.initial_model_delete_button = DeleteButton(
            master=self.workflow_tabview.tab("    1 >    "),
            command=self.onDeleteModel,
            row=2,
            column=2,
            a=self.appearance
        )

        self.initial_model_shell_image = ImageWindow(
            master=self.workflow_tabview.tab("    1 >    "),
            path=[ "images/represent_model.png", "images/represent_shell.png" ],
            width=46,
            height =10,
            row=(1,1),
            column=(0,3),
            appearance=self.appearance
        )

        self.shell_model_label = StepTitle(
            master = self.workflow_tabview.tab("    1 >    "),
            text = " Erstellung des Schalenmodells aus dem Vollkörper",
            width = 46,
            appearance = self.appearance,
            row = ( 4, 1 ),
            column= ( 0, 3 )
        )

        self.shell_thickness_frame = ctk.CTkFrame(master = self.workflow_tabview.tab("    1 >    "),
                                                  border_color=self.appearance.fg_dark,
                                                  fg_color = self.appearance.fg_dark,
                                                  border_width=2,
                                                  corner_radius=self.appearance.radius)
        self.shell_thickness_frame.grid(row=5, column=0, columnspan=3, padx=self.appearance.spacing, pady = self.appearance.spacing, sticky='w')

        self.shell_thickness_frame_label = ctk.CTkLabel(master = self.shell_thickness_frame,
                                                 width =  44 * self.appearance.spacing,
                                                 height= 1 * self.appearance.spacing,
                                                 text=" Wandstärken in mm",
                                                 fg_color=self.appearance.fg_dark,
                                                 anchor='w',
                                                 text_color="white"
        )

        self.shell_thickness_frame_label.grid(row=0, column=0, columnspan=4, padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.shell_thickness_internal_label = ctk.CTkLabel(master = self.shell_thickness_frame,
                                                 width =  21 * self.appearance.spacing,
                                                 height= 3 * self.appearance.spacing,
                                                 text=" innen:",
                                                 fg_color="#F0F0F0",
                                                 anchor='w',
                                                 text_color='#000000',
                                                 corner_radius=self.appearance.radius
        )

        self.shell_thickness_internal_label.grid(row=1, column=0, columnspan=2, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='w')

        self.shell_thickness_external_label = ctk.CTkLabel(master = self.shell_thickness_frame,
                                                 width =  21 * self.appearance.spacing,
                                                 height= 3 * self.appearance.spacing,
                                                 text=" außen:",
                                                 fg_color="#F0F0F0",
                                                 anchor='w',
                                                 text_color='#000000',
                                                 corner_radius=self.appearance.radius
        )

        self.shell_thickness_external_label.grid(row=1, column=2, columnspan=2, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='w')

        self.shell_thickness_internal_entry = ctk.CTkEntry( master=self.shell_thickness_frame,
                                                            fg_color="white",
                                                            bg_color='#F0F0F0',
                                                            text_color='#000000',
                                                            placeholder_text="0.",
                                                            corner_radius=self.appearance.radius,
                                                            border_width=2,
                                                            width=6*self.appearance.spacing,
                                                            textvariable=ctk.StringVar(value=str(0.)),
                                                            height=2*self.appearance.spacing )
        self.shell_thickness_internal_entry.grid(row=1, column=1, sticky='e', padx=1.5*self.appearance.spacing, pady=self.appearance.spacing)

        self.shell_thickness_external_entry = ctk.CTkEntry( master=self.shell_thickness_frame,
                                                            fg_color="white",
                                                            bg_color='#F0F0F0',
                                                            text_color='#000000',
                                                            placeholder_text="0.",
                                                            textvariable=ctk.StringVar(value=str(0.)),
                                                            corner_radius=self.appearance.radius,
                                                            border_width=2,
                                                             width=6*self.appearance.spacing,
                                                            height=2*self.appearance.spacing )
        self.shell_thickness_external_entry.grid(row=1, column=3, sticky='e', padx=1.5*self.appearance.spacing, pady=self.appearance.spacing)

        self.shell_button_bar = ButtonBar(
            master=self.workflow_tabview.tab("    1 >    "),
            commands={ "Erstellen" : self.onCreateShell,
                       "Löschen": self.onDeleteShell,
                       "Speichern": self.onExportShell },
            appearance=self.appearance,
            row=6
        )

        self.workflow_tabview.add("    2 >    ")

        self.cell_initialize_frame_label = StepTitle(
            master = self.workflow_tabview.tab("    2 >    "),
            text = " Initialisierung der Elementarzelle",
            width = 46,
            appearance = self.appearance,
            row = ( 0, 1 ),
            column= ( 0, 3 )
        )

        self.cell_initialize_represent_frame = ctk.CTkFrame(master=self.workflow_tabview.tab("    2 >    "),
                                                        corner_radius=self.appearance.radius,
                                                        border_color=self.appearance.fg_dark,
                                                        fg_color="white",
                                                        border_width=2,
                                                        width=44 * self.appearance.spacing,
                                                        height=20 * self.appearance.spacing)

        self.cell_initialize_represent_frame.grid(row=1, column=0, columnspan=3, padx=self.appearance.spacing,
                                              pady=self.appearance.spacing)

        self.cell_initialize_model_represent_label = ctk.CTkLabel(master=self.cell_initialize_represent_frame,
                                                              width=self.appearance.spacing * 21,
                                                              height=0 * self.appearance.spacing,
                                                              text="")
        self.cell_initialize_model_represent_label.grid(row=0, column=0, padx=self.appearance.spacing,
                                                    pady=self.appearance.spacing)

        self.cell_initialize_label_spacing = ctk.CTkLabel(
            master = self.cell_initialize_represent_frame,
            width = 44 * self.appearance.spacing,
            height = 0,
            text=""
        )
        self.cell_initialize_label_spacing.grid(row=0, column=0, columnspan=2, padx=self.appearance.spacing,
                                                     pady=self.appearance.spacing)

        self.cell_initialize_canvas = LatticeViewer(widget=self.cell_initialize_represent_frame,
                                                    width=20 * self.appearance.spacing / self.appearance.width,
                                                    height=20 * self.appearance.spacing / self.appearance.height,
                                                    winwidth=self.winfo_width(),
                                                    winheight=self.winfo_height())
        self.cell_initialize_canvas.get_tk_widget().grid(row=0, column=0, padx=self.appearance.spacing,
                                                     pady=self.appearance.spacing)

        self.cell_initialize_previewtype = ctk.CTkLabel(
            master=self.cell_initialize_represent_frame,
            height=1*self.appearance.spacing,
            width=10*self.appearance.spacing,
            fg_color=self.appearance.selected_color,
            text_color='white',
            text="Vorschau",
            corner_radius=self.appearance.radius
        )
        self.cell_initialize_previewtype.grid(row= 0, column=0,padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='nw')

        self.cell_initialize_sizes_frame = ctk.CTkFrame(master = self.workflow_tabview.tab("    2 >    "),
                                                  border_color=self.appearance.fg_dark,
                                                  fg_color = self.appearance.fg_dark,
                                                  border_width=2,
                                                  corner_radius=self.appearance.radius)
        self.cell_initialize_sizes_frame.grid(row=2, column=0, columnspan=3, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='w')

        self.cell_initialize_sizes_frame_label_dir = ctk.CTkLabel(master = self.cell_initialize_sizes_frame,
                                                 width =  30 * self.appearance.spacing,
                                                 height= 1 * self.appearance.spacing,
                                                 text=" Grundabmaße in mm in",
                                                 fg_color=self.appearance.fg_dark,
                                                 anchor='w',
                                                 text_color="white"
        )
        self.cell_initialize_sizes_frame_label_dir.grid(row=0, column=0, columnspan=2, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='w')

        self.cell_initialize_sizes_frame_label_strict = ctk.CTkLabel(master = self.cell_initialize_sizes_frame,
                                                 width =  12 * self.appearance.spacing,
                                                 height= 1 * self.appearance.spacing,
                                                 text=" genau",
                                                 fg_color=self.appearance.fg_dark,
                                                 anchor='w',
                                                 text_color="white"
        )

        self.cell_initialize_sizes_frame_label_strict.grid(row=0, column=2, columnspan=2, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='e')

        self.cell_initialize_sizes_dirx_label = ctk.CTkLabel(master = self.cell_initialize_sizes_frame,
                                                 width =  44 * self.appearance.spacing,
                                                 height= 3 * self.appearance.spacing,
                                                 text=" x-Richtung:",
                                                 fg_color="#F0F0F0",
                                                 anchor='w',
                                                 text_color='#000000',
                                                 corner_radius=self.appearance.radius
        )
        self.cell_initialize_sizes_dirx_label.grid(row=1, column=0, columnspan=4, padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.cell_initialize_sizes_diry_label = ctk.CTkLabel(master = self.cell_initialize_sizes_frame,
                                                 width =  44 * self.appearance.spacing,
                                                 height= 3 * self.appearance.spacing,
                                                 text=" y-Richtung:",
                                                 fg_color="#F0F0F0",
                                                 anchor='w',
                                                 text_color='#000000',
                                                 corner_radius=self.appearance.radius
        )
        self.cell_initialize_sizes_diry_label.grid(row=2, column=0, columnspan=4, padx=self.appearance.spacing)

        self.cell_initialize_sizes_dirz_label = ctk.CTkLabel(master = self.cell_initialize_sizes_frame,
                                                 width =  44 * self.appearance.spacing,
                                                 height= 3 * self.appearance.spacing,
                                                 text=" z-Richtung:",
                                                 fg_color="#F0F0F0",
                                                 anchor='w',
                                                 text_color='#000000',
                                                 corner_radius=self.appearance.radius
        )
        self.cell_initialize_sizes_dirz_label.grid(row=3, column=0, columnspan=4, padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.cell_initialize_sizes_dirx_entry = ctk.CTkEntry(master=self.cell_initialize_sizes_frame,
                                                            fg_color="white",
                                                            bg_color='#F0F0F0',
                                                            text_color='#000000',
                                                            placeholder_text="10.",
                                                            corner_radius=self.appearance.radius,
                                                            border_width=2,
                                                            width=16*self.appearance.spacing,
                                                            textvariable=ctk.StringVar(value=str(10.)),
                                                            height=2*self.appearance.spacing
        )
        self.cell_initialize_sizes_dirx_entry.grid(row=1, column=1, padx=1.5*self.appearance.spacing, sticky='e')

        self.cell_initialize_sizes_diry_entry = ctk.CTkEntry(master=self.cell_initialize_sizes_frame,
                                                            fg_color="white",
                                                            bg_color='#F0F0F0',
                                                            text_color='#000000',
                                                            placeholder_text="10.",
                                                            corner_radius=self.appearance.radius,
                                                            border_width=2,
                                                            width=16*self.appearance.spacing,
                                                            textvariable=ctk.StringVar(value=str(10.)),
                                                            height=2*self.appearance.spacing
        )
        self.cell_initialize_sizes_diry_entry.grid(row=2, column=1, padx=1.5*self.appearance.spacing, sticky='e')

        self.cell_initialize_sizes_dirz_entry = ctk.CTkEntry(master=self.cell_initialize_sizes_frame,
                                                            fg_color="white",
                                                            bg_color='#F0F0F0',
                                                            text_color='#000000',
                                                            placeholder_text="10.",
                                                            corner_radius=self.appearance.radius,
                                                            border_width=2,
                                                            width=16*self.appearance.spacing,
                                                            textvariable=ctk.StringVar(value=str(10.)),
                                                            height=2*self.appearance.spacing
        )
        self.cell_initialize_sizes_dirz_entry.grid(row=3, column=1, padx=1.5*self.appearance.spacing, sticky='e')

        self.cell_config_sizes_dirx_control = ctk.CTkSwitch( master=self.cell_initialize_sizes_frame,
                                                               height =2*self.appearance.spacing,
                                                               width=4*self.appearance.spacing,
                                                               switch_width=4*self.appearance.spacing,
                                                               switch_height=2*self.appearance.spacing,
                                                               corner_radius=self.appearance.radius,
                                                               border_color=self.appearance.fg_dark,
                                                               border_width=2,
                                                               text='',
                                                               fg_color=self.appearance.fg_dark,
                                                               bg_color='#F0F0F0',
                                                               progress_color=self.appearance.selected_color)
        self.cell_config_sizes_dirx_control.grid(row=1, column=2, sticky='w', padx=self.appearance.spacing)

        self.cell_config_sizes_diry_control = ctk.CTkSwitch( master=self.cell_initialize_sizes_frame,
                                                               height =2*self.appearance.spacing,
                                                               width=4*self.appearance.spacing,
                                                               switch_width=4*self.appearance.spacing,
                                                               switch_height=2*self.appearance.spacing,
                                                               corner_radius=self.appearance.radius,
                                                               border_color=self.appearance.fg_dark,
                                                               border_width=2,
                                                               text='',
                                                               fg_color=self.appearance.fg_dark,
                                                               bg_color='#F0F0F0',
                                                               progress_color=self.appearance.selected_color)
        self.cell_config_sizes_diry_control.grid(row=2, column=2, sticky='w', padx=self.appearance.spacing)

        self.cell_config_sizes_dirz_control = ctk.CTkSwitch( master=self.cell_initialize_sizes_frame,
                                                               height =2*self.appearance.spacing,
                                                               width=4*self.appearance.spacing,
                                                               switch_width=4*self.appearance.spacing,
                                                               switch_height=2*self.appearance.spacing,
                                                               corner_radius=self.appearance.radius,
                                                               border_color=self.appearance.fg_dark,
                                                               border_width=2,
                                                               text='',
                                                               fg_color=self.appearance.fg_dark,
                                                               bg_color='#F0F0F0',
                                                               progress_color=self.appearance.selected_color)
        self.cell_config_sizes_dirz_control.grid(row=3, column=2, sticky='w', padx=self.appearance.spacing)

        self.cell_config_sizes_initialize_button = ctk.CTkButton(master=self.workflow_tabview.tab("    2 >    "),
                                                                 width=46*self.appearance.spacing,
                                                                 height=3 * self.appearance.spacing,
                                                                 text="Elementarzelle initialisieren",
                                                                 fg_color=self.appearance.fg_dark,
                                                                 text_color="white",
                                                                 corner_radius=self.appearance.radius,
                                                                 command=self.onInitializeCell,
                                                                 hover_color=self.appearance.selected_color
        )

        self.cell_config_sizes_initialize_button.grid(row=3, column=0, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='w')

        self.workflow_tabview.add("    3 >    ")

        self.cell_config_frame_label = StepTitle(
            master = self.workflow_tabview.tab("    3 >    "),
            text = " Konfiguration der Elementarzelle",
            width = 46,
            appearance = self.appearance,
            row = ( 0, 1 ),
            column= ( 0, 3 )
        )

        self.cell_config_represent_frame = ctk.CTkFrame(master=self.workflow_tabview.tab("    3 >    "),
                                                    corner_radius=self.appearance.radius,
                                                    border_color=self.appearance.fg_dark,
                                                    fg_color="white",
                                                    border_width=2,
                                                    width=44* self.appearance.spacing,
                                                    height=20*self.appearance.spacing)

        self.cell_config_represent_frame.grid(row=1, column=0, columnspan=3, padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.cell_config_previewtype = ctk.CTkLabel(
            master=self.cell_config_represent_frame,
            height=1*self.appearance.spacing,
            width=10*self.appearance.spacing,
            fg_color=self.appearance.selected_color,
            text_color='white',
            text="Vorschau",
            corner_radius=self.appearance.radius
        )
        self.cell_config_previewtype.grid(row= 0, column=0,padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='nw')


        self.cell_config_model_represent_label = ctk.CTkLabel(master=self.cell_config_represent_frame,
                                                          width=self.appearance.spacing * 21,
                                                          height=0 * self.appearance.spacing,
                                                          text="")
        self.cell_config_model_represent_label.grid(row=0, column=0, padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.cell_config_canvas = CellViewer( widget=self.cell_config_represent_frame,
                                              width= 21 * self.appearance.spacing / self.appearance.width,
                                              height=21 * self.appearance.spacing / self.appearance.height,
                                              winwidth = self.winfo_width(),
                                              winheight = self.winfo_height())
        self.cell_config_canvas.get_tk_widget().grid(row=0, column=0, padx=self.appearance.spacing, pady=self.appearance.spacing)

        self.cell_config_generic_entrybox_frame = ctk.CTkFrame(
            master = self.cell_config_represent_frame,
            border_color=self.appearance.fg_light,
            fg_color = self.appearance.fg_light,
            border_width=0,
            corner_radius=self.appearance.radius)

        self.cell_config_generic_entrybox_frame.grid(row=0, column=1, columnspan=1,padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='w')

        self.cell_config_editor_label = ctk.CTkLabel( master = self.cell_config_generic_entrybox_frame,
                                                 width = 20 * self.appearance.spacing,
                                                 height=self.appearance.spacing,
                                                 text="Editor",
                                                 fg_color="white",
                                                 anchor='w',
                                                 text_color=self.appearance.fg_dark,
                                                 corner_radius=self.appearance.radius)

        self.cell_config_editor_label.grid(row=0, column=0, columnspan=2,padx=self.appearance.spacing*0.5, pady=self.appearance.spacing*0.5, sticky='w')

        self.cell_config_options_button = ctk.CTkSegmentedButton(
            master=self.cell_config_generic_entrybox_frame,
            width=self.appearance.spacing * 20,
            height=self.appearance.spacing * 2,
            values=['⌫', '⟳', '⎙' ],
            corner_radius=self.appearance.radius,
            fg_color=self.appearance.fg_dark,
            command=self.onSelectOption,
            selected_color=self.appearance.selected_color,
            selected_hover_color=self.appearance.selected_color,
            unselected_hover_color=self.appearance.selected_color,
            dynamic_resizing=False
        )

        self.cell_config_options_button.grid( row=1, column=0, columnspan=2, padx=0.5*self.appearance.spacing, pady=0.5*self.appearance.spacing, sticky='w' )

        self.cell_config_log = ctk.CTkTextbox(
            master = self.cell_config_generic_entrybox_frame,
            width=self.appearance.spacing *20,
            height=self.appearance.spacing *20,
            corner_radius=self.appearance.radius,
            border_width=1,
            border_color="#D0D0D0",
            fg_color=self.appearance.fg_light,
            wrap='none',
            font=ctk.CTkFont( family="Consolas" )
        )
        self.cell_config_log.grid(row=2,column=0,  columnspan=2, padx=self.appearance.spacing*0.5, pady=self.appearance.spacing*0.5,sticky='e')

        self.cell_config_feature_type_select = ctk.CTkOptionMenu(
            master=self.cell_config_generic_entrybox_frame,
            width=self.appearance.spacing * 20,
            height=2 * self.appearance.spacing,
            values=["Punkt", "Strebe", "Fläche", "Aus Vorlage", "Variable", "Verrundung"],
            button_color=self.appearance.fg_dark,
            dropdown_fg_color=self.appearance.fg_dark,
            text_color="white",
            fg_color=self.appearance.fg_dark,
            corner_radius=self.appearance.radius,
            command=self.onSelectFeatureType,
            button_hover_color=self.appearance.selected_color,
            dropdown_hover_color=self.appearance.selected_color,
        )

        self.cell_config_feature_type_select.grid( row=3, column=0, columnspan=2, padx=0.5*self.appearance.spacing, pady = 0.5*self.appearance.spacing, sticky='w')

        self.cell_config_genericentry_entry = ctk.CTkEntry( master=self.cell_config_generic_entrybox_frame,
                                                            fg_color="white",
                                                            text_color='#000000',
                                                            placeholder_text="[ ]",
                                                            textvariable=ctk.StringVar(value="[0, {'diameter':0.}]"),
                                                            corner_radius=self.appearance.radius,
                                                            border_width=2,
                                                            width=17*self.appearance.spacing,
                                                            height=2*self.appearance.spacing)

        self.cell_config_genericentry_entry.grid(row=4, column=0, padx=0.5*self.appearance.spacing, pady=self.appearance.spacing*0.5, sticky='w')

        self.cell_config_genericentry_add_button = ctk.CTkButton(master=self.cell_config_generic_entrybox_frame,
                                                          width=2*self.appearance.spacing,
                                                          height=2 * self.appearance.spacing,
                                                          text="+",
                                                          fg_color=self.appearance.fg_dark,
                                                          text_color="white",
                                                          corner_radius=self.appearance.radius,
                                                          command=self.onAddFeatureEntry,
                                                          hover_color=self.appearance.selected_color
        )

        self.cell_config_genericentry_add_button.grid(row=4, column=1, pady= 0.5 * self.appearance.spacing, padx=0.5*self.appearance.spacing, sticky='e')

        self.cell_button_bar = ButtonBar(
            master=self.workflow_tabview.tab("    3 >    "),
            commands={ "Erstellen" : self.onCreateCell,
                       "Löschen": self.onDeleteCell,
                       "Speichern": self.onExportCell },
            appearance=self.appearance,
            row=3
        )

        self.workflow_tabview.add("    4 >    ")

        self.grid_frame_label = StepTitle(
            master = self.workflow_tabview.tab("    4 >    "),
            text = " Erstellung des Gitters aus der Elementarzelle",
            width = 46,
            appearance = self.appearance,
            row = ( 0, 1 ),
            column= ( 0, 3 )
        )

        self.grid_image = ImageWindow(
            master=self.workflow_tabview.tab("    4 >    "),
            path="images/represent_grid.png",
            width=46,
            height =10,
            row=(1,1),
            column=(0,3),
            appearance=self.appearance
        )

        self.grid_button_bar = ButtonBar(
            master=self.workflow_tabview.tab("    4 >    "),
            commands={ "Erstellen" : self.onCreateGrid,
                       "Löschen": self.onDeleteGrid,
                       "Speichern": self.onExportGrid },
            appearance=self.appearance,
            row=2
        )

        self.grid_intersect_spacing = ctk.CTkLabel( master = self.workflow_tabview.tab("    4 >    "),
                                                    fg_color='#F0F0F0',
                                                    text='',
                                                    height = 0
        )
        self.grid_intersect_spacing.grid(row=3, column=0, columnspan=3, pady=self.appearance.spacing)

        self.intersected_frame_label = StepTitle(
            master = self.workflow_tabview.tab("    4 >    "),
            text = " Überschneidung des Gitters mit dem Eingangsmodell",
            width = 46,
            appearance = self.appearance,
            row = ( 4, 1 ),
            column= ( 0, 3 )
        )

        self.intersected_image = ImageWindow(
            master=self.workflow_tabview.tab("    4 >    "),
            path="images/represent_intersected.png",
            width=46,
            height =10,
            row=(5,1),
            column=(0,3),
            appearance=self.appearance
        )

        self.intersected_button_bar = ButtonBar(
            master=self.workflow_tabview.tab("    4 >    "),
            commands={ "Erstellen" : self.onCreateGridIntersected,
                       "Löschen": self.onDeleteGridIntersected,
                       "Speichern": self.onExportGridIntersected },
            appearance=self.appearance,
            row=6
        )

        self.workflow_tabview.add("    5    ")

        self.unified_frame_label = StepTitle(
            master = self.workflow_tabview.tab("    5    "),
            text = " Vereinigung des Gitters mit der Schalengeometrie",
            width = 46,
            appearance = self.appearance,
            row = ( 0, 1 ),
            column= ( 0, 3 )
        )

        self.unified_image = ImageWindow(
            master=self.workflow_tabview.tab("    5    "),
            path="images/represent_unified.png",
            width=46,
            height =10,
            row=(1,1),
            column=(0,3),
            appearance=self.appearance
        )

        self.unified_button_bar = ButtonBar(
            master=self.workflow_tabview.tab("    5    "),
            commands={ "Erstellen" : self.onCreateUnified,
                       "Löschen": self.onDeleteUnified,
                       "Speichern": self.onExportUnified },
            appearance=self.appearance,
            row=2
        )

        self.progress_bar = ctk.CTkProgressBar( master= self,
                                                mode='indeterminate',
                                                indeterminate_speed=2,
                                                width=self.appearance.width,
                                                height=self.appearance.spacing,
                                                corner_radius=self.appearance.radius,
                                                progress_color=self.appearance.fg_dark
        )

        self.progress_bar.grid(row=4, column=0, padx=self.appearance.spacing)

        self.message_box_entry = ctk.CTkTextbox(master=self,
                                                width=self.appearance.width,
                                                height=8*self.appearance.spacing,
                                                fg_color="#F0F0F0",
                                                border_color=self.appearance.fg_dark,
                                                border_width=2,
                                                corner_radius=self.appearance.radius,
                                                state='disabled',
                                                wrap='none')
        self.message_box_entry.grid(row=5, column=0, padx=self.appearance.spacing, pady=self.appearance.spacing, sticky='s')

        self.notify("[info]", "Programm gestartet.")

    def quit_program(self):
        self.quit()

    def help(self):
        webbrowser.open(url="https://github.com/sxhulzenstein/LatticeGeometryUI")

    def toolbar_events(self, value: str):
        if value == "Beenden":
            self.quit_program()
        if value == "Hilfe":
            self.help()

    def progress(self, flag: bool = False):
        if flag:
            self.progress_bar.configure(progress_color=self.appearance.selected_color)
            self.progress_bar.start()
        else:
            self.progress_bar.configure(progress_color=self.appearance.fg_dark)
            self.progress_bar.stop()

    def notify(self, type: str, message: str) -> None:
        self.message_box_entry.configure(state='normal')
        self.message_box_entry.insert(ctk.END, type+'\t'+message+'\n')
        self.message_box_entry.configure(state='disabled')

    def onSelectModel(self, choice: str = ''):
        if choice == "Schale":
            self.initial_model_shell_image.change()
            self.notify("[info]","Eingangsmodell ist als Schalenobjekt deklariert.")
        elif choice == "Vollkörper":
            self.initial_model_shell_image.change()
            self.notify("[info]","Eingangsmodell ist als Vollkörper deklariert.")

    def onImportModel(self):
        filetype = (
            ('STEP-Datei', '.STEP'),
            ('STEP-Datei', '.STP')
        )
        self.progress(True)

        filename = fd.askopenfile(title="Eingangsmodell auswählen", initialdir='C:/',filetypes=filetype)

        filepath = os.path.abspath(filename.name)

        self.notify("[info]",f"Pfad: {filepath} ausgewählt.")

        if self.initial_model_selectType.get() == "Vollkörper":
            try:
                self.lib.import_initial_model(filepath)
                self.notify("[info]","Vollkörper erfolgreich eingeladen.")
                self.initial_model_label.toggle(True)
                self.progress()
            except:
                self.bell()
                self.notify("[error]","Vollkörper konnte nicht eingelesen werden.")
                self.progress()
        elif self.initial_model_selectType.get() == "Schale":
            try:
                self.lib.import_initial_model(filepath)
                self.notify("[info]","Schalenobjekt erfolgreich eingeladen.")
                self.shell_model_label.toggle(True)
                self.shell_button_bar.toggle( "Erstellen", False)
                self.shell_thickness_internal_entry.configure(state=ctk.DISABLED)
                self.shell_thickness_external_entry.configure(state=ctk.DISABLED)
                self.progress()
            except:
                self.bell()
                self.notify("[error]","Schalenobjekt konnte nicht eingelesen werden.")
                self.progress()
        self.progress()

    def onExportShell(self):
        filetype = (
            ('STL-Datei', '.stl'),
            ('STL-Datei', '.STL'),
            ('STEP-Datei', '.STEP')
        )

        filename = fd.asksaveasfile(confirmoverwrite=True, filetypes=filetype,initialdir='C:/', initialfile='shell_model.stl')

        filepath = os.path.abspath(filename.name)

        self.notify("[info]", f"Pfad: {filepath}")

        self.progress(True)

        try:
            self.lib.export_shell(filepath)
            self.notify("[info]","Vollkörper erfolgreich exportiert.")
        except Exception as error:
            self.bell()
            self.notify("[error]","Schalenkörper konnte nicht exportiert werden.")
            self.notify("[error]", str(error) )
        self.progress()

    def onCreateShell(self):

        in_th = float(self.shell_thickness_internal_entry.get())
        ex_th = float(self.shell_thickness_external_entry.get())
        self.progress(True)

        if in_th <= 0. and ex_th <= 0.:
            self.bell()
            self.notify("[error]","Mindestens ein Dickenwert muss ungleich 0 sein.")
            self.progress()
            return

        try:
            self.lib.create_shell(inner_thickness=in_th, outer_thickness=ex_th)
            self.notify("[info]","Schalenkörper erfolgreich erstellt.")
            self.shell_model_label.toggle(True)
        except Exception as error:
            self.bell()
            self.notify("[error]","Schalenkörper konnte nicht erstellt werden.")
            self.notify("[error]", str(error) )
        self.progress()

    def onDeleteModel(self):
        self.progress(True)
        self.lib.delete_initial_model()
        self.notify("[info]", "Schalenkörper und Vollkörper erfolgreich gelöscht")
        self.initial_model_label.toggle(False)
        self.shell_model_label.toggle(False)
        self.cell_initialize_frame_label.toggle(False)
        self.cell_config_frame_label.toggle(False)
        self.grid_frame_label.toggle(False)
        self.intersected_frame_label.toggle(False)
        self.unified_frame_label.configure(text_color=self.appearance.fg_dark)
        self.shell_button_bar.toggle("Erstellen", True)
        self.shell_thickness_internal_entry.configure(state=ctk.NORMAL)
        self.shell_thickness_external_entry.configure(state=ctk.NORMAL)
        self.progress()

    def onDeleteShell(self):
        self.progress(True)
        self.lib.delete_shell()
        self.notify("[info]", "Schalenkörper erfolgreich gelöscht")
        self.shell_model_label.toggle(False)
        self.cell_initialize_frame_label.toggle(False)
        self.cell_config_frame_label.toggle(False)
        self.grid_frame_label.toggle(False)
        self.intersected_frame_label.toggle(False)
        self.unified_frame_label.configure(text_color=self.appearance.fg_dark)
        self.shell_button_bar.toggle("Erstellen", True)
        self.shell_thickness_internal_entry.configure(state=ctk.NORMAL)
        self.shell_thickness_external_entry.configure(state=ctk.NORMAL)
        self.progress()

    def onInitializeCell(self):
        self.progress(True)

        dx = float( self.cell_initialize_sizes_dirx_entry.get() )
        dy = float( self.cell_initialize_sizes_diry_entry.get() )
        dz = float( self.cell_initialize_sizes_dirz_entry.get() )

        sx = bool(self.cell_config_sizes_dirx_control.get())
        sy = bool(self.cell_config_sizes_diry_control.get())
        sz = bool(self.cell_config_sizes_dirz_control.get())

        try:
            self.lib.init_unitary_cell( (dx, dy, dz), (sx, sy, sz) )
            self.notify("[info]", "Elementarzelle wurde initialisiert.")
            self.notify("[info]",
                        f"Abmaße der Zelle: " + str(self.lib.cell.size) )
            self.cell_initialize_frame_label.toggle(True)
            self.cell_initialize_canvas.reset()
            self.cell_initialize_canvas.create( self.lib.cell.size, self.lib.lattice.periodicity )
            self.cell_config_canvas.add_initial_points(self.lib.cell.vertices)

        except ZeroDivisionError:
            self.notify("[error]","Die gegebenen Abmaße der Elementarzelle sind größer als das Modell selbst. Bitte wählen Sie andere Werte.")
        except Exception as error:
            self.notify("[error]", "Elementarzelle konnte nicht initialisiert werden.")
            self.notify("[error]", f"{error}")

        self.progress()

    def onSelectFeatureType(self, value):
        if value == "Punkt":
            self.cell_config_genericentry_entry.delete("0", ctk.END)
            self.cell_config_genericentry_entry.insert( ctk.END, "[0, {'diameter': 0.0 }]" )

        if value == "Strebe":
            self.cell_config_genericentry_entry.delete("0", ctk.END)
            self.cell_config_genericentry_entry.insert( ctk.END,"[0, 0, {'diameter': 0.0 }]" )

        if value == "Fläche":
            self.cell_config_genericentry_entry.delete("0", ctk.END)
            self.cell_config_genericentry_entry.insert( ctk.END,"[0, 0, 0, {'thickness': 0.0 }]")

        if value == "Variable":
            self.cell_config_genericentry_entry.delete("0", ctk.END)
            self.cell_config_genericentry_entry.insert( ctk.END,"['fillet',{'radius': 0.0}]")

        if value == "Aus Vorlage":
            self.cell_config_genericentry_entry.delete("0", ctk.END)
            self.onLoadTemplate()

        if value == "Verrundung":
            self.cell_config_genericentry_entry.delete("0", ctk.END)
            self.cell_config_genericentry_entry.insert( ctk.END,"['var', {'name': 'k', 'value': 0.0 }]")

    def onAddFeatureEntry(self):
        self.progress(True)
        info = self.cell_config_genericentry_entry.get()
        try:
            self.notify( "[info]", f"Das Feature konnte erfolgreich hinzugefügt werden.")
            if self.cell_config_log.get("0.0", ctk.END).strip() == "":
                self.cell_config_log.insert( index = ctk.END, text=info )
            else:
                self.cell_config_log.insert( index = ctk.END, text=",\n"+info )
        except SyntaxError as se:
            self.notify("[error]", f"Ihre Eingabe {info} besitzt einen Syntaxfehler.")
        except Exception as error:
            self.notify("[error]", "Das Feature konnte nicht hinzugefügt werden.")
            self.notify("[error]", f"{error}")

        self.onUpdateFeatures()
        self.progress()

    def onSelectOption(self, value) -> None:
        if value == '⌫':
            self.onDeleteFeatureList()
        elif value == '⟳':
            self.onUpdateFeatures()
        elif value == '⎙':
            self.onSaveAsTemplate()

    def update_features(self, info: str ) -> None:
        info = info.replace( "\n", "" )
        self.lib.config.reset()
        self.lib.config.insert( info )

    def onUpdateFeatures(self):
        self.progress(True)
        try:
            self.update_features(  self.cell_config_log.get("0.0",ctk.END) )
            self.cell_config_canvas.reset()

            if not self.lib.config.empty():
                self.cell_config_canvas.add_feature( self.lib.config )

        except ValueError as ve:
            self.notify("[error]", f"{ve}")
        except SyntaxError as se:
            self.notify("[error]", f"In Ihrer Eingabe gibt es einen Syntaxfehler.")
            self.notify("[error]", f"{se}")

        self.notify("[info]", f"{len(self.lib.config)} Features wurden aktualisiert.")
        self.progress()

    def onDeleteFeatureList(self):
        self.progress(True)
        self.cell_config_log.delete("0.0", ctk.END)
        self.lib.delete_features()
        self.onInitializeCell()
        self.progress()
        self.cell_config_canvas.reset()
        self.notify("[info]", "Alle Features wurden erfolgreich gelöscht.")

    def onSaveAsTemplate(self):
        self.progress(True)

        if not len(self.lib.config) == 0:
            filetype = (
                ('Textdatei', '.txt'),
                ('Template-Datei', '.template')
            )

            filename = fd.asksaveasfile(confirmoverwrite=True, filetypes=filetype, initialdir='C:/',
                                        initialfile='features.template')

            filepath = os.path.abspath(filename.name)
            self.notify("[info]", f"Pfad: {filepath}")

            new_file = open( filepath, 'w' )

            info = self.cell_config_log.get("0.0", ctk.END)

            new_file.write( info )

            self.notify("[info]", f"Features wurden erfolgreich als Vorlage abgespeichert.")

        else:
            self.notify("[info]", "Es wurden keine Features zum exportieren gefunden.")
        self.progress()

    def onLoadTemplate(self):
        filetype = (
            ('Text-Datei', '.txt'),
            ('Vorlage-Datei', '.template')
        )
        self.progress(True)

        filename = fd.askopenfile(title="Vorlage auswählen", initialdir='C:/', filetypes=filetype)

        filepath = os.path.abspath(filename.name)

        self.notify("[info]", f"Pfad: {filepath} ausgewählt")

        self.lib.config.append( [ 'template', {'filepath': filepath} ] )

        self.cell_config_log.delete("0.0", ctk.END)
        self.cell_config_log.insert(ctk.END, str(self.lib.config))

        self.onUpdateFeatures()

        self.progress()

    def onCreateCell(self):
        self.progress(True)
        try:
            self.lib.create_unitary_cell()
            self.notify("[info]", "Elementarzelle konnte erfolgreich erstellt werden.")
            self.notify("[info]", f"Elementarzelle besitzt die relative Dichte {self.lib.cell.density()}.")
            self.cell_config_frame_label.toggle(True)
        except Exception as e:
            self.notify("[error]", "Elementarzelle konnte nicht erstellt werden.")
            self.notify("[error", str(e))
        self.progress()

    def onExportCell(self):
        filetype = (
            ('STL-Datei', '.stl'),
            ('STL-Datei', '.STL'),
            ('STEP-Datei', '.STEP')
        )

        filename = fd.asksaveasfile(confirmoverwrite=True, filetypes=filetype,initialdir='C:/', initialfile='cell_model.stl')

        filepath = os.path.abspath(filename.name)

        self.notify("[info]", f"Pfad: {filepath}")

        self.progress(True)

        try:
            self.lib.export_unitary_cell(filepath)
            self.notify("[info]","Einheitszelle erfolgreich exportiert.")
        except Exception as error:
            self.bell()
            self.notify("[error]","Einheitszelle konnte nicht exportiert werden.")
            self.notify("[error]", str(error) )
        self.progress()

    def onDeleteCell(self):
        print(self.winfo_width(), self.winfo_height())
        self.progress(True)
        self.lib.delete_unitary_cell()
        self.notify("[info]", "Einheitszelle erfolgreich gelöscht")
        self.cell_config_frame_label.toggle(False)
        self.grid_frame_label.toggle(False)
        self.intersected_frame_label.toggle(False)
        self.unified_frame_label.configure(text_color=self.appearance.fg_dark)
        self.progress()

    def onCreateGrid(self):
        self.progress(True)
        try:
            self.lib.create_lattice()
            self.notify("[info]", "Gitter konnte erfolgreich erstellt werden.")
            self.grid_frame_label.toggle(True)
        except:
            self.notify("[error]", "Gitter konnte nicht erstellt werden.")
        self.progress()

    def onExportGrid(self):
        filetype = (
            ('STL-Datei', '.stl'),
            ('STL-Datei', '.STL'),
            ('STEP-Datei', '.STEP')
        )

        filename = fd.asksaveasfile(confirmoverwrite=True, filetypes=filetype,initialdir='C:/', initialfile='lib.stl')

        filepath = os.path.abspath(filename.name)

        self.notify("[info]", f"Pfad: {filepath}")

        self.progress(True)

        try:
            self.lib.export_lattice(filepath)
            self.notify("[info]","Gitter erfolgreich exportiert.")
        except Exception as error:
            self.bell()
            self.notify("[error]","Gitter konnte nicht exportiert werden.")
            self.notify("[error]", str(error) )
        self.progress()

    def onDeleteGrid(self):
        self.progress(True)
        self.lib.delete_lattice()
        self.notify("[info]", "Gitter erfolgreich gelöscht")
        self.grid_frame_label.toggle(False)
        self.intersected_frame_label.toggle(False)
        self.unified_frame_label.toggle(False)
        self.progress()

    def onCreateGridIntersected(self):
        self.progress(True)
        try:
            self.lib.intersect_lattice()
            self.notify("[info]", "Gitter konnte erfolgreich zurechtgeschnitten werden.")
            self.intersected_frame_label.toggle(True)
        except Exception as error:
            self.notify("[error]", "Gitter konnte nicht zurechtgeschnitten werden.")
            self.notify("[error]", str(error))
        self.progress()

    def onExportGridIntersected(self):
        filetype = (
            ('STL-Datei', '.stl'),
            ('STL-Datei', '.STL'),
            ('STEP-Datei', '.STEP')
        )

        filename = fd.asksaveasfile(confirmoverwrite=True, filetypes=filetype,initialdir='C:/', initialfile='intersected_model.stl')

        filepath = os.path.abspath(filename.name)

        self.notify("[info]", f"Pfad: {filepath}")

        self.progress(True)

        try:
            self.lib.export_intersected_lattice(filepath)
            self.notify("[info]","Zurechtgeschnittenes Gitter erfolgreich exportiert.")
        except Exception as error:
            self.bell()
            self.notify("[error]","Zurechtgeschnittenes Gitter konnte nicht exportiert werden.")
            self.notify("[error]", str(error) )
        self.progress()

    def onDeleteGridIntersected(self):
        self.progress(True)
        self.lib.delete_intersected_lattice()
        self.notify("[info]", "Zurechtgeschnittenes Gitter erfolgreich gelöscht")
        self.intersected_frame_label.toggle(False)
        self.unified_frame_label.toggle(False)
        self.progress()

    def onCreateUnified(self):
        self.progress(True)
        try:
            self.lib.unify()
            self.notify("[info]", "Schale und Gitter wurden erfolgreich zusammengefügt.")
            self.unified_frame_label.toggle(True)
        except Exception as error:
            self.notify("[error]", "Schale und Gitter konnten nicht verschmolzen werden.")
            self.notify("[error]", str(error))
        self.progress()

    def onExportUnified(self):
        filetype = (
            ('STL-Datei', '.stl'),
            ('STL-Datei', '.STL'),
            ('STEP-Datei', '.STEP')
        )

        filename = fd.asksaveasfile(confirmoverwrite=True, filetypes=filetype,initialdir='C:/', initialfile='unified_model.stl')

        filepath = os.path.abspath(filename.name)

        self.notify("[info]", f"Pfad: {filepath}")

        self.progress(True)

        try:
            self.lib.export_unified(filepath)
            self.notify("[info]","Modell mit Gitter erfolgreich exportiert.")
        except Exception as error:
            self.bell()
            self.notify("[error]","Modell mit Gitter konnte nicht exportiert werden.")
            self.notify("[error]", str(error) )
        self.progress()

    def onDeleteUnified(self):
        self.progress(True)
        self.lib.delete_unified()
        self.notify("[info]", "Modell mit Gitter erfolgreich gelöscht")
        self.unified_frame_label.toggle(False)
        self.progress()


app = LatticeGeometryUI()
app.mainloop()
