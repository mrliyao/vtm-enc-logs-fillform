from tkinter import Tk
from tkinter import filedialog, messagebox
import os, sys
import re

# 一些正则表达式
pattenLogName = re.compile(r'enc_\w+\.log')
pattenSeqName = re.compile(r'enc_(\w+)_(lowdelay_P|lowdelay|randomaccess|intra)_\w+\.log')
pattenQp = re.compile(r'Q(\d{1,3}).log')
pattenTestName = re.compile(r'((lowdelay_P|lowdelay|randomaccess|intra)\w+)_Q\d+')
pattenLogBDStas = re.compile(r'\b\d+\s*a\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\b')
pattenLogTimeStas = re.compile(r'\bTotal Time:\s*(\d+\.\d+)[^0-9]+(\d+\.\d+)\b')

def getInfoFromLog(logPath):
    with open(logPath) as log:
        logData = log.read(1000000)
        if pattenLogBDStas.search(logData):
            bitRate = pattenLogBDStas.search(logData).group(1)
            yPsnr = pattenLogBDStas.search(logData).group(2)
            uPsnr = pattenLogBDStas.search(logData).group(3)
            vPsnr = pattenLogBDStas.search(logData).group(4)
            yuvPsnr = pattenLogBDStas.search(logData).group(5)
            encTime = pattenLogTimeStas.search(logData).group(1)
            return (bitRate, yPsnr, uPsnr, vPsnr, yuvPsnr, encTime)
        else:
            return ('', '', '', '', '', '')


if __name__ == '__main__':
    # 选择log文件夹
    print("请选择Log文件夹...")
    root = Tk()
    root.wm_attributes('-topmost', True)
    # root.after_idle(root.wm_attributes, '-topmost', False)
    root.withdraw()
    dir = filedialog.askdirectory(initialdir=os.getcwd(), title="请选择 Log 文件夹")
    if dir == '':
        messagebox.showinfo(title="提示", message="未选中任何文件夹")
        sys.exit(0)
    if os.path.isdir(dir):
        logNames = os.listdir(dir)
    else:
        messagebox.showerror(title="错误", message="该路径不是一个文件夹")
        sys.exit(-1)

    # 检验文件夹下是否存在合规的log文件，保留合规的log文件名称
    legalLogNames = []
    emptyFlag = True
    for logName in logNames:
        res = pattenLogName.match(logName)
        if res:
            emptyFlag = False
            legalLogNames.append(logName)
    if emptyFlag:
        messagebox.showerror(title="错误", message="所选文件夹内无符合规范的 Log 文件")
        sys.exit(0)

    print("处理中...")
    logInfo = {}
    #遍历得到所有的测试配置
    for logName in legalLogNames:
        cfgName = pattenTestName.search(logName).group(1)
        logInfo[cfgName] = {}
    # 遍历得到每个测试配置下所有的序列名字
    for cfgName in logInfo.keys():
        for logName in legalLogNames:
            if cfgName in logName:
                seqName = pattenSeqName.match(logName).group(1)
                logInfo[cfgName][seqName] = {}
    # 遍历得到每个测试配置下、每个序列名称下所有的QP
    for cfgName in logInfo.keys():
        for seqName in logInfo[cfgName].keys():
            for logName in legalLogNames:
                if cfgName in logName and seqName in logName:
                    qp = pattenQp.search(logName).group(1)
                    logInfo[cfgName][seqName][qp] = {}

   # 遍历所有的log，保存信息到对应的字典
    for logName in legalLogNames:
        cfgName = pattenTestName.search(logName).group(1)
        seqName = pattenSeqName.match(logName).group(1)
        qp = pattenQp.search(logName).group(1)
        (bitRate, yPsnr, uPsnr, vPsnr, yuvPsnr, encTime) = getInfoFromLog(dir + '/' + logName)
        logInfo[cfgName][seqName][qp]['bitRate'] = bitRate
        logInfo[cfgName][seqName][qp]['yPsnr'] = yPsnr
        logInfo[cfgName][seqName][qp]['uPsnr'] = uPsnr
        logInfo[cfgName][seqName][qp]['vPsnr'] = vPsnr
        logInfo[cfgName][seqName][qp]['yuvPsnr'] = yuvPsnr
        logInfo[cfgName][seqName][qp]['encTime'] = encTime

    # 保存至文件
    for cfgName in logInfo.keys():
        outFormPath = dir + '/form-' + cfgName + '.csv'
        with open(outFormPath, 'w') as f:
            f.write(cfgName + '\n')
            for seqName in logInfo[cfgName].keys():
                f.write(seqName + '\n')
                qpList = []
                for qp in logInfo[cfgName][seqName]:
                    qpList.append(int(qp))
                    qpList.sort()
                for qp in qpList:
                    qp = str(qp)
                    f.write(qp + ',')
                    f.write(logInfo[cfgName][seqName][qp]['bitRate'] + ',')
                    f.write(logInfo[cfgName][seqName][qp]['yPsnr'] + ',')
                    f.write(logInfo[cfgName][seqName][qp]['uPsnr'] + ',')
                    f.write(logInfo[cfgName][seqName][qp]['vPsnr'] + ',')
                    # f.write(logInfo[cfgName][seqName][qp]['yuvPsnr'] + ',')
                    f.write(logInfo[cfgName][seqName][qp]['encTime'] + '\n')

    # 打开文件夹
    print("处理完成！")
    dir = dir.replace('/', '\\')
    os.system("explorer.exe %s" % dir)

