# 使用指南
所有package均从vnpy的github下载
建议使用conda创建虚拟python环境
```shell
conda create --name quant_trade python=3.11.12
```
激活虚拟环境
```shell
conda activate quant_trade
```
安装依赖
```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 其中ta-lib需要手动安装
cd depend
# pip安装 ta_lib-0.6.3-cp311-cp311-win_amd64.whl
pip install ta_lib-0.6.3-cp311-cp311-win_amd64.whl
```

检查依赖是否安装成功
```shell
pip list
```