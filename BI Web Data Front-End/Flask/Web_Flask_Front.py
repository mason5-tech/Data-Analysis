#!/usr/bin/env python
# coding: utf-8


import glob,os
import sys
from io import BytesIO
from lxml import etree
import base64
import pandas as pd

files = []
path = r"C:\Users\Mma4\Desktop\TNA"
files = sorted(glob.glob(os.path.join(path, "TNA*.html"))) #, key=os.path.getmtime

htmlf=open(files[0],'r',encoding="utf-8")
htmlcont=htmlf.read()
htmlf2=open(files[1],'r',encoding="utf-8")
htmlcont2=htmlf2.read()
htmlf3=open(files[2],'r',encoding="utf-8")
htmlcont3=htmlf3.read()
htmlf4=open(files[3],'r',encoding="utf-8")
htmlcont4=htmlf4.read()

htmlf5=open(files[4],'r',encoding="utf-8")
htmlcont5=htmlf5.read()

htmlf6=open(files[5],'r',encoding="utf-8")
htmlcont6=htmlf6.read()


htmlcontMap = open(r'C:\Users\Mma4\Desktop\TNA\TNA HetMap.html','r',encoding="utf-8").read()
#htmlcont_all = htmlcont + "<br/><br/>" + htmlcont2 + "<br/><br/>" + htmlcont3 + "<br/><br/>" +  htmlcont4


df_table_data = pd.read_excel(r"C:\Users\Mma4\Desktop\TNA\excel\data.xlsx")
df_html = df_table_data.to_html()
                
df_html = df_html.replace('dataframe','table table-striped')  
df_circle = open(r'C:\Users\Mma4\Desktop\TNA\TNA_Daily.html','r',encoding="utf-8").read()
files


# In[4]:


format_html ='''
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- 上述3个meta标签*必须*放在最前面，任何其他内容都*必须*跟随其后！ -->
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="../../favicon.ico">

    <title>TNA_Failure_Performance Data Visualization & AI Group</title>

    <!-- Bootstrap core CSS -->
    <link href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">

    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="../../assets/css/ie10-viewport-bug-workaround.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="dashboard.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
    <script src="../../assets/js/ie-emulation-modes-warning.js"></script>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://cdn.bootcss.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  

<body>

<table width="1000" border="1">
<tr>
<td colspan="1" style="background-color:RGB(255, 255, 255);">'''+ htmlcont3 + '''</td>
</tr>
</table>
'''


format_html2 ='''
<table border="1" width="1000"> 
<tr>

    <th> '''+ htmlcont + '''</th>

</tr>
</table>

<br/>

<table border="1" width="1000">
<tr>

    <th>'''+ htmlcont6 + '''</th>

</tr>
</table>

<table border="1" width="1000">

<br/>

<tr>

    <th>'''+ df_circle + '''</th>

</tr>
</table>
<br/>

'''

 #   <th>'''+ htmlcont + '''</th>
 #   <th>'''+ htmlcont6+ '''</th>

format_html3 ='''
<table border="1" width="1000">
<tr>
<td colspan="1" style="background-color:RGB(255, 255, 255);">'''+ "/n /n" + htmlcont4 +'''

</td>
</tr>
	
<tr>	
<td colspan="1" style="background-color:RGB(255, 255, 255);text-align:center;">
TNA_Failure</td>
</tr>
</table>

</body>
</html>'''




# In[5]:


htmlcont_all = format_html2  #   + "<br/>" +  "<br/>"  +  format_html3  #format_html

htmlcont_all2 = htmlcontMap +  format_html3

format_html4 ='''
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <style type="text/css">
    body {transform: scale(0.8) translate(0px, 0px); }
    </style>
  
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- 上述3个meta标签*必须*放在最前面，任何其他内容都*必须*跟随其后！ -->
    <title>TNA Failure DashBoard</title>
 
    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/jquery@1.12.4/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/js/bootstrap.min.js"></script>

 
  </head>
  <body> 
  
  
    <div class="container">
        <div class="row">
            <div class="col-md-25"> 
                <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
                    <div class="panel panel-default">
                        <div class="panel-heading" role="tab" id="headingOne">
                            <h4 class="panel-title">
                                <a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
                                    1. TNA Failure Hourly 
                                </a>
                            </h4>
                        </div>
                        <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
                            <div class="panel-body">
                                <p>'''+ htmlcont5 + '''<p>

                            </div>
                        </div>
                    </div>
                    <div class="panel panel-default">
                        <div class="panel-heading" role="tab" id="headingTwo">
                            <h4 class="panel-title">
                                <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                                    2. TNA Failure Daily 
                                </a>
                            </h4>
                        </div>
                        <div id="collapseTwo" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingTwo">
                            <div class="panel-body">
                                <p>'''+ htmlcont2 +'''</p>
                            </div>
                        </div>
                    </div>
                    <div class="panel panel-default">
                        <div class="panel-heading" role="tab" id="headingThree">
                            <h4 class="panel-title">
                                <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                                    3. TNA Failure Monthly 
                                </a>
                            </h4>
                        </div>
                        <div id="collapseThree" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingThree">
                            <div class="panel-body">
                                <p> ''' + htmlcont_all + '''</p>
                            </div>
                        </div>
                    </div>
                                        <div class="panel panel-default">
                        <div class="panel-heading" role="tab" id="headingFour">
                            <h4 class="panel-title">
                                <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                                    4. TNA Failure one Year Summary 
                                </a>
                            </h4>
                        </div>
                        <div id="collapseFour" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingFour">
                            <div class="panel-body">
                                <p> ''' + htmlcont_all2 + '''</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div> 
  </body>
</html>
'''





# In[ ]:


from flask import Flask, render_template, request, redirect
from datetime import timedelta

app = Flask(__name__,template_folder= r'C:\Users\Mma4\Desktop\TNA',static_folder= r'C:\Users\Mma4\Desktop\TNA',static_url_path='/')   


app.config['DEBUG'] = False

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=0.1) # 设置缓存时间为1秒

@app.route('/', methods=['GET', 'POST']) 


def home():
    return render_template(r"C:\Users\Mma4\Desktop\TNA\index.html")

if __name__ == '__main__':

    
    app.run(host="10.86.xxx.xxx", port=8090)
