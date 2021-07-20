import os

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QFileSystemModel, QGraphicsScene

from paragon.ui.views.ui_directory_textures_viewer import Ui_DirectoryTexturesViewer


class DirectoryTexturesViewer(Ui_DirectoryTexturesViewer):
    def __init__(self, gs, path, load_fn, valid_extensions):
        super().__init__()

        self.setWindowTitle("Paragon Textures Viewer - " + path)

        self.rom_path = os.path.normpath(gs.project.rom_path)
        self.output_path = os.path.normpath(gs.project.output_path)
        self.gd = gs.data
        self.load_fn = load_fn
        self.path = os.path.normpath(path)
        self.valid_extensions = valid_extensions

        self.model = QFileSystemModel()
        self.model.setNameFilterDisables(False)
        self.tree_view.setModel(self.model)

        self.layers_box.setCurrentIndex(0)
        self._refresh_model()

        self.layers_box.currentIndexChanged.connect(self._refresh_model)

    def _refresh_model(self):
        if self.layers_box.currentIndex() == 0:
            root = os.path.join(self.rom_path, self.path)
        else:
            root = os.path.join(self.output_path, self.path)
        self.model.setRootPath(root)
        self.model.setNameFilters(self.valid_extensions)
        self.tree_view.setRootIndex(self.model.index(root))
        self.tree_view.selectionModel().currentChanged.connect(self._on_select)

    def _on_select(self, index: QModelIndex):
        if not index.isValid():
            return
        index = self.model.index(index.row(), 0, index.parent())
        full_path = os.path.join(self.path, self.model.fileName(index))
        textures = self.load_fn(self.gd, full_path)
        texture = next(map(lambda t: t[1], textures.items()), None)
        if texture:
            scene = QGraphicsScene()
            scene.addPixmap(texture.to_qpixmap())
            self.image_view.setScene(scene)
            self.image_view.setSceneRect(0.0, 0.0, float(texture.width), float(texture.height))
