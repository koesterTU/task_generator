import kivy
import json
import os
import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# 注册中文字体（确保fonts文件夹与main.py同目录，或修改路径）
LabelBase.register(name="ChineseFont", fn_regular="fonts/SourceHanSansSC-Regular.OTF")

kivy.require('2.1.0')

# JSON文件路径（存储任务数据）
TASKS_JSON_PATH = "tasks.json"

# 默认任务池（无JSON文件时使用）
DEFAULT_TASKS = {
    "short_tasks": [  # 短任务（5分钟左右）
        "完成10个对墙俯卧撑",
        "背诵5个目标语言单词",
        "做一次动态激活",
        "清理手机相册（最近10张）",
        "进行10分钟正念冥想"
    ],
    "medium_tasks": [  # 中任务（30分钟）
        "写一篇100字的目标语言短文",
        "练习15分钟吉他",
        "学习30分钟Python",
        "整理书桌",
        "阅读5页重要书籍/文献"
    ],
    "long_tasks": [  # 长任务（1小时起步）
        "打扫房间（全面整理）",
        "规划明日重要任务（详细清单）",
        "写1000字文章",
        "完成一个Python小项目模块",
        "系统整理电脑文件（分类归档）"
    ]
}


class TaskGeneratorApp(App):
    def build(self):
        # 初始化：读取任务数据（无文件则用默认）
        self.tasks = self.load_tasks_from_json()
        
        # 主布局（垂直排列）
        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # 1. 顶部：管理任务按钮（右上角）
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.manage_btn = Button(
            text="管理任务",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.5, 0.5, 0.9, 1),
            size_hint=(0.2, 1)
        )
        self.manage_btn.bind(on_press=self.open_task_management)
        top_layout.add_widget(Label(size_hint=(0.8, 1)))  # 占位，将按钮推到右侧
        top_layout.add_widget(self.manage_btn)
        self.main_layout.add_widget(top_layout)
        
        # 2. 任务显示区域（初始显示选择任务池的提示）
        self.task_label = Label(
            text="你现在想进行什么任务？",
            font_name="ChineseFont",
            font_size=28,
            size_hint=(1, 0.5),
            halign='center',
            valign='middle'
        )
        self.main_layout.add_widget(self.task_label)
        
        # 3. 任务池选择按钮（短/中/长）
        pool_btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=20)
        self.short_pool_btn = Button(
            text="短任务（5min）",
            font_name="ChineseFont",
            font_size=20,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.medium_pool_btn = Button(
            text="中任务（30min）",
            font_name="ChineseFont",
            font_size=20,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        self.long_pool_btn = Button(
            text="长任务（1h+）",
            font_name="ChineseFont",
            font_size=20,
            background_color=(0.8, 0.4, 0.2, 1)
        )
        # 绑定按钮事件（选择任务池并生成随机任务）
        self.short_pool_btn.bind(on_press=lambda x: self.select_pool_and_generate("short_tasks"))
        self.medium_pool_btn.bind(on_press=lambda x: self.select_pool_and_generate("medium_tasks"))
        self.long_pool_btn.bind(on_press=lambda x: self.select_pool_and_generate("long_tasks"))
        pool_btn_layout.add_widget(self.short_pool_btn)
        pool_btn_layout.add_widget(self.medium_pool_btn)
        pool_btn_layout.add_widget(self.long_pool_btn)
        self.main_layout.add_widget(pool_btn_layout)
        
        # 4. 再次生成按钮（初始隐藏，选择任务池后显示）
        self.regenerate_btn = Button(
            text="再换一个",
            font_name="ChineseFont",
            font_size=20,
            background_color=(0.9, 0.6, 0.2, 1),
            size_hint=(1, 0.15),
            opacity=0  # 默认隐藏
        )
        self.regenerate_btn.bind(on_press=self.regenerate_current_pool_task)
        self.main_layout.add_widget(self.regenerate_btn)
        
        # 记录当前选中的任务池（初始为None）
        self.current_pool = None
        
        return self.main_layout

    def load_tasks_from_json(self):
        """从JSON文件读取任务，无文件则返回默认任务并创建文件"""
        if os.path.exists(TASKS_JSON_PATH):
            try:
                with open(TASKS_JSON_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # 文件损坏或读取失败，用默认任务覆盖
                self.save_tasks_to_json(DEFAULT_TASKS)
                return DEFAULT_TASKS
        else:
            # 无文件，创建并写入默认任务
            self.save_tasks_to_json(DEFAULT_TASKS)
            return DEFAULT_TASKS

    def save_tasks_to_json(self, tasks_data):
        """将任务数据写入JSON文件"""
        try:
            with open(TASKS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=4)
            return True
        except IOError:
            self.show_popup("保存失败", "无法写入任务文件，请检查权限！")
            return False

    def select_pool_and_generate(self, pool_key):
        """选择任务池并生成随机任务"""
        self.current_pool = pool_key
        # 显示"再换一个"按钮
        self.regenerate_btn.opacity = 1
        # 生成随机任务
        self.generate_task()

    def generate_task(self):
        """从当前选中的任务池生成随机任务"""
        if not self.current_pool:
            return
        pool_tasks = self.tasks[self.current_pool]
        if not pool_tasks:
            self.task_label.text = "当前任务池为空，请先添加任务！"
            return
        random_task = random.choice(pool_tasks)
        self.task_label.text = f"随机任务：\n{random_task}"

    def regenerate_current_pool_task(self, instance):
        """重新生成当前任务池的任务"""
        self.generate_task()

    def open_task_management(self, instance):
        """打开任务管理弹窗（选择要管理的任务池）"""
        # 管理弹窗布局
        manage_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        manage_layout.add_widget(Label(
            text="选择要管理的任务池",
            font_name="ChineseFont",
            font_size=22,
            halign='center'
        ))
        
        # 任务池选择按钮
        short_manage_btn = Button(
            text="管理短任务池",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        medium_manage_btn = Button(
            text="管理中任务池",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        long_manage_btn = Button(
            text="管理长任务池",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.8, 0.4, 0.2, 1)
        )
        # 绑定事件：打开对应任务池的管理界面
        short_manage_btn.bind(on_press=lambda x: self.show_pool_management("short_tasks"))
        medium_manage_btn.bind(on_press=lambda x: self.show_pool_management("medium_tasks"))
        long_manage_btn.bind(on_press=lambda x: self.show_pool_management("long_tasks"))
        
        manage_layout.add_widget(short_manage_btn)
        manage_layout.add_widget(medium_manage_btn)
        manage_layout.add_widget(long_manage_btn)
        
        # 创建弹窗
        self.manage_popup = Popup(
            title="任务管理",
            content=manage_layout,
            size_hint=(0.8, 0.6),
            title_font="ChineseFont",
            title_size=20 #正确属性名
        )
        self.manage_popup.open()

    def show_pool_management(self, pool_key):
        """显示指定任务池的管理界面（查看/添加/修改/删除任务）"""
        # 关闭上一级弹窗
        self.manage_popup.dismiss()
        
        # 任务池名称映射（用于显示）
        pool_names = {
            "short_tasks": "短任务池（5min）",
            "medium_tasks": "中任务池（30min）",
            "long_tasks": "长任务池（1h+）"
        }
        pool_name = pool_names[pool_key]
        pool_tasks = self.tasks[pool_key]
        
        # 1. 管理界面主布局（垂直）
        pool_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 2. 标题和添加任务区域
        top_manage_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)
        top_manage_layout.add_widget(Label(
            text=pool_name,
            font_name="ChineseFont",
            font_size=22,
            halign='center'
        ))
        # 添加任务按钮
        add_task_btn = Button(
            text="+ 添加任务",
            font_name="ChineseFont",
            font_size=16,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint=(0.3, 1)
        )
        add_task_btn.bind(on_press=lambda x: self.add_task_to_pool(pool_key))
        top_manage_layout.add_widget(add_task_btn)
        pool_layout.add_widget(top_manage_layout)
        
        # 3. 任务列表（带滚动条）
        scroll_view = ScrollView(size_hint=(1, 0.7))
        task_grid = GridLayout(cols=1, spacing=10, size_hint=(1, None))
        task_grid.bind(minimum_height=task_grid.setter('height'))  # 自适应高度
        
        # 添加任务项（每个任务带"修改"/"删除"按钮）
        if not pool_tasks:
            task_grid.add_widget(Label(
                text="当前任务池为空，点击'添加任务'按钮添加",
                font_name="ChineseFont",
                font_size=18,
                halign='center',
                color=(0.8, 0.2, 0.2, 1)
            ))
        else:
            for idx, task in enumerate(pool_tasks):
                task_item_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=60)
                # 任务文本
                task_label = Label(
                    text=f"{idx+1}. {task}",
                    font_name="ChineseFont",
                    font_size=18,
                    halign='left',
                    valign='middle',
                    size_hint=(0.6, 1)
                )
                # 修改按钮
                edit_btn = Button(
                    text="修改",
                    font_name="ChineseFont",
                    font_size=16,
                    background_color=(0.2, 0.6, 0.9, 1),
                    size_hint=(0.2, 1)
                )
                edit_btn.bind(on_press=lambda x, i=idx: self.edit_pool_task(pool_key, i))
                # 删除按钮
                delete_btn = Button(
                    text="删除",
                    font_name="ChineseFont",
                    font_size=16,
                    background_color=(0.8, 0.2, 0.2, 1),
                    size_hint=(0.2, 1)
                )
                delete_btn.bind(on_press=lambda x, i=idx: self.delete_pool_task(pool_key, i))
                
                task_item_layout.add_widget(task_label)
                task_item_layout.add_widget(edit_btn)
                task_item_layout.add_widget(delete_btn)
                task_grid.add_widget(task_item_layout)
        
        scroll_view.add_widget(task_grid)
        pool_layout.add_widget(scroll_view)
        
        # 4. 创建任务池管理弹窗
        self.pool_manage_popup = Popup(
            title=f"管理 {pool_name}",
            content=pool_layout,
            size_hint=(0.9, 0.8),
            title_font="ChineseFont",
            title_size=20
        )
        self.pool_manage_popup.open()

    def add_task_to_pool(self, pool_key):
        """添加任务到指定任务池（弹窗输入）"""
        # 输入布局
        input_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        input_layout.add_widget(Label(
            text="输入新任务内容",
            font_name="ChineseFont",
            font_size=20,
            halign='center'
        ))
        task_input = TextInput(
            hint_text="例如：完成10个俯卧撑",
            font_name="ChineseFont",
            font_size=18,
            multiline=False,
            size_hint=(1, 0.3)
        )
        
        # 按钮布局
        btn_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 0.2))
        confirm_btn = Button(
            text="确认添加",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        cancel_btn = Button(
            text="取消",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        # 绑定事件
        def on_confirm(instance):
            new_task = task_input.text.strip()
            if new_task:
                self.tasks[pool_key].append(new_task)
                self.save_tasks_to_json(self.tasks)
                self.show_popup("添加成功", f"已添加任务：{new_task}")
                add_popup.dismiss( )  #关闭“添加任务”弹窗
                # 刷新任务池管理界面
                self.pool_manage_popup.dismiss()
                self.show_pool_management(pool_key)
            else:
                self.show_popup("输入错误", "任务内容不能为空！")
        
        confirm_btn.bind(on_press=on_confirm)
        cancel_btn.bind(on_press=lambda x: add_popup.dismiss())
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        input_layout.add_widget(task_input)
        input_layout.add_widget(btn_layout)
        
        # 创建添加弹窗
        add_popup = Popup(
            title="添加新任务",
            content=input_layout,
            size_hint=(0.8, 0.6),
            title_font="ChineseFont",
            title_size=20
        )

        # -------------------------- 新增：键盘监听逻辑 --------------------------
        from kivy.core.window import Window
        original_y = input_layout.y  # 记录输入布局初始y坐标
    
        def on_keyboard_show(*args):
               # 键盘弹出时，输入布局向上偏移（偏移量为键盘高度的80%，可调整）
               keyboard_height = args[1].height
               input_layout.y = original_y + keyboard_height * 0.8
    
        def on_keyboard_hide(*args):
               # 键盘收起时，恢复输入布局初始位置
               input_layout.y = original_y

        # 绑定键盘事件
        Window.bind(on_keyboard_show=on_keyboard_show)
        Window.bind(on_keyboard_hide=on_keyboard_hide)
    
        # 弹窗关闭时，解绑键盘事件（避免内存泄漏）
        def on_popup_dismiss(*args):
               Window.unbind(on_keyboard_show=on_keyboard_show)
               Window.unbind(on_keyboard_hide=on_keyboard_hide)
    
        add_popup.bind(on_dismiss=on_popup_dismiss)
        # ------------------------------------------------------------------------
    
        add_popup.open()


    def edit_pool_task(self, pool_key, task_index):
        """修改任务池中的指定任务（弹窗输入）"""
        current_task = self.tasks[pool_key][task_index]
        # 输入布局
        input_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        input_layout.add_widget(Label(
            text="修改任务内容",
            font_name="ChineseFont",
            font_size=20,
            halign='center'
        ))
        task_input = TextInput(
            text=current_task,
            font_name="ChineseFont",
            font_size=18,
            multiline=False,
            size_hint=(1, 0.3)
        )
        
        # 按钮布局
        btn_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 0.2))
        confirm_btn = Button(
            text="确认修改",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        cancel_btn = Button(
            text="取消",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        # 绑定事件
        def on_confirm(instance):
            modified_task = task_input.text.strip()
            if modified_task:
                self.tasks[pool_key][task_index] = modified_task
                self.save_tasks_to_json(self.tasks)
                self.show_popup("修改成功", f"任务已更新为：{modified_task}")
                edit_popup.dismiss( )  #关闭“修改任务”弹窗
                # 刷新任务池管理界面
                self.pool_manage_popup.dismiss()
                self.show_pool_management(pool_key)
            else:
                self.show_popup("输入错误", "任务内容不能为空！")
        
        confirm_btn.bind(on_press=on_confirm)
        cancel_btn.bind(on_press=lambda x: edit_popup.dismiss())
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        input_layout.add_widget(task_input)
        input_layout.add_widget(btn_layout)
        
        # 创建修改弹窗
        edit_popup = Popup(
            title="修改任务",
            content=input_layout,
            size_hint=(0.8, 0.6),
            title_font="ChineseFont",
            title_size=20
        )
    
        # -------------------------- 新增：键盘监听逻辑 --------------------------
        from kivy.core.window import Window
        original_y = input_layout.y  # 记录输入布局初始y坐标
    
        def on_keyboard_show(*args):
               keyboard_height = args[1].height
               input_layout.y = original_y + keyboard_height * 0.8
    
        def on_keyboard_hide(*args):
               input_layout.y = original_y
    
        Window.bind(on_keyboard_show=on_keyboard_show)
        Window.bind(on_keyboard_hide=on_keyboard_hide)
    
        def on_popup_dismiss(*args):
               Window.unbind(on_keyboard_show=on_keyboard_show)
               Window.unbind(on_keyboard_hide=on_keyboard_hide)
    
        edit_popup.bind(on_dismiss=on_popup_dismiss)
        # ------------------------------------------------------------------------
    
        edit_popup.open()
        
        
    def delete_pool_task(self, pool_key, task_index):
        """删除任务池中的指定任务（二次确认）"""
        task_to_delete = self.tasks[pool_key][task_index]
        # 确认布局
        confirm_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        confirm_layout.add_widget(Label(
            text=f"确定要删除任务吗？\n\n{task_to_delete}",
            font_name="ChineseFont",
            font_size=18,
            halign='center',
            color=(0.8, 0.2, 0.2, 1)
        ))
        
        # 按钮布局
        btn_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 0.3))
        confirm_btn = Button(
            text="确认删除",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        cancel_btn = Button(
            text="取消",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        
        # 绑定事件
        def on_confirm(instance):
            del self.tasks[pool_key][task_index]
            self.save_tasks_to_json(self.tasks)
            self.show_popup("删除成功", "任务已从任务池移除")
            delete_popup.dismiss( ) # 关闭“删除确认”弹窗
            # 刷新任务池管理界面
            self.pool_manage_popup.dismiss()
            self.show_pool_management(pool_key)
        
        confirm_btn.bind(on_press=on_confirm)
        cancel_btn.bind(on_press=lambda x: delete_popup.dismiss())
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        confirm_layout.add_widget(btn_layout)
        
        # 创建删除确认弹窗
        delete_popup = Popup(
            title="删除任务",
            content=confirm_layout,
            size_hint=(0.8, 0.5),
            title_font="ChineseFont",
            title_size=20
        )
        delete_popup.open()

    def show_popup(self, title, content):
        """通用弹窗（显示提示信息）"""
        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        popup_layout.add_widget(Label(
            text=content,
            font_name="ChineseFont",
            font_size=18,
            halign='center'
        ))
        close_btn = Button(
            text="关闭",
            font_name="ChineseFont",
            font_size=18,
            background_color=(0.5, 0.5, 0.9, 1),
            size_hint=(0.4, 0.3)
        )
        
        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(0.7, 0.4),
            title_font="ChineseFont",
            title_size=20,
            auto_dismiss=False  # 禁止点击外部关闭
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        popup_layout.add_widget(close_btn)
        popup.open()


if __name__ == '__main__':
    TaskGeneratorApp().run()