<?php
	session_start();

	$_SESSION['user'] = getenv("username");
	echo getenv("username");
	echo "User created";
?>