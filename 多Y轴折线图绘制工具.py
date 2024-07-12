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
rcParams['font.family'] = 'SimHei'
matplotlib.use('wxAgg')


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='多坐标折线图绘制tool.exe', size=(1200,640))
        self._init_UI()

        #布局
        self.figure = mfigure.Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        self.checklist = wx.CheckListBox(self, -1, choices=[])
        self.checklist.Bind(wx.EVT_CHECKLISTBOX, self.on_checklist_change)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        sizer.Add(self.checklist, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_MENU, self.on_open_directory, self.menu_item_open)
        
    #菜单
    def _init_UI(self):
        self.menu_file = wx.Menu()
        self.menu_item_open = self.menu_file.Append(wx.ID_ANY, "打开文件", "打开指定文件")
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

    #打开文件夹
    def on_open_directory(self, event):
        dialog = wx.DirDialog(self, "Choose a directory", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.load_data_from_directory(dialog.GetPath())
        dialog.Destroy()

    #读取excel
    def load_data_from_directory(self, directory):
        self.directory = directory
        self.filenames = [os.path.splitext(f)[0] for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')]
        self.extension = [os.path.splitext(f)[1] for f in os.listdir(directory) if f.endswith('.xlsx') or f.endswith('.xls')]
        self.checklist.Set(self.filenames)

    #绘制图片
    def on_checklist_change(self, event):
        self.draw_figure()

    #具体生成过程
    def draw_figure(self):
        j = 0
        self.figure.clear()

        #颜色集
        colors = list(mcolors.TABLEAU_COLORS.keys())

        #总时间戳
        min_date = None
        max_date = None

        for i in range(len(self.filenames)):
            if self.checklist.IsChecked(i):
                df = pd.read_excel(os.path.join(self.directory, self.filenames[i])+self.extension[i])
                df.set_index('month', inplace=True)
                df.index = pd.to_datetime(df.index)

                if min_date is None or min(df.index) < min_date:
                    min_date = min(df.index)
                if max_date is None or max(df.index) > max_date:
                    max_date = max(df.index)

        total_timestamp = pd.date_range(start=min_date, end=max_date, freq='MS')
        
        ax = self.figure.add_subplot(111)
        ax.spines['left'].set_color(colors[0])
        ax.yaxis.label.set_color(colors[0])
        ax.tick_params(axis='y', colors=colors[0])

        lines = []
        labels = []

        #判定循环
        for i in range(len(self.filenames)):
            if self.checklist.IsChecked(i):
                df = pd.read_excel(os.path.join(self.directory, self.filenames[i])+self.extension[i])
                df.set_index('month', inplace=True)
                df.index = pd.to_datetime(df.index)
                df = df.reindex(total_timestamp, fill_value=np.nan)

                #孪生Y轴
                if j == 0:
                    line = ax.plot(df.index, df['value'], label=self.filenames[i], color=colors[j % len(colors)])
                    ax.set_ylabel(self.filenames[i], color=colors[j % len(colors)])
                else:
                    ax_new = ax.twinx()
                    ax_new.spines['right'].set_position(('outward', (j - 1) * 60))
                    ax_new.spines['right'].set_color(colors[j % len(colors)])
                    ax_new.yaxis.label.set_color(colors[j % len(colors)])
                    ax_new.tick_params(axis='y', colors=colors[j % len(colors)])
                    line = ax_new.plot(df.index, df['value'], label=self.filenames[i], color=colors[j % len(colors)])
                    ax_new.set_ylabel(self.filenames[i], color=colors[j % len(colors)])

                lines += line
                labels.append(self.filenames[i])

                j += 1

        #图例
        self.figure.legend(lines, labels, loc='upper right')
        self.figure.autofmt_xdate()
        self.figure.canvas.draw()
        
    #退出
    def exitapp(self, event):
        wx.CallAfter(self.Close)

    #帮助
    def helpyou(self, event):
        os.system("start " + os.getcwd() + "\\readme.txt")

    #反馈
    def feedback(self, event):
        wx.MessageBox("请联系20009100138@stu.xidian.edu.cn", "Help", wx.OK | wx.ICON_INFORMATION)

#主程序
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()