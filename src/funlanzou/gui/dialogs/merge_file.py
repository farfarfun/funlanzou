import os
from pickle import load

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
)

from funlanzou.debug import SRC_DIR
from funlanzou.gui.others import MyLineEdit
from funlanzou.gui.qss import others_style, btn_style


def get_minimum_file(file_lst: list) -> str:
    """ 返回大小最小的文件名 """
    if not file_lst:
        return ""
    if len(file_lst) == 1:
        return file_lst[0]
    res = file_lst[0]
    size = os.path.getsize(res)
    for f in file_lst[1:]:
        _size = os.path.getsize(f)
        if _size < size:
            res = f
            size = _size

    return res


def un_serialize(folder):
    """反序列化文件信息数据"""
    txt_lst = []
    folder_lst = os.listdir(folder)
    for item in folder_lst:
        _file = os.path.join(folder, item)
        if os.path.isfile(_file):
            if _file.endswith(".txt"):
                txt_lst.append(_file)
    record_file = get_minimum_file(txt_lst)
    if not record_file:
        msg = "没有 txt 记录文件"
        return False, msg
    record = {}
    try:
        with open(record_file, "rb") as f_handle:
            _record = load(f_handle)
        if isinstance(_record, dict):
            record = _record
    except Exception as e:  # 这里可能会丢奇怪的异常
        # logger.debug(f"Pickle e={e}")
        pass
    if not record:
        msg = f"{record_file} : 记录文件不对"
        return False, msg
    else:
        files_info = {}
        not_complete = False
        for _file in record["parts"]:
            full_path = os.path.join(folder, _file)
            if not os.path.isfile(full_path):
                not_complete = True
                files_info[_file] = False

        if not_complete:
            msg = "文件不全"
            return False, msg
        merged_file_name = os.path.join(folder, record["name"])
        with open(merged_file_name, "ab") as merge_f:
            for _file in record["parts"]:
                part_file_name = os.path.join(folder, _file)
                with open(part_file_name, "rb") as f:
                    for data in f:
                        merge_f.write(data)

        if os.path.getsize(merged_file_name) == record["size"]:
            for _file in record["parts"]:
                part_file_name = os.path.join(folder, _file)
                os.remove(part_file_name)
            os.remove(record_file)
            return True, ""
        else:
            msg = "文件大小对不上"

        return False, msg


class MergeFileDialog(QDialog):
    check_update = pyqtSignal(str, bool)

    def __init__(self, user_home, parent=None):
        super(MergeFileDialog, self).__init__(parent)
        self.cwd = user_home
        self.selected = ""
        self.initUI()
        self.setStyleSheet(others_style)

    def initUI(self):
        self.setWindowTitle("合并文件")
        self.setWindowIcon(QIcon(SRC_DIR + "upload.png"))
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(SRC_DIR + "logo3.gif"))
        self.logo.setStyleSheet("background-color:rgb(0,153,255);")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # lable
        self.choose_lb = QLabel("选择文件夹")
        # folder
        self.choose_folder = MyLineEdit(self)
        self.choose_folder.setObjectName("choose_folder")
        self.choose_folder.clicked.connect(self.slot_choose_folder)
        self.status = QLabel(self)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("提取")
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("关闭")
        self.buttonBox.setStyleSheet(btn_style)

        vbox = QVBoxLayout()
        hbox_head = QHBoxLayout()
        hbox_button = QHBoxLayout()
        hbox_head.addWidget(self.choose_lb)
        hbox_head.addWidget(self.choose_folder)
        hbox_button.addWidget(self.buttonBox)
        vbox.addWidget(self.logo)
        vbox.addStretch(1)
        vbox.addWidget(self.status)
        vbox.addLayout(hbox_head)
        vbox.addStretch(1)
        vbox.addLayout(hbox_button)
        self.setLayout(vbox)
        self.setMinimumWidth(350)

        # 设置信号
        self.buttonBox.accepted.connect(self.slot_btn_ok)
        self.buttonBox.rejected.connect(self.slot_btn_no)
        self.buttonBox.rejected.connect(self.reject)

    def slot_choose_folder(self):
        dir_choose = QFileDialog.getExistingDirectory(self, "选择文件夹", self.cwd)  # 起始路径
        if dir_choose == "":
            return
        self.selected = dir_choose
        self.choose_folder.setText(self.selected)
        self.status.setText("")
        self.cwd = os.path.dirname(dir_choose)

    def slot_btn_no(self):
        self.selected = ""
        self.choose_folder.setText(self.selected)
        self.status.setText("")

    def slot_btn_ok(self):
        if self.selected:
            success, msg = un_serialize(self.selected)
            if success:
                text = "提取成功✅"
            else:
                text = f"提取失败❌, {msg}"
        else:
            text = "未选择文件夹📂"
        self.status.setText(text)
