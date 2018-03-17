<!doctype HTML>
<html>
<head>
<title>Criar um novo post</title>
</head>
<body>
<form action="/newpost" method="POST">
<h2>Title</h2>
<input type="text" name="subject" size="120" value="{{subject}}"><br>
<h2>Blog Entry<h2>
<textarea name="body" cols="120" rows="20">{{body}}</textarea><br>
<h2>Tags</h2>
Separados por virgula, por favor<br>
<input type="text" name="tags" size="120" value="{{tags}}"><br>
<h2>Category</h2>
 <select name="category">
 %for category in categories:
  <option value="{{category['name']}}">{{category['name']}}</option>
%end
</select> 
<p>


<input type="submit" value="Submit">

</body>
</html>