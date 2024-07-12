中文介绍：

此文件介绍了项目运行后需要的输入文件格式。
项目输入需要选择一个文件夹，自动读取文件夹中的所有Excel表格文件，兼容xls和slsx两种文件格式。文件名兼容中文和英文。
每个Excel表格文件读取第一个表单的前两列数据，第一列数据代表时间，第二列数据代表数值。第一行内容不读取，其余未解释的内容不读取。

推荐的格式：新建一个文件夹，其中存有不同指标的Excel表格文件，每个文件的名称就是指标的名称。每个文件内只有一个表单，此表单只有两列数据，第一列是时间，第二列是数值。
Github上的Excel_Files文件夹就是输入数据样例。



English Introduction:

This document introduces the input file format required after the project runs.
The project input requires selecting a folder and automatically reading all Excel spreadsheet files in the folder, compatible with both xls and slsx file formats. The file name is compatible with both Chinese and English.
Each Excel spreadsheet file reads the first two columns of data from the first form, with the first column representing time and the second column representing numerical values. The first line of content is not read, and the remaining unexplained content is not read.

Recommended format: Create a new folder containing Excel spreadsheet files for different indicators, with each file named after the indicator. Each file contains only one form, which has two columns of data: the first column is time and the second column is numerical value.
The Excel Files folder on Github is the input data sample.
