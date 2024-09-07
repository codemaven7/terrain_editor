import sys

import qtawesome as qta  # icons
from PyQt5.Qt import QStyleOptionViewItem
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QFont
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout, QLayout, QSizePolicy
from PyQt5.QtWidgets import QLabel, QMainWindow, QAction, QPushButton, QComboBox
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QStyleOptionComboBox
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtWidgets import QWidget, QListView, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QDataWidgetMapper
from PyQt5.QtCore import QModelIndex, QAbstractListModel

# from PyQt5.QtCore import QObject


import images_qrc


from pathlib import Path


# length in qt pixels
# terrain_square_length = 32
terrain_square_length = 48
# terrain_square_length = 64



# def get_path_to_rom_hack():
#     import os
#     
#     # rom_path = 'R2.smc'
#     rom_path = 'rotk2.sfc'
#     adjusted_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', rom_path)
#     rom_path = adjusted_path
#     return rom_path



# def get_containing_directory():

#     import sys, os


#     if getattr(sys, 'frozen', False):
#             # we are running in a bundle
#             # frozen = True
#             bundle_dir = sys._MEIPASS
#     else:
#             # we are running in a normal Python environment
#             # frozen = False
#             bundle_dir = os.path.dirname(os.path.abspath(__file__))

#     return bundle_dir



def get_terrain_setups_wrapper(rom_path):  # Expected rom path is only filename; also the file path currently defaults to a hardcoded path!

    import terrain_setups_from_binary
    from copier_header import smc_header

    SMC_header = smc_header(rom_path)

    with open(rom_path, "rb") as f_rom:

        ## the SFC start location is 0x32994.
        ## the SMC start read location is 0x32B94. The amount to read is 0xc7e, i.e. smc: (0x33812 - 0x32B94).
        f_rom.seek(0x32994 + SMC_header, 0)
        province_terrain_setups_binary = f_rom.read(0xc7e)

        ## attacker and defender starting points
        ## SMC: (start + 1) minus end (length in bytes): (0x32B93 + 1) - 0x31F16
        f_rom.seek(0x31D16 + SMC_header, 0)
        battle_maps_starting_points_binary = f_rom.read(0xc7e)



    # this is currently implemented as 2d list:
    battle_setups_terrain = terrain_setups_from_binary.obtain_collection_of_setups(province_terrain_setups_binary)

    battle_setups_starting_points = terrain_setups_from_binary.obtain_collection_of_setups(battle_maps_starting_points_binary)


    # debugging / examination / assertion stuff
    assert not [y for L in battle_setups_terrain for y in L if y > 6]  # 0 to 6 inclusive
    assert max([y for L in battle_setups_starting_points for y in L]) <= 7 # 0 to 7 inclusive


    D = {'terrain': battle_setups_terrain, 'starting': battle_setups_starting_points}

    return D


def create_rom_base(rom_path):
    """Obtain rom bytes, while excluding the smc header if it exists."""

    from copier_header import smc_header

    SMC_header = smc_header(rom_path)

    with open(rom_path, "rb") as f_rom:

        f_rom.seek(SMC_header, 0)  # strip out smc header if it exists
        rom_base_sfc_format = f_rom.read(-1)


    return rom_base_sfc_format


