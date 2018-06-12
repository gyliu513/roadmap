https://en.wikipedia.org/wiki/Server_Name_Indication

Server Name Indication (SNI) is an extension to the TLS computer networking protocol[1] by which a client indicates which hostname it is attempting to connect to at the start of the handshaking process. This allows a server to present multiple certificates on the same IP address and TCP port number and hence allows multiple secure (HTTPS) websites (or any other service over TLS) to be served by the same IP address without requiring all those sites to use the same certificate. It is the conceptual equivalent to HTTP/1.1 name-based virtual hosting, but for HTTPS. The desired hostname is not encrypted,[2] so an eavesdropper can see which site is being requested.

https://blog.csdn.net/gufachongyang02/article/details/52708964

SNI（Server Name Indication）是一个对TLS计算机网络协议的扩展。握手过程开始时，通过这个协议一个客户端能够指示哪个主机名是它试图去链接的主机名。这允许一个服务器在同一个ip地址和tcp端口号的情况下能够拥有多个证书，因此允许多个安全的（https）网站（或其它使用TLS的服务）在使用同一个ip地址的情况下提供服务，但不要求所有这些网站使用相同的证书。这个机制在概念上等效于HTTP/1.1基于名称的虚拟主机，但对于HTTPS，被请求的主机名称是没有被加密的，所以一个窃听者能够看出那个网站正在被请求。


为了让SNI可用，与其它任何协议一样，绝大多数的访问者必须使用实现了SNI机制的web浏览器。这些没有实现SNI的浏览器的用户，提供了一个默认的证书，因此很可能接收到证书的告警。

https://blog.csdn.net/makenothing/article/details/53292335
