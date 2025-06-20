import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput #**加入输入文本框
from kivy.core.text import LabelBase # *新增字体注册模块
import random

# *新增：注册中文字体
LabelBase.register(name="ChineseFont", fn_regular="fonts/SourceHanSansSC-Regular.OTF") #*替换文字路径

kivy.require('2.1.0')

class TaskGeneratorApp(App):
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # 任务显示区域
        task_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
        self.task_label = Label(text="点击下方按钮获取随机任务", 
                              font_size=28,
                              size_hint=(1, 0.8),
                              text_size=(None, None),#**移除self.width, 该用自动适应
                              font_name="ChineseFont", 
                              halign='center',
                              valign='middle')
        task_layout.add_widget(self.task_label)
        
        # 按钮区域
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        
        # 获取随机任务按钮
        self.get_task_button = Button(text="获取随机任务", 
                                    font_size=20,
                                    font_name="ChineseFont",
                                    background_color=(0.2, 0.6, 0.9, 1))
        self.get_task_button.bind(on_press=self.generate_task)
        
        # 添加任务按钮
        self.add_task_button = Button(text="添加新任务", 
                                    font_size=20,
                                    font_name="ChineseFont", 
                                    background_color=(0.2, 0.8, 0.2, 1))
        self.add_task_button.bind(on_press=self.show_add_task)
        
        
        button_layout.add_widget(self.get_task_button)
        button_layout.add_widget(self.add_task_button)
        
        # 添加任务区域（默认隐藏）
        self.add_task_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=10, opacity=0)
        
        self.new_task_input = TextInput(hint_text="输入新任务...", 
                                      multiline=False,
                                      font_name="ChineseFont",
                                      font_size=20,
                                      input_type='text',
                                      write_tab=False
                                      )  #**解决无法输入汉字的问题
        
        self.submit_button = Button(text="添加", 
                                  font_size=20,
                                  font_name="ChineseFont",
                                  background_color=(0.2, 0.6, 0.9, 1))
        self.submit_button.bind(on_press=self.add_new_task)
        
        self.cancel_button = Button(text="取消", 
                                  font_size=20,
                                  font_name="ChineseFont",
                                  background_color=(0.8, 0.2, 0.2, 1))
        self.cancel_button.bind(on_press=self.hide_add_task)
        
        input_layout = BoxLayout(orientation='horizontal', spacing=10)
        input_layout.add_widget(self.new_task_input)
        input_layout.add_widget(self.submit_button)
        
        self.add_task_layout.add_widget(input_layout)
        self.add_task_layout.add_widget(self.cancel_button)
        
        # 将所有布局添加到主布局
        main_layout.add_widget(task_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.add_task_layout)
        
        # 定义任务库
        self.tasks = [
            "完成10个对墙俯卧撑",
            "背诵5个目标语言单词",
            "写一篇100字的目标语言短文",
            "做一次动态激活",
            "练习15分钟吉他",
            "打扫房间",
            "学习30分钟Python",
            "整理书桌",
            "规划明日重要任务",
            "清理手机相册",
            "阅读5页重要书籍/文献",
            "进行10min正念冥想",
            "写1000字文章"
        ]

        return main_layout
    
    def generate_task(self, instance):
        # 从任务库中随机选择一个任务
        random_task = random.choice(self.tasks)
        # 更新标签文本
        self.task_label.text = random_task
    
    def show_add_task(self, instance):
        # 显示添加任务区域
        self.add_task_layout.opacity = 1
        self.add_task_layout.size_hint_y = 0.3
        self.get_task_button.disabled = True
        self.add_task_button.disabled = True
    
    def hide_add_task(self, instance):
        # 隐藏添加任务区域
        self.add_task_layout.opacity = 0
        self.add_task_layout.size_hint_y = 0
        self.get_task_button.disabled = False
        self.add_task_button.disabled = False
        self.new_task_input.text = ""
    
    def add_new_task(self, instance):
        # 添加新任务到任务库
        new_task = self.new_task_input.text.strip()
        if new_task:
            self.tasks.append(new_task)
            self.task_label.text = f"已添加任务: {new_task}"
        self.hide_add_task(instance)

if __name__ == '__main__':
    TaskGeneratorApp().run()