class combo_delegate_terrain_basic(QStyledItemDelegate):
    """A delegate for painting only icons in a combobox.

    Based off c++ source from Chris Kawa at https://forum.qt.io/topic/61659/qcombobox-with-icons-but-no-text-how/5
    """

    def __init__(self):
        super().__init__()


    def paint(self, painter, option, index):
        o = option

        self.initStyleOption(o, index)

        # o.decorationSize.setWidth(o.rect.width())

        # o.decorationSize.setHeight(terrain_square_length)  # this shouldn't be a static number
        # o.decorationSize.setWidth(terrain_square_length)  # this shouldn't be a static number
        o.decorationSize = QSize(terrain_square_length, terrain_square_length)


        # Remove the HasDisplay flag; only want QStyleOptionViewItem.HasDecoration flag.
        o.features = QStyleOptionViewItem.HasDecoration


        # This is probably not the right approach (weird bugs occur):
        # o.rect = QRect(0, 0, terrain_square_length, terrain_square_length)



        # o.showDecorationSelected = False  # QStyleOptionViewItem.showDecorationSelected

        # o.decorationAlignment = Qt.AlignCenter

        # # this seems to remove the side margin bar thing:
        o.decorationPosition = QStyleOptionViewItem.Top


        # "The item is the only one on the row, and is therefore both at the beginning and the end."
        # o.ViewItemPosition = QStyleOptionViewItem.OnlyOne


        style = o.widget.style() if o.widget else QApplication.style()

        style.drawControl(QStyle.CE_ItemViewItem, o, painter, o.widget)

        pass # for debugging


        def sizeHint(self, option, index):  # doesn't seem to do anything


            result = QSize(terrain_square_length, terrain_square_length)
            return result



class customComboBox(QComboBox):

    def __init__(self):
        super().__init__()


    # def paintEvent(self, ev):
    #     pass
    #     pass



class customComboBox_no_arrow(QComboBox):

    # Should a parent parameter be used here?:
    # def __init__(self, parent=None):
    #     super().__init__(parent)

    def __init__(self):
        super().__init__()




    # # This runs but isn't what is desired
    #
    # def paintEvent(self, ev):
    #     p = QPainter()
    #     p.begin(self)
    #     opt = QStyleOptionComboBox()
    #     opt.initFrom(self)
    #
    #
    #     self.style().drawPrimitive(QStyle.PE_PanelButtonBevel, opt, p, self)
    #     self.style().drawPrimitive(QStyle.PE_PanelButtonCommand, opt, p, self)
    #     # Don't want item text right?
    #     self.style().drawItemText(p, self.rect(), Qt.AlignCenter, self.palette(), self.isEnabled(), self.currentText())
    #
    #
    #     p.end()



    def paintEvent(self, ev):
        p = QPainter()
        p.begin(self)
        opt = QStyleOptionComboBox()
        opt.initFrom(self)


        # self.style().drawPrimitive(QStyle.PE_PanelButtonBevel, opt, p, self)
        # self.style().drawPrimitive(QStyle.PE_PanelButtonCommand, opt, p, self)


        # # icons used:
        # icon_to_show = self.currentData(Qt.DecorationRole)
        # icon_to_show.paint(p, self.rect(), Qt.AlignCenter)

        # # convert icon to pixmap, then draw pixmap using QStyle
        # # the size might need to be changed based on widget size
        pixmap_to_show = self.currentData(Qt.DecorationRole).pixmap(self.size())
        self.style().drawItemPixmap(p, self.rect(), Qt.AlignCenter, pixmap_to_show)

        p.end()



    # def minimumSizeHint(self):
    #     pass
    #     pass


    # """This implementation caches the size hint to avoid resizing when the contents change dynamically.
    # To invalidate the cached value change the sizeAdjustPolicy."""

    def sizeHint(self):

        result = QSize(terrain_square_length, terrain_square_length)
        return result


class ComboListModel(QAbstractListModel):
    def __init__(self, list_items, parent=None):
        super().__init__(parent)


        self.data_list = [x for x in list_items]


    def rowCount(self, parent=QModelIndex()):  # should parent default be None? Or simply no default parameter?

        return len(self.data_list)


    # currently no headerData method
    # def headerData(self, section, orientation, role):
    # ...


    def data(self, index, role):
        if not index.isValid():
            return None

        if index.row() >= len(self.data_list):
            return None

        if role == Qt.DisplayRole:
            return self.data_list[index.row()]
        # elif role == DecorationRole:
            # ...
        else:
            return None



class TerrainTileCombo(QComboBox):

    def __init__(self, tile_icons_list, parent=None):
        super().__init__(parent)

        self.init_setup()


    def init_setup(self):

        ...




## terrain widget containing widget:

