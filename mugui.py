from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
import sys
import json


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.list = ['地域歧视', '种族歧视', '性别歧视', 'LGBTQ', '其他歧视', '非歧视']
        self.wordlist = ['Region', 'Racism', 'Sexism', 'LGBTQ', 'others', 'non-hate']
        self.setWindowTitle("仇恨文本人工分类GUI")
        self.setGeometry(300, 300, 500, 300)

        self.selected = set()
        self.index = 0
        self.sep = 0
        self.now = ''
        self.group = ''
        self.subject = ''
        self.opinion = ''

        # 加载数据
        with open('test1.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        with open('org.txt', 'r', encoding='utf-8') as f:
            self.pre = f.read().split('\n')[:len(self.data)]

        with open('new.txt', 'r', encoding='utf-8') as f:
            tmp = f.read().split('\n')
        for line in tmp:
            if line.strip():
                self.index += 1

        self.init_ui()

    def gettext(self):
        ans = ''
        content = self.data[self.index]['content']
        data = self.pre[self.index].replace(' [END]', '').split(' [SEP] ')

        if 0 <= self.sep < len(data):
            subject, opinion = data[self.sep].split(' | ')[:2]
            self.subject = subject
            self.opinion = opinion
            ans += '输入文本：' + content + '\n'
            ans += '评论主体：' + subject + '\n'
            ans += '评论观点：' + opinion + '\n'
            return ans

        elif self.sep >= len(data):
            self.sep = 0
            self.index += 1
            print(self.now)
            with open('new.txt','a+',encoding='utf-8') as f:
                self.now+='\n'
                self.now=self.now.replace('[SEP] \n','[END]\n')
                f.write(self.now)
            self.now = ''
            self.group = ''
            self.text_edit.setPlaceholderText("仇恨类别 [" + str(self.index) + '/2000]')
            return self.gettext()
        else:
            with open('new.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                lines = lines[:-1]
            with open('new.txt', 'w', encoding='utf-8') as f:
                f.writelines(lines)

            self.index -= 1
            self.sep = 0
            self.now = ''
            self.group = ''
            return self.gettext()

    def init_ui(self):
        # 文本框（展示信息）
        self.text_edit0 = QTextEdit(self)
        self.text_edit0.setPlaceholderText(self.gettext())

        # 文本框（展示分类结果）
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("仇恨类别 ["+str(self.index)+'/2000]')

        # 按钮布局
        self.buttons = []  # 所有按钮
        self.category_buttons = []  # 前六个分类按钮
        button_layout = QHBoxLayout()

        # 上一个按钮
        btn_pre = QPushButton('上一个')
        btn_pre.clicked.connect(self.prev)
        self.buttons.append(btn_pre)
        button_layout.addWidget(btn_pre)

        # 六个分类按钮
        for i in range(6):
            btn = QPushButton(self.list[i])
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, x=i: self.on_button_click(x))
            self.buttons.append(btn)
            self.category_buttons.append(btn)
            button_layout.addWidget(btn)

        # 下一个按钮
        btn_next = QPushButton('下一个')
        btn_next.clicked.connect(self.next)
        self.buttons.append(btn_next)
        button_layout.addWidget(btn_next)

        # 布局组合
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.text_edit0)
        main_layout.addWidget(self.text_edit)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def next(self):
        self.sep += 1
        self.now += self.subject + ' | ' + self.opinion + ' | ' + self.group + ' | '
        if self.group == 'non-hate':
            self.now += 'non-hate [SEP] '
        else:
            self.now += 'hate [SEP] '
        self.clear_selections()
        self.selected = set()
        self.text_edit0.setPlaceholderText(self.gettext())
        self.text_edit.clear()

    def prev(self):
        self.sep -= 1
        self.now=''
        self.clear_selections()
        self.selected = set()
        self.text_edit0.setPlaceholderText(self.gettext())
        self.text_edit.clear()

    def on_button_click(self, number):
        if number == 5:  # “非歧视”
            self.clear_selections()
            self.selected = {5}
            self.category_buttons[5].setChecked(True)
        else:
            if 5 in self.selected:
                self.category_buttons[5].setChecked(False)
                self.selected.remove(5)
            if number in self.selected:
                self.selected.remove(number)
                self.category_buttons[number].setChecked(False)
            else:
                self.selected.add(number)
                self.category_buttons[number].setChecked(True)

        self.update_textbox()

    def clear_selections(self):
        for btn in self.category_buttons:
            btn.setChecked(False)
        self.selected.clear()

    def update_textbox(self):
        self.text_edit.clear()
        ans = ''
        for idx in sorted(self.selected):
            ans += self.wordlist[idx] + ', '
        self.group = ans.rstrip(', ')
        self.text_edit.append(self.group)


# 运行程序
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
