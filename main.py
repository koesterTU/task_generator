import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.metrics import dp

import random
import json
import os

# ========= 关键：保持你原先的字体路径 =========
LabelBase.register(name="ChineseFont", fn_regular="fonts/SourceHanSansSC-Regular.OTF")

kivy.require('2.1.0')


class TaskGeneratorApp(App):
    def build(self):
        # 路径
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.base_dir, "tasks.json")

        # 分类名映射（中文 <-> 内部key）
        self.cn2key = {"短时任务": "short", "中时任务": "medium", "长时任务": "long"}
        self.key2cn = {v: k for k, v in self.cn2key.items()}

        # 载入/初始化任务库
        self.load_tasks()

        # ========== 主布局 ==========
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))

        # ---------- 开始选择层（默认显示） ----------
        self.start_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, 1), opacity=1)

        question = Label(text="你想进行什么样的任务？",
                         font_size=dp(20), font_name="ChineseFont", size_hint=(1, None), height=dp(40))
        self.start_layout.add_widget(question)

        btn_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint=(1, None))
        btn_box.height = dp(3*44 + 2*8)

        for cn in ["短时任务", "中时任务", "长时任务"]:
            b = Button(text=cn, font_size=dp(16), font_name="ChineseFont",
                       size_hint=(1, None), height=dp(44))
            b.bind(on_press=lambda inst, c=cn: self.choose_category_from_start(c))
            btn_box.add_widget(b)

        self.start_layout.add_widget(btn_box)

        # ---------- 内容层（默认隐藏，选择后显示） ----------
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, 1), opacity=0)
        # 顶部：当前类型 + 切换类型
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(36), spacing=dp(6))
        self.current_type_label = Label(text="当前类型：未选择",
                                        font_size=dp(14), font_name="ChineseFont",
                                        halign='left', valign='middle')
        self.current_type_label.bind(size=lambda w, s: setattr(self.current_type_label, 'text_size', s))

        self.switch_type_btn = Button(text="切换类型", font_size=dp(14), font_name="ChineseFont",
                                      size_hint=(None, None), height=dp(32), width=dp(90))
        self.switch_type_btn.bind(on_press=lambda _: self.show_start_layer())

        top_bar.add_widget(self.current_type_label)
        top_bar.add_widget(self.switch_type_btn)
        self.content_layout.add_widget(top_bar)

        # 任务显示区域
        task_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.55))
        self.task_label = Label(text="点击下方按钮获取随机任务",
                                font_size=dp(18),
                                size_hint=(1, 1),
                                font_name="ChineseFont",
                                halign='center',
                                valign='middle')
        self.task_label.bind(size=lambda w, s: setattr(self.task_label, 'text_size', s))
        task_layout.add_widget(self.task_label)

        self.content_layout.add_widget(task_layout)

        # 按钮区域
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(44), spacing=dp(8))
        self.get_task_button = Button(text="获取任务", font_size=dp(16), font_name="ChineseFont")
        self.get_task_button.bind(on_press=self.generate_task)

        self.manage_task_button = Button(text="管理任务", font_size=dp(16), font_name="ChineseFont")
        self.manage_task_button.bind(on_press=self.show_manage_task)

        button_layout.add_widget(self.get_task_button)
        button_layout.add_widget(self.manage_task_button)
        self.content_layout.add_widget(button_layout)

        # ---------- 任务管理层（默认隐藏） ----------
        self.manage_task_layout = BoxLayout(orientation='vertical', size_hint=(1, 0), opacity=0, spacing=dp(8))

        # 添加任务输入行
        add_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(6))
        self.new_task_input = TextInput(hint_text="输入任务内容…",
                                        multiline=False,
                                        font_name="ChineseFont",
                                        font_size=dp(14))
        self.add_category_spinner = Spinner(
            text="短时任务",
            values=("短时任务", "中时任务", "长时任务"),
            font_name="ChineseFont",
            size_hint=(None, None),
            height=dp(36),
            width=dp(110)
        )

        self.submit_button = Button(text="添加", font_size=dp(14), font_name="ChineseFont",
                                    size_hint=(None, None), height=dp(36), width=dp(72))
        self.submit_button.bind(on_press=self.add_new_task)

        add_row.add_widget(self.new_task_input)
        add_row.add_widget(self.add_category_spinner)
        add_row.add_widget(self.submit_button)
        self.manage_task_layout.add_widget(add_row)

        # 列表（可滚动）
        self.task_list_scroll = ScrollView(size_hint=(1, 1))
        self.task_list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=(0, dp(4)))
        self.task_list_box.bind(minimum_height=self.task_list_box.setter('height'))
        self.task_list_scroll.add_widget(self.task_list_box)
        self.manage_task_layout.add_widget(self.task_list_scroll)

        # 关闭管理
        close_manage_row = BoxLayout(size_hint=(1, None), height=dp(40))
        self.close_manage_button = Button(text="关闭管理", font_size=dp(14), font_name="ChineseFont",
                                          size_hint=(None, None), height=dp(36), width=dp(90))
        self.close_manage_button.bind(on_press=self.hide_manage_task)
        close_manage_row.add_widget(self.close_manage_button)
        self.manage_task_layout.add_widget(close_manage_row)

        # 将所有布局加入主布局（注意顺序：先内容层，再管理层在其下方）
        self.main_layout.add_widget(self.start_layout)
        self.main_layout.add_widget(self.content_layout)
        self.main_layout.add_widget(self.manage_task_layout)

        # 当前选择的类别（内部key）
        self.current_key = None

        return self.main_layout

    # ========== 数据 ==========
    def load_tasks(self):
        """加载/初始化任务库"""
        if os.path.exists(getattr(self, "data_file", "tasks.json")):
            path = getattr(self, "data_file", "tasks.json")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception:
                self.tasks = self._default_tasks()
        else:
            self.tasks = self._default_tasks()
            self.save_tasks()

        # 防御：保证三个池存在
        for k in ("short", "medium", "long"):
            self.tasks.setdefault(k, [])

    def _default_tasks(self):
        return {
            "short": ["完成10个对墙俯卧撑", "背诵5个目标语言单词", "整理书桌"],
            "medium": ["学习30分钟Python", "阅读5页重要书籍/文献", "练习15分钟吉他"],
            "long": ["写1000字文章", "打扫房间", "规划明日重要任务"]
        }

    def save_tasks(self):
        path = getattr(self, "data_file", "tasks.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    # ========== 开始层/主界面 切换 ==========
    def choose_category_from_start(self, cn_name):
        """从开始层选择类别后，进入主界面"""
        self.current_key = self.cn2key[cn_name]
        self.current_type_label.text = f"当前类型：{cn_name}"
        # 显示内容层，隐藏开始层
        self.start_layout.opacity = 0
        self.start_layout.size_hint_y = 0

        self.content_layout.opacity = 1
        self.content_layout.size_hint_y = 1

        # 同时把管理层关掉（避免残留）
        self.hide_manage_task(None)

    def show_start_layer(self):
        """重新选择任务类型"""
        self.start_layout.opacity = 1
        self.start_layout.size_hint_y = 1

        self.content_layout.opacity = 0
        self.content_layout.size_hint_y = 0

        # 管理层也隐藏
        self.hide_manage_task(None)

    # ========== 获取随机任务 ==========
    def generate_task(self, instance):
        if not self.current_key:
            self.task_label.text = "请先选择任务类型（点击“切换类型”）"
            return
        pool = self.tasks.get(self.current_key, [])
        if not pool:
            self.task_label.text = "该任务池为空，请在“管理任务”中添加"
        else:
            self.task_label.text = random.choice(pool)

    # ========== 管理任务：显隐 ==========
    def show_manage_task(self, instance):
        # 打开管理层并刷新列表
        self.manage_task_layout.opacity = 1
        self.manage_task_layout.size_hint_y = 0.8
        self.refresh_task_list()

    def hide_manage_task(self, instance):
        self.manage_task_layout.opacity = 0
        self.manage_task_layout.size_hint_y = 0

    # ========== 管理任务：增删改 ==========
    def refresh_task_list(self):
        """刷新三类任务的可编辑列表"""
        self.task_list_box.clear_widgets()

        # 以 short/medium/long 顺序展示
        for key in ("short", "medium", "long"):
            cn = self.key2cn[key]
            # 分类标题
            title = Label(text=f"[{cn}]",
                          font_name="ChineseFont",
                          font_size=dp(15),
                          size_hint=(1, None), height=dp(28),
                          markup=True, halign='left', valign='middle')
            title.bind(size=lambda w, s: setattr(title, 'text_size', s))
            self.task_list_box.add_widget(title)

            for idx, task in enumerate(self.tasks.get(key, [])):
                row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(36), spacing=dp(6))

                lbl = Label(text=task, font_name="ChineseFont", font_size=dp(14),
                            halign='left', valign='middle')
                lbl.bind(size=lambda w, s: setattr(lbl, 'text_size', s))

                edit_btn = Button(text="修改", font_name="ChineseFont", font_size=dp(12),
                                  size_hint=(None, None), height=dp(30), width=dp(60))
                delete_btn = Button(text="删除", font_name="ChineseFont", font_size=dp(12),
                                    size_hint=(None, None), height=dp(30), width=dp(60))

                # 绑定事件（注意默认参数捕获）
                edit_btn.bind(on_press=lambda _b, k=key, i=idx: self.open_edit_popup(k, i))
                delete_btn.bind(on_press=lambda _b, k=key, i=idx: self.delete_task(k, i))

                row.add_widget(lbl)
                row.add_widget(edit_btn)
                row.add_widget(delete_btn)
                self.task_list_box.add_widget(row)

    def add_new_task(self, instance):
        """管理层里添加任务"""
        text = self.new_task_input.text.strip()
        cn = self.add_category_spinner.text
        if not text or cn not in self.cn2key:
            # 简单提示
            self.task_label.text = "请输入任务内容并选择类别"
            return
        key = self.cn2key[cn]
        self.tasks[key].append(text)
        self.save_tasks()
        self.new_task_input.text = ""
        self.task_label.text = f"已添加：{text}"
        self.refresh_task_list()

    def delete_task(self, key, idx):
        """删除任务"""
        if 0 <= idx < len(self.tasks.get(key, [])):
            removed = self.tasks[key].pop(idx)
            self.save_tasks()
            self.task_label.text = f"已删除：{removed}"
            self.refresh_task_list()

    def open_edit_popup(self, key, idx):
        """弹窗修改任务文本"""
        if not (0 <= idx < len(self.tasks.get(key, []))):
            return
        old = self.tasks[key][idx]

        # 弹窗内容
        box = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        ti = TextInput(text=old, multiline=False, font_name="ChineseFont", font_size=dp(14))
        box.add_widget(ti)

        btn_row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint=(1, None), height=dp(36))
        ok_btn = Button(text="保存", font_name="ChineseFont", font_size=dp(13),
                        size_hint=(None, None), height=dp(32), width=dp(70))
        cancel_btn = Button(text="取消", font_name="ChineseFont", font_size=dp(13),
                            size_hint=(None, None), height=dp(32), width=dp(70))
        btn_row.add_widget(ok_btn)
        btn_row.add_widget(cancel_btn)
        box.add_widget(btn_row)

        popup = Popup(title="修改任务", content=box, size_hint=(0.9, None), height=dp(180))

        def do_save(_):
            new_text = ti.text.strip()
            if new_text:
                self.tasks[key][idx] = new_text
                self.save_tasks()
                self.task_label.text = "任务已修改"
                self.refresh_task_list()
            popup.dismiss()

        ok_btn.bind(on_press=do_save)
        cancel_btn.bind(on_press=lambda _: popup.dismiss())
        popup.open()


if __name__ == '__main__':
    TaskGeneratorApp().run()