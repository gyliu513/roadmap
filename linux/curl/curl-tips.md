 
cURL是我在Linux上经常用的一个小工具，我理解它是一个“客户端”。今天记录一下我的使用心得。达人请忽略。

cURL是一个利用URL语法在命令行方式下工作的文件传输工具。它支持很多协议：FTP,  FTPS,  HTTP, HTTPS, GOPHER等。

## 场景一：测试域名绑定

我常需要在开发环境中，测试某台服务器上的Web Server是否正确绑定了域名。比如，我希望在服务器192.168.1.10上绑定www.kuqin.com。但需要修改hosts才能看到效果，这活儿很累人。

所谓“域名绑定”，就是把host映射到对应的目录。如果手头有cURL，可以使用 -H 参数，在请求头信息中多写一个 Host 字段。就可以测试是否配置正确了。
```
# curl -H "Host: www.kuqin.com" http://192.168.1.10/
```

## 场景二：查看头信息

响应头信息中包含了很多东西。除了HTTP版本和响应代码，还有Server、Content-Type、Content-Length等信息，如果有写入Cookie的操作，也会体现在头信息中。

使用cURL的 -I 参数，就可以看到这些头信息。比如淘宝的：
```
# curl -I http://www.taobao.com/
HTTP/1.1 200 OK
Date: Sun, 14 Feb 2010 08:57:35 GMT
Server: Apache
Set-Cookie: abt=b; expires=Sun, 28-Feb-2010 08:57:35 GMT; path=/; domain=www.taobao.com
at_catetype: b (咦，这是什么？)
Set-Cookie: _lang=zh_CN:GBK; Domain=.taobao.com; Path=/
Cache-Control: max-age=3600
Expires: Sun, 14 Feb 2010 09:57:35 GMT
Vary: Accept-Encoding
Content-Type: text/html; charset=GB2312
Content-Language: cn
```
我昨天也修改了一下我服务器的server信息，大家感兴趣可以 `curl -I http://www.kuqin.com/` 看看。

这里插一句，不建议把使用Web服务器的版本暴露出来（其实服务器信息也最好隐藏掉，或者把Apache伪装成nginx什么的  ）。免得突然爆出漏洞时，措手不及，被人利用。

## 场景三：跟踪URL跳转

如果遇到了一个多次跳转的URL，可以先用curl的 -L 参数看看，这个URL最终跳转到了什么地方。-L 参数最好配合 -I 使用，不然cURL会把最后一次请求获得的数据输出到控制台。

没有合适的URL拿来做例子，意会一下吧 

## 场景四：发送压缩的请求

cURL提供了一个 –compress 参数，可以用来发送支持压缩的请求。但使用了–compress之后，虽然传输过程是压缩的，cURL的输出还是解压之后的，难以看到效果。

我一般用 -H 参数，自己写一个 Accept-Encoding 字段在头信息中。
```
curl -H "Accept-Encoding: gzip" http://www.kuqin.com/
```
如果直接运行上面的命令，会得到一堆乱码，因为cURL输出的内容，是压缩后的数据。不妨在后面接一个gunzip试试。
```
curl -H "Accept-Encoding: gzip" http://www.kuqin.com/ | gunzip
```
使用gunzip解压之后，信息又被还原了。

## 场景五：忽略证书错误

平日上网，遇到证书错误一定要小心。但我在工作中，经常需要用自签的假证书搭建开发环境。cURL在遇到证书错误时罢工，使用 -k 参数就可以让它不做证书校验。
