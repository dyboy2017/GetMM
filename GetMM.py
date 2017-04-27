#这是主文件 This is the main file!
#coding: utf-8
import argparse #argparse模块的作用是用于解析命令行参数
import urllib
import requests#urllib的request模块抓取URL内容
import os#系统啦

from MuchThread import MuchThread #引入多线程
from urllib import request #引入request
from bs4 import BeautifulSoup #BeautifulSoup 4.x引入，beautifulsoup可以从HTML或XML文件中提取(解析)数据的Python库

#得到网页HTML的内容,源代码 get_html(URL)
def get_html(url_address):
    #构造请求头的客户端headers
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    #urllib.request.Request(url,date,headers)
    #获取网页
    req = urllib.request.Request(url=url_address,headers=headers)
    return urllib.request.urlopen(req)

#小东留名！啊哈哈-www.dyboy.cn
#get_soup(html) 将urlib获取的html封装到bs中，方便文档处理，返回bs的一个实例
def get_soup(html):
    #判断是否成功获取了网页
    if html == None:
        return None
    #使用方法BeautifulSoup(markup, "html.parser")
    #html.read(),读取当前对象html文档的内容,html转化为unicode编码的，解析成xml
    return BeautifulSoup(html.read(), "html.parser")


#get_img_dirs(soup),获取所有相册标题&链接，参数为bs的一个实例，返回字典（key:标题，value:内容）
def get_img_dirs(soup):
    #判断对象是否存在
    if soup == None:
        return None
    #bs.find(tag,attributes,recursive,text,keywords)函数
    #bs.findAll(tag,attributes,recursive,text,limit,keywords)
    #find(id="pic")find(name,attrs,recursive,text,**wargs)
    '''这些参数相当于过滤器一样可以进行筛选处理，不同的参数过滤可以应用到以下情况：
    查找标签，基于name参数
    查找文本，基于text参数
    基于正则表达式的查找
    查找标签的属性，以及基于attrs参数
    基于函数的查找'''
    # soup.find(id="pins").findAll(name='li')，找到id="pins"，下所有的li标签
    lis = soup.find(id="pins").findAll(name='li') # findAll(name='a') # attrs={'class':'lazy'}
    if lis != None:
        img_dirs = {};#新的存储相册目录字典
        for li in lis:
            links = li.find('a')#找到li标签下的最近一个a标签内容
            alt = links.find('img').attrs['alt']#在a标签内容中找到最近的img的属性alt的值
            site = links.attrs['href']#在a标签下的属性href值为相册地址
            img_dirs[alt] = site;#alt相册名字，site相册链接
        print(img_dirs)#输出获取到的相册字典
        return img_dirs#返回字典

#获取相册中的内页图片get_album_num(links, dir_soup),links:链接，get_soup:一个bs对象，返回图片总数
def get_album_num(links, dir_soup):
    ##############后期修改的地方#######################
    #找到links页面下属性class为pagenavi的div
    divs = dir_soup.findAll(name='div', attrs={'class':'pagenavi'})
    navi = divs[0]#有相同的取第一个
    code = navi['class']#code 为 div下class对应的值-pagenavi

    links2 = navi.findAll(name='a')
    if links2 == None:
        return None
    a = []
    url_list = []
    #循环获取div下的数字
    for link in links2:
        h = str(link['href'])#获取links2下的href的属性值-网址，转化为字符串便于使用str.replace(old, new[, max])
        n = h.replace(links+"/", "")#得到字符数字
        #异常处理，把int(n)加到a[]的末尾
        try:
            a.append(int(n))
        except Exception as e:
            print(e)
            
    _max = max(a)#获取a[]下最大的数字，即为最大页数
    for i in range(1, _max):
        u = str(links+"/"+str(i))#构造页面链接
        url_list.append(u)#添加到链接列表
    return url_list#返回链接列表

#获取相册下的图片download_img_from_page(name, page_url)
def download_img_from_page(name, page_url):
    dir_html = get_html(page_url)#获取网页HTML
    dir_soup = get_soup(dir_html)#封装到bs中

    # 得到当前页面的图片
    main_image = dir_soup.findAll(name='div', attrs={'class':'main-image'})#找到当前页面下的“main-image”对应的div
    if main_image != None:
        for image_parent in main_image:
            imgs = image_parent.findAll(name='img')#找到img标签的内容
            if imgs != None:
                img_url = str(imgs[0].attrs['src'])#找到第一个img下属性src的值，转换为字符串
                filename = img_url.split('/')[-1]#文件名为src的网址用split分割/，取最后一个作为文件名，避免重复
                print("开始下载:" + img_url + ", 保存为："+filename)
                save_file(name, filename, img_url)#保存

#定义保存图片save_file()
def save_file(name, filename, img_url):
    print(img_url+"=========")
    img = requests.get(img_url)#获取图片
    name = str(name+"/"+filename)#文件夹名
    #with expresion as variable
    with open(name, "wb") as code:
        code.write(img.content)

#download_imgs(info):下载图片函数info为一个字典（相册列表）
def download_imgs(info):
    if info == None:
        return

    name = info[0]#album->alt
    links = info[1]#album->href
    if name == None or links == None:
        return None#获取内容失败
    print("正在创建相册：" + name +" " + links)
    #异常处理
    try:
        os.mkdir(name)#当前目录创建文件夹 还有makedirs(path[,mode]) mode默认0777
    except Exception as e:
        print("文件夹："+name+"，已经存在了，呱唧~")
    print("正在获取相册《" + name + "》内，图片的数量...")
    dir_html = get_html(links)#获取网页内容，返回HTML
    dir_soup = get_soup(dir_html)#编码HTML，封装到bs中
    img_page_url = get_album_num(links, dir_soup)#获取当前相册下的照片数量
    '''
    # 得到当前相册的封面,Just for a test!
    main_image = dir_soup.findAll(name='div', attrs={'class':'main-image'})
    if None != main_image:
        for image_parent in main_image:
        imgs = image_parent.findAll(name='img')
            if None != imgs:
                img_url = str(imgs[0].attrs['src'])
                filename = img_url.split('/')[-1]
                print("开始下载:" + img_url + ", 保存为："+filename)
                save_file(t, filename, img_url)'''

    # 获取相册下的图片
    for photo_web_url in img_page_url:
        download_img_from_page(name, photo_web_url)

#main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()#命令行下
    parser.add_argument("echo")
    # parser.add_argument("url")
    # url = int(args.url)
    args = parser.parse_args()
    url = str(args.echo)
    print("开始解析：" + url)

    html = get_html(url)#获取用户输入的链接的相册列表网页
    soup = get_soup(html)#封装至bs
    img_dirs = get_img_dirs(soup)#获取相册的名字及链接
    if img_dirs == None:
        print("呱唧!无法获取该网页下的相册内容...")
    else:
        for d in img_dirs:
            my_thread = MuchThread(download_imgs, (d, img_dirs.get(d)))
            my_thread.start()
            my_thread.join()
