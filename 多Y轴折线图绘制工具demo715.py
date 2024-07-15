import wx
import numpy as np
import matplotlib
import matplotlib.figure as mfigure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib import rcParams
import pandas as pd
import os
import matplotlib.colors as mcolors
import matplotlib.dates as mdates  # 新增导入

rcParams['font.family'] = 'SimHei'
matplotlib.use('wxAgg')

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='多坐标折线图绘制tool.exe', size=(1440, 800))
        self._init_UI()
        # 布局
        self.figure = mfigure.Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        # 创建一个面板用于放置 CheckBox
        self.panel = wx.Panel(self, size=(1200, 160))
        self.grid_sizer = wx.GridSizer(6, 3, 5, 5)  # 6 行，3 列，水平和垂直间距为 5
        self.panel.SetSizer(self.grid_sizer)
        # 创建翻页按钮
        self.prev_button = wx.Button(self, label="上一页")
        self.next_button = wx.Button(self, label="下一页")
        self.prev_button.Bind(wx.EVT_BUTTON, self.on_prev_page)
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next_page)
        # 创建主布局
        main_sizer = wx.GridBagSizer(5, 5)
        # 创建上半部分的布局
        plot_sizer = wx.BoxSizer(wx.VERTICAL)
        plot_sizer.Add(self.canvas, 1, wx.EXPAND)
        plot_sizer.Add(self.toolbar, 0, wx.EXPAND)
        main_sizer.Add(plot_sizer, pos=(0, 0), span=(1, 9), flag=wx.EXPAND)
        main_sizer.Add(self.create_legend_panel(), pos=(0, 9), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)
        # 创建下半部分的布局
        main_sizer.Add(self.panel, pos=(1, 0), span=(1, 9), flag=wx.EXPAND)
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(self.prev_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        button_sizer.Add(self.next_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        button_sizer.AddStretchSpacer()
        main_sizer.Add(button_sizer, pos=(1, 9), span=(1, 1), flag=wx.EXPAND)
        main_sizer.AddGrowableRow(0, 3)
        main_sizer.AddGrowableRow(1, 1)
        main_sizer.AddGrowableCol(0, 9)
        main_sizer.AddGrowableCol(1, 1)
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_MENU, self.on_open_directory, self.menu_item_open)
        self.current_page = 0
        self.checkbox_states = {}
        self.file_colors = {}  # 用于存储文件对应的颜色

    # 菜单
    def _init_UI(self):
        self.menu_file = wx.Menu()
        self.menu_item_open = self.menu_file.Append(wx.ID_ANY, "打开文件夹", "打开指定文件")
        self.menu_item_exit = self.menu_file.Append(wx.ID_ANY, "退出", "退出程序")
        self.Bind(wx.EVT_MENU, self.exitapp, self.menu_item_exit)
        self.menu_help = wx.Menu()
        self.menu_item_help = self.menu_help.Append(wx.ID_ANY, "打开说明文档")
        self.menu_item_feedback = self.menu_help.Append(wx.ID_ANY, "问题反馈")
        self.menu_bar = wx.MenuBar()
        self.menu_bar.Append(self.menu_file, "文件")
        self.menu_bar.Append(self.menu_help, "帮助")
        self.Bind(wx.EVT_MENU, self.helpyou, self.menu_item_help)
        self.Bind(wx.EVT_MENU, self.feedback, self.menu_item_feedback)
        self.SetMenuBar(self.menu_bar)

    # 打开文件夹
    def on_open_directory(self, event):
        dialog = wx.DirDialog(self, "Choose a directory", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.load_data_from_directory(dialog.GetPath())
        dialog.Destroy()

    # 读取excel
    def load_data_from_directory(self, directory):
        self.figure.canvas.draw()
        self.figure.clear()
        self.clear_cache()  # 清除缓存
        self.directory = directory
        self.filenames = [f for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')]
        self.current_page = 0
        self.checkbox_states = {filename: False for filename in self.filenames}
        self.assign_colors_to_files()
        self.update_checkboxes()
        
    # 清除缓存
    def clear_cache(self):
        self.checkbox_states = {}
        self.file_colors = {}
        self.legend_sizer.Clear(True)
        self.figure.canvas.draw()
        self.figure.clear()
        
    # 分配颜色
    def assign_colors_to_files(self):
        colors = list(mcolors.TABLEAU_COLORS.values())
        for i, filename in enumerate(self.filenames):
            self.file_colors[filename] = colors[i % len(colors)]

    # 更新复选框
    def update_checkboxes(self):
        self.grid_sizer.Clear(True)
        start = self.current_page * 18
        end = start + 18
        for filename in self.filenames[start:end]:
            checkbox = wx.CheckBox(self.panel, label=filename)
            checkbox.SetValue(self.checkbox_states[filename])
            self.grid_sizer.Add(checkbox, 0, wx.EXPAND)
            checkbox.Bind(wx.EVT_CHECKBOX, self.on_checklist_change)
        self.panel.Layout()

    # 上一页
    def on_prev_page(self, event):
        if self.current_page > 0:
            self.save_checkbox_states()
            self.current_page -= 1
            self.update_checkboxes()

    # 下一页
    def on_next_page(self, event):
        if (self.current_page + 1) * 18 < len(self.filenames):
            self.save_checkbox_states()
            self.current_page += 1
            self.update_checkboxes()

    # 保存复选框状态
    def save_checkbox_states(self):
        for checkbox in self.grid_sizer.GetChildren():
            window = checkbox.GetWindow()
            self.checkbox_states[window.GetLabel()] = window.GetValue()

    # 绘制图片
    def on_checklist_change(self, event):
        self.save_checkbox_states()
        self.draw_figure()
        
    # 具体生成过程
    def draw_figure(self):
        j = 0
        self.figure.clear()
        self.legend_sizer.Clear(True)
        # 总时间戳
        min_date = None
        max_date = None
        for filename, checked in self.checkbox_states.items():
            if checked:
                df = pd.read_excel(os.path.join(self.directory, filename))
                df.set_index('month', inplace=True)
                df.index = pd.to_datetime(df.index)
                if min_date is None or min(df.index) < min_date:
                    min_date = min(df.index)
                if max_date is None or max(df.index) > max_date:
                    max_date = max(df.index)
        if min_date is None or max_date is None:
            self.figure.canvas.draw()
            return
        total_timestamp = pd.date_range(start=min_date, end=max_date, freq='MS')
        ax = self.figure.add_subplot(111)

        lines = []
        labels = []
        used_colors = []  # 用于存储实际使用的颜色
        # 设置默认的subplots_adjust参数
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0)
        # 判定循环
        for filename, checked in self.checkbox_states.items():
            if checked:
                df = pd.read_excel(os.path.join(self.directory, filename))
                df.set_index('month', inplace=True)
                df.index = pd.to_datetime(df.index)
                df = df.reindex(total_timestamp, fill_value=np.nan)
                # 孪生Y轴
                if j == 0:
                    ax.spines['left'].set_color(self.file_colors[filename])
                    ax.spines['right'].set_color('none')
                    ax.yaxis.label.set_color(self.file_colors[filename])
                    ax.tick_params(axis='y', colors=self.file_colors[filename], labelsize=12)
                    line = ax.plot(df.index, df['value'], label=filename, color=self.file_colors[filename])
                    ax.set_ylabel(os.path.splitext(filename)[0], color=self.file_colors[filename], fontsize=12, fontweight='bold')
                else:
                    ax_new = ax.twinx()
                    ax_new.spines['right'].set_position(('outward', (j - 1) * 60))
                    ax_new.spines['right'].set_color(self.file_colors[filename])
                    ax_new.spines['left'].set_color('none')
                    ax_new.yaxis.label.set_color(self.file_colors[filename])
                    ax_new.tick_params(axis='y', colors=self.file_colors[filename], labelsize=12)
                    #line = ax_new.plot(df.index, df['value'], label=filename, color=self.file_colors[filename])
                    ax_new.set_ylabel(os.path.splitext(filename)[0], color=self.file_colors[filename], fontsize=12, fontweight='bold')
                    # 压缩图表
                    self.figure.subplots_adjust(right=0.95 - (j - 1) * 0.05)
                lines += line
                labels.append(os.path.splitext(filename)[0])  # 去掉文件后缀
                used_colors.append(self.file_colors[filename])  # 记录使用的颜色
                j += 1
        # 图例
        self.update_legend_panel(labels, used_colors)  # 传递实际使用的颜色
        self.figure.autofmt_xdate()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # 新增日期格式化
        ax.tick_params(axis='x', labelsize=12)
        ax.set_xlabel('日期', fontsize=12, fontweight='bold')
        self.figure.canvas.draw()

    def create_legend_panel(self):
        self.legend_panel = wx.Panel(self, size=(120, 480))
        self.legend_sizer = wx.BoxSizer(wx.VERTICAL)
        self.legend_panel.SetSizer(self.legend_sizer)
        return self.legend_panel

    def update_legend_panel(self, labels, colors):
        self.legend_sizer.Clear(True)
        for i, label in enumerate(labels):
            color_box = wx.StaticText(self.legend_panel, label="■", style=wx.ALIGN_CENTER)
            color_box.SetForegroundColour(colors[i % len(colors)])  # 修改颜色
            text = wx.StaticText(self.legend_panel, label=label, style=wx.ALIGN_CENTER)
            text.SetForegroundColour(colors[i % len(colors)])  # 修改颜色
            font = text.GetFont()
            font.SetPointSize(8)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            text.SetFont(font)
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(color_box, 0, wx.ALIGN_CENTER | wx.ALL, 5)
            hbox.Add(text, 0, wx.ALIGN_CENTER | wx.ALL, 5)
            self.legend_sizer.Add(hbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.legend_panel.Layout()

    # 退出
    def exitapp(self, event):
        wx.CallAfter(self.Close)

    # 帮助
    def helpyou(self, event):
        os.system("start " + os.getcwd() + "\\readme.txt")

    # 反馈
    def feedback(self, event):
        wx.MessageBox("请联系20009100138@stu.xidian.edu.cn", "Help", wx.OK | wx.ICON_INFORMATION)

# 主程序
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()