class TerrainCombos(QWidget):
    def __init__(self, tile_icons_list, initial_setups=None, parent=None):
        super().__init__(parent)

        from PyQt5.QtWidgets import QLineEdit, QTextEdit


        # todo: fix initial update/sync issues from mapper model to widgets!!!



        if initial_setups == None:
            # initial_setups = [[0] * 156 for i in range(41)]  # all grass / terrain type 0

            temp_implementation_initial_setups = [[2] * 156 for i in range(41)]
            initial_setups = temp_implementation_initial_setups


        # Set up the model.
        self.setupModel(initial_setups=initial_setups)

        self.setupWidgets(tile_icons_list)



    def setupWidgets(self, tile_icons_list):


        terrain_rows = 12
        terrain_columns = 13  # but also an additional black bar chr (1/2 of a terrain square in height)



        terrain_combo_box_list = [None] * 156
        for i in range(156):  # 156 terrain squares (not counting black bars)

            # x = QComboBox()
            # x = customComboBox()
            x = customComboBox_no_arrow()


            # Placing the stylesheet section before the later adjustments is important!

            ### this may need to be adjusted to avoid problems
            x.setView(QListView())



            ##
            ## Removed the stylesheet that was here. Can return it later.
            ##




            x.setFrame(False)


            x.setIconSize(QSize(terrain_square_length, terrain_square_length))  # needed


            # """Unless explicitly set this returns the default value of the current style.
            # "This size is the maximum size that icons can have; icons of smaller size are not scaled up."""
            # x.setIconSize = QSize(terrain_square_length, terrain_square_length)

            x.setMinimumSize(terrain_square_length, terrain_square_length)


            # x.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # horizonal and vertical
            # probably necessary if using a scale slider, etc.
            x.setSizeAdjustPolicy(QComboBox.AdjustToContents)  # may not want this; the default is QComboBox.AdjustToContentsOnFirstShow


            # print(x.iconSize())  # before using setIconSize(), this was always printing 16 by 16



            # Avoids extra spacing in grid!
            x.setMaximumSize(terrain_square_length, terrain_square_length)


            x.setItemDelegate(combo_delegate_terrain_basic())



            for combo_index in range(7): # seven kinds of terrain
                current_icon = QIcon(tile_icons_list[combo_index])
                x.insertItem(combo_index, current_icon, '')  # could also change the userData parameter (roles)



            terrain_combo_box_list[i] = (x)





        # Set up the mapper.
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)





        terrain_grid_layout = QGridLayout()




        black_chr_pixmap = QPixmap(terrain_square_length // 2, terrain_square_length // 2)
        black_chr_pixmap.fill(QColor(0, 0, 0))

        black_rectangle_pixmap = QPixmap(terrain_square_length, terrain_square_length // 2)
        black_rectangle_pixmap.fill(QColor(0, 0, 0))
        # black_rectangle_pixmap.fill(QColor(Qt.black))


        # # labels implementation illustration (but without black bar offsetting!!!!):
        #
        # widgets_list = [None] * 156
        # for r in range(terrain_rows):
        #     for c in range(terrain_columns):
        #         idx = r * terrain_columns + c
        #         # w = TerrainTileCombo(tile_icons_list)
        #         w = QLabel(str(idx))
        #         widgets_list[idx] = w
        #
        # for r in range(terrain_rows):
        #     for c in range(terrain_columns):
        #
        #         idx = r * 13 + c
        #         w = widgets_list[idx]
        #         terrain_grid_layout.addWidget(w, r, c, 1, 1)



        # # only used for when using demonstative labels instead of pixmaps (while implementing)
        # consolas_font = QFont("Consolas", 8)


        # black bars example list comps: [(b + 1) % 2 for b in range(13)]; [b * 2 for b in range(13)]
        # black bars:
        for b in range(13):

            black_chr_column_start = b * 2
            black_chr_row_start = ((b + 1) % 2) * 24

            # # for ascii debugging visualizations
            # black_bar_widget = QLabel("000")  # ascii stand in for black bars
            # black_bar_widget.setFont(consolas_font)

            """ copied in, needs some slight editing: """
            # with spanning:
            black_bar_widget = QLabel()
            black_bar_widget.setPixmap(QPixmap(black_rectangle_pixmap))
            # optional: label_widget_rectangle.setMaximumSize(terrain_square_length, terrain_square_length // 2)


            terrain_grid_layout.addWidget(black_bar_widget, black_chr_row_start, black_chr_column_start, 1, 2)  # span one row, two columns


        for r in range(terrain_rows):
            for c in range(terrain_columns):
                black_bar_offset = c % 2

                chr_row_span_from = r * 2 + black_bar_offset
                chr_column_span_from = c * 2


                # print("r * terrain_columns + c is:", r * terrain_columns + c)

                # # useful for debugging visualization:
                # label_string = '{:_>3d}'.format(r * terrain_columns + c)
                # widget = QLabel(label_string)
                # widget.setFont(consolas_font)


                widget = terrain_combo_box_list[r * terrain_columns + c]


                terrain_grid_layout.addWidget(widget, chr_row_span_from, chr_column_span_from, 2, 2)  # fromRow and fromColumn, with a span of 2

                mapper_idx = r * terrain_columns + c
                self.mapper.addMapping(widget, mapper_idx, b'currentIndex')




        # update widgets (doesn't seem to work, also might only be for one section of the mapper)
        # self.mapper.toFirst()
        # self.mapper.revert()




        # SPACING

        terrain_grid_layout.setSpacing(0)
        terrain_grid_layout.setContentsMargins(0, 0, 0, 0)

        # probably other ways to accomplish this:
        terrain_grid_layout.setSizeConstraint(QLayout.SetFixedSize)  # an alternative enum value is QLayout.SetMinAndMaxSize


        # chr sized grid cells, instead of larger 2 by 2 terrain squares size

        for r in range(terrain_rows * 2):
            terrain_grid_layout.setRowMinimumHeight(r, terrain_square_length // 2)

        for c in range(terrain_columns * 2 + 1):
            terrain_grid_layout.setColumnMinimumWidth(c, terrain_square_length // 2)

            # print(terrain_grid_layout.columnMinimumWidth(2))
            # print(terrain_grid_layout.rowMinimumHeight(2))



        # Set up the next and previous buttons.  (Some adaptations need to be made to sync with the provinces selection combo box!)
        self.nextButton = QPushButton("&Next")
        self.previousButton = QPushButton("&Previous")


        # Set up connections and layouts.
        self.previousButton.clicked.connect(self.mapper.toPrevious)
        self.nextButton.clicked.connect(self.mapper.toNext)

        self.mapper.currentIndexChanged.connect(self.updateButtons)




        self.combo_province = QComboBox()

        self.combo_province.addItems(["Province " + str(i + 1) for i in range(41)])

        self.combo_province.currentIndexChanged[int].connect(self.mapper.setCurrentIndex)


        # todo: re-implement setCurrentIndex method to check for old value (or take a look at qt source code for the method)
        # No circularity issue because a non-change ends the cycle, right?
        self.mapper.currentIndexChanged.connect(self.combo_province.setCurrentIndex)


        # widget size policy can be trumped by managing layout size policy, maybe?
        # self.combo_province.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.previousButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nextButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


        # for debugging
        # self.mapper.currentIndexChanged.connect(lambda x: print("huzzah!"))



        self.mapper.currentIndexChanged.connect(lambda x: print(
                "debug print:", self.mapper.currentIndex(), self.model.item(x, 0).data(Qt.DisplayRole), self.model.item(x, 0).data(Qt.EditRole)
                )
            )


        vbox_layout = QVBoxLayout()
        smaller_hbox = QHBoxLayout()
        # grid_layout = QGridLayout()

        smaller_hbox.addWidget(self.combo_province)
        smaller_hbox.addWidget(self.previousButton)
        smaller_hbox.addWidget(self.nextButton)

        vbox_layout.addLayout(smaller_hbox)
        # vbox_layout.addLayout(grid_layout)


        terrain_grid_wrapper_widget = QWidget()
        terrain_grid_wrapper_widget.setLayout(terrain_grid_layout)
        vbox_layout.addWidget(terrain_grid_wrapper_widget)  # an optional arg expression: Qt.AlignTop | Qt.AlignLeft


        self.setLayout(vbox_layout)

        self.setWindowTitle("(Many Modifications) Combo-box Widget Mapper")
        self.mapper.toFirst()


    def setupModel(self, initial_setups=None):

        # from PyQt5.QtCore import  QStringListModel
        from PyQt5.QtGui import QStandardItemModel, QStandardItem


        if initial_setups == None:
            initial_setups = [[0] * 156 for i in range(41)]  # all grass / terrain type 0


        self.model = QStandardItemModel(41, 156, self)

        # self.terrain_combo_model = ...

        for prov in range(41):
            for square in range(156):
                self.model.setItem(prov, square, QStandardItem(str(initial_setups[prov][square])))  # string instead of an integer

        # breakpoint hook for debugging:
        pass


    def updateButtons(self, row):
        self.previousButton.setEnabled(row > 0)
        self.nextButton.setEnabled(row < self.model.rowCount() - 1)




# class TerrainWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         ...



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.statusBar()

        # openFile = QAction(QIcon('open.png'), 'Open', self) # currently no icon
        openFile = QAction(QIcon(qta.icon('fa.file')), 'Open', self)
        # openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open Rom File')
        openFile.triggered.connect(self.load_rom)


        saveAsFile = QAction(QIcon(qta.icon('fa.save')), 'Save As', self)  # Shouldn't SAVE AS have a distinct icon from SAVE?
        saveAsFile.setShortcut('Ctrl+S')  # this shortcut key combination can either be for SAVE or SAVE AS
        saveAsFile.setStatusTip('Save As New Rom File')
        saveAsFile.triggered.connect(self.showSaveAsDialog)




        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveAsFile)



        self.setGeometry(100, 100, 1280, 720)
        # self.setWindowTitle('An App')
        self.setWindowTitle('rotk2 terrain editor')

        # windowIcon = qta.icon('ei.key', color='Yellow')
        # self.setWindowIcon(windowIcon)

        # self.setWindowIcon(QIcon(castle_pix))
        icon_for_window = (self.terrainPixmaps()[6])  # the castle is at index 6
        self.setWindowIcon(QIcon(icon_for_window))


        # main_layout = QGridLayout()
        self.layout_for_terrain_comboboxes = QGridLayout()

        widget_for_terrain_comboboxes = QWidget()

        widget_for_terrain_comboboxes.setLayout(self.layout_for_terrain_comboboxes)

        self.setCentralWidget(widget_for_terrain_comboboxes)



        # keep attempting to load a rom by asking for a file name until one is given
        has_rom_been_loaded_yet = False
        while not has_rom_been_loaded_yet:
            has_rom_been_loaded_yet = self.load_rom()


        

    def initialize_terrain_comboboxes_widget(self):
        
        # during_implementation_modifications_terrain_combos = TerrainCombos(self.terrain_pixmaps_list)
        self.terrain_combos_instance = TerrainCombos(self.terrain_pixmaps_list, initial_setups=self.battle_setups_terrain_initial_version_from_rom)
        
        self.layout_for_terrain_comboboxes.addWidget(self.terrain_combos_instance, 0, 1)  # row, column

        # self.layout_for_terrain_comboboxes.addWidget(QLabel("start of a section"), 1, 0)



    def load_rom(self):


        input_rom_path = self.showOpenDialog()

        if not input_rom_path:
            return False

        else:

            self.current_filename = input_rom_path

            try:
                input_rom_as_binary = create_rom_base(rom_path=input_rom_path)

                # ROM DATA
                self.rom_base_bytes = input_rom_as_binary

            except Exception as e:
                print("an exception just occurred")
                raise


            # Use data obtained from the ROM (to-do: move this to a function called after a rom is selected by user):

            self.terrain_pixmaps_list = self.terrainPixmaps()  # Not currently read from rom, currently via PNG resources.

            # obtain province battle map terrain setups
            self.battle_setups_terrain_initial_version_from_rom = get_terrain_setups_wrapper(input_rom_path)['terrain']


            self.initialize_terrain_comboboxes_widget()


            # TODO: maybe move this somewhere else
            self.setWindowTitle('rotk2 terrain editor: ' + str(self.current_filename))

            return True




    def terrainPixmaps(self):


        # for scaled() method, default transformMode=Qt.FastTransformation is nearest neighbor

        ## these could be other terrain types in modded roms
        grass_pix = QPixmap(':/images/grass_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                               Qt.KeepAspectRatio)
        forest_pix = QPixmap(':/images/forest_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                                 Qt.KeepAspectRatio)
        hill_pix = QPixmap(':/images/hill_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                             Qt.KeepAspectRatio)
        mountain_pix = QPixmap(':/images/mountain_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                                     Qt.KeepAspectRatio)
        fort_pix = QPixmap(':/images/fort_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                             Qt.KeepAspectRatio)
        castle_pix = QPixmap(':/images/castle_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                                 Qt.KeepAspectRatio)
        # actually should be four water terrain squares
        water_pix = QPixmap(':/images/water_16x16.png').scaled(terrain_square_length, terrain_square_length,
                                                               Qt.KeepAspectRatio)




        ### terrain order in rom (but not correct order for province battle maps setups integers):
        ### grass, forest, hill, mountain, fort, castle, water



        # ordered by enum mapping from integer to picture
        terrain_pixmaps_list_visual_order = [
            grass_pix,
            forest_pix,
            hill_pix,
            mountain_pix,
            water_pix,
            fort_pix,
            castle_pix,
        ]
        return [x.copy() for x in terrain_pixmaps_list_visual_order]



    # this returns a bytes file when successful, rather than a filename
    def showOpenDialog(self):
    

        fname = QFileDialog.getOpenFileName(self, 'Open File', '/', "ROM (*.sfc *.smc)")

        if fname[0]:
            input_rom_path = fname[0]

            # self.current_filename = input_rom_path

            return input_rom_path

        else:
            return False


    def showSaveAsDialog(self):

        fname = QFileDialog.getSaveFileName(self, 'Save As File', '/', "SFC (*.sfc);;SMC (*.smc)")

        if fname[0]:
            output_rom_path = fname[0]

            output_binary = self.create_save_rom()

            if output_rom_path[-3:] == 'smc':  # ... in ['smc', 'swc']
                output_binary = bytes(512) + output_binary  # add empty padding for smc header

            with open(output_rom_path, "wb") as f_rom:
                f_rom.write(output_binary)
        else:
            pass


    def get_terrain_standard_item_model_data(self):

        standard_item_model = self.terrain_combos_instance.model  # QStandardItemModel


        L = [None] * 41
        for r in range(41):
            current_province = [None] * 156
            for c in range(156):
                item = standard_item_model.item(r, c)  # QStandardItem
                item_integer = int(item.text())

                current_province[c] = item_integer
            L[r] = current_province

        return L


    def create_save_rom(self):

        rom = bytearray(self.rom_base_bytes)


        ## This function appears to work!
        def battle_terrain_mutation_attempt_next_day(rom):

            import itertools

            battle_terrain_2d = self.get_terrain_standard_item_model_data()

            flat_terrain_data = tuple(itertools.chain(*battle_terrain_2d))

            terrain_output_bytes = bytearray(78 * 41)
            for p in range(41):
                for t in range(156):
                    flat_input_idx = t + (156 * p)
                    terrain = flat_terrain_data[flat_input_idx]

                    output_idx = (t // 2) + (78 * p)

                    shift = ((t + 1) % 2) * 4  # alternating high and low nybble
                    nybble = terrain << shift

                    terrain_output_bytes[output_idx] += nybble  # change to BINARY OR later


            rom[0x32994 : 0x32994 + 0xc7e] = terrain_output_bytes


        battle_terrain_mutation_attempt_next_day(rom)


        return rom



if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()

    window.showMaximized()


    sys.exit(app.exec_())

