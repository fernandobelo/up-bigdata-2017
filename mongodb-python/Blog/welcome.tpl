<!DOCTYPE html>

<html>
<head>
<title>Welcome</title>
<style type="text/css">
.label {text-align: right}
.error {color: red}
</style>

</head>

<body>

%if (username != None):
Welcome {{username}}        <a href="/logout">Logout</a> | <a href="/newpost">New Post</a><p>
%end
<p>
<ul>
<li><a href="/">Goto Blog Home</a></li>
<li>
<a href="/logout">Logout</a>
</li>
<li>
<a href="/newpost">Create a New Post</a>
</li>


</body>

</html>