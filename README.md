**处理zabbix图形界面乱码问题**

+ 在windows目录C:\Windows\Fonts下找到楷体常规
+ 上传至zabbix的fonts目录，如/usr/share/zabbix/fonts
+ 更改其名字为mv SIMKAI.TTF kaiti.tt
* 修改vim /usr/share/zabbix/include/defines.inc.php文件，全文修改graphfont为kaiti，:%s/graphfont/kaiti/g
