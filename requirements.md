# 视频时长筛选器需求文档

## 项目概述

视频时长筛选器是一个用于筛选和移动指定时长视频文件的工具，旨在帮助用户快速整理视频文件库，将符合特定时长要求的视频文件移动到指定位置。

## 功能需求

### 核心功能

1. **视频文件筛选**
   - 根据用户设定的最大时长（秒）筛选视频文件
   - 支持递归扫描源文件夹及其所有子文件夹
   - 支持多种常见视频格式（mp4, avi, mkv, mov, wmv, flv, webm）

2. **文件移动**
   - 将符合条件的视频文件从源文件夹移动到目标文件夹
   - 保持原有的文件夹结构，便于追溯视频来源
   - 移动过程中自动创建必要的目录结构

3. **用户界面**
   - 提供图形用户界面（GUI），操作简单直观
   - 包含源文件夹和目标文件夹选择功能
   - 提供最大时长设置输入框
   - 显示处理进度条和状态信息
   - 提供实时日志显示区域
   - 支持中断处理过程

4. **日志记录**
   - 记录程序运行过程中的关键操作和错误信息
   - 将日志保存到本地文件，便于后续查看和问题排查
   - 在界面上实时显示处理日志

## 技术规格

### 开发环境

- 编程语言：Python 3.x
- 图形界面：Tkinter

### 依赖项

- **必选依赖**：以下依赖项至少需要安装一个
  - moviepy（推荐，视频处理更稳定）
  - opencv-python（备选，作为替代方案）

- **内置依赖**
  - os, sys, shutil：文件操作
  - tkinter：GUI界面
  - threading：多线程处理
  - logging：日志记录
  - datetime：日期时间处理

### 性能要求

- 能够处理大量视频文件
- 在处理过程中保持界面响应
- 支持中断长时间运行的处理过程

## 用户场景

### 场景一：整理短视频集合

用户有一个包含各种时长视频的文件夹，希望将所有30秒以内的短视频移动到另一个文件夹中进行专门处理或分享。

### 场景二：筛选预览视频

用户需要从大量视频素材中筛选出所有时长不超过2分钟的预览视频，以便快速浏览内容。

### 场景三：整理教学视频

教育工作者需要将一系列教学视频按照时长进行分类，将简短的概念讲解视频（不超过5分钟）单独归类。

## 界面设计要求

- 简洁明了的用户界面
- 清晰的操作指引和说明
- 实时反馈处理进度和状态
- 合理的控件布局和间距
- 适当的错误提示和警告信息

## 错误处理

- 处理无法读取的视频文件
- 处理文件移动过程中的权限或路径错误
- 处理依赖库缺失的情况
- 提供友好的错误提示和解决建议

## 未来扩展可能

- 添加复制（而非移动）文件的选项
- 支持更多视频格式
- 添加按视频分辨率筛选的功能
- 添加批处理模式，支持命令行参数
- 多语言支持