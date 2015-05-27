# AMapBMap

Two functions are provided to transform the AMap(Gaode) coordination to BMap(Baidu) coordination: 1. a function; 2. using the API provided by Gaode & Baidu
You could find the details about the APIs here: http://developer.baidu.com/map/index.php?title=webapi/guide/changeposition, http://bbs.amap.com/thread-18617-1-1.html

A sample program is provided to test the difference between the two functions: 1. In original GPS coordination, choose 1k * 1k nodes, 2. first covert the node to Gaode Coordination mar_node, then convert mar_node to ba